"""This module contains functions for turning Mathics3 expressions to
InputForm-formatted strings.

`InputForm` produces textual output suitable for being parsed and
evaluated in Mathics CLI.

`InputForm` is not affected by MakeBox assignment.

InputForm versus FullForm
--------------------------

In contrast to `FullForm`, `InputForm` shows arithmetic expressions in
traditional mathematical notation. Apart from that and the allowance
of `InputForm` output to be altered via a `Format` assignment, the
appearance of the result is about the same as `FullForm`.

Internally, `FullForm` produces `String` object,  while `FullForm`
produces a nested `RowBox` structure.

`InputForm` conversion produces an `InterpretationBox` The
`InterpetationBox` preserves information about the original
expression. In contrast, `FullForm` output produces a `TagBox`. In
both cases, underneath the `InterpretationBox` or `Tagbox` is a
`StyleBox`.

"""

from typing import Callable, Dict

from mathics.core.atoms import Integer, String
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Atom
from mathics.core.systemsymbols import (
    SymbolInputForm,
    SymbolLeft,
    SymbolNonAssociative,
    SymbolRight,
)
from mathics.eval.makeboxes.formatvalues import do_format  # , format_element
from mathics.eval.makeboxes.precedence import compare_precedence
from mathics.settings import SYSTEM_CHARACTER_ENCODING

from .util import (
    ARITHMETIC_OPERATOR_STRINGS,
    BLANKS_TO_STRINGS,
    _WrongFormattedExpression,
    bracket,
    collect_in_pre_post_arguments,
    get_operator_str,
    parenthesize,
)

EXPR_TO_INPUTFORM_TEXT_MAP: Dict[str, Callable] = {}


def register_inputform(head_name):
    def _register(func):
        EXPR_TO_INPUTFORM_TEXT_MAP[head_name] = func
        return func

    return _register


def render_input_form(expr, evaluation, **kwargs):
    """
    Build a string with the InputForm of the expression.
    """
    format_expr: Expression = do_format(expr, evaluation, SymbolInputForm)
    while format_expr.has_form("HoldForm", 1):  # type: ignore
        format_expr = format_expr.elements[0]

    lookup_name: str = format_expr.get_head().get_lookup_name()

    try:
        result = EXPR_TO_INPUTFORM_TEXT_MAP[lookup_name](
            format_expr, evaluation, **kwargs
        )
        return result
    except _WrongFormattedExpression:
        # If the key is not present, or the execution fails for any reason, use
        # the default
        pass
    except KeyError:
        pass
    return _generic_to_inputform_text(format_expr, evaluation, **kwargs)

    return ""


@register_inputform("System`Association")
def _association_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
):
    elements = expr.elements
    result = ", ".join(
        [render_input_form(elem, evaluation, **kwargs) for elem in elements]
    )
    return f"<|{result}|>"


def _generic_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Default representation of a function
    """
    if isinstance(expr, Atom):
        result = expr.atom_to_boxes(SymbolInputForm, evaluation)
        if isinstance(result, String):
            return result.value
        return result.boxes_to_text(**kwargs)

    expr_head = expr.head
    head = render_input_form(expr_head, evaluation, **kwargs)
    comma = ", "
    elements = [render_input_form(elem, evaluation, **kwargs) for elem in expr.elements]
    result = elements.pop(0) if elements else ""
    while elements:
        result = result + comma + elements.pop(0)

    return head + bracket(result)


@register_inputform("System`List")
def _list_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    elements = tuple(
        render_input_form(element, evaluation, **kwargs) for element in expr.elements
    )
    result = "{"
    if elements:
        first, *rest = elements
        result += first
        for elem in rest:
            result += ", " + elem
    return result + "}"


@register_inputform("System`Infix")
def _infix_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Convert Infix[...] into a InputForm string.
    """
    # In WMA, expressions associated to Infix operators are not
    # formatted using this path: in some way, when an expression
    # has a head that matches with a symbol associated to an infix
    # operator, WMA builds its inputform without passing through
    # its "Infix" form.
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, ops_lst, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Infix needs at least two operands:
    if len(operands) < 2:
        raise _WrongFormattedExpression

    # Process the operands:
    parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
    for index, operand in enumerate(operands):
        operand_txt = str(render_input_form(operand, evaluation, **kwargs))
        cmp_precedence = compare_precedence(operand, precedence)
        if cmp_precedence is not None and (
            cmp_precedence == -1 or (cmp_precedence == 0 and parenthesized)
        ):
            operand_txt = parenthesize(operand_txt)

        if index == 0:
            result = operand_txt
            # After the first element, for lateral
            # associativity, parenthesized is flipped:
            if group in (SymbolLeft, SymbolRight):
                parenthesized = not parenthesized
        else:
            num_ops = len(ops_lst)
            curr_op = ops_lst[(index - 1) % num_ops]
            if curr_op not in ARITHMETIC_OPERATOR_STRINGS:
                # In the tests, we add spaces just for + and -:
                curr_op = f" {curr_op} "

            result = "".join(
                (
                    result,
                    curr_op,
                    operand_txt,
                )
            )
    return result


@register_inputform("System`Prefix")
def _prefix_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Convert Prefix[...] into a OutputForm string.
    """
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, op_head, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Prefix works with just one operand:
    if len(operands) != 1:
        raise _WrongFormattedExpression
    operand = operands[0]
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    cmp_precedence = compare_precedence(operand, precedence)
    target_txt = render_input_form(operand, evaluation, **kwargs)
    if cmp_precedence is not None and cmp_precedence != 1:
        target_txt = parenthesize(target_txt)
    return op_head + target_txt


@register_inputform("System`Postfix")
def _postfix_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Convert Postfix[...] into a OutputForm string.
    """
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, op_head, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Prefix works with just one operand:
    if len(operands) != 1:
        raise _WrongFormattedExpression
    operand = operands[0]
    cmp_precedence = compare_precedence(operand, precedence)
    target_txt = render_input_form(operand, evaluation, **kwargs)
    if cmp_precedence is not None and cmp_precedence != 1:
        target_txt = parenthesize(target_txt)
    return target_txt + op_head


@register_inputform("System`Blank")
@register_inputform("System`BlankSequence")
@register_inputform("System`BlankNullSequence")
def _blanks(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) > 1:
        return _generic_to_inputform_text(expr, evaluation, **kwargs)
    if elements:
        elem = render_input_form(elements[0], evaluation, **kwargs)
    else:
        elem = ""
    head = expr.head
    try:
        return BLANKS_TO_STRINGS[head] + elem
    except KeyError:
        return _generic_to_inputform_text(expr, evaluation, **kwargs)


@register_inputform("System`Pattern")
def _pattern(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) != 2:
        return _generic_to_inputform_text(expr, evaluation, **kwargs)
    name, pat = (render_input_form(elem, evaluation, **kwargs) for elem in elements)
    return name + pat


@register_inputform("System`Rule")
@register_inputform("System`RuleDelayed")
def _rule_to_inputform_text(expr, evaluation: Evaluation, **kwargs):
    """Rule|RuleDelayed[{...}]"""
    head = expr.head
    elements = expr.elements
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    if len(elements) != 2:
        return _generic_to_inputform_text(expr, evaluation, **kwargs)
    pat, rule = (render_input_form(elem, evaluation, **kwargs) for elem in elements)
    kwargs["_render_function"] = render_input_form
    op_str = get_operator_str(head, evaluation, **kwargs)
    # In WMA there are spaces between operators.
    return pat + f" {op_str} " + rule


@register_inputform("System`Slot")
def _slot_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
):
    elements = expr.elements
    if len(elements) != 1:
        raise _WrongFormattedExpression
    slot = elements[0]
    if isinstance(slot, Integer):
        slot_value = slot.value
        if slot_value < 0:
            raise _WrongFormattedExpression
        return f"#{slot_value}"
    if isinstance(slot, String):
        return f"#{slot.value}"
    raise _WrongFormattedExpression


@register_inputform("System`SlotSequence")
def _slotsequence_expression_to_inputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
):
    elements = expr.elements
    if len(elements) != 1:
        raise _WrongFormattedExpression
    slot = elements[0]
    if isinstance(slot, Integer):
        slot_value = slot.value
        if slot_value < 0:
            raise _WrongFormattedExpression
        return f"##{slot_value}"
    if isinstance(slot, String):
        return f"##{slot.value}"
    raise _WrongFormattedExpression
