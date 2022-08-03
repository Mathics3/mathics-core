# cython: language_level=3
# -*- coding: utf-8 -*-

import sympy
import time
import typing
from typing import Any, Optional

from mathics.core.element import (
    BaseElement,
    EvalMixin,
    ensure_context,
    fully_qualified_symbol_name,
)

# I put this constants here instead of inside `mathics.core.convert.sympy`
# to avoid a circular reference. Maybe they should be in its own module.

sympy_symbol_prefix = "_Mathics_User_"
sympy_slot_prefix = "_Mathics_Slot_"


# FIXME: This is repeated below
class NumericOperators:
    """
    This is a mixin class for Element-like objects that might have numeric values.
    It adds or "mixes in" numeric functions for these objects like round_to_float().

    It also adds methods to the class to facilite building
    ``Expression``s in the Mathics Python code using Python syntax.

    So for example, instead of writing in Python:

        to_expression("Abs", -8)
        Expression(SymbolPlus, Integer1, Integer2)

    you can instead have:
        abs(Integer(-8))
        Integer(1) + Integer(2)
    """

    def __abs__(self) -> BaseElement:
        return self.create_expression(SymbolAbs, self)

    def __add__(self, other) -> BaseElement:
        return self.create_expression(SymbolPlus, self, other)

    def __pos__(self):
        return self

    def __neg__(self):
        from mathics.core.atoms import IntegerM1

        return self.create_expression(SymbolTimes, self, IntegerM1)

    def __sub__(self, other) -> BaseElement:
        from mathics.core.atoms import IntegerM1

        return self.create_expression(
            SymbolPlus, self, self.create_expression(SymbolTimes, other, IntegerM1)
        )

    def __mul__(self, other) -> BaseElement:
        return self.create_expression(SymbolTimes, self, other)

    def __truediv__(self, other) -> BaseElement:
        return self.create_expression(SymbolDivide, self, other)

    def __floordiv__(self, other) -> BaseElement:
        return self.create_expression(
            SymbolFloor, self.create_expression(SymbolDivide, self, other)
        )

    def __pow__(self, other) -> BaseElement:
        return self.create_expression(SymbolPower, self, other)

    def round_to_float(self, evaluation=None, permit_complex=False) -> Optional[float]:
        """
        Round to a Python float. Return None if rounding is not possible.
        This can happen if self or evaluation is NaN.
        """
        value = (
            self
            if evaluation is None
            else self.create_expression(SymbolN, self).evaluate(evaluation)
        )
        if hasattr(value, "round") and hasattr(value, "get_float_value"):
            value = value.round()
            return value.get_float_value(permit_complex=permit_complex)
        return None


# system_symbols_dict({'SomeSymbol': ...}) -> {Symbol('System`SomeSymbol'): ...}
def system_symbols_dict(d):
    return {Symbol(k): v for k, v in d.items()}


def valid_context_name(ctx, allow_initial_backquote=False) -> bool:
    return (
        isinstance(ctx, str)
        and ctx.endswith("`")
        and "``" not in ctx
        and (allow_initial_backquote or not ctx.startswith("`"))
    )


def strip_context(name) -> str:
    if "`" in name:
        return name[name.rindex("`") + 1 :]
    return name


class Monomial:
    """
    An object to sort monomials, used in Expression.get_sort_key and
    Symbol.get_sort_key.
    """

    def __init__(self, exps_dict):
        self.exps = exps_dict

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

    def __eq__(self, other) -> bool:
        return self.__cmp(other) == 0

    def __le__(self, other) -> bool:
        return self.__cmp(other) <= 0

    def __lt__(self, other) -> bool:
        return self.__cmp(other) < 0

    def __ge__(self, other) -> bool:
        return self.__cmp(other) >= 0

    def __gt__(self, other) -> bool:
        return self.__cmp(other) > 0

    def __ne__(self, other) -> bool:
        return self.__cmp(other) != 0


class Atom(BaseElement):
    """
    Atoms are the (some) leaves and the Heads of an S-Expression or an M-Expression.

    In other words, they are the expression's elements (leaves of the
    expression) which we cannot dig down deeper structurally.

    Of note is the fact that the Mathics ``Part[]`` function of an
    Atom object does not exist.

    Atom is not a directly-mentioned WL entity, although conceptually
    it very much seems to exist.

    The other kinds expression element is a Builtin, e.g. `ByteArray``, `CompiledCode`` or ``Image``.
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

    def evaluate(self, evaluation) -> BaseElement:
        """Returns the value of the expression.

        The value of an Atom is itself.
        """
        return self

    # comment @mmatera: This just makes sense if the Expression has elements...
    # rocky: It is currently getting called when on Atoms; so more work
    # is needed to remove this, probably by fixing the callers.
    def evaluate_elements(self, evaluation) -> "Atom":
        """
        Create a new expression by evaluating the head and elements of self.
        """
        return self

    def get_atom_name(self) -> str:
        return self.__class__.__name__

    def get_atoms(self, include_heads=True) -> typing.List["Atom"]:
        return [self]

    # We seem to need this because the caller doesn't distinguish something with elements
    # from a single atom.
    def get_elements(self):
        return []

    # Compatibility with old code. Deprecated, but remove after a little bit.
    get_leaves = get_elements

    def get_head(self) -> "Symbol":
        return Symbol(self.class_head_name)

    def get_head_name(self) -> "str":
        return self.class_head_name  # System`" + self.__class__.__name__

    #    def get_option_values(self, evaluation, allow_symbols=False, stop_on_error=True):
    #        """
    #        Build a dictionary of options from an expression.
    #        For example Symbol("Integrate").get_option_values(evaluation, allow_symbols=True)
    #        will return a list of options associated to the definition of the symbol "Integrate".
    #        If self is not an expression,
    #        """
    #        print("get_option_values is trivial for ", (self, stop_on_error, allow_symbols ))
    #        1/0
    #        return None if stop_on_error else {}

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return (0, 0, 1, 1, 0, 0, 0, 1)
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

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a `definitions`
        parameter.

        Most Atoms, like Numbers and Strings, do not need evaluation
        or reevaluation. However some kinds of Atoms like Symbols do
        in general. The Symbol class or any other class that is
        subclassed from here (Atom) then needs to override this method, when
        it might is literal in general.

        """
        return True

    def is_uncertain_final_definitions(self, definitions) -> bool:
        """
        Used in Expression.do_format() to determine if we may need to
        (re)evaluate an expression.

        Most Atoms, like Numbers and Strings, do not need evaluation
        or reevaluation. However some kinds of Atoms like Symbols
        sometimes do. The Symbol class or any other class like this
        that is subclassed from Atom then needs to override this
        method.
        """
        return False

    def numerify(self, evaluation) -> "Atom":
        return self

    def replace_vars(self, vars, options=None, in_scoping=True) -> "Atom":
        return self

    def replace_slots(self, slots, evaluation) -> "Atom":
        return self


class Symbol(Atom, NumericOperators, EvalMixin):
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

    def __eq__(self, other) -> bool:
        return self is other

    def __getnewargs__(self):
        return (self.name, self.sympy_dummy)

    def __hash__(self):
        return hash(("Symbol", self.name))  # to distinguish from String

    def __ne__(self, other) -> bool:
        return self is not other

    def __str__(self) -> str:
        return self.name

    def atom_to_boxes(self, f, evaluation) -> "_BoxedString":
        from mathics.builtin.box.inout import _BoxedString

        return _BoxedString(evaluation.definitions.shorten_name(self.name))

    def default_format(self, evaluation, form) -> str:
        return self.name

    def do_copy(self) -> "Symbol":
        return Symbol(self.name)

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

    def get_head(self) -> "Symbol":
        return Symbol("Symbol")

    def get_head_name(self):
        return "System`Symbol"

    def get_option_values(self, evaluation, allow_symbols=False, stop_on_error=True):
        """
        Build a dictionary of options from an expression.
        For example Symbol("Integrate").get_option_values(evaluation, allow_symbols=True)
        will return a list of options associated to the definition of the symbol "Integrate".
        If self is not an expression,
        """
        if allow_symbols:
            options = evaluation.definitions.get_options(self.get_name())
            return options.copy()
        else:
            return None if stop_on_error else {}

    def has_symbol(self, symbol_name: str) -> bool:
        """
        Return True if the Symbol is ``symbol_name``.
        """
        return self.name == ensure_context(symbol_name)

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a `definitions`
        parameter.

        Here, we have to be pessimistic and return False.
        """
        return False

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

    def is_uncertain_final_definitions(self, definitions) -> bool:
        """
        Used in Expression.do_format() to determine if we need to
        (re)evaluate an expression.

        Here, we have to be pessimistic and return True. For example,
        in:

           Context[]

        this routine will get called where "self" is $System`Context. We
        can't stop here, but must continue evaluation to get the function's value,
        such as "Global`".
        """
        return True

    def get_attributes(self, definitions):
        return definitions.get_attributes(self.name)

    def get_name(self) -> str:
        return self.name

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super(Symbol, self).get_sort_key(True)
        else:
            return (
                1 if self.is_numeric() else 2,
                2,
                Monomial({self.name: 1}),
                0,
                self.name,
                1,
            )

    def user_hash(self, update) -> None:
        update(b"System`Symbol>" + self.name.encode("utf8"))

    def replace_vars(self, vars, options={}, in_scoping=True):
        assert all(fully_qualified_symbol_name(v) for v in vars)
        var = vars.get(self.name, None)
        if var is None:
            return self
        else:
            return var

    def sameQ(self, rhs: Any) -> bool:
        """Mathics SameQ"""
        return self is rhs

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


class PredefinedSymbol(Symbol):
    """
    A Predefined Symbol of the Mathics system.

    A Symbol which is defined because it is used somewhere in the
    Mathics system as a built-in name, Attribute, Property, Option,
    or a Symbolic Constant.

    In contrast to Symbol where the name might not have been added to
    a list of known Symbol names or where the name might get deleted,
    this never occurs here.
    """

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a `definitions`
        parameter.

        We have to be pessimistic here. There may be certain situations though
        where the above context changes this. For example, `If`
        has the property HoldRest. That kind of thing though is detected
        at the higher level in handling the expression setup for `If`, not here.
        """
        return False

    def is_uncertain_final_definitions(self, definitions) -> bool:
        """
        Used in Expression.do_format() to determine if we need to
        (re)evaluate an expression.


        We know that we won't need to reevaluate because these
        kinds of Symbols have already been created, and can't get
        removed.
        """
        return False


# system_symbols('A', 'B', ...) -> [Symbol('System`A'), Symbol('System`B'), ...]
def system_symbols(*symbols) -> typing.FrozenSet[Symbol]:
    """
    Return a frozenset of symbols from a list of names (strings).
    We will use this in testing membership, so an immutable object is fine.

    In 2021, we benchmarked frozenset versus list, tuple, and set and frozenset was the fastest.
    """
    return frozenset(Symbol(s) for s in symbols)


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


# Symbols used in this module.

# Note, below we are only setting PredefinedSymbol for Symbols which
# are both predefined and have the Locked attribute.

# An experiment using PredefinedSymbol("Pi") in the Python code and
# running:
#    {Pi, Unprotect[Pi];Pi=4; Pi, Pi=.; Pi }
# show that this does not change the output in any way.
#
# That said, for now we will proceed very conservatively and
# cautiously. However we may decide in the future to
# more of the below and in systemsymbols
# PredefineSymbol.

SymbolFalse = PredefinedSymbol("System`False")
SymbolList = PredefinedSymbol("System`List")
SymbolTrue = PredefinedSymbol("System`True")

SymbolAbs = Symbol("Abs")
SymbolDivide = Symbol("Divide")
SymbolFloor = Symbol("Floor")
SymbolFullForm = Symbol("FullForm")
SymbolGraphics = Symbol("System`Graphics")
SymbolGraphics3D = Symbol("System`Graphics3D")
SymbolHoldForm = Symbol("System`HoldForm")
SymbolMachinePrecision = Symbol("MachinePrecision")
SymbolMakeBoxes = Symbol("System`MakeBoxes")
SymbolMaxPrecision = Symbol("$MaxPrecision")
SymbolMinPrecision = Symbol("$MinPrecision")
SymbolN = Symbol("System`N")
SymbolNull = Symbol("System`Null")
SymbolNumberForm = Symbol("System`NumberForm")
SymbolPlus = Symbol("Plus")
SymbolPostfix = Symbol("System`Postfix")
SymbolPower = Symbol("Power")
SymbolRepeated = Symbol("System`Repeated")
SymbolRepeatedNull = Symbol("System`RepeatedNull")
SymbolSequence = Symbol("System`Sequence")
SymbolUpSet = Symbol("UpSet")
SymbolTeXForm = Symbol("TeXForm")
SymbolTimes = Symbol("Times")

# NumericOperators uses some of the Symbols above.
class NumericOperators:
    """
    This is a mixin class for Element-like objects that might have numeric values.
    It adds or "mixes in" numeric functions for these objects like round_to_float().

    It also adds methods to the class to facilite building
    ``Expression``s in the Mathics Python code using Python syntax.

    So for example, instead of writing in Python:

        to_expression("Abs", -8)
        Expression(SymbolPlus, Integer1, Integer2)

    you can instead have:
        abs(Integer(-8))
        Integer(1) + Integer(2)
    """

    def __abs__(self) -> BaseElement:
        return self.create_expression(SymbolAbs, self)

    def __add__(self, other) -> BaseElement:
        return self.create_expression(SymbolPlus, self, other)

    def __pos__(self):
        return self

    def __neg__(self):
        from mathics.core.atoms import IntegerM1

        return self.create_expression(SymbolTimes, self, IntegerM1)

    def __sub__(self, other) -> BaseElement:
        from mathics.core.atoms import IntegerM1

        return self.create_expression(
            SymbolPlus, self, self.create_expression(SymbolTimes, other, IntegerM1)
        )

    def __mul__(self, other) -> BaseElement:
        return self.create_expression(SymbolTimes, self, other)

    def __truediv__(self, other) -> BaseElement:
        return self.create_expression(SymbolDivide, self, other)

    def __floordiv__(self, other) -> BaseElement:
        return self.create_expression(
            SymbolFloor, self.create_expression(SymbolDivide, self, other)
        )

    def __pow__(self, other) -> BaseElement:
        return self.create_expression(SymbolPower, self, other)

    def round_to_float(self, evaluation=None, permit_complex=False) -> Optional[float]:
        """
        Round to a Python float. Return None if rounding is not possible.
        This can happen if self or evaluation is NaN.
        """
        value = (
            self
            if evaluation is None
            else self.create_expression(SymbolN, self).evaluate(evaluation)
        )
        if hasattr(value, "round") and hasattr(value, "get_float_value"):
            value = value.round()
            return value.get_float_value(permit_complex=permit_complex)
        return None
