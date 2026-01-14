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
    Integer2,
    IntegerM1,
    Rational,
    Real,
    String,
)
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolList, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolDerivative,
    SymbolGrid,
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
from mathics.eval.makeboxes import (  # , format_element
    NumberForm_to_String,
    compare_precedence,
    do_format,
)
from mathics.eval.makeboxes.numberform import get_baseform_elements
from mathics.eval.testing_expressions import expr_min
from mathics.settings import SYSTEM_CHARACTER_ENCODING

from .util import (
    BLANKS_TO_STRINGS,
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


def _default_expression_to_outputform_text(
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
    head = expression_to_outputform_text(expr_head, evaluation, **kwargs)
    comma = ", "
    elements = [
        expression_to_outputform_text(elem, evaluation) for elem in expr.elements
    ]
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
    return expression_to_outputform_text(infix_form, evaluation, **kwargs)


def _strip_1_parm_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    if len(expr.elements) != 1:
        raise _WrongFormattedExpression
    return expression_to_outputform_text(expr.elements[0], evaluation, **kwargs)


def register_outputform(head_name):
    def _register(func):
        EXPR_TO_OUTPUTFORM_TEXT_MAP[head_name] = func
        return func

    return _register


@register_outputform("System`BaseForm")
def _baseform_outputform(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) != 2:
        evaluation.message("BaseForm", "argr", Integer(len(elements)), Integer2)
        raise _WrongFormattedExpression

    number, base_expr = elements
    try:
        val, base = get_baseform_elements(number, base_expr, evaluation)
    except ValueError:
        raise _WrongFormattedExpression

    if base is None:
        return expression_to_outputform_text(number, evaluation, **kwargs)
    return val + "_" + str(base)


@register_outputform("System`Blank")
@register_outputform("System`BlankSequence")
@register_outputform("System`BlankNullSequence")
def blank_pattern(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) > 1:
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
    if elements:
        elem = expression_to_outputform_text(elements[0], evaluation, **kwargs)
    else:
        elem = ""
    head = expr.head
    try:
        return BLANKS_TO_STRINGS[head] + elem
    except KeyError:
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)


@register_outputform("System`Derivative")
def derivative_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    """Derivative operator"""
    head = expr.get_head()
    if head is SymbolDerivative:
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
    super_head = head.get_head()
    if super_head is SymbolDerivative:
        expr_elements = expr.elements
        if len(expr_elements) != 1:
            return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
        function_head = expression_to_outputform_text(
            expr_elements[0], evaluation, **kwargs
        )
        derivatives = head.elements
        if len(derivatives) == 1:
            order_iv = derivatives[0]
            if order_iv == Integer1:
                return function_head + "'"
            elif order_iv == Integer2:
                return function_head + "''"

        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)

    # Full Function with arguments: delegate to the default conversion.
    # It will call us again with the head
    return _default_expression_to_outputform_text(expr, evaluation, **kwargs)


@register_outputform("System`Divide")
def divide_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    if len(expr.elements) != 2:
        raise _WrongFormattedExpression
    num, den = expr.elements
    return _divide(num, den, evaluation, **kwargs)


def expression_to_outputform_text(expr: BaseElement, evaluation: Evaluation, **kwargs):
    """
    Build a pretty-print text from an `Expression`
    """
    format_expr: Expression = do_format(expr, evaluation, SymbolOutputForm)  # type: ignore

    while format_expr.has_form("HoldForm", 1):  # type: ignore
        format_expr = format_expr.elements[0]

    if format_expr is None:
        return ""

    lookup_name: str = format_expr.get_head().get_lookup_name()
    try:
        result = EXPR_TO_OUTPUTFORM_TEXT_MAP[lookup_name](
            format_expr, evaluation, **kwargs
        )
        return result
    except _WrongFormattedExpression:
        # If the key is not present, or the execution fails for any reason, use
        # the default
        pass
    except KeyError:
        pass
    return _default_expression_to_outputform_text(format_expr, evaluation, **kwargs)


@register_outputform("System`Graphics")
def graphics(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    return "-Graphics-"


@register_outputform("System`Graphics3D")
def graphics3d(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    return "-Graphics3D-"


@register_outputform("System`Grid")
def grid_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
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
                    expression_to_outputform_text(item_elem, evaluation, **kwargs)
                    for item_elem in item.elements
                ]
            )
        else:
            rows.append(expression_to_outputform_text(item, evaluation, **kwargs))

    return text_cells_to_grid(rows)


register_outputform("System`HoldForm")(_strip_1_parm_expression_to_outputform_text)


@register_outputform("System`FullForm")
@register_outputform("System`InputForm")
def other_forms(expr, evaluation, **kwargs):
    from mathics.eval.makeboxes import format_element

    result = format_element(expr, evaluation, SymbolStandardForm, **kwargs)
    if isinstance(result, String):
        return result.value
    return result.boxes_to_text()


@register_outputform("System`Image")
def image_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs):
    return "-Image-"


@register_outputform("System`Infix")
def _infix_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
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

    # Process the first operand:
    parenthesized = group in (SymbolNone, SymbolRight, SymbolNonAssociative)
    operand = operands[0]
    result = str(expression_to_outputform_text(operand, evaluation, **kwargs))
    result = parenthesize(precedence, operand, result, parenthesized)

    if group in (SymbolLeft, SymbolRight):
        parenthesized = not parenthesized

    # Process the rest of operands
    num_ops = len(ops_lst)
    for index, operand in enumerate(operands[1:]):
        curr_op = ops_lst[index % num_ops]
        # In OutputForm we always add the spaces, except for
        # " "
        if curr_op != " ":
            curr_op = f" {curr_op} "

        operand_txt = str(expression_to_outputform_text(operand, evaluation, **kwargs))
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
    from .inputform import render_input_form

    return render_input_form(expr, evaluation, **kwargs)


@register_outputform("System`Integer")
def integer_expression_to_outputform_text(n: Integer, evaluation: Evaluation, **kwargs):
    return str(n.value)


@register_outputform("System`List")
def list_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    elements = expr.elements
    if not elements:
        return "{}"

    result, *rest_elems = (
        expression_to_outputform_text(elem, evaluation, **kwargs)
        for elem in expr.elements
    )
    comma_tb = ", "
    for next_elem in rest_elems:
        result = result + comma_tb + next_elem
    return "{" + result + "}"


@register_outputform("System`MathMLForm")
def mathmlform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    #  boxes = format_element(expr.elements[0], evaluation)
    boxes = Expression(
        Symbol("System`MakeBoxes"), expr.elements[0], SymbolTraditionalForm
    ).evaluate(evaluation)
    return boxes.boxes_to_mathml()  # type: ignore[union-attr]


@register_outputform("System`MatrixForm")
def matrixform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    # return parenthesize(tableform_expression_to_outputform_text(expr, evaluation, **kwargs))
    return tableform_expression_to_outputform_text(expr, evaluation, **kwargs)


@register_outputform("System`MessageName")
def message_name_outputform(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) != 2:
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
    symb, msg = elements
    if not (isinstance(symb, Symbol) and isinstance(msg, String)):
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
    symbol_name = evaluation.definitions.shorten_name(symb.get_name())
    return f"{symbol_name}::{msg.value}"


@register_outputform("System`OutputForm")
def outputform(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) != 1:
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
    return expression_to_outputform_text(elements[0], evaluation, **kwargs)


@register_outputform("System`Part")
def part(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) == 0:
        raise _WrongFormattedExpression
    elements_fmt = [
        expression_to_outputform_text(elem, evaluation, **kwargs) for elem in elements
    ]
    if len(elements_fmt) == 1:
        return elements_fmt[0]
    result = elements_fmt[0]
    args = ", ".join(elements_fmt[1:])
    return f"{result}[[{args}]]"


@register_outputform("System`Pattern")
def pattern(expr: Expression, evaluation: Evaluation, **kwargs):
    elements = expr.elements
    if len(elements) != 2:
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
    name, pat = (
        expression_to_outputform_text(elem, evaluation, **kwargs) for elem in elements
    )
    return name + pat


@register_outputform("System`Plus")
def plus_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> str:
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
                        + expression_to_outputform_text(
                            Expression(SymbolTimes, *term.elements[1:]),
                            evaluation,
                            **kwargs,
                        )
                    )
                    continue
                elif first.value < 0:
                    result = (
                        result
                        + " "
                        + expression_to_outputform_text(term, evaluation, **kwargs)
                    )
                    continue
            elif isinstance(first, Real):
                if first.value < 0:
                    result = (
                        result
                        + " "
                        + expression_to_outputform_text(term, evaluation, **kwargs)
                    )
                    continue
            result = (
                result
                + " + "
                + expression_to_outputform_text(term, evaluation, **kwargs)
            )
            ## TODO: handle complex numbers?
        else:
            elem_txt = expression_to_outputform_text(term, evaluation, **kwargs)
            if (compare_precedence(term, PRECEDENCE_PLUS) or -1) < 0:
                elem_txt = parenthesize(elem_txt)
                result = result + " + " + elem_txt
            elif i == 0 or (
                (isinstance(term, Integer) and term.value < 0)
                or (isinstance(term, Real) and term.value < 0)
            ):
                result = result + elem_txt
            else:
                result = (
                    result
                    + " + "
                    + expression_to_outputform_text(term, evaluation, **kwargs)
                )
    return result


@register_outputform("System`Power")
def power_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
):
    if len(expr.elements) != 2:
        raise _WrongFormattedExpression

    infix_form = Expression(
        SymbolInfix,
        ListExpression(*(expr.elements)),
        String("^"),
        Integer(PRECEDENCE_POWER),
        SymbolRight,
    )
    return expression_to_outputform_text(infix_form, evaluation, **kwargs)


@register_outputform("System`PrecedenceForm")
def precedenceform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> str:
    if len(expr.elements) == 2:
        return expression_to_outputform_text(expr.elements[0], evaluation, **kwargs)
    raise _WrongFormattedExpression


@register_outputform("System`Prefix")
def _prefix_output_text(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    """
    Convert Prefix[...] into a InputForm string.
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
    target_txt = expression_to_outputform_text(operand, evaluation, **kwargs)
    parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
    target_txt = parenthesize(precedence, operand, target_txt, True)
    return op_head + target_txt


@register_outputform("System`Postfix")
def _postfix_output_text(expr: Expression, evaluation: Evaluation, **kwargs) -> str:
    """
    Convert Postfix[...] into a InputForm string.
    """
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    operands, op_head, precedence, group = collect_in_pre_post_arguments(
        expr, evaluation, **kwargs
    )
    # Prefix works with just one operand:
    if len(operands) != 1:
        raise _WrongFormattedExpression
    operand = operands[0]
    target_txt = expression_to_outputform_text(operand, evaluation, **kwargs)
    parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
    target_txt = parenthesize(precedence, operand, target_txt, True)
    return target_txt + op_head


@register_outputform("System`Rational")
def rational_expression_to_outputform_text(
    n: Union[Rational, Expression], evaluation: Evaluation, **kwargs
):
    if n.has_form("Rational", 2):
        num, den = n.elements  # type: ignore[union-attr]
    else:
        num, den = n.numerator(), n.denominator()  # type: ignore[union-attr]
    return _divide(num, den, evaluation, **kwargs)


@register_outputform("System`Real")
def real_expression_to_outputform_text(n: Real, evaluation: Evaluation, **kwargs):
    str_n = n.make_boxes("System`OutputForm").boxes_to_text()  # type: ignore[attr-defined]
    return str(str_n)


@register_outputform("System`Row")
def row_to_outputform_text(expr, evaluation: Evaluation, **kwargs):
    """Row[{...}]"""
    elements = expr.elements[0].elements
    return "".join(
        expression_to_outputform_text(elem, evaluation, **kwargs) for elem in elements
    )


@register_outputform("System`Rule")
@register_outputform("System`RuleDelayed")
def rule_to_outputform_text(expr, evaluation: Evaluation, **kwargs):
    """Rule|RuleDelayed[{...}]"""
    head = expr.head
    elements = expr.elements
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    if len(elements) != 2:
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
    pat, rule = (
        expression_to_outputform_text(elem, evaluation, **kwargs) for elem in elements
    )
    kwargs["_render_function"] = expression_to_outputform_text
    op_str = get_operator_str(head, evaluation, **kwargs)
    return f"{pat} {op_str} {rule}"


@register_outputform("System`SequenceForm")
def sequenceform_to_outputform_text(expr, evaluation: Evaluation, **kwargs):
    """Row[{...}]"""
    elements = expr.elements
    return "".join(
        expression_to_outputform_text(elem, evaluation, **kwargs) for elem in elements
    )


@register_outputform("System`Slot")
def _slot_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs):
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
def string_expression_to_outputform_text(
    expr: String, evaluation: Evaluation, **kwargs
) -> str:
    # lines = expr.value.split("\n")
    # max_len = max([len(line) for line in lines])
    # lines = [line + (max_len - len(line)) * " " for line in lines]
    # return "\n".join(lines)
    return expr.value


@register_outputform("System`StringForm")
def stringform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    strform = expr.elements[0]
    if not isinstance(strform, String):
        raise _WrongFormattedExpression

    items = list(
        expression_to_outputform_text(item, evaluation, **kwargs)
        for item in expr.elements[1:]
    )

    curr_indx = 0
    parts = strform.value.split("`")
    result = str(parts[0])
    if len(parts) <= 1:
        return result

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
                result = result + items[curr_indx]
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
            result = result + items[indx - 1]
            curr_indx = indx
            quote_open = False
            continue

        result = result + part
        quote_open = True

    return result


@register_outputform("System`Style")
def style_to_outputform_text(expr: String, evaluation: Evaluation, **kwargs) -> str:
    elements = expr.elements
    if not elements:
        raise _WrongFormattedExpression
    return expression_to_outputform_text(elements[0], evaluation, **kwargs)


@register_outputform("System`Symbol")
def symbol_expression_to_outputform_text(
    symb: Symbol, evaluation: Evaluation, **kwargs
):
    return evaluation.definitions.shorten_name(symb.name)


@register_outputform("System`TableForm")
def tableform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    from mathics.builtin.tensors import get_dimensions

    elements = expr.elements

    if len(elements) == 0:
        raise _WrongFormattedExpression

    table, *opts = elements
    dims = len(get_dimensions(table, head=SymbolList))
    process_options(kwargs, opts)
    depth = expr_min((Integer(dims), kwargs.pop("TableDepth", SymbolInfinity))).value
    if depth is None:
        evaluation.message(self.get_name(), "int")
        raise _WrongFormattedExpression
    if depth <= 0:
        return expression_to_outputform_text(table, evaluation, **kwargs)
    if depth == 1:
        return text_cells_to_grid(
            [
                [expression_to_outputform_text(elem, evaluation, **kwargs)]
                for elem in table.elements
            ]
        )
    kwargs["TableDepth"] = Integer(depth - 2)

    def transform_item(item):
        if depth > 2:
            return tableform_expression_to_outputform_text(
                Expression(SymbolTableForm, item), evaluation, **kwargs
            )
        else:
            return expression_to_outputform_text(item, evaluation, **kwargs)

    grid_array = [[transform_item(elem) for elem in row] for row in table.elements]
    return text_cells_to_grid(grid_array)


@register_outputform("System`TeXForm")
def _texform_outputform(expr, evaluation, **kwargs):
    boxes = Expression(
        Symbol("System`MakeBoxes"), expr.elements[0], SymbolTraditionalForm
    ).evaluate(evaluation)
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
def times_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    elements = expr.elements
    if len(elements) < 2:
        return _default_expression_to_outputform_text(expr, evaluation, **kwargs)
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
        return expression_to_outputform_text(num[0], evaluation, **kwargs)

    prefactor = 1
    result: str = ""
    for i, factor in enumerate(num):
        if factor is IntegerM1:
            prefactor *= -1
            continue
        if isinstance(factor, Integer):
            prefactor *= -1
            factor = Integer(-factor.value)

        factor_txt = expression_to_outputform_text(factor, evaluation, **kwargs)
        if compare_precedence(factor, PRECEDENCE_TIMES):
            factor_txt = parenthesize(factor_txt)
        if i == 0:
            result = factor_txt
        else:
            result = result + " " + factor_txt
    if result == "":
        result = "1"
    if prefactor == -1:
        result = "-" + result
    return result


@register_outputform("System`NumberForm")
def _numberform_outputform(expr, evaluation, **kwargs):
    py_options = self.check_options(options, evaluation)
    if py_options is None:
        return fallback

    if isinstance(expr, Integer):
        py_n = len(str(abs(expr.get_int_value())))
    elif isinstance(expr, Real):
        if expr.is_machine_precision():
            py_n = 6
        else:
            py_n = dps(expr.get_precision())
    else:
        py_n = None

    if py_n is not None:
        py_options["_Form"] = form.get_name()
        return NumberForm_to_String(expr, py_n, None, evaluation, py_options)
    raise _WrongFormattedExpression
