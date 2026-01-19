"""
This module implements the "OutputForm" textual representation of expressions.

OutputForm is two-dimensional keyboard-character-only output, suitable for CLI
and text terminals.
"""

import re
from typing import Callable, Dict, List, Union

from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    PrecisionReal,
    Rational,
    Real,
    String,
)
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import BoxError, Expression
from mathics.core.list import ListExpression
from mathics.core.number import dps
from mathics.core.symbols import Atom, Symbol, SymbolFullForm, SymbolList, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolDerivative,
    SymbolInfinity,
    SymbolInfix,
    SymbolLeft,
    SymbolNonAssociative,
    SymbolNone,
    SymbolOutputForm,
    SymbolPower,
    SymbolRight,
    SymbolStandardForm,
    SymbolTableForm,
    SymbolTraditionalForm,
)
from mathics.eval.strings import safe_backquotes
from mathics.eval.testing_expressions import expr_min
from mathics.format.box import do_format, format_element
from mathics.format.box.numberform import (
    get_baseform_elements,
    get_numberform_parameters,
    numberform_to_boxes,
)
from mathics.settings import SYSTEM_CHARACTER_ENCODING

from .inputform import render_input_form
from .util import (
    BLANKS_TO_STRINGS,
    PRECEDENCE_FUNCTION_APPLY,
    PRECEDENCE_PLUS,
    PRECEDENCE_POWER,
    PRECEDENCE_TIMES,
    _WrongFormattedExpression,
    collect_in_pre_post_arguments,
    get_operator_str,
    parenthesize,
    process_options,
    square_bracket,
    text_cells_to_grid,
)

EXPR_TO_OUTPUTFORM_TEXT_MAP: Dict[str, Callable] = {}
MULTI_NEWLINE_RE = re.compile(r"\n{2,}")


class IsNotGrid(Exception):
    pass


class IsNot2DArray(Exception):
    pass


def _default_render_output_form(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """
    Default representation of a function
    """
    if isinstance(expr, Atom):
        result = expr.atom_to_boxes(SymbolOutputForm, evaluation)
        if isinstance(result, String):
            return result.value
        return result.boxes_to_text()

    expr_head = expr.head
    head = render_output_form(expr_head, evaluation, **kwargs)
    if not isinstance(expr_head, Atom):
        head = parenthesize(PRECEDENCE_FUNCTION_APPLY, expr_head, head, False)

    comma = ", "
    elements = [render_output_form(elem, evaluation) for elem in expr.elements]
    result = elements.pop(0) if elements else ""
    while elements:
        result = result + comma + elements.pop(0)

    form = kwargs.get("_Form", SymbolOutputForm)

    if form is SymbolTraditionalForm:
        return head + f"({result})"
    return head + square_bracket(result)


def _divide(num, den, evaluation, **kwargs):
    infix_form = Expression(
        SymbolInfix,
        ListExpression(num, den),
        String("/"),
        Integer(PRECEDENCE_TIMES),
        SymbolLeft,
    )
    return render_output_form(infix_form, evaluation, **kwargs)


def _strip_1_parm_render_output_form(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    if not isinstance(expr.head, Symbol) or len(expr.elements) != 1:
        raise _WrongFormattedExpression
    inner = expr.elements[0]
    return render_output_form(inner, evaluation, **kwargs)


def register_outputform(head_name):
    def _register(func):
        EXPR_TO_OUTPUTFORM_TEXT_MAP[head_name] = func
        return func

    return _register


@register_outputform("System`Association")
def _association_outputform(expr: Expression, evaluation: Evaluation, **kwargs):
    head = expr.head
    if not isinstance(head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    parts = []
    for element in elements:
        if not element.has_form(("Rule", "RuleDelayed"), 2):
            raise _WrongFormattedExpression
        parts.append(rule_to_outputform_text(element, evaluation, **kwargs))
    return "<|" + ", ".join(parts) + "|>"


@register_outputform("System`BaseForm")
def _baseform_outputform(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    number, base_expr = elements
    try:
        val, base = get_baseform_elements(number, base_expr, evaluation)
    except ValueError:
        raise _WrongFormattedExpression

    if base is None:
        return _default_render_output_form(number, evaluation, **kwargs)
    return val + "_" + str(base)


@register_outputform("System`Blank")
@register_outputform("System`BlankSequence")
@register_outputform("System`BlankNullSequence")
def blank_pattern(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    if len(elements) > 1:
        return _default_render_output_form(expr, evaluation, **kwargs)
    if elements:
        elem = render_output_form(elements[0], evaluation, **kwargs)
    else:
        elem = ""
    head = expr.head
    try:
        return BLANKS_TO_STRINGS[head] + elem
    except KeyError:
        return _default_render_output_form(expr, evaluation, **kwargs)


@register_outputform("System`Derivative")
def derivative_render_output_form(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """Derivative operator"""
    head = expr.get_head()
    # Pure derivative 'Derivative[...]'
    if head is SymbolDerivative:
        return _default_render_output_form(expr, evaluation, **kwargs)

    super_head = head.get_head()
    # Derivative[...][F]
    if super_head is SymbolDerivative:
        expr_elements = expr.elements
        if len(expr_elements) != 1:
            return _default_render_output_form(expr, evaluation, **kwargs)
        function_head = render_output_form(expr_elements[0], evaluation, **kwargs)
        derivatives = head.elements
        if len(derivatives) == 1:
            order_iv = derivatives[0]
            if isinstance(order_iv, Integer):
                order_value = order_iv.value
                if 0 < order_value < 3:
                    return function_head + "'" * order_value
                # -> f^(value)
        # -> f^(fomat(derivatives))

    # Derivative[...][F][...]....
    # Full Function with arguments: delegate to the default conversion.
    # It will call us again with the head
    return _default_render_output_form(expr, evaluation, **kwargs)


@register_outputform("System`Divide")
def divide_render_output_form(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    if len(expr.elements) != 2:
        raise _WrongFormattedExpression
    num, den = expr.elements
    return _divide(num, den, evaluation, **kwargs)


def render_output_form(expr: BaseElement, evaluation: Evaluation, **kwargs):
    """
    Build a pretty-print text from an `Expression`
    """
    format_expr: Expression = do_format(expr, evaluation, SymbolOutputForm)  # type: ignore

    while format_expr.has_form("HoldForm", 1):  # type: ignore
        format_expr = format_expr.elements[0]

    if format_expr is None:
        return ""

    head = format_expr.get_head()
    lookup_name: str = head.get_name() or head.get_lookup_name()
    callback = EXPR_TO_OUTPUTFORM_TEXT_MAP.get(lookup_name, None)
    if callback is None:
        if head in evaluation.definitions.outputforms:
            callback = other_forms
        else:
            callback = _default_render_output_form
    try:
        result = callback(format_expr, evaluation, **kwargs)
        return result
    except _WrongFormattedExpression:
        # If the key is not present, or the execution fails for any reason, use
        # the default
        pass
    return _default_render_output_form(format_expr, evaluation, **kwargs)


@register_outputform("System`Graphics")
def graphics(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    return "-Graphics-"


@register_outputform("System`Graphics3D")
def graphics3d(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    return "-Graphics3D-"


@register_outputform("System`Grid")
def grid_render_output_form(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    if len(expr.elements) == 0:
        raise IsNotGrid
    if len(expr.elements) > 1 and not expr.elements[1].has_form(
        ["Rule", "RuleDelayed"], 2
    ):
        raise IsNotGrid
    if not expr.elements[0].has_form("List", None):
        raise IsNotGrid

    elements = expr.elements[0].elements
    rows = []
    for idx, item in enumerate(elements):
        if item.has_form("List", None):
            rows.append(
                [
                    render_output_form(item_elem, evaluation, **kwargs)
                    for item_elem in item.elements
                ]
            )
        else:
            rows.append(render_output_form(item, evaluation, **kwargs))

    return text_cells_to_grid(rows)


register_outputform("System`HoldForm")(_strip_1_parm_render_output_form)


@register_outputform("System`FullForm")
def other_forms(expr, evaluation, **kwargs):
    from mathics.format.box import format_element

    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    print("format", expr)
    result = format_element(expr, evaluation, SymbolStandardForm, **kwargs)
    return result.boxes_to_text()


@register_outputform("System`Integer")
def integer_outputform(n, evaluation, **kwargs):
    if not isinstance(n, Integer):
        raise _WrongFormattedExpression

    py_digits, py_options = kwargs.setdefault(
        "_numberform_args",
        (
            (None, None),
            {},
        ),
    )
    digits, padding = py_digits
    result = numberform_to_boxes(n, digits, padding, evaluation, py_options)
    if isinstance(result, String):
        return result.value
    return result.boxes_to_text()


@register_outputform("System`Image")
def image_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr, Atom):
        raise _WrongFormattedExpression

    return "-Image-"


@register_outputform("System`Infix")
def _infix_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    """
    Convert Infix[...] into a InputForm string.
    """
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    # In WMA, expressions associated to Infix operators are not
    # formatted using this path: in some way, when an expression
    # has a head that matches with a symbol associated to an infix
    # operator, WMA builds its inputform without passing through
    # its "Infix" form.
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, ops_lst, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # In WMA, Infix needs at least two operands:
    # In Mathics, we allow Infix with one operator:
    # if len(operands) < 2:
    #    raise _WrongFormattedExpression

    # Process the first operand:
    parenthesized = group in (SymbolRight, SymbolNonAssociative)
    operand = operands[0]
    result = str(render_output_form(operand, evaluation, **kwargs))
    result = parenthesize(precedence, operand, result, parenthesized)

    # Process the rest of operands
    parenthesized = group in (SymbolLeft, SymbolNonAssociative)
    num_ops = len(ops_lst)
    for index, operand in enumerate(operands[1:]):
        curr_op = ops_lst[index % num_ops]
        # In OutputForm we always add the spaces, except for
        # " "
        if curr_op != " ":
            curr_op = f" {curr_op} "

        operand_txt = str(render_output_form(operand, evaluation, **kwargs))
        operand_txt = parenthesize(precedence, operand, operand_txt, parenthesized)

        result = "".join(
            (
                result,
                curr_op,
                operand_txt,
            )
        )
    return result


@register_outputform("System`InputForm")
def inputform(expr: Expression, evaluation: Evaluation, **kwargs):
    return render_input_form(expr, evaluation, **kwargs)


@register_outputform("System`List")
def list_render_output_form(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression
    elements = expr.elements
    if not elements:
        return "{}"

    result, *rest_elems = (
        render_output_form(elem, evaluation, **kwargs) for elem in expr.elements
    )
    comma_tb = ", "
    for next_elem in rest_elems:
        result = result + comma_tb + next_elem
    return "{" + result + "}"


@register_outputform("System`MathMLForm")
def mathmlform_render_output_form(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    if not expr.has_form("MathMLForm", 1):
        raise _WrongFormattedExpression

    #  boxes = format_element(expr.elements[0], evaluation)
    boxes = format_element(expr.elements[0], evaluation, SymbolTraditionalForm)
    return boxes.boxes_to_mathml()  # type: ignore[union-attr]


@register_outputform("System`MatrixForm")
def matrixform_render_output_form(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    # return parenthesize(tableform_render_output_form(expr, evaluation, **kwargs))
    return tableform_render_output_form(expr, evaluation, **kwargs)


@register_outputform("System`MessageName")
def message_name_outputform(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    if len(elements) != 2:
        return _default_render_output_form(expr, evaluation, **kwargs)
    symb, msg = elements
    if not (isinstance(symb, Symbol) and isinstance(msg, String)):
        return _default_render_output_form(expr, evaluation, **kwargs)
    symbol_name = evaluation.definitions.shorten_name(symb.get_name())
    return f"{symbol_name}::{msg.value}"


@register_outputform("System`NumberForm")
def _numberform_outputform(expr, evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    target, precision, py_options = get_numberform_parameters(expr, evaluation)
    if isinstance(precision, Integer):
        py_precision = (
            precision.value,
            None,
        )
    elif precision is not None and precision.has_form("List", 2):
        py_precision = precision.to_python()
    else:
        py_precision = (
            None,
            None,
        )

    kwargs["_numberform_args"] = (
        py_precision,
        py_options,
    )
    return render_output_form(target, evaluation, **kwargs)


@register_outputform("System`Out")
def out_outputform(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    if len(elements) > 1:
        raise _WrongFormattedExpression
    if len(elements) == 0:
        return "%"
    indx = elements[0]
    if not isinstance(indx, Integer):
        raise _WrongFormattedExpression
    value = indx.value
    if value == 0:
        raise _WrongFormattedExpression
    if value > 0:
        return f"%{value}"
    return "%" * (-value)


@register_outputform("System`OutputForm")
def outputform(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    if len(elements) != 1:
        return _default_render_output_form(expr, evaluation, **kwargs)
    return render_output_form(elements[0], evaluation, **kwargs)


@register_outputform("System`Part")
def part(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    if len(elements) == 0:
        raise _WrongFormattedExpression
    elements_fmt = [render_output_form(elem, evaluation, **kwargs) for elem in elements]
    if len(elements_fmt) == 1:
        return elements_fmt[0]
    result = elements_fmt[0]
    args = ", ".join(elements_fmt[1:])
    return f"{result}[[{args}]]"


@register_outputform("System`Pattern")
def pattern(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    if len(elements) != 2:
        return _default_render_output_form(expr, evaluation, **kwargs)
    name, pat = (render_output_form(elem, evaluation, **kwargs) for elem in elements)
    return name + pat


@register_outputform("System`Plus")
def plus_render_output_form(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    result = ""
    for i, term in enumerate(elements):
        if term.has_form("Times", None):
            # If the first element is -1, remove it and use
            # a minus sign. Otherwise, if negative, do not add a sign.
            first = term.elements[0]
            if isinstance(first, Integer):
                if first.value == -1:
                    result = (
                        result
                        + " - "
                        + render_output_form(
                            Expression(SymbolTimes, *term.elements[1:]),
                            evaluation,
                            **kwargs,
                        )
                    )
                    continue
                elif first.value < 0:
                    result = (
                        result + " " + render_output_form(term, evaluation, **kwargs)
                    )
                    continue
            elif isinstance(first, Real):
                if first.value < 0:
                    result = (
                        result + " " + render_output_form(term, evaluation, **kwargs)
                    )
                    continue
            result = result + " + " + render_output_form(term, evaluation, **kwargs)
            ## TODO: handle complex numbers?
        else:
            elem_txt: str = render_output_form(term, evaluation, **kwargs)
            elem_txt = parenthesize(PRECEDENCE_PLUS, term, elem_txt, True)
            result = result + " + " + elem_txt

    return result


@register_outputform("System`Power")
def power_render_output_form(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    if len(expr.elements) != 2:
        raise _WrongFormattedExpression

    infix_form = Expression(
        SymbolInfix,
        ListExpression(*(expr.elements)),
        String("^"),
        Integer(PRECEDENCE_POWER),
        SymbolRight,
    )
    return render_output_form(infix_form, evaluation, **kwargs)


@register_outputform("System`PrecedenceForm")
def precedenceform_render_output_form(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    if len(expr.elements) == 2:
        return render_output_form(expr.elements[0], evaluation, **kwargs)
    raise _WrongFormattedExpression


@register_outputform("System`Prefix")
def _prefix_output_text(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    """
    Convert Prefix[...] into a InputForm string.
    """
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, op_head, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Prefix works with just one operand:
    if len(operands) != 1:
        raise _WrongFormattedExpression
    operand = operands[0]
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    target_txt = render_output_form(operand, evaluation, **kwargs)
    parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
    target_txt = parenthesize(precedence, operand, target_txt, parenthesized)
    return op_head + target_txt


@register_outputform("System`Postfix")
def _postfix_output_text(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    """
    Convert Postfix[...] into a InputForm string.
    """
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, op_head, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Prefix works with just one operand:
    if len(operands) != 1:
        raise _WrongFormattedExpression
    operand = operands[0]
    target_txt = render_output_form(operand, evaluation, **kwargs)
    parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
    target_txt = parenthesize(precedence, operand, target_txt, parenthesized)
    return target_txt + op_head


@register_outputform("System`Rational")
def rational_render_output_form(
    n: Union[Rational, Expression], evaluation: Evaluation, **kwargs
):
    if isinstance(n, Rational):
        num, den = n.numerator(), n.denominator()  # type: ignore[union-attr]
    elif n.has_form("Rational", 2):
        num, den = n.elements  # type: ignore[union-attr]
    else:
        raise _WrongFormattedExpression
    return _divide(num, den, evaluation, **kwargs)


@register_outputform("System`Real")
def real_render_output_form(n: Real, evaluation: Evaluation, **kwargs):
    if not isinstance(n, Real):
        raise _WrongFormattedExpression
    py_digits, py_options = kwargs.setdefault(
        "_numberform_args",
        (
            (None, None),
            {},
        ),
    )
    py_options["_Form"] = "System`OutputForm"
    digits, padding = py_digits
    if digits is None:
        digits = dps(n.get_precision()) if isinstance(n, PrecisionReal) else 6

    result = numberform_to_boxes(n, digits, padding, evaluation, py_options)
    if isinstance(result, String):
        return result.value
    return result.boxes_to_text()


@register_outputform("System`Row")
def row_to_outputform_text(expr, evaluation: Evaluation, **kwargs):
    """Row[{...}]"""
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements[0].elements
    return "".join(render_output_form(elem, evaluation, **kwargs) for elem in elements)


@register_outputform("System`Rule")
@register_outputform("System`RuleDelayed")
def rule_to_outputform_text(expr, evaluation: Evaluation, **kwargs):
    """Rule|RuleDelayed[{...}]"""
    head = expr.head
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    if len(elements) != 2:
        return _default_render_output_form(expr, evaluation, **kwargs)
    pat, rule = (render_output_form(elem, evaluation, **kwargs) for elem in elements)
    kwargs["_render_function"] = render_output_form
    op_str = get_operator_str(head, evaluation, **kwargs)
    return f"{pat} {op_str} {rule}"


@register_outputform("System`SequenceForm")
def sequenceform_to_outputform_text(expr, evaluation: Evaluation, **kwargs):
    """Row[{...}]"""
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    return "".join(render_output_form(elem, evaluation, **kwargs) for elem in elements)


@register_outputform("System`Slot")
def _slot_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

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


@register_outputform("System`SlotSequence")
def _slotsequence_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs):
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

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


@register_outputform("System`String")
def string_render_output_form(expr: String, evaluation: Evaluation, **kwargs) -> str:
    # lines = expr.value.split("\n")
    # max_len = max([len(line) for line in lines])
    # lines = [line + (max_len - len(line)) * " " for line in lines]
    # return "\n".join(lines)
    value = expr.value
    return value


@register_outputform("System`StringForm")
def stringform_render_output_form(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    items = expr.elements
    if len(items) == 0:
        evaluation.message("StringForm", "argm", Integer0)
        raise _WrongFormattedExpression
    strform, *items = items

    if not isinstance(strform, String):
        evaluation.message("StringForm", "string", strform)
        raise _WrongFormattedExpression

    items = [render_output_form(item, evaluation, **kwargs) for item in items]

    curr_indx = 0
    strform_str = safe_backquotes(strform.value)
    parts = strform_str.split("`")
    parts = [part.replace("\\[RawBackquote]", "`") for part in parts]
    result = [parts[0]]
    if len(parts) <= 1:
        return result[0]

    quote_open = True
    remaining = len(parts) - 1
    num_items = len(items)
    for part in parts[1:]:
        remaining -= 1
        # If quote_open, the part must be a placeholder
        if quote_open:
            # If not remaining, there is a not closed '`'
            # character:
            if not remaining:
                evaluation.message("StringForm", "sfq", strform)
                return strform.value
            # part must be an index or an empty string.
            # If is an empty string, pick the next element:
            if part == "":
                if curr_indx >= num_items:
                    evaluation.message(
                        "StringForm",
                        "sfr",
                        Integer(num_items + 1),
                        Integer(num_items),
                        strform,
                    )
                    return strform.value
                result.append(items[curr_indx])
                curr_indx += 1
                quote_open = False
                continue
            # Otherwise, must be a positive integer:
            try:
                indx = int(part)
            except ValueError:
                evaluation.message(
                    "StringForm", "sfr", Integer0, Integer(num_items), strform
                )
                return strform.value
            # indx must be greater than 0, and not greater than
            # the number of items
            if indx <= 0 or indx > len(items):
                evaluation.message(
                    "StringForm", "sfr", Integer(indx), Integer(len(items)), strform
                )
                return strform.value
            result.append(items[indx - 1])
            curr_indx = indx
            quote_open = False
            continue

        result.append(part)
        quote_open = True

    return "".join(result)


@register_outputform("System`Style")
def style_to_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    if not elements:
        raise _WrongFormattedExpression
    return render_output_form(elements[0], evaluation, **kwargs)


@register_outputform("System`Symbol")
def symbol_render_output_form(symb: Symbol, evaluation: Evaluation, **kwargs):
    if not isinstance(symb, Symbol):
        raise _WrongFormattedExpression

    return evaluation.definitions.shorten_name(symb.name)


@register_outputform("System`TableForm")
def tableform_render_output_form(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    from mathics.builtin.tensors import get_dimensions

    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements

    if len(elements) == 0:
        raise _WrongFormattedExpression

    table, *opts = elements
    dims = len(get_dimensions(table, head=SymbolList))
    process_options(kwargs, opts)

    def value_or_none(x):
        if isinstance(x, Integer):
            return x.value
        return None

    depth = value_or_none(
        expr_min((Integer(dims), kwargs.pop("TableDepth", SymbolInfinity)))
    )
    if depth is None:
        evaluation.message(expr.head.get_name(), "int")
        raise _WrongFormattedExpression
    if depth <= 0:
        return render_output_form(table, evaluation, **kwargs)
    if depth == 1:
        return text_cells_to_grid(
            [
                [render_output_form(elem, evaluation, **kwargs)]
                for elem in table.elements
            ]
        )
    kwargs["TableDepth"] = Integer(depth - 2)

    def transform_item(item):
        if depth > 2:
            return tableform_render_output_form(
                Expression(SymbolTableForm, item), evaluation, **kwargs
            )
        else:
            return render_output_form(item, evaluation, **kwargs)

    grid_array = [[transform_item(elem) for elem in row] for row in table.elements]
    return text_cells_to_grid(grid_array)


@register_outputform("System`TeXForm")
def _texform_outputform(expr, evaluation, **kwargs):
    if not expr.has_form("TeXForm", 1):
        raise _WrongFormattedExpression

    boxes = format_element(expr.elements[0], evaluation, SymbolTraditionalForm)
    try:
        tex = boxes.boxes_to_tex(evaluation=evaluation)  # type: ignore[union-attr]
        tex = MULTI_NEWLINE_RE.sub("\n", tex)
        tex = tex.replace(" \uF74c", " \\, d")  # tmp hack for Integrate
        return tex
    except BoxError:
        evaluation.message(
            "General",
            "notboxes",
            Expression(SymbolFullForm, boxes).evaluate(evaluation),
        )
        raise _WrongFormattedExpression


@register_outputform("System`Times")
def times_render_output_form(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    if not isinstance(expr.head, Symbol):
        raise _WrongFormattedExpression

    elements = expr.elements
    if len(elements) < 2:
        return _default_render_output_form(expr, evaluation, **kwargs)
    num: List[BaseElement] = []
    den: List[BaseElement] = []
    # First, split factors with integer, negative powers:
    for factor in elements:
        if factor.has_form("Power", 2):
            base, exponent = factor.elements
            if isinstance(exponent, Integer):
                if exponent.value == -1:
                    den.append(base)
                    continue
                elif exponent.value < 0:
                    den.append(Expression(SymbolPower, base, Integer(-exponent.value)))
                    continue
        elif isinstance(factor, Rational):
            num.append(factor.numerator())
            den.append(factor.denominator())
            continue
        elif factor.has_form("Rational", 2):
            elem_elements = factor.elements
            num.append(elem_elements[0])
            den.append(elem_elements[1])
            continue

        num.append(factor)

    # If there are integer, negative powers, process as a fraction:
    if den:
        den_expr = den[0] if len(den) == 1 else Expression(SymbolTimes, *den)
        num_expr = (
            Expression(SymbolTimes, *num)
            if len(num) > 1
            else num[0]
            if len(num) == 1
            else Integer1
        )
        return _divide(num_expr, den_expr, evaluation, **kwargs)

    # there are no integer negative powers:
    if len(num) == 1:
        return render_output_form(num[0], evaluation, **kwargs)

    prefactor = 1
    result: str = ""
    for i, factor in enumerate(num):
        if factor is IntegerM1:
            prefactor *= -1
            continue
        if isinstance(factor, Integer):
            prefactor *= -1
            factor = Integer(-factor.value)

        factor_txt = render_output_form(factor, evaluation, **kwargs)
        factor_txt = parenthesize(PRECEDENCE_TIMES, factor, factor_txt, True)
        if i == 0:
            result = factor_txt
        else:
            result = result + " " + factor_txt
    if result == "":
        result = "1"
    if prefactor == -1:
        result = "-" + result
    return result
