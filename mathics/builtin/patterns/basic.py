# -*- coding: utf-8 -*-
"""
Basic Pattern Objects

"""

from abc import ABC
from typing import Optional as OptionalType

from mathics.core.builtin import PatternObject
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.keycomparable import (
    BASIC_ATOM_PATTERN_SORT_KEY,
    BLANK_GENERAL_PATTERN_SORT_KEY,
    BLANK_WITH_PATTERN_PATTERN_SORT_KEY,
    BLANKNULLSEQUENCE_GENERAL_PATTERN_SORT_KEY,
    BLANKNULLSEQUENCE_WITH_PATTERN_PATTERN_SORT_KEY,
    BLANKSEQUENCE_GENERAL_PATTERN_SORT_KEY,
    BLANKSEQUENCE_WITH_PATTERN_PATTERN_SORT_KEY,
)
from mathics.core.symbols import BaseElement, Symbol

# This tells documentation how to sort this module
sort_order = "mathics.builtin.rules-and-patterns.basic"


class _Blank(PatternObject, ABC):
    arg_counts = [0, 1]
    target_head: OptionalType[Symbol]
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
            target_head = expr.elements[0]
            assert isinstance(target_head, Symbol)
            self.target_head = target_head
        else:
            # FIXME: elsewhere, some code wants to
            # get the attributes of head.
            # So is this really the best thing to do here?
            self.target_head = None


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
        if expression.has_form("Sequence", 0):
            return

        target_head = self.target_head
        if target_head is not None and expression.get_head() is not target_head:
            return

        # Match!
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]
        yield_func(vars_dict, None)

    @property
    def element_order(self):
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return self.expr.element_order

    @property
    def pattern_precedence(self):
        pattern_key = (
            BLANK_WITH_PATTERN_PATTERN_SORT_KEY
            if self.elements
            else BLANK_GENERAL_PATTERN_SORT_KEY
        )
        return (
            pattern_key,
            BASIC_ATOM_PATTERN_SORT_KEY,
            tuple(element.pattern_precedence for element in self.elements),
        )


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

        target_head = self.target_head
        if target_head:
            elements = expression.get_sequence()
            is_uniform = False
            if isinstance(expression, Expression):
                element_properties = expression.elements_properties
                if element_properties is not None:
                    is_uniform = element_properties.is_uniform
            for element in elements:
                if target_head is not element.get_head():
                    return
                # If the expression is uniform, no further checks are necessary.
                if is_uniform:
                    break

        # Match!
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]
        yield_func(vars_dict, None)

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return self.expr.element_order

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> tuple:
        return (0, None)

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        pattern_key = (
            BLANKNULLSEQUENCE_WITH_PATTERN_PATTERN_SORT_KEY
            if self.elements
            else BLANKNULLSEQUENCE_GENERAL_PATTERN_SORT_KEY
        )
        return (
            pattern_key,
            BASIC_ATOM_PATTERN_SORT_KEY,
            tuple(element.pattern_precedence for element in self.elements),
        )


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
        elements = expression.get_sequence()

        if not elements:
            return

        target_head = self.target_head
        if target_head:
            is_uniform = False
            if isinstance(expression, Expression):
                element_properties = expression.elements_properties
                if element_properties is not None:
                    is_uniform = element_properties.is_uniform
            for element in elements:
                if target_head is not element.get_head():
                    return
                # If the expression is uniform, no further checks are necessary.
                if is_uniform:
                    break

        # Match!
        vars_dict = pattern_context["vars_dict"]
        yield_func = pattern_context["yield_func"]
        yield_func(vars_dict, None)

    def get_match_count(self, vars_dict: OptionalType[dict] = None) -> tuple:
        return (1, None)

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return self.expr.element_order

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        pattern_key = (
            BLANKSEQUENCE_WITH_PATTERN_PATTERN_SORT_KEY
            if self.elements
            else BLANKSEQUENCE_GENERAL_PATTERN_SORT_KEY
        )
        return (
            pattern_key,
            BASIC_ATOM_PATTERN_SORT_KEY,
            tuple(element.pattern_precedence for element in self.elements),
        )
