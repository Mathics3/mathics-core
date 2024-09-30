# cython: language_level=3
# cython: profile=False
# -*- coding: utf-8 -*-
"""Core to Mathics3 is are patterns which match symbolic expressions. A pattern are built up in a custon pattern notation.
The parts of a pattern are called "Pattern Objects".

While there is a built-in function which allows users to match parts of expressions, patterns are also used in applying of transformation
rules and deciding functions that get applied.

See also: mathics.core.rules and https://reference.wolfram.com/language/tutorial/PatternsAndTransformationRules.html
"""


from abc import ABC
from itertools import chain
from typing import Callable, List, Optional, Tuple, Union

from mathics.core.atoms import Integer
from mathics.core.attributes import A_FLAT, A_ONE_IDENTITY, A_ORDERLESS
from mathics.core.element import BaseElement, ensure_context
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, SymbolDefault
from mathics.core.symbols import Atom, Symbol, symbol_set
from mathics.core.systemsymbols import (
    SymbolAlternatives,
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolCondition,
    SymbolOptional,
    SymbolOptionsPattern,
    SymbolPattern,
    SymbolPatternTest,
    SymbolRepeated,
    SymbolRepeatedNull,
    SymbolSequence,
)
from mathics.core.util import permutations, subranges, subsets

SYSTEM_SYMBOLS_PATTERNS = symbol_set(
    SymbolAlternatives,
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolCondition,
    SymbolOptional,
    SymbolOptionsPattern,
    SymbolPattern,
    SymbolPatternTest,
    SymbolRepeated,
    SymbolRepeatedNull,
)

pattern_objects = {}


class StopGenerator(Exception):
    """
    StopGenerator is the exception raised when
    an expression matches a pattern.
    The exception holds the attribute `value`
    that is used as a return value in `match`.
    """

    def __init__(self, value=None):
        self.value = value


class StopGenerator_ExpressionPattern_match(StopGenerator):
    """
    Exception raised when an ExpressionPattern matches
    an expression.
    """


class StopGenerator_Pattern(StopGenerator):
    """
    Exception raised when  BasePattern matches
    an expression.
    """


class BasePattern(ABC):
    """
    This is the base class for Mathics3 Pattern objects.

    A Pattern is a way to represent classes of expressions.
    For example, ``F[x_Symbol]`` is a pattern which matches an expression whose
    Head is ``F`` and that has a single parameter which is kind of Symbol.
    When the pattern matches, the symbol is bound to the parameter ``x``.
    """

    expr: BaseElement

    # this attribute allows for a faster match algorithm based on sameq.
    # Probably we should split ExpressionPattern into two different classes,
    # one for literal patterns and the other for "Regular" ExpressionPatterns.
    isliteral: bool = False

    # TODO: In WMA, when a BasePattern is created, the attributes
    # from the head are read from the evaluation context and
    # stored as a part of a rule.
    #
    # As BasePatterns are nested structures, the factory not only needs
    # the attributes of the head, but also the full evaluation context
    # which is needed to create patterns for its elements.
    #
    #
    # For instance,  `rule=Times[c__, Plus[Q[a_],Q[b_]]]->Q[c*(a+b)]`
    # builds the pattern `Times[c__, Plus[Q[a_],Q[b_]]]`.
    # The constructor of the pattern then creates recursively
    #     `c__`
    #     `Plus[Q[a_],Q[b_]]`
    #         `Plus`
    #         `Q[a_]`
    #           `Q`
    #           `a_`
    #         `Q[b_]`
    #           `Q`
    #           `b_`
    #
    # Also, when the initial Definitions object for the evaluation
    # context is created, many rules must be created without an
    # evaluation context available. For that case, we still
    # must be able to create Pattern objects without the evaluation context.
    #
    # In any case, just by caching the attributes in the first use of
    # the pattern there is a win ~5% in performance.
    #
    # A better implementation would take into account the attributes
    # to specialize the match method.
    #
    #
    # Corner case: `Alternatives`
    # ===========================
    #
    # Notice also that the case of `Alternatives` is a corner case,
    # where attributes are read at the moment of the rule application:
    #
    # For example, in WMA, let's consider this example
    # ```
    #    In[1]:= SetAttributes[P,Orderless];
    #    In[2]:= rule=Alternatives[P,Q][_Integer,_Symbol]->True;
    # ```
    #
    # At this point, the rule `rule` was created. As the head of the pattern
    # is an expression, it does not provides special attributes to the pattern.
    # As expected, the pattern does not match with `Q[a, 1]` because the order of the
    # parameters:
    # ```
    #    In[3]:= Q[a, 1]/.rule
    #    Out[3]= Q[a, 1]
    # ```
    #
    # On the other hand, it does take into account the attributes of `P`:
    #
    # ```
    #    In[4]:= P[a, 1]/.rule
    #    Out[4]= True
    # ```
    # These attributes are not stored in the rule: if we remove the attribute
    # ```
    #    In[5]:= Attributes[P]={};
    # ```
    #
    # the attribute is not used anymore, and the rule application fails:
    #
    # ```
    #    In[6]:= P[a, 1]/.rule
    #    Out[6]= P[a, 1]
    # ``
    #
    #
    @staticmethod
    def create(
        expr: BaseElement,
        attributes: Optional[int] = None,
        evaluation: Optional[Evaluation] = None,
    ) -> "BasePattern":
        """
        If ``expr`` is listed in ``pattern_object``  return the pattern found there.
        Otherwise, if ``expr`` is an ``Atom``, create and return  ``AtomPattern`` for ``expr``.
        Otherwise, create and return and ``ExpressionPattern`` for ``expr``.
        """
        name = expr.get_head_name()
        pattern_object = pattern_objects.get(name)
        if pattern_object is not None:
            return pattern_object(expr, evaluation=evaluation)
        if isinstance(expr, Atom):
            return AtomPattern(expr, evaluation)
        return ExpressionPattern(expr, attributes, evaluation)

    def get_attributes(self, definitions):
        """The attributes of the expression"""
        return self.expr.get_attributes(definitions)

    def get_elements(self):
        """The elements of the expression."""
        return self.expr.get_elements()

    def get_head(self):
        """The head of the expression"""
        return self.expr.get_head()

    def get_head_name(self):
        """
        Return the name of the symbol in head.
        If head is not a symbol, return "".
        """
        return self.expr.get_head_name()

    def get_lookup_name(self):
        """
        Return symbol name of leftmost head.
        """
        return self.expr.get_lookup_name()

    def get_name(self, short=False) -> str:
        """Return the name of the expression."""
        name = self.expr.get_name()
        return name.split("`")[-1] if short else name

    def get_sequence(self):
        """The sequence of elements in the expression"""
        return self.expr.get_sequence()

    def get_sort_key(self, pattern_sort: bool = False) -> tuple:
        """The sort key of the expression"""
        return self.expr.get_sort_key(pattern_sort=pattern_sort)

    def get_option_values(self):
        """Option values of the expression"""
        return self.expr.get_option_values()

    def has_form(self, *args):
        """Compare the expression against a form"""
        return self.expr.has_form(*args)

    def match(
        self,
        yield_func: Callable,
        expression: BaseElement,
        vars_dict: dict,
        evaluation: Evaluation,
        head: Optional[Symbol] = None,
        element_index: Optional[int] = None,
        element_count: Optional[int] = None,
        fully: bool = True,
    ):
        """
        Check if the expression matches the pattern (self).
        If it does, calls `yield_func`.
        vars collects subexpressions associated to named subpatterns.
        head: Symbol. Provided by match_element, used by `Optional`.
        element_index: int  the position
        element_count: int and the number of optional elements. Used by `Optional`
        for calling `get_default_value`.

        Note: this complexity would disappear if Defaults would be stored as in WMA
        at the creation time of the object.

        fully is used in `match_element`, for the case of Orderless patterns.
        """
        raise NotImplementedError

    def does_match(
        self,
        expression: BaseElement,
        evaluation: Evaluation,
        vars_dict: Optional[dict] = None,
        fully: bool = True,
    ) -> bool:
        """returns True if `expression` matches self or we have
        reached the end of the matches, and False if it does not.
        """

        if vars_dict is None:
            vars_dict = {}
        # for sub_vars, rest in self.match(  # nopep8
        #    expression, vars, evaluation, fully=fully):
        #    return True

        def yield_match(sub_vars, rest):
            raise StopGenerator_Pattern(True)

        try:
            self.match(yield_match, expression, vars_dict, evaluation, fully=fully)
        except StopGenerator_Pattern as exc:
            return exc.value
        return False

    def get_match_candidates(
        self,
        elements: Tuple[BaseElement],
        expression: BaseElement,
        attributes: int,
        evaluation: Evaluation,
        vars_dict: Optional[dict] = None,
    ):
        """
        Get the candidates that matches with the pattern.
        """
        return tuple()

    def get_match_candidates_count(
        self,
        elements: Tuple[BaseElement],
        expression: BaseElement,
        attributes: int,
        evaluation: Evaluation,
        vars_dict: Optional[dict] = None,
    ):
        """Return the number of candidates that match with the pattern."""
        return len(
            self.get_match_candidates(
                elements, expression, attributes, evaluation, vars_dict
            )
        )

    def sameQ(self, other: BaseElement) -> bool:
        """Mathics SameQ"""
        return self.expr.sameQ(other.expr)


class AtomPattern(BasePattern):
    """
    A pattern that matches with an atom.
    """

    # Atoms are always literals
    isliteral: bool = True

    def __init__(self, expr: Atom, evaluation: Optional[Evaluation] = None) -> None:
        self.expr = expr
        self.atom = expr
        if isinstance(expr, Symbol):
            self.match = self.match_symbol
            self.get_match_candidates = self.get_match_symbol_candidates

    def __repr__(self):
        return f"<AtomPattern: {self.atom}>"

    def match_symbol(
        self,
        yield_func: Callable,
        expression: BaseElement,
        vars_dict: dict,
        evaluation: Evaluation,
        head: Optional[Symbol] = None,
        element_index: Optional[int] = None,
        element_count: Optional[int] = None,
        fully: bool = True,
    ):
        """Match against a symbol"""
        if expression is self.atom:
            yield_func(vars_dict, None)

    def get_match_symbol_candidates(
        self,
        elements: tuple,
        expression: BaseElement,
        attributes: int,
        evaluation: Evaluation,
        vars_dict: Optional[dict] = None,
    ):
        """Find the candidates that matches with the pattern"""
        return [element for element in elements if element is self.atom]

    def match(
        self,
        yield_func: Callable,
        expression: BaseElement,
        vars_dict: dict,
        evaluation: Evaluation,
        head: Optional[Symbol] = None,
        element_index: Optional[int] = None,
        element_count: Optional[int] = None,
        fully: bool = True,
    ):
        """Try to match the patterh with the expression."""
        if isinstance(expression, Atom) and expression.sameQ(self.atom):
            # yield vars, None
            yield_func(vars_dict, None)

    def get_match_candidates(
        self,
        elements: Tuple[BaseElement],
        expression: BaseElement,
        attributes: int,
        evaluation: Evaluation,
        vars_dict: Optional[dict] = None,
    ):
        return [
            element
            for element in elements
            if (isinstance(element, Atom) and element.sameQ(self.atom))
        ]

    def get_match_count(self, vars_dict: Optional[dict] = None):
        """The number of matches"""
        return (1, 1)


# class StopGenerator_ExpressionPattern_match(StopGenerator):
#    pass


class ExpressionPattern(BasePattern):
    """
    Pattern that matches with an Expression.
    """

    # get_pre_choices = pattern_nocython.get_pre_choices
    # match = pattern_nocython.match

    attributes: Optional[int] = None

    def __init__(
        self,
        expr: Expression,
        attributes: Optional[int] = None,
        evaluation: Optional[Evaluation] = None,
    ):
        self.expr = expr
        head = expr.head
        if attributes is None and evaluation:
            attributes = head.get_attributes(evaluation.definitions)
        self.head = BasePattern.create(head, evaluation=evaluation)
        self.elements = [
            BasePattern.create(element, evaluation=evaluation)
            for element in expr.elements
        ]
        self.__set_pattern_attributes__(attributes)

    def __set_pattern_attributes__(self, attributes):
        if attributes is None or self.attributes is not None:
            return

        self.attributes = attributes
        if A_ORDERLESS & attributes:
            self.sort()
            self.get_pre_choices = get_pre_choices_orderless
        else:
            self.get_pre_choices = get_pre_choices_with_order
            if not (A_ONE_IDENTITY + A_FLAT) & attributes:
                self.isliteral = self.head.isliteral and all(
                    element.isliteral for element in self.elements
                )

    def match(
        self,
        yield_func: Callable,
        expression: BaseElement,
        vars_dict: dict,
        evaluation: Evaluation,
        head: Optional[Symbol] = None,
        element_index: Optional[int] = None,
        element_count: Optional[int] = None,
        fully: bool = True,
    ):
        """Try to match the pattern against an Expression"""
        evaluation.check_stopped()
        if self.isliteral:
            if expression.sameQ(self.expr):
                # yield vars, None
                yield_func(vars_dict, None)
            return

        if self.attributes is None:
            self.__set_pattern_attributes__(
                self.head.get_attributes(evaluation.definitions)
            )
        attributes = self.attributes

        if not A_FLAT & attributes:
            fully = True

        parms = {
            "attributes": attributes,
            "evaluation": evaluation,
            "expression": expression,
            "fully": fully,
            "self": self,
            "vars_dict": vars_dict,
            "yield_func": yield_func,
        }

        if not isinstance(expression, Atom):
            try:
                basic_match_expression(
                    parms,
                )
            except StopGenerator_ExpressionPattern_match:
                return

        if A_ONE_IDENTITY & attributes:
            match_expression_with_one_identity(
                parms,
                element_index=element_index,
                element_count=element_count,
                head=head,
            )

    def get_pre_choices(
        self,
        yield_choice: Callable,
        expression: BaseElement,
        attributes: int,
        vars_dict: dict,
    ):
        """
        If not Orderless, call yield_choice with vars as the parameter.
        """
        if A_ORDERLESS & attributes:
            get_pre_choices_orderless(
                self, yield_choice, expression, attributes, vars_dict
            )
        else:
            yield_choice(vars_dict)

    def filter_elements(self, head_name: str):
        """Filter the elements with a given head_name"""
        head_name = ensure_context(head_name)
        return [
            element for element in self.elements if element.get_head_name() == head_name
        ]

    def __repr__(self):
        return f"<ExpressionPattern: {self.expr}>"

    def get_match_count(self, vars_dict: Optional[dict] = None):
        """the number of matches"""
        return (1, 1)

    def get_wrappings(
        self,
        yield_func: Callable,
        items: Tuple,
        max_count: Optional[int],
        expression: Expression,
        attributes: int,
        include_flattened: bool = True,
    ):
        """Get the possible wrappings"""
        if len(items) == 1:
            yield_func(items[0])
        else:
            if max_count is None or len(items) <= max_count:
                if A_ORDERLESS & attributes:
                    for perm in permutations(items):
                        sequence = Expression(SymbolSequence, *perm)
                        sequence.pattern_sequence = True
                        yield_func(sequence)
                else:
                    sequence = Expression(SymbolSequence, *items)
                    sequence.pattern_sequence = True
                    yield_func(sequence)
            if A_FLAT & attributes and include_flattened:
                yield_func(Expression(expression.get_head(), *items))

    def match_element(
        self,
        yield_func: Callable,
        element: BaseElement,
        rest_elements: Tuple,
        rest_expression: Tuple[List, List],
        vars_dict: dict,
        expression: BaseElement,
        attributes: int,
        evaluation: Evaluation,
        element_index: int = 1,
        element_count: Optional[int] = None,
        first: bool = False,
        fully: bool = True,
        depth: int = 1,
    ):
        """Try to match an element."""
        if rest_expression is None:
            rest_expression = ([], [])

        evaluation.check_stopped()

        match_count = element.get_match_count(vars_dict)
        element_candidates = element.get_match_candidates(
            tuple(rest_expression[1]),  # element.candidates,
            expression,
            attributes,
            evaluation,
            vars_dict,
        )

        if len(element_candidates) < match_count[0]:
            return

        candidates = tuple(rest_expression[1])

        # "Artificially" only use more elements than specified for some kind
        # of pattern.
        # TODO: This could be further optimized!
        try_flattened = A_FLAT & attributes and (
            element.get_head() in SYSTEM_SYMBOLS_PATTERNS
        )

        if try_flattened:
            set_lengths = (match_count[0], None)
        else:
            set_lengths = match_count

        # try_flattened is used later to decide whether wrapping of elements
        # into one operand may occur.
        # This can of course also be when flat and same head.
        try_flattened = try_flattened or (
            A_FLAT & attributes and element.get_head() == expression.head
        )

        less_first = len(rest_elements) > 0

        if A_ORDERLESS & attributes:
            parms = {
                "expression": expression,
                "element": element,
                "vars_dict": vars_dict,
                "attributes": attributes,
            }

            sets = expression_pattern_match_element_orderless(
                parms,
                candidates,
                element_candidates,
                less_first,
                set_lengths,
            )
        else:
            # a generator that yields partitions of
            # candidates as [before | block | after ]

            sets = subranges(
                candidates,
                flexible_start=first and not fully,
                included=element_candidates,
                less_first=less_first,
                *set_lengths,
            )

        parms = {
            "attributes": attributes,
            "depth": depth + 1,
            "element": element,
            "element_count": element_count,
            "element_index": element_index,
            "evaluation": evaluation,
            "expression": expression,
            "fully": fully,
            "match_count": match_count,
            "next_index": element_index + 1,
            "pattern": self,
            "rest_elements": rest_elements,
            "rest_expression": rest_expression,
            "try_flattened": try_flattened,
            "yield_func": yield_func,
            "vars": vars_dict,
        }
        if rest_elements:
            parms["next_element"] = rest_elements[0]
            parms["next_rest_elements"] = rest_elements[1:]

        for items, items_rest in sets:
            expression_pattern_match_element_process_items(items, items_rest, parms)

    def get_match_candidates(
        self,
        elements: Tuple[BaseElement],
        expression: BaseElement,
        attributes: int,
        evaluation: Evaluation,
        vars_dict: Optional[dict] = None,
    ):
        """
        Finds possible elements that could match the pattern, ignoring future
        pattern variable definitions, but taking into account already fixed
        variables.
        """
        # TODO: fixed_vars!

        return [
            element
            for element in elements
            if self.does_match(element, evaluation, vars_dict)
        ]

    def get_match_candidates_count(
        self,
        elements: Tuple[BaseElement],
        expression: BaseElement,
        attributes: int,
        evaluation: Evaluation,
        vars_dict: Optional[dict] = None,
    ):
        """
        Finds possible elements that could match the pattern, ignoring future
        pattern variable definitions, but taking into account already fixed
        variables.
        """
        # TODO: fixed_vars!

        count = 0
        for element in elements:
            if self.does_match(element, evaluation, vars_dict):
                count += 1
        return count

    def sort(self):
        """Sort the elements according to their sort key"""
        self.elements.sort(key=lambda e: e.get_sort_key(pattern_sort=True))


def match_expression_with_one_identity(
    parms: dict,
    element_index: Optional[int],
    element_count: Optional[int],
    head: Symbol,
):
    """
    Process expressions with the attribute OneIdentity.
    """
    # This is all about the pattern. We do this
    # each time because at some point we should need
    # to check the default values each time...

    # This tries to reduce the pattern to a non empty
    # set of default values, and a single pattern.
    from mathics.builtin.patterns import Pattern

    self: ExpressionPattern = parms["self"]
    vars_dict: dict = parms["vars_dict"]
    evaluation: Evaluation = parms["evaluation"]

    default_indx: int = 0
    optionals: dict = {}
    new_pattern: Optional[Pattern] = None
    pattern_head: Expression = self.head.expr
    for pat_elem in self.elements:
        default_indx += 1
        if isinstance(pat_elem, AtomPattern):
            if new_pattern is not None:
                return
            new_pattern = pat_elem
            # TODO: check into account the second argument,
            # and if there is a default value...
        elif pat_elem.get_head_name() == "System`Optional":
            if len(pat_elem.elements) == 2:
                pat, value = pat_elem.elements
                if isinstance(pat, Pattern):
                    key = pat.elements[0].atom.name
                else:
                    # if the first element of the Optional
                    # is not a `Pattern`, then we need to
                    # store an empty element.
                    key = ""
                optionals[key] = value
            elif len(pat_elem.elements) == 1:
                pat = pat_elem.elements[0]
                if isinstance(pat, Pattern):
                    key = pat.elements[0].atom.name
                else:
                    key = ""
                # Now, determine the default value
                defaultvalue_expr = Expression(
                    SymbolDefault, pattern_head, Integer(default_indx)
                )
                value = defaultvalue_expr.evaluate(evaluation)
                if value.sameQ(defaultvalue_expr):
                    return
                optionals[key] = value
            else:
                return
        else:
            if new_pattern is not None:
                return
            new_pattern = pat_elem

    # If there is not optional values in the pattern, then
    # it can not match any expression as a OneIdentity pattern:
    if len(optionals) == 0:
        return

    # Remove the empty key and load the default values in vars
    if "" in optionals:
        del optionals[""]
    vars_dict.update(optionals)
    # Try to match the non-optional element with the expression
    new_pattern.match(
        parms["yield_func"],
        parms["expression"],
        vars_dict,
        evaluation,
        head=head,
        element_index=element_index,
        element_count=element_count,
        fully=parms["fully"],
    )


def basic_match_expression(parms):
    """
    Try to match a pattern with an expression
    """
    # don't do this here, as self.get_pre_choices changes the
    # ordering of the elements!
    # if self.elements:
    #    next_element = self.elements[0]
    #    next_elements = self.elements[1:]

    self: ExpressionPattern = parms["self"]
    yield_func: Callable = parms["yield_func"]
    expression: Expression = parms["expression"]
    vars_dict: dict = parms["vars_dict"]
    evaluation: Evaluation = parms["evaluation"]
    attributes: int = parms["attributes"]
    fully: bool = parms["fully"]

    def yield_choice(pre_vars):
        next_element = self.elements[0]
        next_elements = self.elements[1:]

        # "leading_blanks" below handles expressions with leading Blanks H[x_, y_, ...]
        # much more efficiently by not calling get_match_candidates_count() on elements
        # that have already been matched with one of the leading Blanks. this approach
        # is only valid for Expressions that are not Orderless (as with Orderless, the
        # concept of leading items does not exist).
        #
        # simple performance test case:
        #
        # f[x_, {a__, b_}] = 0;
        # f[x_, y_] := y + Total[x];
        # First[Timing[f[Range[5000], 1]]]"
        #
        # without "leading_blanks", Range[5000] will be tested against {a__, b_} in a
        # call to get_match_candidates_count(), which is slow.

        unmatched_elements = expression.elements
        leading_blanks = not A_ORDERLESS & attributes

        for element in self.elements:
            match_count = element.get_match_count()

            if leading_blanks:
                if tuple(match_count) == (
                    1,
                    1,
                ):  # Blank? (i.e. length exactly 1?)
                    if not unmatched_elements:
                        raise StopGenerator_ExpressionPattern_match()
                    if not element.does_match(
                        unmatched_elements[0], evaluation, pre_vars
                    ):
                        raise StopGenerator_ExpressionPattern_match()
                    unmatched_elements = unmatched_elements[1:]
                else:
                    leading_blanks = False

            if not leading_blanks:
                candidates = element.get_match_candidates_count(
                    unmatched_elements,
                    expression,
                    attributes,
                    evaluation,
                    pre_vars,
                )
                if candidates < match_count[0]:
                    raise StopGenerator_ExpressionPattern_match()

        # for new_vars, rest in self.match_element(    # nopep8
        #    self.elements[0], self.elements[1:], ([], expression.elements),
        #    pre_vars, expression, attributes, evaluation, first=True,
        #    fully=fully, element_count=len(self.elements)):
        # def yield_element(new_vars, rest):
        #    yield_func(new_vars, rest)
        self.match_element(
            yield_func,
            next_element,
            tuple(next_elements),
            ([], expression.elements),
            pre_vars,
            expression,
            attributes,
            evaluation,
            first=True,
            fully=fully,
            element_count=len(self.elements),
        )

    # for head_vars, _ in self.head.match(expression.get_head(), vars,
    # evaluation):
    def yield_head(head_vars, _):
        if self.elements:
            # pre_choices = self.get_pre_choices(
            #    expression, attributes, head_vars)
            # for pre_vars in pre_choices:

            self.get_pre_choices(self, yield_choice, expression, attributes, head_vars)
        else:
            if not expression.elements:
                yield_func(head_vars, None)
            else:
                return

    self.head.match(yield_head, expression.get_head(), vars_dict, evaluation)


def expression_pattern_match_element_orderless(
    parms: dict,
    candidates: tuple,
    element_candidates: Union[tuple, set],
    less_first: bool,
    set_lengths: tuple,
):
    """
    match element for orderless expressions
    """
    # we only want element_candidates to be a set if we're orderless.
    # otherwise, constructing a set() is very slow for large lists.
    # performance test case:
    # x = Range[100000]; Timing[Combinatorica`BinarySearch[x, 100]]
    from mathics.builtin.patterns import Pattern

    element: BaseElement = parms["element"]
    element_candidates = set(element_candidates)  # for fast lookup

    sets = None
    if isinstance(element, Pattern):
        varname = element.elements[0].get_name()
        existing = parms["vars_dict"].get(varname, None)
        if existing is not None:
            head = existing.get_head()
            if head.get_name() == "System`Sequence" or (
                A_FLAT & parms["attributes"] and head == parms["expression"].get_head()
            ):
                needed = existing.elements
            else:
                needed = (existing,)
            available = list(candidates)
            for needed_element in needed:
                if (
                    needed_element in available
                    and needed_element in element_candidates  # nopep8
                ):
                    available.remove(needed_element)
                else:
                    return set()
            sets = [
                (
                    needed,
                    (
                        [],
                        available,
                    ),
                )
            ]

    if sets is None:
        sets = subsets(
            candidates,
            included=element_candidates,
            less_first=less_first,
            *set_lengths,
        )
    return sets


# TODO: adding the annotations for items
# and items_rest as ``tuples`` produce failures in cython.
# We should investigate what is the right type to pass here.
def expression_pattern_match_element_process_items(
    items: Union[tuple, list],
    items_rest: Union[tuple, list],
    parms: dict,
):
    # Include wrappings like Plus[a, b] only if not all items taken
    # - in that case we would match the same expression over and over.

    attributes: int = parms["attributes"]
    element_count: int = parms["element_count"]
    expression: Expression = parms["expression"]
    evaluation: Evaluation = parms["evaluation"]
    fully: bool = parms["fully"]
    pattern: ExpressionPattern = parms["pattern"]
    rest_expression = parms["rest_expression"]
    yield_func: Callable = parms["yield_func"]

    include_flattened: bool = parms["try_flattened"] and 0 < len(items) < len(
        expression.elements
    )

    # Don't try flattened when the expression would remain the same!

    def element_yield(next_vars_parm, next_rest_parm):
        # if next_rest is None:
        #    next_rest = ([], [])
        # yield_func(next_vars, (rest_expression[0] + items_rest[0],
        # next_rest[1]))
        if next_rest_parm is None:
            yield_func(
                next_vars_parm,
                (list(chain(rest_expression[0], items_rest[0])), []),
            )
        else:
            yield_func(
                next_vars_parm,
                (
                    list(chain(rest_expression[0], items_rest[0])),
                    next_rest_parm[1],
                ),
            )

    def match_yield(new_vars, _):
        if parms["rest_elements"]:
            pattern.match_element(
                element_yield,
                parms["next_element"],
                parms["next_rest_elements"],
                items_rest,
                new_vars,
                expression,
                attributes,
                evaluation,
                fully=fully,
                depth=parms["depth"],
                element_index=parms["next_index"],
                element_count=element_count,
            )
        else:
            if not fully or (not items_rest[0] and not items_rest[1]):
                yield_func(new_vars, items_rest)

    def yield_wrapping(item):
        parms["element"].match(
            match_yield,
            item,
            parms["vars"],
            evaluation,
            fully=True,
            head=expression.head,
            element_index=parms["element_index"],
            element_count=element_count,
        )

    pattern.get_wrappings(
        yield_wrapping,
        tuple(items),
        parms["match_count"][1],
        expression,
        attributes,
        include_flattened=include_flattened,
    )


# TODO: these two functions should collect all their arguments
# in a dict
def get_pre_choices_with_order(
    pat: ExpressionPattern,
    yield_choice: Callable,
    expression: Expression,
    attributes: int,
    vars_dict: dict,
):
    """
    Yield pre choices for expressions without
    the attribute Orderless.

    In this case, all we have to do is to call
    the parameter `yield_choice` with the collected
    var_dict.
    """
    yield_choice(vars_dict)


def get_pre_choices_orderless(
    pat: ExpressionPattern,
    yield_choice: Callable,
    expression: Expression,
    attributes: int,
    vars_dict: dict,
):
    """
    Yield pre choices for expressions with
    the attribute Orderless.

    This case is more involved, since the pattern can include subpatterns.

    """
    patterns = pat.filter_elements("Pattern")
    # a dict with entries having patterns with the same name
    # which are not in vars_dict.
    groups = {}
    prev_pattern = prev_name = None
    for pattern in patterns:
        name = pattern.elements[0].get_name()
        existing = vars_dict.get(name, None)
        if existing is None:
            # There's no need for pre-choices if the variable is
            # already set.
            if name == prev_name:
                if name in groups:
                    groups[name].append(pattern)
                else:
                    groups[name] = [prev_pattern, pattern]
            prev_pattern = pattern
            prev_name = name
    # prev_element = None

    # count duplicate elements
    expr_groups = {}
    for element in expression.elements:
        expr_groups[element] = expr_groups.get(element, 0) + 1

    def per_name(yield_name: Callable, groups: Tuple, vars_dict: dict):
        """
        Yields possible variable settings (dictionaries) for the
        remaining pattern groups
        """
        # TODO: check why this condition is never reached in tests.
        if groups:
            # name, patterns = groups[0]

            # match_count = [0, None]
            # for pattern in patterns:
            #     sub_match_count = pattern.get_match_count()
            #     if sub_match_count[0] > match_count[0]:
            #         match_count[0] = sub_match_count[0]
            #     if match_count[1] is None or (
            #         sub_match_count[1] is not None
            #         and sub_match_count[1] < match_count[1]
            #     ):
            #         match_count[1] = sub_match_count[1]
            # # possibilities = [{}]
            # # sum = 0

            # def per_expr(yield_expr, expr_groups, sum_int=0):
            #     """
            #     Yields possible values (sequence lists) for the current
            #     variable (name) taking into account the
            #     (expression, count)'s in expr_groups
            #     """

            #     if expr_groups:
            #         expr, count = expr_groups.popitem()
            #         max_per_pattern = count // len(patterns)
            #         for per_pattern in range(max_per_pattern, -1, -1):
            #             for next_expr in per_expr(  # nopep8
            #                 expr_groups, sum_int + per_pattern
            #             ):
            #                 yield_expr([expr] * per_pattern + next_expr)
            #     else:
            #         if sum_int >= match_count[0]:
            #             yield_expr([])
            #         # Until we learn that the below is incorrect,
            #         # we'll return basically no match.
            #         yield None

            # # for sequence in per_expr(expr_groups.items()):
            # def yield_expr(sequence):
            #     # FIXME: this call is wrong and needs a
            #     # wrapper_function as the 1st parameter.
            #     wrappings = pat.get_wrappings(
            #         sequence, match_count[1], expression, attributes
            #     )
            #     for wrapping in wrappings:
            #         1/0
            #         # for next in per_name(groups[1:], vars_dict):

            #         def yield_next(next_expr):
            #             setting = next_expr.copy()
            #             setting[name] = wrapping
            #             yield_name(setting)

            #         per_name(yield_next, groups[1:], vars_dict)

            # per_expr(yield_expr, expr_groups)
            pass
        else:  # no groups left
            yield_name(vars_dict)

    # for setting in per_name(groups.items(), vars):
    # def yield_name(setting):
    #    yield_func(setting)
    per_name(yield_choice, tuple(groups.items()), vars_dict)
