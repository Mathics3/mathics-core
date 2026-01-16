# -*- coding: utf-8 -*-
"""
This module contains basic low-level functions that combine an ``Expression``
with an ``Evaluation`` objects to produce ``BoxExpressions``, following
makeboxes rules.
"""


from typing import Optional, Union

from mathics.core.atoms import Complex, Rational, String
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFullForm,
    SymbolList,
    SymbolMakeBoxes,
)
from mathics.core.systemsymbols import (  # SymbolRule, SymbolRuleDelayed,
    SymbolComplex,
    SymbolInputForm,
    SymbolRational,
    SymbolStandardForm,
    SymbolTraditionalForm,
)
from mathics.eval.makeboxes.formatvalues import do_format
from mathics.eval.makeboxes.precedence import parenthesize


def to_boxes(x, evaluation: Evaluation, options={}) -> BoxElementMixin:
    """
    This function takes the expression ``x``
    and tries to reduce it to a ``BoxElementMixin``
    expression using an evaluation object.
    """
    if isinstance(x, BoxElementMixin):
        return x
    if isinstance(x, Atom):
        x = x.atom_to_boxes(SymbolStandardForm, evaluation)
        return to_boxes(x, evaluation, options)
    if isinstance(x, Expression):
        if x.has_form("MakeBoxes", None):
            x_boxed = x.evaluate(evaluation)
        else:
            x_boxed = eval_makeboxes(x, evaluation)
        if isinstance(x_boxed, BoxElementMixin):
            return x_boxed
        if isinstance(x_boxed, Atom):
            return to_boxes(x_boxed, evaluation, options)
    return eval_makeboxes_fullform(x, evaluation)


# this temporarily replaces the _BoxedString class
def _boxed_string(string: str, **options):
    from mathics.builtin.box.layout import StyleBox

    return StyleBox(String(string), **options)


def eval_makeboxes_outputform(expr, evaluation, form, **kwargs):
    """
    Build a 2D representation of the expression using only keyboard characters.
    """
    from mathics.builtin.box.layout import PaneBox
    from mathics.form.outputform import expression_to_outputform_text

    text_outputform = str(expression_to_outputform_text(expr, evaluation, **kwargs))
    elem1 = PaneBox(String('"' + text_outputform + '"'))
    return elem1


# TODO: evaluation is needed because `atom_to_boxes` uses it. Can we remove this
# argument?
def eval_makeboxes_fullform(
    expr: BaseElement, evaluation: Evaluation
) -> BoxElementMixin:
    """Same as MakeBoxes[FullForm[expr_], f_]"""
    from mathics.builtin.box.layout import RowBox

    if isinstance(expr, BoxElementMixin):
        expr = expr.to_expression()
    if isinstance(expr, Atom):
        if isinstance(expr, Rational):
            expr = Expression(SymbolRational, expr.numerator(), expr.denominator())
        elif isinstance(expr, Complex):
            expr = Expression(SymbolComplex, expr.real, expr.imag)
        else:
            return expr.atom_to_boxes(SymbolFullForm, evaluation)
    head, elements = expr.head, expr.elements
    boxed_elements = tuple(
        (eval_makeboxes_fullform(element, evaluation) for element in elements)
    )
    # In some places it would be less verbose to use special outputs for
    # `List`, `Rule` and `RuleDelayed`. WMA does not that, but we do it for
    # `List`.
    #
    # if head is SymbolRule and len(elements) == 2:
    #    return RowBox(boxed_elements[0], String("->"), boxed_elements[1])
    # if head is SymbolRuleDelayed and len(elements) == 2:
    #    return RowBox(boxed_elements[0], String(":>"), boxed_elements[1])
    if head is SymbolList:
        left, right, sep = (String(ch) for ch in ("{", "}", ","))
        result_elements = [left]
    else:
        left, right, sep = (String(ch) for ch in ("[", "]", ","))
        result_elements = [eval_makeboxes_fullform(head, evaluation), left]

    if len(boxed_elements) > 1:
        arguments = []
        for b_elem in boxed_elements:
            if len(arguments) > 0:
                arguments.append(sep)
            arguments.append(b_elem)
        result_elements.append(RowBox(*arguments))
    elif len(boxed_elements) == 1:
        result_elements.append(boxed_elements[0])
    result_elements.append(right)
    return RowBox(*result_elements)


def eval_generic_makeboxes(expr, f, evaluation):
    """MakeBoxes[expr_,
    f:TraditionalForm|StandardForm|OutputForm|InputForm]"""
    from mathics.builtin.box.layout import RowBox

    if isinstance(expr, BoxElementMixin):
        expr = expr.to_expression()
    if isinstance(expr, Atom):
        return expr.atom_to_boxes(f, evaluation)
    else:
        head = expr.head
        elements = expr.elements

        f_name = f.get_name()
        if f_name == "System`TraditionalForm":
            left, right = "(", ")"
        else:
            left, right = "[", "]"

        # Parenthesize infix operators at the head of expressions,
        # like (a + b)[x], but not f[a] in f[a][b].
        #
        head_boxes = parenthesize(
            670, head, Expression(SymbolMakeBoxes, head, f), False
        )
        head_boxes = head_boxes.evaluate(evaluation)
        head_boxes = to_boxes(head_boxes, evaluation)
        result = [head_boxes, to_boxes(String(left), evaluation)]

        if len(elements) > 1:
            row = []
            if f_name in (
                "System`InputForm",
                "System`OutputForm",
            ):
                sep = ", "
            else:
                sep = ","
            for index, element in enumerate(elements):
                if index > 0:
                    row.append(to_boxes(String(sep), evaluation))
                row.append(
                    to_boxes(
                        Expression(SymbolMakeBoxes, element, f).evaluate(evaluation),
                        evaluation,
                    )
                )
            result.append(RowBox(*row))
        elif len(elements) == 1:
            result.append(
                to_boxes(
                    Expression(SymbolMakeBoxes, elements[0], f).evaluate(evaluation),
                    evaluation,
                )
            )
        result.append(to_boxes(String(right), evaluation))
        return RowBox(*result)


def eval_makeboxes(
    expr, evaluation: Evaluation, form=SymbolStandardForm
) -> Optional[BaseElement]:
    """
    This function takes the definitions provided by the evaluation
    object, and produces a boxed fullform for expr.

    Basically: MakeBoxes[expr // form]
    """
    # This is going to be reimplemented. By now, much of the formatting
    # relies in rules of the form `MakeBoxes[expr, OutputForm]`
    # which is wrong.
    if form in (SymbolFullForm, SymbolInputForm):
        expr = Expression(form, expr)
        form = SymbolStandardForm
    result = Expression(SymbolMakeBoxes, expr, form).evaluate(evaluation)
    return result


def format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol, **kwargs
) -> Optional[Union[BoxElementMixin, BaseElement]]:
    """
    Applies formats associated to the expression, and then calls Makeboxes
    """
    # Halt any potential evaluation tracing while performing boxing.
    evaluation.is_boxing = True

    if form not in (SymbolStandardForm, SymbolTraditionalForm):
        element = Expression(form, element)
        form = SymbolStandardForm

    while element.get_head() is form:
        element = element.elements[0]

    # In order to work like in WMA, `format_element`
    # should evaluate `MakeBoxes[element//form, StandardForm]`
    # Then, MakeBoxes[expr_, StandardForm], for any expr,
    # should apply Format[...] rules, and then
    # MakeBoxes[...] rules. These rules should be stored
    # as FormatValues[...]
    # As a first step in that direction, let's mimic this behaviour
    # just for the case of OutputForm:
    if element.has_form("OutputForm", 1):
        return eval_makeboxes_outputform(element.elements[0], evaluation, form)

    formatted_expr = do_format(element, evaluation, form)
    if formatted_expr is None:
        return None

    result_box = eval_makeboxes(formatted_expr, evaluation, form)
    if isinstance(result_box, String):
        return result_box
    if isinstance(result_box, BoxElementMixin):
        return result_box
    else:
        return eval_makeboxes_fullform(element, evaluation)
