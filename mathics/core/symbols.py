# cython: language_level=3
# -*- coding: utf-8 -*-

import time
from typing import Any, FrozenSet, List, Optional, Tuple

import sympy

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

    def get_atoms(self, include_heads=True) -> List["Atom"]:
        return [self]

    # We seem to need this because the caller doesn't distinguish something with elements
    # from a single atom.
    def get_elements(self):
        return []

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
        """True if the value can't change and has a Python representation,
        i.e. a value is set and it does not depend on definition
        bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a
        `definitions` parameter.

        Most Atoms, like Numbers and Strings, do not need evaluation
        or reevaluation. However some kinds of Atoms like Symbols do
        in general. The Symbol class or any other class that is
        subclassed from here (Atom) then needs to override this method, when
        it might is literal in general.

        """
        return False

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

    def replace_vars(self, vars, options=None, in_scoping=True) -> "Atom":
        return self

    def replace_slots(self, slots, evaluation) -> "Atom":
        return self


class Symbol(Atom, NumericOperators, EvalMixin):
    """A Symbol is a kind of Atom that acts as a symbolic variable.

    All Symbols have a name that can be converted to string.

    A Variable Symbol is a ``Symbol`` that is associated with a
    ``Definition`` that has an ``OwnValue`` that determines its
    evaluation value.

    A Function Symbol, like a Variable Symbol, is a ``Symbol`` that is
    also associated with a ``Definition``. But it has a ``DownValue``
    that is used in its evaluation.

    A Function Symbol, like a Variable Symbol, is a ``Symbol`` that is
    also associated with a ``Definition``. But it has a ``DownValue``
    that is used in its evaluation.

    We also have Symbols which, in contrast to Variables Symbols, have
    a constant value that cannot change. System`True and System`False
    are like this.

    These however are in class SymbolConstant. See that class for
    more information.

    Symbol acts like Python's intern() built-in function or Lisp's
    Symbol without its modifyable property list.  Here, the only
    attribute we care about is the value which is unique across all
    mentions and uses, and therefore needs it only to be stored as a
    single object in the system.

    Note that the mathics.core.parser.Symbol works exactly this way.
    """

    name: str
    hash: str
    sympy_dummy: Any

    # Dictionary of Symbols defined so far.
    # We use this for object uniqueness.
    # The key is the Symbol object's string name, and the
    # diectionary's value is the Mathics object for the Symbol.
    _symbols = {}

    class_head_name = "System`Symbol"

    # __new__ instead of __init__ is used here because we want
    # to return the same object for a given "name" value.
    def __new__(cls, name: str, sympy_dummy=None):
        """
        Allocate an object ensuring that for a given ``name`` and ``cls`` we get back the same object,
        id(object) is the same and its object.__hash__() is the same.

        SymbolConstant's like System`True and System`False set
        ``value`` to something other than ``None``.

        """
        name = ensure_context(name)

        # A lot of the below code is similar to
        # the corresponding for numeric constants like Integer, Real.
        self = cls._symbols.get(name)

        if self is None:
            self = super().__new__(cls)
            self.name = name

            # Cache object so we don't allocate again.
            cls._symbols[name] = self

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast. Note that in contrast to the
            # cached object key, the hash key needs to be unique across *all*
            # Python objects, so we include the class in the
            # event that different objects have the same Python value.
            # For example, this can happen with String constants.

            self.hash = hash((cls, name))

            # TODO: revise how we convert sympy.Dummy
            # symbols.
            #
            # In some cases, SymPy returns a sympy.Dummy
            # object. It is converted to Mathics as a
            # Symbol. However, we probably should have
            # a different class for this kind of symbols.
            # Also, sympy_dummy should be stored as the
            # value attribute.
            self.sympy_dummy = sympy_dummy

            self._short_name = strip_context(name)

        return self

    def __eq__(self, other) -> bool:
        return self is other

    def __getnewargs__(self):
        return (self.name, self.sympy_dummy)

    def __hash__(self) -> int:
        """
        We need self.__hash__() so that we can use Symbols as keys in dictionaries.
        """
        return self.hash

    def __ne__(self, other) -> bool:
        return self is not other

    def __str__(self) -> str:
        return self.name

    def atom_to_boxes(self, f, evaluation) -> "String":
        from mathics.core.atoms import String

        return String(evaluation.definitions.shorten_name(self.name))

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

    def get_head_name(self) -> str:
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
        In general, for Atoms its value can change and might not have a Python
        representation. Symbol is an example of this.

        So Here, we have to be pessimistic and return False. A number of
        subclasses, like Integer, Real, String, change the value returned
        to True.

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

    @property
    def short_name(self) -> str:
        """The symbol name with its context stripped off"""
        return self._short_name

    def user_hash(self, update) -> None:
        update(b"System`Symbol>" + self.name.encode("utf8"))

    def to_python(self, *args, python_form: bool = False, **kwargs):
        if self is SymbolTrue:
            return True
        if self is SymbolFalse:
            return False
        if self is SymbolNull:
            return None

        # This was introduced before `mathics.eval.nevaluator.eval_N`
        # provided a simple way to convert an expression into a number.
        # Now it makes this routine harder to describe.
        n_evaluation = kwargs.get("n_evaluation")
        if n_evaluation is not None:
            import warnings

            warnings.warn(
                "use instead ``eval_N(obj, evaluation).to_python()``",
                DeprecationWarning,
            )

            from mathics.eval.nevaluator import eval_N

            value = eval_N(self, n_evaluation)
            if value is not self:
                return value.to_python()

        # For general symbols, the default behaviour is
        # to return a 'str'. The reason seems to be
        # that native (builtin) Python types
        # are better for being used as keys in
        # dictionaries.
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


class SymbolConstant(Symbol):
    """
    A Symbol Constant is Symbol of the Mathics system whose value can't
    be changed and has a corresponding Python representation.

    Therefore, like an ``Integer`` constant such as ``Integer0``, we don't
    need to go through ``Definitions`` to get its Python-equivalent value.

    For example for the ``SymbolConstant`` ``System`True``, has its
    value set to the Python ``True`` value.

    Note this is not the same thing as a Symbolic Constant like ``Pi``,
    which doesn't have an (exact) Python equivalent representation.
    Also, Pi *can* be Unprotected and changed, while True, cannot.

    Also note that ``SymbolConstant`` differs from ``Symbol`` in that
    Symbol has no value field (even when its value happens to be
    representable in Python. Symbols need to go through Definitions
    get a Symbol's current value, based on the current context and the
    state of prior operations on that Symbol/Definition binding.

    In sum, SymbolConstant is partly like Symbol, and partly like
    Numeric constants.
    """

    # Dictionary of SymbolConstants defined so far.
    # We use this for object uniqueness.
    # The key is the SymbolConstant's value, and the
    # diectionary's value is the Mathics object representing that Python value.
    _symbol_constants = {}

    # We use __new__ here to unsure that two Integer's that have the same value
    # return the same object.
    def __new__(cls, name, value):

        name = ensure_context(name)
        self = cls._symbol_constants.get(name)
        if self is None:
            self = super().__new__(cls, name)
            self._value = value

            # Cache object so we don't allocate again.
            self._symbol_constants[name] = self

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast. Note that in contrast to the
            # cached object key, the hash key needs to be unique across all
            # Python objects, so we include the class in the
            # event that different objects have the same Python value
            self.hash = hash((cls, name))
        return self

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

    @property
    def value(self):
        return self._value


def symbol_set(*symbols: Tuple[Symbol]) -> FrozenSet[Symbol]:
    """
    Return a frozenset of symbols from a Symbol arguments.
    We will use this in testing membership, so an immutable object is fine.

    In 2021, we benchmarked frozenset versus list, tuple, and set and frozenset was the fastest.
    """
    return frozenset(symbols)


# Symbols used in this module.

# Note, below we are only setting SymbolConstant for Symbols which
# are both predefined and have the Locked attribute.

# An experiment using SymbolConstant("Pi") in the Python code and
# running:
#    {Pi, Unprotect[Pi];Pi=4; Pi, Pi=.; Pi }
# show that this does not change the output in any way.
#
# That said, for now we will proceed very conservatively and
# cautiously. However we may decide in the future to
# more of the below and in systemsymbols
# PredefineSymbol.

SymbolFalse = SymbolConstant("System`False", value=False)
SymbolList = SymbolConstant("System`List", value=list)
SymbolTrue = SymbolConstant("System`True", value=True)

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
