# -*- coding: utf-8 -*-
"""
Basic Pattern Objects

"""

from abc import ABC
from typing import Optional as OptionalType

from mathics.core.builtin import PatternObject
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.pattern import ATOM_PATTERN_SORT_KEY
from mathics.core.symbols import BaseElement

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.basic"


class _Blank(PatternObject, ABC):
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
      <dt>'Blank'[$h$]
      <dt>'_$h$'
      <dd>represents any expression with head $h$.
    </dl>

    >> MatchQ[a + b, _]
     = True

    Patterns of the form '_'$h$ can be used to test the types of \
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

    def match(self, expression: BaseElement, pattern_context: dict):
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]

        if not expression.has_form("Sequence", 0):
            if self.head is not None:
                if expression.get_head().sameQ(self.head):
                    yield_func(vars_dict, None)
            else:
                yield_func(vars_dict, None)

    def get_sort_key(self, pattern_sort=True):
        if pattern_sort:
            return (
                2,
                11 if self.elements else 21,
                1,
                1,
                0,
                ATOM_PATTERN_SORT_KEY,
                1
                if any(element.undefined_sequence_length() for element in pat.elements)
                else 0,
                tuple(elem.get_sort_key(True) for elem in self.elements),
                1,
            )
        return self.expr.get_sort_key()


class BlankNullSequence(_Blank):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/BlankNullSequence.html</url>

    <dl>
      <dt>'BlankNullSequence[]'
      <dt>'___'
      <dd>represents any sequence of expression elements in a pattern, \
        including an empty sequence.
    </dl>

    'BlankNullSequence' is like 'BlankSequence', except it can match an \
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

    def get_sort_key(self, pattern_sort=True):
        if pattern_sort:
            return (
                2,
                13 if self.elements else 23,
                1,
                1,
                0,
                ATOM_PATTERN_SORT_KEY,
                1
                if any(element.undefined_sequence_length() for element in pat.elements)
                else 0,
                tuple(elem.get_sort_key(True) for elem in self.elements),
                1,
            )
        return self.expr.get_sort_key()

    def undefined_sequence_length(self):
        """
        True if it can match with a variable number of elements.
        For example, `BlankSequence`, `BlankNullSequence` or `RepeatedNull`
        returns `True`. Other pattern objects like `Pattern[name, pat]` returns
        the value associated to `pat`.
        """
        return False


class BlankSequence(_Blank):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/BlankSequence.html</url>

    <dl>
      <dt>'BlankSequence[]'
      <dt>'__'
      <dd>represents any non-empty sequence of expression elements in \
        a pattern.
      <dt>'BlankSequence'[$h$]
      <dt>'__$h$'
      <dd>represents any sequence of elements, all of which have head $h$.
    </dl>

    Use a 'BlankSequence' pattern to stand for a non-empty sequence of \
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

    The value captured by a named 'BlankSequence' pattern is a \
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

    def get_sort_key(self, pattern_sort=True):
        if pattern_sort:
            return (
                2,
                12 if self.elements else 22,
                1,
                1,
                0,
                ATOM_PATTERN_SORT_KEY,
                1
                if any(element.undefined_sequence_length() for element in pat.elements)
                else 0,
                tuple(elem.get_sort_key(True) for elem in self.elements),
                1,
            )
        return self.expr.get_sort_key()

    def undefined_sequence_length(self):
        """
        True if it can match with a variable number of elements.
        For example, `BlankSequence`, `BlankNullSequence` or `RepeatedNull`
        returns `True`. Other pattern objects like `Pattern[name, pat]` returns
        the value associated to `pat`.
        """
        return False
