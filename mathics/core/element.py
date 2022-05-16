# -*- coding: utf-8 -*-
"""
(Base) Element of an general (M-)Expression.

Here we have the base class and related function for element inside an Expression.
"""

from mathics.core.attributes import no_attributes
from typing import Any, Optional, Tuple


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

    def get_sort_key(self):
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

    # FIXME: kwargs seems to be is needed because Real.__new_() takes a parameter
    # and magically that gets turned into kwargs here.
    # Figure out how to address this.
    def __init__(self, *args, **kwargs):
        self.options = None
        self.pattern_sequence = False
        # This property would be useful for a BoxExpression
        # (see comment in mathocs.core.expression.) However,
        # WL has a way to handle the connection between
        # an expression and a Box expression ``InterpretationBox``.
        # self.unformatted = self  # This may be a garbage-collection nightmare.

    # comment @mmatera: The next method have a name that starts with ``apply``.
    # This obstaculizes to define ``InstanceableBuiltin``
    # with ``Element`` as an ancestor class. I would like to have this
    # to reimplement  ``mathics.builtin.BoxConstruct`` in a way that do not
    # require to redefine several of the methods of this class.
    # I propose then to change the name to ``do_apply_rules``.
    # This change implies to change just an small number of lines
    # in the code of ``mathics.core`` and ``mathics.builtin``. In particular
    # the afected files apart from this would be:
    #
    # mathics/core/expression.py
    # mathics/builtin/inference.py
    # mathics/builtin/patterns.py
    # mathics/builtin/assignments/internals.py

    def apply_rules(
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

    # FIXME the fact that we have to import all of these symbols means
    # modularity is broken somehwere.
    # And do_format really doesn't belong here.
    def do_format(self, evaluation, form):
        """
        Applies formats associated to the expression and removes
        superfluous enclosing formats.
        """
        from mathics.core.symbols import (
            Atom,
            Symbol,
            SymbolFullForm,
            SymbolGraphics,
            SymbolGraphics3D,
            SymbolHoldForm,
            SymbolList,
            SymbolNumberForm,
            SymbolOutputForm,
            SymbolPostfix,
            SymbolRepeated,
            SymbolRepeatedNull,
            SymbolStandardForm,
            format_symbols,
        )

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
            # If form is Fullform, return it without changes
            if form is SymbolFullForm:
                if include_form:
                    expr = self.create_expression(form, expr)
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
                if not (isinstance(expr, Atom)) and not (isinstance(expr.head, Atom)):
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
                and not isinstance(expr, Atom)
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

    def evaluate(self, evaluation) -> "BaseElement":
        """Returns the value of the expression. The subclass must implement this"""
        raise NotImplementedError

    # FIXME the fact that we have to import all of these symbols means
    # modularity is broken somehwere.
    # And format really doesn't belong here.
    def format(self, evaluation, form, **kwargs) -> "BaseElement":
        """
        Applies formats associated to the expression, and then calls Makeboxes
        """
        from mathics.core.symbols import (
            Symbol,
            SymbolMakeBoxes,
        )

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
        """
        Build a dictionary of options from an expression.
        For example Symbol("Integrate").get_option_values(evaluation, allow_symbols=True)
        will return a list of options associated to the definition of the symbol "Integrate".
        If self is not an expression,
        """
        # comment @mmatera: The implementation of this is awfull.
        # This general method (in BaseElement) should be simpler (Numbers does not have Options).
        # The implementation should be move to Symbol and Expression classes.

        from mathics.core.atoms import String
        from mathics.core.symbols import SymbolList

        options = self
        if options.has_form("List", None):
            options = options.flatten_with_respect_to_head(SymbolList)
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
        from mathics.core.symbols import SymbolList

        # comment mm: This makes sense for expressions, but not for numbers. This should
        # have at most a trivial implementation here, and specialize it
        # in the `Expression` class.

        list_expr = self.flatten_with_respect_to_head(SymbolList)
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
        """Convert's a Mathics Sequence into a Python's list of elements"""
        from mathics.core.symbols import SymbolSequence

        if self.get_head() is SymbolSequence:
            return self.leaves
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
        with Head.name in `heads` and a number of leaves according to the specification in
        element_counts.
        """
        return False

    # Warning - this is going away
    def is_true(self) -> bool:
        """Better use self is SymbolTrue"""
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

    def rewrite_apply_eval_step(self, evaluation) -> Tuple["Expression", bool]:
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
        raise NotImplementedError
