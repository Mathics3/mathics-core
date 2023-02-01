# -*- coding: utf-8 -*-
"""
List Functions - Miscellaneous

Functions here will eventually get moved to more suitable subsections.
"""

from mathics.builtin.base import Builtin, Test
from mathics.builtin.box.layout import RowBox
from mathics.core.attributes import A_LOCKED, A_PROTECTED
from mathics.core.exceptions import InvalidLevelspecError
from mathics.core.list import ListExpression
from mathics.eval.lists import list_boxes
from mathics.eval.parts import python_levelspec


class LevelQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LevelQ.html</url>

    <dl>
      <dt>'LevelQ[$expr$]'
      <dd>tests whether $expr$ is a valid level specification.
    </dl>

    >> LevelQ[2]
     = True
    >> LevelQ[{2, 4}]
     = True
    >> LevelQ[Infinity]
     = True
    >> LevelQ[a + b]
     = False
    """

    summary_text = "test whether is a valid level specification"

    def test(self, ls):
        try:
            start, stop = python_levelspec(ls)
            return True
        except InvalidLevelspecError:
            return False


class List(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/List.html</url>

    <dl>
      <dt>'List[$e1$, $e2$, ..., $ei$]'
      <dt>'{$e1$, $e2$, ..., $ei$}'
      <dd>represents a list containing the elements $e1$...$ei$.
    </dl>

    'List' is the head of lists:
    >> Head[{1, 2, 3}]
     = List

    Lists can be nested:
    >> {{a, b, {c, d}}}
     = {{a, b, {c, d}}}
    """

    attributes = A_LOCKED | A_PROTECTED
    summary_text = "specify a list explicitly"

    def eval(self, elements, evaluation):
        """List[elements___]"""
        # Pick out the elements part of the parameter elements;
        # we we will call that `elements_part_of_elements__`.
        # Note that the parameter elements may be wrapped in a Sequence[]
        # so remove that if when it is present.
        elements_part_of_elements__ = elements.get_sequence()
        return ListExpression(*elements_part_of_elements__)

    def eval_makeboxes(self, items, f, evaluation):
        """MakeBoxes[{items___},
        f:StandardForm|TraditionalForm|OutputForm|InputForm|FullForm]"""

        items = items.get_sequence()
        return RowBox(*list_boxes(items, f, evaluation, "{", "}"))


class NotListQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/NotListQ.html</url>

    <dl>
      <dt>'NotListQ[$expr$]'
      <dd>returns true if $expr$ is not a list.
    </dl>
    """

    summary_text = "test if an expression is not a list"

    def test(self, expr):
        return expr.get_head_name() != "System`List"
