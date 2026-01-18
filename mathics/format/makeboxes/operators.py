from typing import Union

from mathics.core.atoms import Integer, Integer1, String
from mathics.core.convert.op import operator_to_ascii, operator_to_unicode
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.parser.parser import NEVER_ADD_PARENTHESIS
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import (
    SymbolInputForm,
    SymbolMakeBoxes,
    SymbolOutputForm,
    SymbolRowBox,
)
from mathics.format.makeboxes.precedence import parenthesize


# FIXME: op should be a string, so remove the Union.
def make_boxes_infix(
    elements, op: Union[String, list], precedence: int, grouping, form: Symbol
):
    result = []
    for index, element in enumerate(elements):
        if index > 0:
            if isinstance(op, list):
                result.append(op[index - 1])
            else:
                result.append(op)
        parenthesized = False
        if grouping == "System`NonAssociative":
            parenthesized = True
        elif grouping == "System`Left" and index > 0:
            parenthesized = True
        elif grouping == "System`Right" and index == 0:
            parenthesized = True

        element_boxes = Expression(SymbolMakeBoxes, element, form)
        element = parenthesize(precedence, element, element_boxes, parenthesized)

        result.append(element)
    return Expression(SymbolRowBox, ListExpression(*result))


def eval_infix(
    self, expr, operator, precedence: Integer, grouping, form: Symbol, evaluation
):
    """MakeBoxes[Infix[expr_, operator_, precedence_:None, grouping_:None],
    form:StandardForm|TraditionalForm|OutputForm|InputForm]"""
    py_precedence = (
        precedence.value if hasattr(precedence, "value") else NEVER_ADD_PARENTHESIS
    )
    grouping = grouping.get_name()

    if isinstance(expr, Atom):
        evaluation.message("Infix", "normal", Integer1)
        return None

    elements = expr.elements
    if len(elements) > 1:
        if operator.has_form("List", len(elements) - 1):
            operator = [format_operator(op, form) for op in operator.elements]
            return make_boxes_infix(elements, operator, py_precedence, grouping, form)
        else:
            encoding_rule = evaluation.definitions.get_ownvalue("$CharacterEncoding")
            encoding = "UTF8" if encoding_rule is None else encoding_rule.value
            op_str = (
                operator.value if isinstance(operator, String) else operator.short_name
            )
            if encoding == "ASCII":
                operator = format_operator(
                    String(operator_to_ascii.get(op_str, op_str)), form
                )
            else:
                operator = format_operator(
                    String(operator_to_unicode.get(op_str, op_str)), form
                )

        return make_boxes_infix(elements, operator, py_precedence, grouping, form)

    elif len(elements) == 1:
        return Expression(SymbolMakeBoxes, elements[0], form)
    else:
        return Expression(SymbolMakeBoxes, expr, form)


def eval_postprefix(self, p, expr, h, precedence, form, evaluation):
    """MakeBoxes[(p:Prefix|Postfix)[expr_, h_, precedence_:None],
    form:StandardForm|TraditionalForm|OutputForm|InputForm]"""

    if not isinstance(h, String):
        h = Expression(SymbolMakeBoxes, h, form)

    py_precedence = precedence.get_int_value()

    elements = expr.elements
    if len(elements) == 1:
        element = elements[0]
        element_boxes = Expression(SymbolMakeBoxes, element, form)
        element = parenthesize(py_precedence, element, element_boxes, True)
        if p.get_name() == "System`Postfix":
            args = (element, h)
        else:
            args = (h, element)

        return Expression(SymbolRowBox, ListExpression(*args).evaluate(evaluation))
    else:
        return Expression(SymbolMakeBoxes, expr, form).evaluate(evaluation)


def format_operator(operator: String, form: BaseElement) -> Union[String, BaseElement]:
    """
    Format infix operator `operator`. To do this outside parameter form is used.
    Sometimes no changes are made and operator is returned unchanged.

    This function probably should be rewritten be more scalable across other forms
    and moved to a module that contiaing similar formatting routines.
    """
    if not isinstance(operator, String):
        return Expression(SymbolMakeBoxes, operator, form)

    op_str = operator.value

    # FIXME: performing a check using the operator symbol representation feels a bit
    # fragile. The operator name seems more straightforward and more robust.
    if form == SymbolInputForm and op_str in ["*", "^", " "]:
        return operator
    elif (
        form in (SymbolInputForm, SymbolOutputForm)
        and not op_str.startswith(" ")
        and not op_str.endswith(" ")
    ):
        # FIXME: Again, testing on specific forms is fragile and not scalable.
        op = String(" " + op_str + " ")
        return op
    return operator
