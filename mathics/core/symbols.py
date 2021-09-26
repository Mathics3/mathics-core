# cython: language_level=3
# -*- coding: utf-8 -*-

import sympy

import typing
from typing import Any, Optional

from mathics.core.convert import sympy_symbol_prefix


# system_symbols('A', 'B', ...) -> ['System`A', 'System`B', ...]
def system_symbols(*symbols) -> typing.List[str]:
    return [ensure_context(s) for s in symbols]


# system_symbols_dict({'SomeSymbol': ...}) -> {'System`SomeSymbol': ...}
def system_symbols_dict(d):
    return {ensure_context(k): v for k, v in d.items()}


def fully_qualified_symbol_name(name) -> bool:
    return (
        isinstance(name, str)
        and "`" in name
        and not name.startswith("`")
        and not name.endswith("`")
        and "``" not in name
    )


def valid_context_name(ctx, allow_initial_backquote=False) -> bool:
    return (
        isinstance(ctx, str)
        and ctx.endswith("`")
        and "``" not in ctx
        and (allow_initial_backquote or not ctx.startswith("`"))
    )


def ensure_context(name, context="System`") -> str:
    assert isinstance(name, str)
    assert name != ""
    if "`" in name:
        # Symbol has a context mark -> it came from the parser
        assert fully_qualified_symbol_name(name)
        return name
    # Symbol came from Python code doing something like
    # Expression('Plus', ...) -> use System` or more generally
    # context + name
    return context + name


def strip_context(name) -> str:
    if "`" in name:
        return name[name.rindex("`") + 1 :]
    return name


class KeyComparable(object):
    def get_sort_key(self):
        raise NotImplementedError

    def __lt__(self, other) -> bool:
        return self.get_sort_key() < other.get_sort_key()

    def __gt__(self, other) -> bool:
        return self.get_sort_key() > other.get_sort_key()

    def __le__(self, other) -> bool:
        return self.get_sort_key() <= other.get_sort_key()

    def __ge__(self, other) -> bool:
        return self.get_sort_key() >= other.get_sort_key()

    def __eq__(self, other) -> bool:
        return (
            hasattr(other, "get_sort_key")
            and self.get_sort_key() == other.get_sort_key()
        )

    def __ne__(self, other) -> bool:
        return (
            not hasattr(other, "get_sort_key")
        ) or self.get_sort_key() != other.get_sort_key()


class BaseExpression(KeyComparable):
    options: Any
    pattern_sequence: bool
    unformatted: Any
    last_evaluated: Any
    # this variable holds a function defined in mathics.core.expression that creates an expression
    create_expression: Any

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        self.options = None
        self.pattern_sequence = False
        self.unformatted = self
        self._cache = None
        return self

    def clear_cache(self):
        self._cache = None

    def equal2(self, rhs: Any) -> Optional[bool]:
        """Mathics two-argument Equal (==)
        returns True if self and rhs are identical.
        """
        if self.sameQ(rhs):
            return True

        # If the types are the same then we'll use the classes definition of == (or __eq__).
        # Superclasses which need to specialized this behavior should redefine equal2()
        #
        # I would use `is` instead `==` here, to compare classes.
        if type(self) is type(rhs):
            return self == rhs
        return None

    def has_changed(self, definitions):
        return True

    def sequences(self):
        return None

    def flatten_sequence(self, evaluation) -> "BaseExpression":
        return self

    def flatten_pattern_sequence(self, evaluation) -> "BaseExpression":
        return self

    def get_attributes(self, definitions):
        return set()

    def evaluate_next(self, evaluation):
        return self.evaluate(evaluation), False

    def evaluate(self, evaluation) -> "BaseExpression":
        evaluation.check_stopped()
        return self

    def get_atoms(self, include_heads=True):
        return []

    def get_name(self):
        "Returns symbol's name if Symbol instance"

        return ""

    def is_symbol(self) -> bool:
        return False

    def is_machine_precision(self) -> bool:
        return False

    def get_lookup_name(self):
        "Returns symbol name of leftmost head"

        return self.get_name()

    def get_head(self):
        return None

    def get_head_name(self):
        return self.get_head().get_name()

    def get_leaves(self):
        return []

    def get_int_value(self):
        return None

    def get_float_value(self, permit_complex=False):
        return None

    def get_string_value(self):
        return None

    def is_atom(self) -> bool:
        return False

    def is_true(self) -> bool:
        return False

    def is_numeric(self, evaluation=None) -> bool:
        # used by NumericQ and expression ordering
        return False

    def has_form(self, heads, *leaf_counts):
        return False

    def flatten(self, head, pattern_only=False, callback=None) -> "BaseExpression":
        return self

    def __hash__(self):
        """
        To allow usage of expression as dictionary keys,
        as in Expression.get_pre_choices
        """
        raise NotImplementedError

    def user_hash(self, update) -> None:
        # whereas __hash__ is for internal Mathics purposes like using Expressions as dictionary keys and fast
        # comparison of elements, user_hash is called for Hash[]. user_hash should strive to give stable results
        # across versions, whereas __hash__ must not. user_hash should try to hash all the data available, whereas
        # __hash__ might only hash a sample of the data available.
        raise NotImplementedError

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return id(self) == id(rhs)

    def get_sequence(self):
        if self.get_head().get_name() == "System`Sequence":
            return self.leaves
        else:
            return [self]

    def evaluate_leaves(self, evaluation) -> "BaseExpression":
        return self

    def apply_rules(
        self, rules, evaluation, level=0, options=None
    ) -> typing.Tuple["BaseExpression", bool]:
        if options:
            l1, l2 = options["levelspec"]
            if level < l1:
                return self, False
            elif l2 is not None and level > l2:
                return self, False

        for rule in rules:
            result = rule.apply(self, evaluation, fully=False)
            if result is not None:
                return result, True
        return self, False

    def do_format(self, evaluation, form):
        """
        Applies formats associated to the expression and removes
        superfluous enclosing formats.
        """

        formats = system_symbols(
            "InputForm",
            "OutputForm",
            "StandardForm",
            "FullForm",
            "TraditionalForm",
            "TeXForm",
            "MathMLForm",
        )

        evaluation.inc_recursion_depth()
        try:
            expr = self
            head = self.get_head_name()
            leaves = self.get_leaves()
            include_form = False
            # If the expression is enclosed by a Format
            # takes the form from the expression and
            # removes the format from the expression.
            if head in formats and len(leaves) == 1:
                expr = leaves[0]
                if not (form == "System`OutputForm" and head == "System`StandardForm"):
                    form = head
                    include_form = True
            unformatted = expr
            # If form is Fullform, return it without changes
            if form == "System`FullForm":
                if include_form:
                    expr = self.create_expression(form, expr)
                    expr.unformatted = unformatted
                return expr

            # Repeated and RepeatedNull confuse the formatter,
            # so we need to hardlink their format rules:
            if head == "System`Repeated":
                if len(leaves) == 1:
                    return self.create_expression(
                        "System`HoldForm",
                        self.create_expression(
                            "System`Postfix",
                            self.create_expression("System`List", leaves[0]),
                            "..",
                            170,
                        ),
                    )
                else:
                    return self.create_expression("System`HoldForm", expr)
            elif head == "System`RepeatedNull":
                if len(leaves) == 1:
                    return self.create_expression(
                        "System`HoldForm",
                        self.create_expression(
                            "System`Postfix",
                            self.create_expression("System`List", leaves[0]),
                            "...",
                            170,
                        ),
                    )
                else:
                    return self.create_expression("System`HoldForm", expr)

            # If expr is not an atom, looks for formats in its definition
            # and apply them.
            def format_expr(expr):
                if not (expr.is_atom()) and not (expr.head.is_atom()):
                    # expr is of the form f[...][...]
                    return None
                name = expr.get_lookup_name()
                formats = evaluation.definitions.get_formats(name, form)
                for rule in formats:
                    result = rule.apply(expr, evaluation)
                    if result is not None and result != expr:
                        return result.evaluate(evaluation)
                return None

            formatted = format_expr(expr)
            if formatted is not None:
                result = formatted.do_format(evaluation, form)
                if include_form:
                    result = self.create_expression(form, result)
                result.unformatted = unformatted
                return result

            # If the expression is still enclosed by a Format,
            # iterate.
            # If the expression is not atomic or of certain
            # specific cases, iterate over the leaves.
            head = expr.get_head_name()
            if head in formats:
                expr = expr.do_format(evaluation, form)
            elif (
                head != "System`NumberForm"
                and not expr.is_atom()
                and head != "System`Graphics"
                and head != "System`Graphics3D"
            ):
                # print("Not inside graphics or numberform, and not is atom")
                new_leaves = [leaf.do_format(evaluation, form) for leaf in expr.leaves]
                expr = self.create_expression(
                    expr.head.do_format(evaluation, form), *new_leaves
                )

            if include_form:
                expr = self.create_expression(form, expr)
            expr.unformatted = unformatted
            return expr
        finally:
            evaluation.dec_recursion_depth()

    def format(self, evaluation, form, **kwargs) -> "BaseExpression":
        """
        Applies formats associated to the expression, and then calls Makeboxes
        """

        expr = self.do_format(evaluation, form)
        result = self.create_expression(SymbolMakeBoxes, expr, Symbol(form)).evaluate(
            evaluation
        )
        return result

    def is_free(self, form, evaluation) -> bool:
        from mathics.builtin.patterns import item_is_free

        return item_is_free(self, form, evaluation)

    def is_inexact(self) -> bool:
        return self.get_precision() is not None

    def get_precision(self):
        return None

    def get_option_values(self, evaluation, allow_symbols=False, stop_on_error=True):
        from mathics.core.atoms import String

        options = self
        if options.has_form("List", None):
            options = options.flatten(SymbolList)
            values = options.leaves
        else:
            values = [options]
        option_values = {}
        for option in values:
            symbol_name = option.get_name()
            if allow_symbols and symbol_name:
                options = evaluation.definitions.get_options(symbol_name)
                option_values.update(options)
            else:
                if not option.has_form(("Rule", "RuleDelayed"), 2):
                    if stop_on_error:
                        return None
                    else:
                        continue
                name = option.leaves[0].get_name()
                if not name and isinstance(option.leaves[0], String):
                    name = ensure_context(option.leaves[0].get_string_value())
                if not name:
                    if stop_on_error:
                        return None
                    else:
                        continue
                option_values[name] = option.leaves[1]
        return option_values

    def get_rules_list(self):
        from mathics.core.rules import Rule

        list_expr = self.flatten(SymbolList)
        list = []
        if list_expr.has_form("List", None):
            list.extend(list_expr.leaves)
        else:
            list.append(list_expr)
        rules = []
        for item in list:
            if not item.has_form(("Rule", "RuleDelayed"), 2):
                return None
            rule = Rule(item.leaves[0], item.leaves[1])
            rules.append(rule)
        return rules

    def to_sympy(self, **kwargs):
        raise NotImplementedError

    def to_mpmath(self):
        return None

    def round_to_float(self, evaluation=None, permit_complex=False):
        """
        Try to round to python float. Return None if not possible.
        """
        from mathics.core.atoms import Number

        if evaluation is None:
            value = self
        elif isinstance(evaluation, sympy.core.numbers.NaN):
            return None
        else:
            value = self.create_expression(SymbolN, self).evaluate(evaluation)
        if isinstance(value, Number):
            value = value.round()
            return value.get_float_value(permit_complex=permit_complex)

    def __abs__(self) -> "BaseExpression":
        return self.create_expression("Abs", self)

    def __pos__(self):
        return self

    def __neg__(self):
        return self.create_expression("Times", self, -1)

    def __add__(self, other) -> "BaseExpression":
        return self.create_expression("Plus", self, other)

    def __sub__(self, other) -> "BaseExpression":
        return self.create_expression(
            "Plus", self, self.create_expression("Times", other, -1)
        )

    def __mul__(self, other) -> "BaseExpression":
        return self.create_expression("Times", self, other)

    def __truediv__(self, other) -> "BaseExpression":
        return self.create_expression("Divide", self, other)

    def __floordiv__(self, other) -> "BaseExpression":
        return self.create_expression(
            "Floor", self.create_expression("Divide", self, other)
        )

    def __pow__(self, other) -> "BaseExpression":
        return self.create_expression("Power", self, other)


class Monomial(object):
    """
    An object to sort monomials, used in Expression.get_sort_key and
    Symbol.get_sort_key.
    """

    def __init__(self, exps_dict):
        self.exps = exps_dict

    def __lt__(self, other) -> bool:
        return self.__cmp(other) < 0

    def __gt__(self, other) -> bool:
        return self.__cmp(other) > 0

    def __le__(self, other) -> bool:
        return self.__cmp(other) <= 0

    def __ge__(self, other) -> bool:
        return self.__cmp(other) >= 0

    def __eq__(self, other) -> bool:
        return self.__cmp(other) == 0

    def __ne__(self, other) -> bool:
        return self.__cmp(other) != 0

    def __cmp(self, other) -> int:
        self_exps = self.exps.copy()
        other_exps = other.exps.copy()
        for var in self.exps:
            if var in other.exps:
                dec = min(self_exps[var], other_exps[var])
                self_exps[var] -= dec
                if not self_exps[var]:
                    del self_exps[var]
                other_exps[var] -= dec
                if not other_exps[var]:
                    del other_exps[var]
        self_exps = sorted((var, exp) for var, exp in self_exps.items())
        other_exps = sorted((var, exp) for var, exp in other_exps.items())

        index = 0
        self_len = len(self_exps)
        other_len = len(other_exps)
        while True:
            if index >= self_len and index >= other_len:
                return 0
            if index >= self_len:
                return -1  # self < other
            if index >= other_len:
                return 1  # self > other
            self_var, self_exp = self_exps[index]
            other_var, other_exp = other_exps[index]
            if self_var < other_var:
                return -1
            if self_var > other_var:
                return 1
            if self_exp != other_exp:
                if index + 1 == self_len or index + 1 == other_len:
                    # smaller exponents first
                    if self_exp < other_exp:
                        return -1
                    elif self_exp == other_exp:
                        return 0
                    else:
                        return 1
                else:
                    # bigger exponents first
                    if self_exp < other_exp:
                        return 1
                    elif self_exp == other_exp:
                        return 0
                    else:
                        return -1
            index += 1
        return 0


class Atom(BaseExpression):
    def is_atom(self) -> bool:
        return True

    def equal2(self, rhs: Any) -> Optional[bool]:
        """Mathics two-argument Equal (==)
        returns True if self and rhs are identical.
        """
        if self.sameQ(rhs):
            return True
        if isinstance(rhs, Symbol) or not isinstance(rhs, Atom):
            return None
        return self == rhs

    def has_form(self, heads, *leaf_counts) -> bool:
        if leaf_counts:
            return False
        name = self.get_atom_name()
        if isinstance(heads, tuple):
            return name in heads
        else:
            return heads == name

    def has_symbol(self, symbol_name) -> bool:
        return False

    def get_head(self) -> "Symbol":
        return Symbol(self.get_atom_name())

    def get_atom_name(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "<%s: %s>" % (self.get_atom_name(), self)

    def replace_vars(self, vars, options=None, in_scoping=True) -> "Atom":
        return self

    def replace_slots(self, slots, evaluation) -> "Atom":
        return self

    def numerify(self, evaluation) -> "Atom":
        return self

    def copy(self, reevaluate=False) -> "Atom":
        result = self.do_copy()
        result.original = self
        return result

    def set_positions(self, position=None) -> None:
        self.position = position

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return [0, 0, 1, 1, 0, 0, 0, 1]
        else:
            raise NotImplementedError

    def get_atoms(self, include_heads=True) -> typing.List["Atom"]:
        return [self]

    def atom_to_boxes(self, f, evaluation):
        raise NotImplementedError


class Symbol(Atom):
    name: str
    sympy_dummy: Any
    defined_symbols = {}

    def __new__(cls, name, sympy_dummy=None):
        name = ensure_context(name)
        self = cls.defined_symbols.get(name, None)
        if self is None:
            self = super(Symbol, cls).__new__(cls)
            self.name = name
            self.sympy_dummy = sympy_dummy
            # cls.defined_symbols[name] = self
        return self

    def __str__(self) -> str:
        return self.name

    def do_copy(self) -> "Symbol":
        return Symbol(self.name)

    def boxes_to_text(self, **options) -> str:
        return str(self.name)

    def atom_to_boxes(self, f, evaluation) -> "String":
        from mathics.core.atoms import String

        return String(evaluation.definitions.shorten_name(self.name))

    def to_sympy(self, **kwargs):
        from mathics.builtin import mathics_to_sympy

        if self.sympy_dummy is not None:
            return self.sympy_dummy

        builtin = mathics_to_sympy.get(self.name)
        if (
            builtin is None
            or not builtin.sympy_name
            or not builtin.is_constant()  # nopep8
        ):
            return sympy.Symbol(sympy_symbol_prefix + self.name)
        return builtin.to_sympy(self, **kwargs)

    def to_python(self, *args, **kwargs):
        if self == SymbolTrue:
            return True
        if self == SymbolFalse:
            return False
        if self == SymbolNull:
            return None
        n_evaluation = kwargs.get("n_evaluation")
        if n_evaluation is not None:
            value = self.create_expression(SymbolN, self).evaluate(n_evaluation)
            return value.to_python()

        if kwargs.get("python_form", False):
            return self.to_sympy(**kwargs)
        else:
            return self.name

    def default_format(self, evaluation, form) -> str:
        return self.name

    def get_attributes(self, definitions):
        return definitions.get_attributes(self.name)

    def get_name(self) -> str:
        return self.name

    def is_symbol(self) -> bool:
        return True

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return super(Symbol, self).get_sort_key(True)
        else:
            return [
                1 if self.is_numeric() else 2,
                2,
                Monomial({self.name: 1}),
                0,
                self.name,
                1,
            ]

    def equal2(self, rhs: Any) -> Optional[bool]:
        """Mathics two-argument Equal (==)"""

        if self.sameQ(rhs):
            return True

        # Booleans are treated like constants, but all other symbols
        # are treated None. We could create a Bool class and
        # define equal2 in that, but for just this doesn't
        # seem to be worth it. If other things come up, this may change.
        if self in (SymbolTrue, SymbolFalse) and rhs in (SymbolTrue, SymbolFalse):
            return self == rhs
        return None

    def sameQ(self, rhs: Any) -> bool:
        """Mathics SameQ"""
        return id(self) == id(rhs) or isinstance(rhs, Symbol) and self.name == rhs.name

    def replace_vars(self, vars, options={}, in_scoping=True):
        assert all(fully_qualified_symbol_name(v) for v in vars)
        var = vars.get(self.name, None)
        if var is None:
            return self
        else:
            return var

    def has_symbol(self, symbol_name) -> bool:
        return self.name == ensure_context(symbol_name)

    def evaluate(self, evaluation):
        rules = evaluation.definitions.get_ownvalues(self.name)
        for rule in rules:
            result = rule.apply(self, evaluation, fully=True)
            if result is not None and not result.sameQ(self):
                return result.evaluate(evaluation)
        return self

    def is_true(self) -> bool:
        return self == Symbol("True")

    def is_numeric(self, evaluation=None) -> bool:
        return self.name in system_symbols(
            "Pi", "E", "EulerGamma", "GoldenRatio", "MachinePrecision", "Catalan"
        )

    def __hash__(self):
        return hash(("Symbol", self.name))  # to distinguish from String

    def user_hash(self, update) -> None:
        update(b"System`Symbol>" + self.name.encode("utf8"))

    def __getnewargs__(self):
        return (self.name, self.sympy_dummy)


SymbolFalse = Symbol("System`False")
SymbolList = Symbol("System`List")
SymbolMakeBoxes = Symbol("System`MakeBoxes")
SymbolN = Symbol("System`N")
SymbolNull = Symbol("System`Null")
SymbolTrue = Symbol("System`True")
