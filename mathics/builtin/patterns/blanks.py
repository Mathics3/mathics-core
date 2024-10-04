# -*- coding: utf-8 -*-
"""
Blank-like patterns.
"""

from typing import Optional as OptionalType

from mathics.core.builtin import PatternObject, PostfixOperator
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.pattern import BasePattern

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.blank-like"


class _Blank(PatternObject):
    arg_counts = [0, 1]

    _instance = None

    def __new__(cls, *args, **kwargs):
        if kwargs.get("expression", None) is False:
            return super().__new__(cls, *args, **kwargs)

        num_elem = len(args[0].elements)
        assert num_elem < 2, f"{cls} should have at most an element."

        if num_elem != 0:
            return super().__new__(cls, *args, **kwargs)
        # no arguments. Use the singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, evaluation=evaluation)
        if expr.elements:
            self.head = expr.elements[0]
        else:
            # FIXME: elswhere, some code wants to
            # get the attributes of head.
            # So is this really the best thing to do here?
            self.head = None


class Blank(_Blank):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Blank.html</url>

    <dl>
      <dt>'Blank[]'
      <dt>'_'
      <dd>represents any single expression in a pattern.
      <dt>'Blank[$h$]'
      <dt>'_$h$'
      <dd>represents any expression with head $h$.
    </dl>

    >> MatchQ[a + b, _]
     = True

    Patterns of the form '_'$h$ can be used to test the types of
    objects:
    >> MatchQ[42, _Integer]
     = True
    >> MatchQ[1.0, _Integer]
     = False
    >> {42, 1.0, x} /. {_Integer -> "integer", _Real -> "real"} // InputForm
     = {"integer", "real", x}

    'Blank' only matches a single expression:
    >> MatchQ[f[1, 2], f[_]]
     = False
    """

    rules = {
        (
            "MakeBoxes[Verbatim[Blank][], "
            "f:StandardForm|TraditionalForm|OutputForm|InputForm]"
        ): '"_"',
        (
            "MakeBoxes[Verbatim[Blank][head_Symbol], "
            "f:StandardForm|TraditionalForm|OutputForm|InputForm]"
        ): ('"_" <> MakeBoxes[head, f]'),
    }
    summary_text = "match to any single expression"

    def match(self, expression: Expression, pattern_context: dict):
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]

        if not expression.has_form("Sequence", 0):
            if self.head is not None:
                if expression.get_head().sameQ(self.head):
                    yield_func(vars_dict, None)
            else:
                yield_func(vars_dict, None)


class BlankSequence(_Blank):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/BlankSequence.html</url>

    <dl>
      <dt>'BlankSequence[]'
      <dt>'__'
      <dd>represents any non-empty sequence of expression elements in
        a pattern.
      <dt>'BlankSequence[$h$]'
      <dt>'__$h$'
      <dd>represents any sequence of elements, all of which have head $h$.
    </dl>

    Use a 'BlankSequence' pattern to stand for a non-empty sequence of
    arguments:
    >> MatchQ[f[1, 2, 3], f[__]]
     = True
    >> MatchQ[f[], f[__]]
     = False

    '__'$h$ will match only if all elements have head $h$:
    >> MatchQ[f[1, 2, 3], f[__Integer]]
     = True
    >> MatchQ[f[1, 2.0, 3], f[__Integer]]
     = False

    The value captured by a named 'BlankSequence' pattern is a
    'Sequence' object:
    >> f[1, 2, 3] /. f[x__] -> x
     = Sequence[1, 2, 3]
    """

    rules = {
        "MakeBoxes[Verbatim[BlankSequence][], f:StandardForm|TraditionalForm|OutputForm|InputForm]": '"__"',
        "MakeBoxes[Verbatim[BlankSequence][head_Symbol], f:StandardForm|TraditionalForm|OutputForm|InputForm]": '"__" <> MakeBoxes[head, f]',
    }
    summary_text = "match to a non-empty sequence of elements"

    def match(self, expression: Expression, pattern_context: dict):
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]
        elements = expression.get_sequence()
        if not elements:
            return
        if self.head:
            ok = True
            for element in elements:
                if element.get_head() != self.head:
                    ok = False
                    break
            if ok:
                yield_func(vars_dict, None)
        else:
            yield_func(vars_dict, None)

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> tuple:
        return (1, None)


class BlankNullSequence(_Blank):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/BlankNullSequence.html</url>

    <dl>
      <dt>'BlankNullSequence[]'
      <dt>'___'
      <dd>represents any sequence of expression elements in a pattern,
        including an empty sequence.
    </dl>

    'BlankNullSequence' is like 'BlankSequence', except it can match an
    empty sequence:
    >> MatchQ[f[], f[___]]
     = True
    """

    rules = {
        "MakeBoxes[Verbatim[BlankNullSequence][], f:StandardForm|TraditionalForm|OutputForm|InputForm]": '"___"',
        "MakeBoxes[Verbatim[BlankNullSequence][head_Symbol], f:StandardForm|TraditionalForm|OutputForm|InputForm]": '"___" <> MakeBoxes[head, f]',
    }
    summary_text = "match to a sequence of zero or more elements"

    def match(self, expression: Expression, pattern_context: dict):
        """Match with a BlankNullSequence"""
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]
        elements = expression.get_sequence()
        if self.head:
            ok = True
            for element in elements:
                if element.get_head() != self.head:
                    ok = False
                    break
            if ok:
                yield_func(vars_dict, None)
        else:
            yield_func(vars_dict, None)

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> tuple:
        return (0, None)


class Repeated(PostfixOperator, PatternObject):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Repeated.html</url>

    <dl>
      <dt>'Repeated[$pattern$]'
      <dd>matches one or more occurrences of $pattern$.
    </dl>

    >> a_Integer.. // FullForm
     = Repeated[Pattern[a, Blank[Integer]]]
    >> 0..1//FullForm
     = Repeated[0]
    >> {{}, {a}, {a, b}, {a, a, a}, {a, a, a, a}} /. {Repeated[x : a | b, 3]} -> x
     = {{}, a, {a, b}, a, {a, a, a, a}}
    >> f[x, 0, 0, 0] /. f[x, s:0..] -> s
     = Sequence[0, 0, 0]
    """

    arg_counts = [1, 2]
    messages = {
        "range": (
            "Range specification in integers (max or {min, max}) "
            "expected at position `1` in `2`."
        )
    }

    operator = ".."
    summary_text = "match to one or more occurrences of a pattern"

    def init(
        self,
        expr: Expression,
        min_idx: int = 1,
        evaluation: OptionalType[Evaluation] = None,
    ):
        self.pattern = BasePattern.create(expr.elements[0], evaluation=evaluation)
        self.max = None
        self.min = min_idx
        if len(expr.elements) == 2:
            element_1 = expr.elements[1]
            allnumbers = not any(
                element.get_int_value() is None for element in element_1.get_elements()
            )
            if element_1.has_form("List", 1, 2) and allnumbers:
                self.max = element_1.elements[-1].get_int_value()
                self.min = element_1.elements[0].get_int_value()
            elif element_1.get_int_value():
                self.max = element_1.get_int_value()
            else:
                self.error("range", 2, expr)

    def match(self, expression: Expression, pattern_context: dict):
        """Match with Repeated[...]"""
        yield_func = pattern_context["yield_func"]
        vars_dict = pattern_context["vars_dict"]
        evaluation = pattern_context["evaluation"]
        elements = expression.get_sequence()
        if len(elements) < self.min:
            return
        if self.max is not None and len(elements) > self.max:
            return

        def iter_fn(yield_iter, rest_elements, vars_dict):
            if rest_elements:
                # for new_vars_dict, rest in self.pattern.match(rest_elements[0],
                # vars_dict, evaluation):
                def yield_match(new_vars_dict, rest):
                    # for sub_vars_dict, sub_rest in iter(rest_elements[1:],
                    #                                new_vars):
                    #    yield sub_vars_dict, rest
                    iter_fn(yield_iter, rest_elements[1:], new_vars_dict)

                self.pattern.match(
                    rest_elements[0],
                    {
                        "yield_func": yield_match,
                        "vars_dict": vars_dict,
                        "evaluation": evaluation,
                    },
                )
            else:
                yield_iter(vars_dict, None)

        # for vars_dict, rest in iter(elements, vars):
        #    yield_func(vars_dict, rest)
        iter_fn(yield_func, elements, vars_dict)

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> tuple:
        return (self.min, self.max)


class RepeatedNull(Repeated):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/RepeatedNull.html</url>

    <dl>
      <dt>'RepeatedNull[$pattern$]'
      <dd>matches zero or more occurrences of $pattern$.
    </dl>

    >> a___Integer...//FullForm
     = RepeatedNull[Pattern[a, BlankNullSequence[Integer]]]
    >> f[x] /. f[x, 0...] -> t
     = t
    """

    operator = "..."
    summary_text = "match to zero or more occurrences of a pattern"

    def init(
        self, expr: Expression, evaluation: OptionalType[Evaluation] = None
    ) -> None:
        super().init(expr, min_idx=0, evaluation=evaluation)
