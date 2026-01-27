# -*- coding: utf-8 -*-
"""
This module contains basic low-level functions that combine an ``Expression``
with an ``Evaluation`` objects to produce ``BoxExpressions``, following
makeboxes rules.
"""


from typing import List

from mathics.core.atoms import Complex, Rational, String
from mathics.core.element import BaseElement, BoxElementMixin, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFalse,
    SymbolFullForm,
    SymbolList,
    SymbolMakeBoxes,
    SymbolTrue,
)
from mathics.core.systemsymbols import (  # SymbolRule, SymbolRuleDelayed,
    SymbolAborted,
    SymbolComplex,
    SymbolRational,
    SymbolStandardForm,
    SymbolTraditionalForm,
)
from mathics.eval.lists import list_boxes
from mathics.format.box.formatvalues import do_format
from mathics.format.box.precedence import parenthesize

BOX_FORMS = {SymbolStandardForm, SymbolTraditionalForm}
PRINT_FORMS_CALLBACK = {}


def is_print_form_callback(head_name: str):
    """Decorator for register print form callbacks"""

    def _register(func):
        PRINT_FORMS_CALLBACK[head_name] = func
        return func

    return _register


# this temporarily replaces the _BoxedString class
def _boxed_string(string: str, **options):
    from mathics.builtin.box.layout import StyleBox

    return StyleBox(String(string), **options)


@is_print_form_callback("System`StandardForm")
def eval_makeboxes_standard_form(expr, evaluation):
    from mathics.builtin.box.layout import FormBox, TagBox

    boxed = apply_makeboxes_rules(expr, evaluation, SymbolStandardForm)
    boxed = FormBox(boxed, SymbolStandardForm)
    boxed = TagBox(boxed, SymbolStandardForm, **{"System`Editable": SymbolTrue})
    return boxed


@is_print_form_callback("System`TraditionalForm")
def eval_makeboxes_traditional_form(expr, evaluation):
    from mathics.builtin.box.layout import FormBox, TagBox

    boxed = apply_makeboxes_rules(expr, evaluation, SymbolTraditionalForm)
    boxed = FormBox(boxed, SymbolTraditionalForm)
    boxed = TagBox(boxed, SymbolTraditionalForm, **{"System`Editable": SymbolTrue})
    return boxed


def apply_makeboxes_rules(
    expr: BaseElement, evaluation: Evaluation, form: Symbol = SymbolStandardForm
) -> BoxElementMixin:
    """
    This function takes the definitions provided by the evaluation
    object, and produces a boxed fullform for expr.

    Basically: MakeBoxes[expr, form]
    """
    assert form in BOX_FORMS, f"{form} not in BOX_FORMS"

    def yield_rules():
        # Look
        for lookup in (expr.get_lookup_name(), "System`MakeBoxes"):
            definition = evaluation.definitions.get_definition(lookup)
            for rule in definition.formatvalues.get("_MakeBoxes", []):
                yield rule

    mb_expr = Expression(SymbolMakeBoxes, expr, form)
    boxed = mb_expr
    for rule in yield_rules():
        try:
            boxed = rule.apply(mb_expr, evaluation, fully=False)
        except OverflowError:
            evaluation.message("General", "ovfl")
            boxed = mb_expr
            continue
        if boxed is mb_expr or boxed is None or boxed.sameQ(mb_expr):
            continue
        if boxed is SymbolAborted:
            return String("Aborted")
        if isinstance(boxed, EvalMixin):
            return boxed.evaluate(evaluation)
        if isinstance(boxed, BoxElementMixin):
            return boxed
    return eval_generic_makeboxes(expr, form, evaluation)


# TODO: evaluation is needed because `atom_to_boxes` uses it. Can we remove this
# argument?
@is_print_form_callback("System`FullForm")
def eval_makeboxes_fullform(
    element: BaseElement, evaluation: Evaluation, **kwargs
) -> BoxElementMixin:
    from mathics.builtin.box.layout import StyleBox, TagBox

    result = eval_makeboxes_fullform_recursive(element, evaluation, **kwargs)
    style_box = StyleBox(
        result,
        **{
            "System`ShowSpecialCharacters": SymbolFalse,
            "System`ShowStringCharacters": SymbolTrue,
            "System`NumberMarks": SymbolTrue,
        },
    )
    return TagBox(style_box, SymbolFullForm)


def eval_makeboxes_fullform_recursive(
    element: BaseElement, evaluation: Evaluation, **kwargs
) -> BoxElementMixin:
    """Same as MakeBoxes[FullForm[expr_], f_]"""
    from mathics.builtin.box.expression import BoxExpression
    from mathics.builtin.box.layout import RowBox

    expr: Expression

    if isinstance(element, BoxExpression):
        expr = element.to_expression()
    elif isinstance(element, Atom):
        if isinstance(element, Rational):
            expr = Expression(
                SymbolRational, element.numerator(), element.denominator()
            )
        elif isinstance(element, Complex):
            expr = Expression(SymbolComplex, element.real, element.imag)
        else:
            return element.atom_to_boxes(SymbolFullForm, evaluation)
    elif isinstance(element, Expression):
        expr = element
    else:
        raise ValueError

    head, elements = expr.head, expr.elements
    boxed_elements = tuple(
        (eval_makeboxes_fullform_recursive(element, evaluation) for element in elements)
    )
    # In some places it would be less verbose to use special outputs for
    # `List`, `Rule` and `RuleDelayed`. WMA does not that, but we do it for
    # `List`.
    #
    # if head is SymbolRule and len(elements) == 2:
    #    return RowBox(boxed_elements[0], String("->"), boxed_elements[1])
    # if head is SymbolRuleDelayed and len(elements) == 2:
    #    return RowBox(boxed_elements[0], String(":>"), boxed_elements[1])
    result_elements: List[BoxElementMixin]
    if head is SymbolList:
        left, right, sep = (String(ch) for ch in ("{", "}", ","))
        result_elements = [left]
    else:
        left, right, sep = (String(ch) for ch in ("[", "]", ","))
        result_elements = [eval_makeboxes_fullform_recursive(head, evaluation), left]

    if len(boxed_elements) > 1:
        arguments: List[BoxElementMixin] = []
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
    f:TraditionalForm|StandardForm]"""
    from mathics.builtin.box.layout import RowBox

    assert f in BOX_FORMS, f"{f} not in BOX_FORMS"
    if isinstance(expr, BoxElementMixin):
        expr = expr.to_expression()
    if isinstance(expr, Atom):
        return expr.atom_to_boxes(f, evaluation)
    if expr.has_form("List", None):
        return RowBox(*list_boxes(expr.elements, f, evaluation, "{", "}"))
    else:
        head = expr.head
        elements = expr.elements
        printform_callback = PRINT_FORMS_CALLBACK.get(head.get_name(), None)
        if printform_callback is not None:
            return printform_callback(elements[0], evaluation)

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
                raise ValueError
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


def format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol, **kwargs
) -> BoxElementMixin:
    """
    Applies formats associated to the expression, and then calls Makeboxes
    """
    # print("format element", element, form)
    evaluation.is_boxing = True
    formatted_expr = do_format(element, evaluation, form)
    # print("formatted_expr", formatted_expr)
    if form not in BOX_FORMS:
        formatted_expr = Expression(form, formatted_expr)
        form = SymbolStandardForm
    result_box = apply_makeboxes_rules(formatted_expr, evaluation, form)
    # print(" boxed", result_box)
    if isinstance(result_box, BoxElementMixin):
        return result_box
    return eval_makeboxes_fullform_recursive(element, evaluation)


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
        if x.has_form("MakeBoxes", 1, 2):
            x_boxed = x.evaluate(evaluation)
            if isinstance(x_boxed, BoxElementMixin):
                return x_boxed
            if isinstance(x_boxed, Atom):
                return to_boxes(x_boxed, evaluation, options)
        else:
            return apply_makeboxes_rules(x, evaluation)
    return eval_makeboxes_fullform_recursive(x, evaluation)
