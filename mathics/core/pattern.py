# cython: language_level=3
# cython: profile=False
# -*- coding: utf-8 -*-


from mathics.core.element import ensure_context
from mathics.core.expression import Expression
from mathics.core.symbols import Atom, Symbol, system_symbols
from mathics.core.systemsymbols import SymbolSequence
from mathics.core.util import subsets, subranges, permutations
from itertools import chain

from mathics.core.attributes import flat, one_identity, orderless

# from mathics.core.pattern_nocython import (
#    StopGenerator #, Pattern #, ExpressionPattern)
# from mathics.core import pattern_nocython


SYSTEM_SYMBOLS_PATTERNS = system_symbols(
    "Pattern",
    "PatternTest",
    "Condition",
    "Optional",
    "Blank",
    "BlankSequence",
    "BlankNullSequence",
    "Alternatives",
    "OptionsPattern",
    "Repeated",
    "RepeatedNull",
)


def Pattern_create(expr):
    from mathics.builtin import pattern_objects

    # from mathics.core.pattern import AtomPattern, ExpressionPattern

    name = expr.get_head_name()
    pattern_object = pattern_objects.get(name)
    if pattern_object is not None:
        return pattern_object(expr)
    if isinstance(expr, Atom):
        return AtomPattern(expr)
    else:
        return ExpressionPattern(expr)


class StopGenerator(Exception):
    def __init__(self, value=None):
        self.value = value


class StopGenerator_ExpressionPattern_match(StopGenerator):
    pass


class StopGenerator_Pattern(StopGenerator):
    pass


class Pattern:
    """
    This is the base class for Mathics Pattern objects.

    A Pattern is a way to represent classes of expressions.
    For example, ``F[x_Symbol]`` is a pattern which matches an expression whose
    Head is ``F`` and that has a single parameter which is kind of Symbol.
    When the pattern matches, the symbol is bound to the parameter ``x``.
    """

    create = staticmethod(Pattern_create)

    def match(
        self,
        yield_func,
        expression,
        vars,
        evaluation,
        head=None,
        element_index=None,
        element_count=None,
        fully=True,
        wrap_oneid=True,
    ):
        raise NotImplementedError

    """def match(self, expression, vars, evaluation,
              head=None, element_index=None, element_count=None,
        fully=True, wrap_oneid=True):
        #raise NotImplementedError
        result = []
        def yield_func(vars, rest):
            result.append(vars, rest)
        self._match(yield_func, expression, vars, evaluation, head,
                    element_index, element_count, fully, wrap_oneid)
        return result"""

    def does_match(self, expression, evaluation, vars=None, fully=True):

        if vars is None:
            vars = {}
        # for sub_vars, rest in self.match(  # nopep8
        #    expression, vars, evaluation, fully=fully):
        #    return True

        def yield_match(sub_vars, rest):
            raise StopGenerator_Pattern(True)

        try:
            self.match(yield_match, expression, vars, evaluation, fully=fully)
        except StopGenerator_Pattern as exc:
            return exc.value
        return False

    def get_name(self):
        return self.expr.get_name()

    def get_head_name(self):
        return self.expr.get_head_name()

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        return self.expr.sameQ(other.expr)

    def get_head(self):
        return self.expr.get_head()

    def get_elements(self):
        return self.expr.get_elements()

    # Compatibily with old code. Deprecated, but remove after a little bit
    get_leaves = get_elements

    def get_sort_key(self, pattern_sort=False) -> tuple:
        return self.expr.get_sort_key(pattern_sort=pattern_sort)

    def get_lookup_name(self):
        return self.expr.get_lookup_name()

    def get_attributes(self, definitions):
        return self.expr.get_attributes(definitions)

    def get_sequence(self):
        return self.expr.get_sequence()

    def get_option_values(self):
        return self.expr.get_option_values()

    def has_form(self, *args):
        return self.expr.has_form(*args)

    def get_match_candidates(
        self, elements, expression, attributes, evaluation, vars={}
    ):
        return []

    def get_match_candidates_count(
        self, elements, expression, attributes, evaluation, vars={}
    ):
        return len(
            self.get_match_candidates(
                elements, expression, attributes, evaluation, vars
            )
        )


class AtomPattern(Pattern):
    def __init__(self, expr):
        self.atom = expr
        self.expr = expr
        if isinstance(expr, Symbol):
            self.match = self.match_symbol
            self.get_match_candidates = self.get_match_symbol_candidates

    def __repr__(self):
        return "<AtomPattern: %s>" % self.atom

    def match_symbol(
        self,
        yield_func,
        expression,
        vars,
        evaluation,
        head=None,
        element_index=None,
        element_count=None,
        fully=True,
        wrap_oneid=True,
    ):
        if expression is self.atom:
            yield_func(vars, None)

    def get_match_symbol_candidates(
        self, elements, expression, attributes, evaluation, vars={}
    ):
        return [element for element in elements if (element is self.atom)]

    def match(
        self,
        yield_func,
        expression,
        vars,
        evaluation,
        head=None,
        element_index=None,
        element_count=None,
        fully=True,
        wrap_oneid=True,
    ):
        if isinstance(expression, Atom) and expression.sameQ(self.atom):
            # yield vars, None
            yield_func(vars, None)

    def get_match_candidates(
        self, elements, expression, attributes, evaluation, vars={}
    ):
        return [
            element
            for element in elements
            if (isinstance(element, Atom) and element.sameQ(self.atom))
        ]

    def get_match_count(self, vars={}):
        return (1, 1)


# class StopGenerator_ExpressionPattern_match(StopGenerator):
#    pass


class ExpressionPattern(Pattern):
    # get_pre_choices = pattern_nocython.get_pre_choices
    # match = pattern_nocython.match

    def match(
        self,
        yield_func,
        expression,
        vars,
        evaluation,
        head=None,
        element_index=None,
        element_count=None,
        fully=True,
        wrap_oneid=True,
    ):
        evaluation.check_stopped()
        attributes = self.head.get_attributes(evaluation.definitions)
        if not flat & attributes:
            fully = True
        if not isinstance(expression, Atom):
            # don't do this here, as self.get_pre_choices changes the
            # ordering of the elements!
            # if self.elements:
            #    next_element = self.elements[0]
            #    next_elements = self.elements[1:]

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
                leading_blanks = not orderless & attributes

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
                #    fully=fully, element_count=len(self.elements),
                #    wrap_oneid=expression.get_head_name() != 'System`MakeBoxes'):
                # def yield_element(new_vars, rest):
                #    yield_func(new_vars, rest)
                self.match_element(
                    yield_func,
                    next_element,
                    next_elements,
                    ([], expression.elements),
                    pre_vars,
                    expression,
                    attributes,
                    evaluation,
                    first=True,
                    fully=fully,
                    element_count=len(self.elements),
                    wrap_oneid=expression.get_head_name() != "System`MakeBoxes",
                )

            # for head_vars, _ in self.head.match(expression.get_head(), vars,
            # evaluation):
            def yield_head(head_vars, _):
                if self.elements:
                    # pre_choices = self.get_pre_choices(
                    #    expression, attributes, head_vars)
                    # for pre_vars in pre_choices:

                    self.get_pre_choices(
                        yield_choice, expression, attributes, head_vars
                    )
                else:
                    if not expression.elements:
                        yield_func(head_vars, None)
                    else:
                        return

            try:
                self.head.match(yield_head, expression.get_head(), vars, evaluation)
            except StopGenerator_ExpressionPattern_match:
                return
        if (
            wrap_oneid
            and not evaluation.ignore_oneidentity
            and one_identity & attributes
            and not self.head.expr.sameQ(expression.get_head())  # nopep8
            and not self.head.expr.sameQ(expression)
        ):
            # and not OneIdentity &
            # (expression.get_attributes(evaluation.definitions) |
            # expression.get_head().get_attributes(evaluation.definitions)):
            new_expression = Expression(self.head.expr, expression)
            for element in self.elements:
                element.match_count = element.get_match_count()
                element.candidates = [expression]
                # element.get_match_candidates(
                #    new_expression.elements, new_expression, attributes,
                #    evaluation, vars)
                if len(element.candidates) < element.match_count[0]:
                    return
            # for new_vars, rest in self.match_element(
            #    self.elements[0], self.elements[1:],
            #    ([], [expression]), vars, new_expression, attributes,
            #    evaluation, first=True, fully=fully,
            #    element_count=len(self.elements), wrap_oneid=True):
            # def yield_element(new_vars, rest):
            #    yield_func(new_vars, rest)
            self.match_element(
                yield_func,
                self.elements[0],
                self.elements[1:],
                ([], [expression]),
                vars,
                new_expression,
                attributes,
                evaluation,
                first=True,
                fully=fully,
                element_count=len(self.elements),
                wrap_oneid=True,
            )

    def get_pre_choices(self, yield_func, expression, attributes, vars):
        if orderless & attributes:
            self.sort()
            patterns = self.filter_elements("Pattern")
            groups = {}
            prev_pattern = prev_name = None
            for pattern in patterns:
                name = pattern.elements[0].get_name()
                existing = vars.get(name, None)
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

            def per_name(yield_name, groups, vars):
                """
                Yields possible variable settings (dictionaries) for the
                remaining pattern groups
                """

                if groups:
                    name, patterns = groups[0]

                    match_count = [0, None]
                    for pattern in patterns:
                        sub_match_count = pattern.get_match_count()
                        if sub_match_count[0] > match_count[0]:
                            match_count[0] = sub_match_count[0]
                        if match_count[1] is None or (
                            sub_match_count[1] is not None
                            and sub_match_count[1] < match_count[1]
                        ):
                            match_count[1] = sub_match_count[1]
                    # possibilities = [{}]
                    # sum = 0

                    def per_expr(yield_expr, expr_groups, sum=0):
                        """
                        Yields possible values (sequence lists) for the current
                        variable (name) taking into account the
                        (expression, count)'s in expr_groups
                        """

                        if expr_groups:
                            expr, count = expr_groups.popitem()
                            max_per_pattern = count // len(patterns)
                            for per_pattern in range(max_per_pattern, -1, -1):
                                for next in per_expr(  # nopep8
                                    expr_groups, sum + per_pattern
                                ):
                                    yield_expr([expr] * per_pattern + next)
                        else:
                            if sum >= match_count[0]:
                                yield_expr([])
                            # Until we learn that the below is incorrect, we'll return basically no match.
                            yield None

                    # for sequence in per_expr(expr_groups.items()):
                    def yield_expr(sequence):
                        # FIXME: this call is wrong and needs a
                        # wrapper_function as the 1st parameter.
                        wrappings = self.get_wrappings(
                            sequence, match_count[1], expression, attributes
                        )
                        for wrapping in wrappings:
                            # for next in per_name(groups[1:], vars):
                            def yield_next(next):
                                setting = next.copy()
                                setting[name] = wrapping
                                yield_name(setting)

                            per_name(yield_next, groups[1:], vars)

                    per_expr(yield_expr, expr_groups)
                else:  # no groups left
                    yield_name(vars)

            # for setting in per_name(groups.items(), vars):
            # def yield_name(setting):
            #    yield_func(setting)
            per_name(yield_func, list(groups.items()), vars)
        else:
            yield_func(vars)

    def __init__(self, expr):
        self.head = Pattern.create(expr.head)
        self.elements = [Pattern.create(element) for element in expr.elements]
        self.expr = expr

    def filter_elements(self, head_name):
        head_name = ensure_context(head_name)
        return [
            element for element in self.elements if element.get_head_name() == head_name
        ]

    def __repr__(self):
        return "<ExpressionPattern: %s>" % self.expr

    def get_match_count(self, vars={}):
        return (1, 1)

    def get_wrappings(
        self,
        yield_func,
        items,
        max_count,
        expression,
        attributes,
        include_flattened=True,
    ):
        if len(items) == 1:
            yield_func(items[0])
        else:
            if max_count is None or len(items) <= max_count:
                if orderless & attributes:
                    for perm in permutations(items):
                        sequence = Expression(SymbolSequence, *perm)
                        sequence.pattern_sequence = True
                        yield_func(sequence)
                else:
                    sequence = Expression(SymbolSequence, *items)
                    sequence.pattern_sequence = True
                    yield_func(sequence)
            if flat & attributes and include_flattened:
                yield_func(Expression(expression.get_head(), *items))

    def match_element(
        self,
        yield_func,
        element,
        rest_elements,
        rest_expression,
        vars,
        expression,
        attributes,
        evaluation,
        element_index=1,
        element_count=None,
        first=False,
        fully=True,
        depth=1,
        wrap_oneid=True,
    ):

        if rest_expression is None:
            rest_expression = ([], [])

        evaluation.check_stopped()

        match_count = element.get_match_count(vars)
        element_candidates = element.get_match_candidates(
            rest_expression[1],  # element.candidates,
            expression,
            attributes,
            evaluation,
            vars,
        )

        if len(element_candidates) < match_count[0]:
            return

        candidates = rest_expression[1]

        # "Artificially" only use more elements than specified for some kind
        # of pattern.
        # TODO: This could be further optimized!
        try_flattened = flat & attributes and (
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
            flat & attributes and element.get_head() == expression.head
        )

        less_first = len(rest_elements) > 0

        if orderless & attributes:
            # we only want element_candidates to be a set if we're orderless.
            # otherwise, constructing a set() is very slow for large lists.
            # performance test case:
            # x = Range[100000]; Timing[Combinatorica`BinarySearch[x, 100]]
            element_candidates = set(element_candidates)  # for fast lookup

            sets = None
            if element.get_head_name() == "System`Pattern":
                varname = element.elements[0].get_name()
                existing = vars.get(varname, None)
                if existing is not None:
                    head = existing.get_head()
                    if head.get_name() == "System`Sequence" or (
                        flat & attributes and head == expression.get_head()
                    ):
                        needed = existing.elements
                    else:
                        needed = [existing]
                    available = list(candidates)
                    for needed_element in needed:
                        if (
                            needed_element in available
                            and needed_element in element_candidates  # nopep8
                        ):
                            available.remove(needed_element)
                        else:
                            return
                    sets = [(needed, ([], available))]

            if sets is None:
                sets = subsets(
                    candidates,
                    included=element_candidates,
                    less_first=less_first,
                    *set_lengths
                )
        else:
            sets = subranges(
                candidates,
                flexible_start=first and not fully,
                included=element_candidates,
                less_first=less_first,
                *set_lengths
            )

        if rest_elements:
            next_element = rest_elements[0]
            next_rest_elements = rest_elements[1:]
        next_depth = depth + 1
        next_index = element_index + 1

        for items, items_rest in sets:
            # Include wrappings like Plus[a, b] only if not all items taken
            # - in that case we would match the same expression over and over.

            include_flattened = try_flattened and 0 < len(items) < len(
                expression.elements
            )

            # Don't try flattened when the expression would remain the same!

            def element_yield(next_vars, next_rest):
                # if next_rest is None:
                #    next_rest = ([], [])
                # yield_func(next_vars, (rest_expression[0] + items_rest[0],
                # next_rest[1]))
                if next_rest is None:
                    yield_func(
                        next_vars, (list(chain(rest_expression[0], items_rest[0])), [])
                    )
                else:
                    yield_func(
                        next_vars,
                        (list(chain(rest_expression[0], items_rest[0])), next_rest[1]),
                    )

            def match_yield(new_vars, _):
                if rest_elements:
                    self.match_element(
                        element_yield,
                        next_element,
                        next_rest_elements,
                        items_rest,
                        new_vars,
                        expression,
                        attributes,
                        evaluation,
                        fully=fully,
                        depth=next_depth,
                        element_index=next_index,
                        element_count=element_count,
                        wrap_oneid=wrap_oneid,
                    )
                else:
                    if not fully or (not items_rest[0] and not items_rest[1]):
                        yield_func(new_vars, items_rest)

            def yield_wrapping(item):
                element.match(
                    match_yield,
                    item,
                    vars,
                    evaluation,
                    fully=True,
                    head=expression.head,
                    element_index=element_index,
                    element_count=element_count,
                    wrap_oneid=wrap_oneid,
                )

            self.get_wrappings(
                yield_wrapping,
                items,
                match_count[1],
                expression,
                attributes,
                include_flattened=include_flattened,
            )

    def get_match_candidates(
        self, elements, expression, attributes, evaluation, vars={}
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
            if self.does_match(element, evaluation, vars)
        ]

    def get_match_candidates_count(
        self, elements, expression, attributes, evaluation, vars={}
    ):
        """
        Finds possible elements that could match the pattern, ignoring future
        pattern variable definitions, but taking into account already fixed
        variables.
        """
        # TODO: fixed_vars!

        count = 0
        for element in elements:
            if self.does_match(element, evaluation, vars):
                count += 1
        return count

    def sort(self):
        self.elements.sort(key=lambda e: e.get_sort_key(pattern_sort=True))
