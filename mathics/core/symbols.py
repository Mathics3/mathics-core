# cython: language_level=3
# -*- coding: utf-8 -*-

import sympy
import time
import typing
from typing import Any, Optional

from mathics.core.attributes import nothing

# I put this constants here instead of inside `mathics.core.convert`
# to avoid a circular reference. Maybe they should be in its own module.

sympy_symbol_prefix = "_Mathics_User_"
sympy_slot_prefix = "_Mathics_Slot_"


# system_symbols('A', 'B', ...) -> [Symbol('System`A'), Symbol('System`B'), ...]
def system_symbols(*symbols) -> typing.FrozenSet[str]:
    """
    Return a frozenset of symbols from a list of names (strings).
    We will use this in testing membership, so an immutable object is fine.

    In 2021, we benchmarked frozenset versus list, tuple, and set and frozenset was the fastest.
    """
    return frozenset(Symbol(s) for s in symbols)


# system_symbols_dict({'SomeSymbol': ...}) -> {Symbol('System`SomeSymbol'): ...}
def system_symbols_dict(d):
    return {Symbol(k): v for k, v in d.items()}


def fully_qualified_symbol_name(name) -> bool:
    """
    Checks if `name` is a fully qualified symbol name.
    """
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


# FIXME: figure out how to split off KeyComparible, BaseExpression and
# Atom from Symbol which is really more "variable"-like in the more
# conventional programming sense of the word.  Also Split off
# SymbolLiteral (the Lisp notion of Symbol, an immutable object like a
# Wolfram Character Symbol) which is distinct from Symbol and seems
# to be intercombined here.


class KeyComparable(object):
    """

    Some Mathics/WL Symbols have an "OrderLess" attribute
    which is used in the evaluation process to arrange items in a list.

    To do that, we need a way to compare Symbols, and that is what
    this class is for.

    This class adds the boilerplate Python comparision operators that
    you expect in Python programs for comparing Python objects.

    This class is not complete in of itself, it is intended to be
    mixed into other classes.

    Each class should provide a `get_sort_key()` method which
    is the primative from which all other comparsions are based on.
    """

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
    """
    This is the base class from which all other Expressions are
    derived from.  If you think of an Expression as tree-like, then a
    BaseExpression is a node in the tree.

    This class is not complete in of itself and subclasses should adapt or fill in
    what is needed

    Some important subclasses: Atom and Expression.
    """

    last_evaluated: Any
    # this variable holds a function defined in mathics.core.expression that creates an expression
    create_expression: Any

    # __new__ seems to be used because this object references itself.
    # In particular:
    #    self.unformatted = self
    #
    # See if there's a way to get rid of this, or ensure that this isn't causing
    # a garbage collection problem.
    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        self.options = None
        self.pattern_sequence = False
        self.unformatted = self  # This may be a garbage-collection nightmare.
        self._cache = None
        return self

    def apply_rules(
        self, rules, evaluation, level=0, options=None
    ) -> typing.Tuple["BaseExpression", bool]:
        """
        Tries to apply one by one the rules in `rules`.
        If one of the rules matches, returns the result and the flag True.
        Otherwise, returns self, False.
        """
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

    def clear_cache(self):
        self._cache = None

    def do_format(self, evaluation, form):
        """
        Applies formats associated to the expression and removes
        superfluous enclosing formats.
        """

        if isinstance(form, str):
            form = Symbol(form)
        formats = format_symbols

        evaluation.inc_recursion_depth()
        try:
            expr = self
            head = self.get_head()
            leaves = self.get_elements()
            include_form = False
            # If the expression is enclosed by a Format
            # takes the form from the expression and
            # removes the format from the expression.
            if head in formats and len(leaves) == 1:
                expr = leaves[0]
                if not (form is SymbolOutputForm and head is SymbolStandardForm):
                    form = head
                    include_form = True
            unformatted = expr
            # If form is Fullform, return it without changes
            if form is SymbolFullForm:
                if include_form:
                    expr = self.create_expression(form, expr)
                    expr.unformatted = unformatted
                return expr

            # Repeated and RepeatedNull confuse the formatter,
            # so we need to hardlink their format rules:
            if head is SymbolRepeated:
                if len(leaves) == 1:
                    return self.create_expression(
                        SymbolHoldForm,
                        self.create_expression(
                            SymbolPostfix,
                            self.create_expression(SymbolList, leaves[0]),
                            "..",
                            170,
                        ),
                    )
                else:
                    return self.create_expression(SymbolHoldForm, expr)
            elif head is SymbolRepeatedNull:
                if len(leaves) == 1:
                    return self.create_expression(
                        SymbolHoldForm,
                        self.create_expression(
                            SymbolPostfix,
                            self.create_expression(SymbolList, leaves[0]),
                            "...",
                            170,
                        ),
                    )
                else:
                    return self.create_expression(SymbolHoldForm, expr)

            # If expr is not an atom, looks for formats in its definition
            # and apply them.
            def format_expr(expr):
                if not (expr.is_atom()) and not (expr.head.is_atom()):
                    # expr is of the form f[...][...]
                    return None
                name = expr.get_lookup_name()
                formats = evaluation.definitions.get_formats(name, form.get_name())
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
            head = expr.get_head()
            if head in formats:
                expr = expr.do_format(evaluation, form)
            elif (
                head is not SymbolNumberForm
                and not expr.is_atom()
                and head is not SymbolGraphics
                and head is not SymbolGraphics3D
            ):
                # print("Not inside graphics or numberform, and not is atom")
                new_elements = [
                    leaf.do_format(evaluation, form) for leaf in expr.leaves
                ]
                expr = self.create_expression(
                    expr.head.do_format(evaluation, form), *new_elements
                )

            if include_form:
                expr = self.create_expression(form, expr)
            expr.unformatted = unformatted
            return expr
        finally:
            evaluation.dec_recursion_depth()

    def equal2(self, rhs: Any) -> Optional[bool]:
        """
        Mathics two-argument Equal (==)
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

    def evaluate(self, evaluation) -> "BaseExpression":
        """Returns the value of the expression. The subclass must implement this"""
        raise NotImplementedError

    def evaluate_elements(self, evaluation) -> "BaseExpression":
        """
        Create a new expression by evaluating the head and elements of self.
        """
        # comment @mmatera: Just make sense if the Expression has elements...
        return self

    def flatten(self, head, pattern_only=False, callback=None) -> "BaseExpression":
        return self

    def flatten_sequence(self, evaluation) -> "BaseExpression":
        return self

    def flatten_pattern_sequence(self, evaluation) -> "BaseExpression":
        return self

    def format(self, evaluation, form, **kwargs) -> "BaseExpression":
        """
        Applies formats associated to the expression, and then calls Makeboxes
        """
        if isinstance(form, str):
            form = Symbol(form)
        expr = self.do_format(evaluation, form)
        result = self.create_expression(SymbolMakeBoxes, expr, form).evaluate(
            evaluation
        )
        return result

    def get_atoms(self, include_heads=True):
        """
        Returns a list of atoms that appears in the expression.
        """
        # Comment @mmatera:
        # This function is used just in Graphics.apply_makeboxes
        # to check if a graphics expression is composed just by
        # real numbers (or integer) or graphics symbols.
        # Probably, there is a simpler way to implement it without using
        # this method.
        return []

    def get_attributes(self, definitions):
        return nothing

    # Probably, this method shouldn't be here.
    def get_elements(self):
        return []

    def has_changed(self, definitions):
        return True

    def get_head(self):
        return None

    def get_head_name(self):
        raise NotImplementedError

    # Compatibily with old code. Deprecated, but remove after a little bit.
    get_leaves = get_elements

    def get_float_value(self, permit_complex=False):
        return None

    def get_int_value(self):
        return None

    def get_lookup_name(self):
        """
        Returns symbol name of leftmost head. This method is used
        to determine which definition must be asked for rules
        to apply in order to do the evaluation.
        """

        return self.get_name()

    def get_name(self):
        "Returns symbol's name if Symbol instance"

        return ""

    def get_option_values(self, evaluation, allow_symbols=False, stop_on_error=True):
        """
        Build a dictionary of options from an expression.
        For example Symbol("Integrate").get_option_values(evaluation, allow_symbols=True)
        will return a list of options associated to the definition of the symbol "Integrate".
        If self is not an expression,
        """
        # comment @mmatera: The implementation of this is awfull.
        # This general method (in BaseExpression) should be simpler (Numbers does not have Options).
        # The implementation should be move to Symbol and Expression classes.

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

    def get_precision(self) -> None:
        """Returns the default specification for precision in N and other
        numerical functions.  It is expected to be redefined in those
        classes that provide inexact arithmetic like PrecisionReal.

        Here in the default base implementation, `None` is used to indicate that the
        precision is either not defined, or it is exact as in the case of Integer. In either case, the
        values is not "inexact".

        This function is called by method `is_inexact()`.
        """
        return None

    def get_rules_list(self):
        """
        If the expression is of the form {pat1->expr1,... {pat_2,expr2},...}
        return a (python) list of rules.
        """
        from mathics.core.rules import Rule

        # comment mm: This makes sense for expressions, but not for numbers. This should
        # have at most a trivial implementation here, and specialize it
        # in the `Expression` class.

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

    def get_sequence(self):
        """Convert's a WL Sequence into a Python's list of expressions"""
        if self.get_head() is SymbolSequence:
            return self.leaves
        else:
            return [self]

    def get_string_value(self):
        return None

    @property
    def is_zero(self) -> bool:
        return False

    def is_symbol(self) -> bool:
        """Checks if self is a Symbol. Better use isinstance(self, Symbol)"""
        return False

    def is_machine_precision(self) -> bool:
        """Check if the number represents a floating point number"""
        return False

    def is_atom(self) -> bool:
        """Better use isinstance(self, Atom)"""
        return False

    def is_true(self) -> bool:
        """Better use self is SymbolTrue"""
        return False

    def is_numeric(self, evaluation=None) -> bool:
        """Check if the expression is a number. If evaluation is given,
        tries to determine if the expression can be evaluated as a number.
        """
        # used by NumericQ and expression ordering
        return False

    def has_form(self, heads, *element_counts):
        """Check if the expression is of the form Head[l1,...,ln]
        with Head.name in `heads` and a number of leaves according to the specification in
        element_counts.
        """
        return False

    def __hash__(self):
        """
        To allow usage of expression as dictionary keys,
        as in Expression.get_pre_choices
        """
        raise NotImplementedError

    def is_free(self, form, evaluation) -> bool:
        """
        Check if self has a subexpression of the form `form`.
        """
        from mathics.builtin.patterns import item_is_free

        return item_is_free(self, form, evaluation)

    def is_inexact(self) -> bool:
        return self.get_precision() is not None

    def rewrite_apply_eval_step(self, evaluation) -> typing.Tuple["Expression", bool]:
        """
        Performs a since rewrite/apply/eval step used in
        evaluation.

        Here we specialize evaluation so that any results returned
        do not need further evaluation.
        """
        return self.evaluate(evaluation), False

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return id(self) == id(rhs)

    def sequences(self):
        return None

    def user_hash(self, update) -> None:
        # whereas __hash__ is for internal Mathics purposes like using Expressions as dictionary keys and fast
        # comparison of elements, user_hash is called for Hash[]. user_hash should strive to give stable results
        # across versions, whereas __hash__ must not. user_hash should try to hash all the data available, whereas
        # __hash__ might only hash a sample of the data available.
        raise NotImplementedError

    def to_sympy(self, **kwargs):
        raise NotImplementedError

    def to_mpmath(self):
        return None

    def round_to_float(self, evaluation=None, permit_complex=False):
        """
        Try to round to python float. Return None if not possible.
        """
        from mathics.core.atoms import Number

        # comment @mmatera: this method should be
        # specialized on each class. This definition is good for
        # Symbols and Expressions, but for String does not make sense,
        # and for Reals is too complicated.

        if evaluation is None:
            value = self
        elif isinstance(evaluation, sympy.core.numbers.NaN):
            return None
        else:
            value = self.create_expression(SymbolN, self).evaluate(evaluation)
        if isinstance(value, Number):
            value = value.round()
            return value.get_float_value(permit_complex=permit_complex)

    # All these methods are a handy way to build arithmetic ``Expression``s
    # using python syntax. Is handy but maybe could be misleading.

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
    """
    Atoms are the leaves (in the common tree sense, not the Mathics
    ``_elements`` sense) and Heads of an Expression or M-Expression.

    In other words, they are the units of an expression that we cannot
    dig down deeper structurally.  Various object primitives i.e.
    ``ByteArray``, `CompiledCode`` or ``Image`` are atoms.

    Of note is the fact that the Mathics ``Part[]`` function of an
    Atom object does not exist.

    Atom is not a directly-mentioned WL entity, although conceptually
    it very much seems to exist.
    """

    _head_name = ""
    _symbol_head = None
    class_head_name = ""

    def __repr__(self) -> str:
        return "<%s: %s>" % (self.get_atom_name(), self)

    def atom_to_boxes(self, f, evaluation):
        """Produces a Box expression that represents
        how the expression should be formatted."""
        raise NotImplementedError

    def copy(self, reevaluate=False) -> "Atom":
        result = self.do_copy()
        result.original = self
        return result

    def equal2(self, rhs: Any) -> Optional[bool]:
        """Mathics two-argument Equal (==)
        returns True if self and rhs are identical.
        """
        if self.sameQ(rhs):
            return True
        if isinstance(rhs, Symbol) or not isinstance(rhs, Atom):
            return None
        return self == rhs

    def evaluate(self, evaluation) -> "BaseExpression":
        """Returns the value of the expression.

        The value of an Atom is itself.
        """
        return self

    rewrite_apply_eval = evaluate

    def get_atom_name(self) -> str:
        return self.__class__.__name__

    def get_atoms(self, include_heads=True) -> typing.List["Atom"]:
        return [self]

    def get_head(self) -> "Symbol":
        return Symbol(self.class_head_name)

    def get_head_name(self) -> "str":
        return self.class_head_name  # System`" + self.__class__.__name__

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return [0, 0, 1, 1, 0, 0, 0, 1]
        else:
            raise NotImplementedError

    def has_form(self, heads, *element_counts) -> bool:
        if element_counts:
            return False
        name = self.get_atom_name()
        if isinstance(heads, tuple):
            return name in heads
        else:
            return heads == name

    def has_symbol(self, symbol_name) -> bool:
        return False

    def is_atom(self) -> bool:
        return True

    def numerify(self, evaluation) -> "Atom":
        return self

    def replace_vars(self, vars, options=None, in_scoping=True) -> "Atom":
        return self

    def replace_slots(self, slots, evaluation) -> "Atom":
        return self


class Symbol(Atom):
    """
    Note: Symbol is right now used in a couple of ways which in the
    future may be separated.

    A Symbol is a kind of Atom that acts as a symbolic variable or
    symbolic constant.

    All Symbols have a name that can be converted to string form.

    Inside a session, a Symbol can be associated with a ``Definition``
    that determines its evaluation value.

    We also have Symbols which are immutable or constant; here the
    definitions are fixed. The predefined Symbols ``True``, ``False``,
    and ``Null`` are like this.

    Also there are situations where the Symbol acts like Python's
    intern() built-in function or Lisp's Symbol without its modifyable
    property list.  Here, the only attribute we care about is the name
    which is unique across all mentions and uses, and therefore
    needs it only to be stored as a single object in the system.

    Note that the mathics.core.parser.Symbol works exactly this way.

    This aspect may or may not be true for the Symbolic Variable use case too.
    """

    name: str
    sympy_dummy: Any
    defined_symbols = {}
    class_head_name = "System`Symbol"

    # __new__ instead of __init__ is used here because we want
    # to return the same object for a given "name" value.
    def __new__(cls, name, sympy_dummy=None):
        """
        Allocate an object ensuring that for a given `name` we get back the same object.
        """
        name = ensure_context(name)
        self = cls.defined_symbols.get(name, None)
        if self is None:
            self = super(Symbol, cls).__new__(cls)
            self.name = name
            self.sympy_dummy = sympy_dummy
            cls.defined_symbols[name] = self
        return self

    def __str__(self) -> str:
        return self.name

    def do_copy(self) -> "Symbol":
        return Symbol(self.name)

    def get_head(self) -> "Symbol":
        return Symbol("Symbol")

    def get_head_name(self):
        return "System`Symbol"

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
        if self is SymbolTrue:
            return True
        if self is SymbolFalse:
            return False
        if self is SymbolNull:
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

        if self is rhs:
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
        return self is rhs

    def __eq__(self, other) -> bool:
        return self is other

    def __ne__(self, other) -> bool:
        return self is not other

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
        """
        Evaluates the symbol by applying the rules (ownvalues) in its definition,
        recursively.
        """
        if evaluation.definitions.trace_evaluation:
            if evaluation.definitions.timing_trace_evaluation:
                evaluation.print_out(time.time() - evaluation.start_time)
            evaluation.print_out(
                "  " * evaluation.recursion_depth + "  Evaluating: %s" % self
            )

        rules = evaluation.definitions.get_ownvalues(self.name)
        for rule in rules:
            result = rule.apply(self, evaluation, fully=True)
            if result is not None and not result.sameQ(self):
                if evaluation.definitions.trace_evaluation:
                    evaluation.print_out(
                        "  " * evaluation.recursion_depth + "  -> %s" % result
                    )
                return result.evaluate(evaluation)
        return self

    def is_true(self) -> bool:
        return self is SymbolTrue

    def is_numeric(self, evaluation=None) -> bool:
        """
        Returns True if the symbol is tagged as a numeric constant.
        """
        if evaluation:
            symbol_definition = evaluation.definitions.get_definition(self.name)
            if symbol_definition is None:
                return False
            return symbol_definition.is_numeric
        return False

    def __hash__(self):
        return hash(("Symbol", self.name))  # to distinguish from String

    def user_hash(self, update) -> None:
        update(b"System`Symbol>" + self.name.encode("utf8"))

    def __getnewargs__(self):
        return (self.name, self.sympy_dummy)


# Symbols used in this module.

SymbolFalse = Symbol("System`False")
SymbolGraphics = Symbol("System`Graphics")
SymbolGraphics3D = Symbol("System`Graphics3D")
SymbolHoldForm = Symbol("System`HoldForm")
SymbolList = Symbol("System`List")
SymbolMachinePrecision = Symbol("MachinePrecision")
SymbolMakeBoxes = Symbol("System`MakeBoxes")
SymbolMaxPrecision = Symbol("$MaxPrecision")
SymbolMinPrecision = Symbol("$MinPrecision")
SymbolN = Symbol("System`N")
SymbolNull = Symbol("System`Null")
SymbolNumberForm = Symbol("System`NumberForm")
SymbolPostfix = Symbol("System`Postfix")
SymbolRepeated = Symbol("System`Repeated")
SymbolRepeatedNull = Symbol("System`RepeatedNull")
SymbolSequence = Symbol("System`Sequence")
SymbolTrue = Symbol("System`True")


# The available formats.

format_symbols = system_symbols(
    "InputForm",
    "OutputForm",
    "StandardForm",
    "FullForm",
    "TraditionalForm",
    "TeXForm",
    "MathMLForm",
)


SymbolInputForm = Symbol("InputForm")
SymbolOutputForm = Symbol("OutputForm")
SymbolStandardForm = Symbol("StandardForm")
SymbolFullForm = Symbol("FullForm")
SymbolTraditionalForm = Symbol("TraditionalForm")
SymbolTeXForm = Symbol("TeXForm")
SymbolMathMLForm = Symbol("MathMLForm")
