"""
This module implements the "OutputForm" textual representation of expressions.

OutputForm is two-dimensional keyboard-character-only output, suitable for CLI
and text terminals.
"""

from typing import Callable, Dict, Final, List, Union

from mathics.core.atoms import (
    Integer,
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
from mathics.core.parser.operators import OPERATOR_DATA
from mathics.core.symbols import Atom, Symbol, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolDerivative,
    SymbolInfix,
    SymbolLeft,
    SymbolNone,
    SymbolOutputForm,
    SymbolPower,
    SymbolRight,
    SymbolStandardForm,
    SymbolTraditionalForm,
)
from mathics.eval.makeboxes import compare_precedence, do_format  # , format_element
from mathics.settings import SYSTEM_CHARACTER_ENCODING

from .util import _WrongFormattedExpression, bracket, get_operator_str, parenthesize

PRECEDENCES: Final = OPERATOR_DATA.get("operator-precedences")
PRECEDENCE_DEFAULT: Final = PRECEDENCES.get("FunctionApply")
PRECEDENCE_PLUS: Final = PRECEDENCES.get("Plus")
PRECEDENCE_TIMES: Final = PRECEDENCES.get("Times")
PRECEDENCE_POWER: Final = PRECEDENCES.get("Power")

# When new mathics-scanner tables are updagted:
# BOX_GROUP_PRECEDENCE: Final = box_operators["BoxGroup"]
BOX_GROUP_PRECEDENCE: Final = PRECEDENCE_DEFAULT

EXPR_TO_OUTPUTFORM_TEXT_MAP: Dict[str, Callable] = {}

SymbolNonAssociative = Symbol("System`NonAssociative")
SymbolPostfix = Symbol("System`Postfix")
SymbolPrefix = Symbol("System`Prefix")


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
    result = elements.pop(0) if elements else " "
    while elements:
        result = result + comma + elements.pop(0)

    form = kwargs.get("_Form", SymbolOutputForm)
    if form is SymbolTraditionalForm:
        return head + parenthesize(result)
    return head + bracket(result)


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


def grid(expr):
    # Very basic implementation.
    result = ""
    for idx_row, row in enumerate(expr):
        if idx_row > 0:
            result += "\n\n"
        for idx_field, field in enumerate(row):
            if idx_field > 0:
                result += "   "
            result += field

    return result


def register_outputform(head_name):
    def _register(func):
        EXPR_TO_OUTPUTFORM_TEXT_MAP[head_name] = func
        return func

    return _register


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
    if head is SymbolBlank:
        return "_" + elem
    elif head is SymbolBlankSequence:
        return "__" + elem
    elif head is SymbolBlankNullSequence:
        return "___" + elem
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

    return grid(rows)


register_outputform("System`HoldForm")(_strip_1_parm_expression_to_outputform_text)


@register_outputform("System`FullForm")
@register_outputform("System`InputForm")
def other_forms(expr, evaluation, **kwargs):
    from mathics.eval.makeboxes import format_element

    form = expr.get_head()
    expr = expr.elements[0]
    result = format_element(expr, evaluation, form, **kwargs)
    if isinstance(result, String):
        return result.value
    return result.boxes_to_text()


@register_outputform("System`Image")
def image_outputform_text(expr: Expression, evaluation: Evaluation, **kwargs):
    return "-Image-"


@register_outputform("System`Infix")
def infix_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)

    elements = expr.elements
    if not (0 <= len(elements) <= 4):
        raise _WrongFormattedExpression

    group = None
    precedence = BOX_GROUP_PRECEDENCE

    # Processing the first argument:
    head = expr.get_head()
    target = expr.elements[0]
    if isinstance(target, Atom):
        raise _WrongFormattedExpression

    operands = list(target.elements)

    if len(operands) < 2:
        raise _WrongFormattedExpression

    # Processing the second argument, if it is there:
    if len(elements) > 1:
        ops = elements[1]
        if head is SymbolInfix:
            # This is not the WMA behaviour, but the Mathics current implementation requires it:
            num_ops = 1
            # TODO: Handle the case where op is not a String or a Symbol.
            kwargs["_render_function"] = expression_to_outputform_text
            if ops.has_form("List", None):
                num_ops = len(ops.elements)
                ops_lst = [
                    get_operator_str(op, evaluation, **kwargs) for op in ops.elements
                ]
            else:
                ops_lst = [get_operator_str(ops, evaluation, **kwargs)]
        elif head in (SymbolPrefix, SymbolPostfix):
            ops_txt = [expression_to_outputform_text(ops, evaluation, **kwargs)]
    else:
        if head is SymbolInfix:
            num_ops = 1
            default_symb = " ~ "
            ops_lst = [
                default_symb
                + expression_to_outputform_text(head, evaluation, **kwargs)
                + default_symb
            ]
        elif head is SymbolPrefix:
            default_symb = " @ "
            ops_txt = (
                expression_to_outputform_text(head, evaluation, **kwargs) + default_symb
            )
        elif head is SymbolPostfix:
            default_symb = " // "
            ops_txt = default_symb + expression_to_outputform_text(
                head, evaluation, **kwargs
            )

    # Processing the third argument, if it is there:
    if len(elements) > 2:
        if isinstance(elements[2], Integer):
            precedence = elements[2].value
        else:
            raise _WrongFormattedExpression

    # Processing the forth argument, if it is there:
    if len(elements) > 3:
        group = elements[3]
        if group not in (SymbolNone, SymbolLeft, SymbolRight, SymbolNonAssociative):
            raise _WrongFormattedExpression
        if group is SymbolNone:
            group = None

    if head is SymbolPrefix:
        operand = operands[0]
        cmp_precedence = compare_precedence(operand, precedence)
        target_txt = expression_to_outputform_text(operand, evaluation, **kwargs)
        if cmp_precedence is not None and cmp_precedence != -1:
            target_txt = parenthesize(target_txt)
        return ops_txt[0] + target_txt
    if head is SymbolPostfix:
        operand = operands[0]
        cmp_precedence = compare_precedence(operand, precedence)
        target_txt = expression_to_outputform_text(operand, evaluation, **kwargs)
        if cmp_precedence is not None and cmp_precedence != -1:
            target_txt = parenthesize(target_txt)
        return target_txt + ops_txt[0]
    else:  # Infix
        parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
        for index, operand in enumerate(operands):
            operand_txt = str(
                expression_to_outputform_text(operand, evaluation, **kwargs)
            )
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
                space = " "
                result_lst: List[str]
                if str(ops_lst[index % num_ops]) != " ":
                    result_lst = [
                        result,
                        space,
                        str(ops_lst[(index - 1) % num_ops]),
                        space,
                        operand_txt,
                    ]
                else:
                    result_lst = [result, space, operand_txt]
                result = "".join(result_lst)

        return result


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
        Symbol("System`MakeBoxes"), expr.elements[0], SymbolStandardForm
    ).evaluate(evaluation)
    return boxes.boxes_to_mathml()  # type: ignore[union-attr]


@register_outputform("System`MatrixForm")
def matrixform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    # return parenthesize(tableform_expression_to_outputform_text(expr, evaluation, **kwargs))
    return tableform_expression_to_outputform_text(expr, evaluation, **kwargs)


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
                            form,
                            **kwargs,
                        )
                    )
                    continue
                elif first.value < 0:
                    result = (
                        result
                        + " "
                        + expression_to_outputform_text(
                            term, evaluation, form, **kwargs
                        )
                    )
                    continue
            elif isinstance(first, Real):
                if first.value < 0:
                    result = (
                        result
                        + " "
                        + expression_to_outputform_text(
                            term, evaluation, form, **kwargs
                        )
                    )
                    continue
            result = (
                result
                + " + "
                + expression_to_outputform_text(term, evaluation, form, **kwargs)
            )
            ## TODO: handle complex numbers?
        else:
            elem_txt = expression_to_outputform_text(term, evaluation, form, **kwargs)
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
                    + expression_to_outputform_text(term, evaluation, form, **kwargs)
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
    return expression_to_outputform_text(infix_form, evaluation, form, **kwargs)


@register_outputform("System`PrecedenceForm")
def precedenceform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> str:
    if len(expr.elements) == 2:
        return expression_to_outputform_text(
            expr.elements[0], evaluation, form, **kwargs
        )
    raise _WrongFormattedExpression


@register_outputform("System`Prefix")
@register_outputform("System`Postfix")
def pre_pos_fix_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> str:
    elements = expr.elements
    if not (0 <= len(elements) <= 4):
        raise _WrongFormattedExpression

    group = None
    precedence = BOX_GROUP_PRECEDENCE

    # Processing the first argument:
    head = expr.get_head()
    target = expr.elements[0]
    if isinstance(target, Atom):
        raise _WrongFormattedExpression

    operands = list(target.elements)
    if len(operands) != 1:
        raise _WrongFormattedExpression

    # Processing the second argument, if it is there:
    if len(elements) > 1:
        ops = elements[1]
        ops_txt = [expression_to_outputform_text(ops, evaluation, form, **kwargs)]
    else:
        if head is SymbolPrefix:
            default_symb = " @ "
            ops_txt = (
                expression_to_outputform_text(head, evaluation, form, **kwargs)
                + default_symb
            )
        elif head is SymbolPostfix:
            default_symb = " // "
            ops_txt = default_symb + expression_to_outputform_text(
                head, evaluation, form, **kwargs
            )

    # Processing the third argument, if it is there:
    if len(elements) > 2:
        if isinstance(elements[2], Integer):
            precedence = elements[2].value
        else:
            raise _WrongFormattedExpression

    # Processing the forth argument, if it is there:
    if len(elements) > 3:
        group = elements[3]
        if group not in (SymbolNone, SymbolLeft, SymbolRight, SymbolNonAssociative):
            raise _WrongFormattedExpression
        if group is SymbolNone:
            group = None

    operand = operands[0]
    cmp_precedence = compare_precedence(operand, precedence)
    target_txt = expression_to_outputform_text(operand, evaluation, form, **kwargs)
    if cmp_precedence is not None and cmp_precedence != -1:
        target_txt = parenthesize(target_txt)

    return ops_txt[0] + target_txt if head is SymbolPrefix else target_txt + ops_txt[0]


@register_outputform("System`Rational")
def rational_expression_to_outputform_text(
    n: Union[Rational, Expression], evaluation: Evaluation, form: Symbol, **kwargs
):
    if n.has_form("Rational", 2):
        num, den = n.elements  # type: ignore[union-attr]
    else:
        num, den = n.numerator(), n.denominator()  # type: ignore[union-attr]
    return _divide(num, den, evaluation, **kwargs)


@register_outputform("System`Real")
def real_expression_to_outputform_text(
    n: Real, evaluation: Evaluation, form: Symbol, **kwargs
):
    str_n = n.make_boxes("System`OutputForm").boxes_to_text()  # type: ignore[attr-defined]
    return str(str_n)


@register_outputform("System`Row")
def row_to_outputform_text(expr, evaluation: Evaluation, form: Symbol, **kwargs):
    """Row[{...}]"""
    elements = expr.elements[0].elements
    return "".join(
        expression_to_outputform_text(elem, evaluation, **kwargs) for elem in elements
    )


@register_outputform("System`Rule")
@register_outputform("System`RuleDelayed")
def rule_to_outputform_text(expr, evaluation: Evaluation, form: Symbol, **kwargs):
    """Rule|RuleDelayed[{...}]"""
    head = expr.head
    elements = expr.elements
    kwargs["encoding"] = kwargs.get("encoding", SYSTEM_CHARACTER_ENCODING)
    if len(elements) != 2:
        return _default_expression_to_outputform_text(expr, evaluation, form, **kwargs)
    pat, rule = (
        expression_to_outputform_text(elem, evaluation, **kwargs) for elem in elements
    )
    kwargs["_render_function"] = expression_to_outputform_text
    op_str = get_operator_str(head, evaluation, **kwargs)
    return pat + " " + op_str + " " + rule


@register_outputform("System`String")
def string_expression_to_outputform_text(
    expr: String, evaluation: Evaluation, **kwargs
) -> str:
    lines = expr.value.split("\n")
    max_len = max([len(line) for line in lines])
    lines = [line + (max_len - len(line)) * " " for line in lines]
    return "\n".join(lines)


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
    if len(parts) == 1:
        return result

    quote_open = True
    remaining = len(parts) - 1

    for part in parts[1:]:
        remaining -= 1
        if quote_open:
            if remaining == 0:
                result = result + "`" + part
                quote_open = False
                continue
            if len(part) == 0:
                result = result + items[curr_indx]
                continue
            try:
                idx = int(part)
            except ValueError:
                idx = None
            if idx is not None and str(idx) == part:
                curr_indx = idx - 1
                result = result + items[curr_indx]
                quote_open = False
                continue
            else:
                result = result + "`" + part + "`"
                quote_open = False
                continue
        else:
            result = result + part
            quote_open = True

    return result


@register_outputform("System`Symbol")
def symbol_expression_to_outputform_text(
    symb: Symbol, evaluation: Evaluation, **kwargs
):
    return evaluation.definitions.shorten_name(symb.name)


@register_outputform("System`TableForm")
def tableform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    return grid_expression_to_outputform_text(expr, evaluation, **kwargs)


@register_outputform("System`TeXForm")
def texform_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    #  boxes = format_element(expr.elements[0], evaluation, form)
    boxes = Expression(
        Symbol("System`MakeBoxes"), expr.elements[0], SymbolStandardForm
    ).evaluate(evaluation)
    return boxes.boxes_to_tex()  # type: ignore


@register_outputform("System`Times")
def times_expression_to_outputform_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> str:
    elements = expr.elements
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
