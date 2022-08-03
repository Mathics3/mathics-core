# -*- coding: utf-8 -*-
"""
(Base) Element of an general (M-)Expression.

Here we have the base class and related function for element inside an Expression.
"""


from typing import Any, Optional, Tuple

from mathics.core.attributes import no_attributes


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
    from recordclass import RecordClass

    # Note: Something in cythonization barfs if we put this in Expression and you try to call this
    # like ExpressionProperties(True, True, True). Cython reports:
    #   number of the arguments greater than the number of the items
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
    class ElementsProperties:
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


class KeyComparable:
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

    # FIXME: return type should be a specific kind of Tuple, not a list.
    # FIXME: Describe sensible, and easy to follow rules by which one
    #        can create the kind of tuple for some new kind of element.
    def get_sort_key(self) -> list:
        """
        This returns a tuple in a way that
        it can be used to compare in expressions.

        Returns a particular encoded list (better though would be a tuple) that is used
        in ``Sort[]`` comparisons and in the ordering that occurs
        in an M-Expression which has the ``Orderless`` property.

        The encoded tuple/list is selected to have the property: when
        compared against element ``expr`` in a compound expression, if

           `self.get_sort_key() <= expr.get_sort_key()`

        then self comes before expr.

        The values in the positions of the list/tuple are used to indicate how comparison should be
        treated for specific element classes.
        """
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        return (
            hasattr(other, "get_sort_key")
            and self.get_sort_key() == other.get_sort_key()
        )

    def __gt__(self, other) -> bool:
        return self.get_sort_key() > other.get_sort_key()

    def __ge__(self, other) -> bool:
        return self.get_sort_key() >= other.get_sort_key()

    def __le__(self, other) -> bool:
        return self.get_sort_key() <= other.get_sort_key()

    def __lt__(self, other) -> bool:
        return self.get_sort_key() < other.get_sort_key()

    def __ne__(self, other) -> bool:
        return (
            not hasattr(other, "get_sort_key")
        ) or self.get_sort_key() != other.get_sort_key()


class BaseElement(KeyComparable):
    """
    This is the base class from which all other Expressions are
    derived from.  If you think of an Expression as tree-like, then a
    BaseElement is a node in the tree.

    This class is not complete in of itself and subclasses should adapt or fill in
    what is needed

    Some important subclasses: Atom and Expression.
    """

    last_evaluated: Any
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

        # If the types are the same then we'll use the classes definition of == (or __eq__).
        # Superclasses which need to specialized this behavior should redefine equal2()
        #
        # I would use `is` instead `==` here, to compare classes.
        if type(self) is type(rhs):
            return self == rhs
        return None

    def format(self, evaluation, form, **kwargs) -> "BoxElement":
        from mathics.core.formatter import format_element
        from mathics.core.symbols import Symbol

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
        return no_attributes

    def get_head_name(self):
        raise NotImplementedError

    # FIXME: this behavior of defining a specific default implementation
    # that is basically saying it isn't implemented is wrong.
    # However fixing this means not only removing but fixing up code
    # in the callers.
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
        pass

    def get_precision(self) -> Optional[float]:
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
        from mathics.core.symbols import SymbolList

        # comment mm: This makes sense for expressions, but not for numbers. This should
        # have at most a trivial implementation here, and specialize it
        # in the `Expression` class.

        list_expr = self.flatten_with_respect_to_head(SymbolList)
        list = []
        if list_expr.has_form("List", None):
            list.extend(list_expr.elements)
        else:
            list.append(list_expr)
        rules = []
        for item in list:
            if not item.has_form(("Rule", "RuleDelayed"), 2):
                return None
            rule = Rule(item.elements[0], item.elements[1])
            rules.append(rule)
        return rules

    def get_sequence(self):
        """Convert's a Mathics Sequence into a Python's list of elements"""
        from mathics.core.symbols import SymbolSequence

        if self.get_head() is SymbolSequence:
            return self.elements
        else:
            return [self]

    def get_string_value(self):
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

    def has_form(self, heads, *element_counts):
        """Check if the expression is of the form Head[l1,...,ln]
        with Head.name in `heads` and a number of elements according to the specification in
        element_counts.
        """
        return False

    @property
    def is_zero(self) -> bool:
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

    def rewrite_apply_eval_step(self, evaluation) -> Tuple["BaseElement", bool]:
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


class BoxElement(ImmutableValueMixin, BaseElement):
    """
    The base class for all the boxed
    elements
    """

    pass
