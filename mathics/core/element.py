# -*- coding: utf-8 -*-
"""
(Base) Element of an general (M-)Expression.

Here we have the base class and related function for element inside an Expression.
"""

from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence, Tuple, Union

from mathics.core.attributes import A_NO_ATTRIBUTES
from mathics.core.keycomparable import KeyComparable

if TYPE_CHECKING:
    from mathics.core.evaluation import Evaluation


def ensure_context(name: str, context="System`") -> str:
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


try:
    from recordclass import RecordClass  # type: ignore[import-not-found]

    # Note: Something in cythonization barfs if we put this in
    # Expression and you try to call this like
    # ExpressionProperties(True, True, True). Cython reports:
    # number of the arguments greater than the number of the items
    class ElementsProperties(RecordClass):
        """Properties of Expression elements that are useful in evaluation.

        In general, if you have some set of properties that you know should
        be set a particular way, but don't know about the others, it is safe
        to set the unknown properties to False. Omitting that property is the
        same as setting a property to False.

        However, when *all* of the properties are unknown, use a `None` value in
        the Expression.properties field instead of creating an
        ElementsProperties object with everything set False.
        By setting the field to None, the code will look over the elements before
        evaluation and set the property values correctly.
        """

        # True if none of the elements needs to be evaluated.
        elements_fully_evaluated: bool = False

        # is_flat: True if none of the elements is an Expression
        # Some Mathics functions allow flattening of elements. Therefore
        # it can be useful to know if the elements are already flat
        is_flat: bool = False

        # is_ordered: True if all of the elements are ordered. Of course this is true,
        # if there are less than 2 elements. Ordered is an Attribute of a
        # Mathics function.
        #
        # In rewrite_eval_apply() if a function is not marked as Ordered this attribute
        # has no effect which means it doesn't matter how it is set. So
        # when it doubt, it is always safe to set is_ordered to False since at worst
        # it will cause an ordering operation on elements sometimes. On the other hand, setting
        # this True elements are not sorted can cause evaluation differences.
        is_ordered: bool = False

except ImportError:
    from dataclasses import dataclass

    @dataclass
    class ElementsProperties:  # type: ignore[no-redef]
        """Properties of Expression elements that are useful in evaluation.

        In general, if you have some set of properties that you know should
        be set a particular way, but don't know about the others, it is safe
        to set the unknown properties to False. Omitting that property is the
        same as setting a property to False.

        However, when *all* of the properties are unknown, use a `None` value in
        the Expression.properties field instead of creating an
        ElementsProperties object with everything set False.
        By setting the field to None, the code will look over the elements before
        evaluation and set the property values correctly.
        """

        # True if none of the elements needs to be evaluated.
        elements_fully_evaluated: bool = False

        # is_flat: True if none of the elements is an Expression
        # Some Mathics functions allow flattening of elements. Therefore
        # it can be useful to know if the elements are already flat
        is_flat: bool = False

        # is_ordered: True if all of the elements are ordered. Of course this is true,
        # if there are less than 2 elements. Ordered is an Attribute of a
        # Mathics function.
        #
        # In rewrite_eval_apply() if a function is not marked as Ordered this attribute
        # has no effect which means it doesn't matter how it is set. So
        # when it doubt, it is always safe to set is_ordered to False since at worst
        # it will cause an ordering operation on elements sometimes. On the other hand, setting
        # this True elements are not sorted can cause evaluation differences.
        is_ordered: bool = False


class ImmutableValueMixin:
    @property
    def is_literal(self) -> bool:
        """
        The value value can't change once it is set.
        """
        return True


class BaseElement(KeyComparable, ABC):
    """
    This is the base class from which all other Expressions are
    derived from.  If you think of an Expression as tree-like, then a
    BaseElement is a node in the tree.

    This class is not complete in of itself and subclasses should adapt or fill in
    what is needed

    Some important subclasses: Atom and Expression.
    """

    options: Optional[Dict[str, Any]]
    last_evaluated: Any
    unevaluated: bool
    # this variable holds a function defined in mathics.core.expression that creates an expression
    create_expression: Any

    def do_apply_rules(
        self, rules, evaluation, level=0, options=None
    ) -> Tuple["BaseElement", bool]:
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

    def equal2(self, rhs: Any) -> Optional[bool]:
        """
        Mathics two-argument Equal (==)
        returns True if self and rhs are identical.
        """
        if self.sameQ(rhs):
            return True

        # If the types are the same then we'll use the classes
        # definition of == (or __eq__).  Superclasses which need to
        # specialized this behavior should redefine equal2()
        #
        # I would use `is` instead `==` here, to compare classes.
        if type(self) is type(rhs):
            return self == rhs
        return None

    def format(self, evaluation, form, **kwargs) -> Optional["BaseElement"]:
        from mathics.core.symbols import Symbol
        from mathics.eval.makeboxes import format_element

        if isinstance(form, str):
            form = Symbol(form)
        return format_element(self, evaluation, form, **kwargs)

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
        return A_NO_ATTRIBUTES

    def get_element(self, index: int) -> "BaseElement":
        return self.get_elements()[index]

    def get_elements(self) -> Sequence["BaseElement"]:
        raise NotImplementedError

    def get_head(self) -> "BaseElement":
        raise NotImplementedError

    def get_head_name(self) -> str:
        """
        All elements have a "Head" whether or not the element is compound.
        The Head of an Atom is its type. The Head of an S-expression is
        its function name.

        Each class must define its own get_head_name.
        """
        raise NotImplementedError

    # FIXME: this behavior of defining a specific default implementation
    # that is basically saying it isn't implemented is wrong.
    # However fixing this means not only removing but fixing up code
    # in the callers.
    def get_float_value(self, permit_complex=False):
        return None

    def get_int_value(self) -> Optional[int]:
        return None

    def get_lookup_name(self) -> str:
        """
        Returns symbol name of leftmost head. This method is used
        to determine which definition must be asked for rules
        to apply in order to do the evaluation.
        """

        return self.get_name()

    def get_name(self, short=False) -> str:
        "Returns symbol's name if Symbol instance"

        return ""

    def get_option_values(
        self, evaluation: "Evaluation", allow_symbols=False, stop_on_error=True
    ) -> Optional[dict]:
        pass

    def get_precision(self) -> Optional[int]:
        """Returns the default specification for precision in N and other
        numerical functions.  It is expected to be redefined in those
        classes that provide inexact arithmetic like PrecisionReal.

        Here in the default base implementation, `None` is used to indicate that the
        precision is either not defined, or it is exact as in the case of Integer. In either case, the
        values is not "inexact".

        This function is called by method `is_inexact()`.
        """
        return None

    def get_sequence(self) -> Sequence["BaseElement"]:
        """
        If ``self`` is a Mathics3 Sequence, return its elements.
        Otherwise, just return self wrapped in a tuple
        """
        from mathics.core.symbols import SymbolSequence

        # Below, we special-case for SymbolSequence. Here is an example to suggest why.
        # Suppose we have this evaluation method:
        #
        # def eval(x, evaluation: Evaluation):
        #     """F[x__]"""
        #     args = x.get_sequence()
        #
        # For the expression "F[a,b]", this function is expected to return:
        #   [Symbol(a), Symbol(b)], while
        # for the expression "F[{a,b}]" this function is expected to return:
        #   ListExpression[Symbol(a), Symbol(b)].
        if self.get_head() is SymbolSequence:
            return self.get_elements()
        else:
            return tuple([self])

    def get_string_value(self) -> Optional[str]:
        return None

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()`, we don't need a `definitions`
        parameter.

        Each subclass should decide what is right here.
        """
        raise NotImplementedError

    def is_uncertain_final_definitions(self, definitions) -> bool:
        """
        Used in Expression.do_format() to determine if we should (re)evaluate
        an expression. Each subclass should decide what is right here.
        """
        raise NotImplementedError

    def is_machine_precision(self) -> bool:
        """Check if the number represents a floating point number"""
        return False

    def is_numeric(self, evaluation=None) -> bool:
        """Check if the expression is a number. If evaluation is given,
        tries to determine if the expression can be evaluated as a number.
        """
        # used by NumericQ and expression ordering
        return False

    def has_form(
        self, heads: Union[Sequence[str], str], *element_counts: Optional[int]
    ) -> bool:
        """Check if the expression is of the form Head[l1,...,ln]
        with Head.name in `heads` and a number of elements according to the specification in
        element_counts.
        """
        return False

    @property
    def is_zero(self) -> bool:
        return False

    def is_free(self, form, evaluation) -> bool:
        """
        Check if self has a subexpression of the form `form`.
        """
        from mathics.eval.test import item_is_free

        return item_is_free(self, form, evaluation)

    def is_inexact(self) -> bool:
        return self.get_precision() is not None

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

    def to_python(self, *args, **kwargs):
        """Returns a native builtin Python object
        something in (int, float, complex, str, tuple, list or dict.).
        (See discussions in
        https://github.com/Mathics3/mathics-core/discussions/550
        and
        https://github.com/Mathics3/mathics-core/pull/551
        """
        raise NotImplementedError

    def to_mpmath(self):
        raise NotImplementedError

    def to_sympy(self, **kwargs):
        raise NotImplementedError

    def copy(self, reevaluate=False) -> "BaseElement":
        raise NotImplementedError

    def default_format(self, evaluation, form) -> str:
        raise NotImplementedError

    def replace_vars(
        self,
        vars: Dict[str, "BaseElement"],
        options=None,
        in_scoping=True,
        in_function=True,
    ) -> "BaseElement":
        raise NotImplementedError


class EvalMixin:
    """
    Class associated to evaluable elements
    """

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()`, we don't need a `definitions`
        parameter.

        Each subclass should decide what is right here.
        """
        return False

    def rewrite_apply_eval_step(
        self, evaluation
    ) -> Tuple[Optional["BaseElement"], bool]:
        """
        Performs a since rewrite/apply/eval step used in
        evaluation.

        Here we specialize evaluation so that any results returned
        do not need further evaluation.
        """
        return self.evaluate(evaluation), False

    def sameQ(self, other) -> bool:
        """Mathics SameQ
        Each class should decide what is right here.
        """
        raise NotImplementedError

    def evaluate(self, evaluation: "Evaluation") -> Optional["BaseElement"]:
        raise NotImplementedError


class BoxElementMixin(ImmutableValueMixin):
    """
    The base class for all the boxed
    elements
    """

    def boxes_to_format(self, format: str, **options: dict) -> str:
        from mathics.core.formatter import boxes_to_format

        return boxes_to_format(self, format, **options)

    def boxes_to_mathml(self, **options: dict) -> str:
        """For compatibility deprecated"""
        return self.boxes_to_format("mathml", **options)

    def boxes_to_tex(self, **options: dict) -> str:
        """For compatibility deprecated"""
        return self.boxes_to_format("latex", **options)

    def boxes_to_text(self, **options: dict) -> str:
        """For compatibility deprecated"""
        return self.boxes_to_format("text", **options)
