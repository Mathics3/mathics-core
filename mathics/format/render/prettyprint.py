"""
This module builts the 2D string associated to the OutputForm
"""

from typing import Callable, Dict, List, Union

from mathics.core.atoms import (
    Integer,
    Integer1,
    Integer2,
    IntegerM1,
    PrecisionReal,
    Rational,
    Real,
    String,
)
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.number import dps
from mathics.core.symbols import Atom, Symbol, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolDerivative,
    SymbolInfix,
    SymbolNone,
    SymbolOutputForm,
    SymbolPower,
    SymbolStandardForm,
    SymbolTraditionalForm,
)
from mathics.format.box import compare_precedence, do_format  # , format_element
from mathics.format.box.numberform import numberform_to_boxes
from mathics.format.render.pane_text import (
    TEXTBLOCK_COMMA,
    TEXTBLOCK_MINUS,
    TEXTBLOCK_NULL,
    TEXTBLOCK_PLUS,
    TEXTBLOCK_QUOTE,
    TEXTBLOCK_SPACE,
    TextBlock,
    bracket,
    curly_braces,
    fraction,
    grid,
    integral_definite,
    integral_indefinite,
    join_blocks,
    parenthesize,
    sqrt_block,
    subscript,
    subsuperscript,
    superscript,
)

SymbolNonAssociative = Symbol("System`NonAssociative")
SymbolPostfix = Symbol("System`Postfix")
SymbolPrefix = Symbol("System`Prefix")
SymbolRight = Symbol("System`Right")
SymbolLeft = Symbol("System`Left")


TEXTBLOCK_ARROBA = TextBlock("@")
TEXTBLOCK_BACKQUOTE = TextBlock("`")
TEXTBLOCK_DOUBLESLASH = TextBlock("//")
TEXTBLOCK_GRAPHICS = TextBlock("-Graphics-")
TEXTBLOCK_GRAPHICS3D = TextBlock("-Graphics3D-")
TEXTBLOCK_ONE = TextBlock("1")
TEXTBLOCK_TILDE = TextBlock("~")

####  Functions that convert Expressions in TextBlock


expr_to_2d_text_map: Dict[str, Callable] = {}


# This Exception if the expression should
# be processed by the default routine
class _WrongFormattedExpression(Exception):
    pass


class IsNotGrid(Exception):
    pass


class IsNot2DArray(Exception):
    pass


def render_2d_text(expr: BaseElement, evaluation: Evaluation, **kwargs):
    """
    Build a 2d text from an `Expression`
    """
    ## TODO: format the expression
    format_expr: Expression = do_format(expr, evaluation, SymbolOutputForm)  # type: ignore

    # Strip HoldForm
    while format_expr.has_form("HoldForm", 1):  # type: ignore
        format_expr = format_expr.elements[0]

    lookup_name = format_expr.get_head().get_lookup_name()
    try:
        result = expr_to_2d_text_map[lookup_name](format_expr, evaluation, **kwargs)
        return result
    except _WrongFormattedExpression:
        # If the key is not present, or the execution fails for any reason, use
        # the default
        pass
    except KeyError:
        pass
    return _default_render_2d_text(format_expr, evaluation, **kwargs)


def _default_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    """
    Default representation of a function
    """
    expr_head = expr.head
    head = render_2d_text(expr_head, evaluation, **kwargs)
    comma = join_blocks(TEXTBLOCK_COMMA, TEXTBLOCK_SPACE)
    elements = [render_2d_text(elem, evaluation) for elem in expr.elements]
    result = elements.pop(0) if elements else TEXTBLOCK_SPACE
    while elements:
        result = join_blocks(result, comma, elements.pop(0))

    if kwargs.get("_Form", SymbolStandardForm) is SymbolTraditionalForm:
        return join_blocks(head, parenthesize(result))
    return join_blocks(head, bracket(result))


def _divide(num, den, evaluation, **kwargs):
    if kwargs.get("2d", False):
        return fraction(
            render_2d_text(num, evaluation, **kwargs),
            render_2d_text(den, evaluation, **kwargs),
        )
    infix_form = Expression(
        SymbolInfix, ListExpression(num, den), String("/"), Integer(400), SymbolLeft
    )
    return render_2d_text(infix_form, evaluation, **kwargs)


def _strip_1_parm_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    if len(expr.elements) != 1:
        raise _WrongFormattedExpression
    return render_2d_text(expr.elements[0], evaluation, **kwargs)


expr_to_2d_text_map["System`HoldForm"] = _strip_1_parm_render_2d_text
expr_to_2d_text_map["System`InputForm"] = _strip_1_parm_render_2d_text


def derivative_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    """Derivative operator"""
    head = expr.get_head()
    if head is SymbolDerivative:
        return _default_render_2d_text(expr, evaluation, **kwargs)
    super_head = head.get_head()
    if super_head is SymbolDerivative:
        expr_elements = expr.elements
        if len(expr_elements) != 1:
            return _default_render_2d_text(expr, evaluation, **kwargs)
        function_head = render_2d_text(expr_elements[0], evaluation, **kwargs)
        derivatives = head.elements
        if len(derivatives) == 1:
            order_iv = derivatives[0]
            if order_iv == Integer1:
                return join_blocks(function_head, TEXTBLOCK_QUOTE)
            elif order_iv == Integer2:
                return join_blocks(function_head, TEXTBLOCK_QUOTE, TEXTBLOCK_QUOTE)

        if not kwargs["2d"]:
            return _default_render_2d_text(expr, evaluation, **kwargs)

        comma = TEXTBLOCK_COMMA
        superscript_tb, *rest_derivatives = (
            render_2d_text(order, evaluation, **kwargs) for order in derivatives
        )
        for order in rest_derivatives:
            superscript_tb = join_blocks(superscript_tb, comma, order)

        superscript_tb = parenthesize(superscript_tb)
        return superscript(function_head, superscript_tb)

    # Full Function with arguments: delegate to the default conversion.
    # It will call us again with the head
    return _default_render_2d_text(expr, evaluation, **kwargs)


expr_to_2d_text_map["System`Derivative"] = derivative_render_2d_text


def divide_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    if len(expr.elements) != 2:
        raise _WrongFormattedExpression
    num, den = expr.elements
    return _divide(num, den, evaluation, **kwargs)


expr_to_2d_text_map["System`Divide"] = divide_render_2d_text


def graphics(expr: Expression, evaluation: Evaluation, **kwargs) -> TextBlock:
    return TEXTBLOCK_GRAPHICS


expr_to_2d_text_map["System`Graphics"] = graphics


def graphics3d(expr: Expression, evaluation: Evaluation, **kwargs) -> TextBlock:
    return TEXTBLOCK_GRAPHICS3D


expr_to_2d_text_map["System`Graphics3D"] = graphics3d


def grid_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
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
                    render_2d_text(item_elem, evaluation, **kwargs)
                    for item_elem in item.elements
                ]
            )
        else:
            rows.append(render_2d_text(item, evaluation, **kwargs))

    return grid(rows)


expr_to_2d_text_map["System`Grid"] = grid_render_2d_text


def integer_render_2d_text(n: Integer, evaluation: Evaluation, **kwargs):
    return TextBlock(str(n.value))


expr_to_2d_text_map["System`Integer"] = integer_render_2d_text


def integrate_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    elems = list(expr.elements)
    if len(elems) > 2 or not kwargs.get("2d", False):
        raise _WrongFormattedExpression

    integrand = elems.pop(0)
    result = render_2d_text(integrand, evaluation, **kwargs)
    while elems:
        var = elems.pop(0)
        if var.has_form("List", 3):
            var_txt, a, b = (
                render_2d_text(item, evaluation, **kwargs) for item in var.elements
            )
            result = integral_definite(result, var_txt, a, b)
        elif isinstance(var, Symbol):
            var_txt = render_2d_text(var, evaluation, **kwargs)
            result = integral_indefinite(result, var_txt)
        else:
            break
    return result


expr_to_2d_text_map["System`Integrate"] = integrate_render_2d_text


def list_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    result, *rest_elems = (
        render_2d_text(elem, evaluation, **kwargs) for elem in expr.elements
    )
    comma_tb = join_blocks(TEXTBLOCK_COMMA, TEXTBLOCK_SPACE)
    for next_elem in rest_elems:
        result = TextBlock(*TextBlock.next(result, comma_tb, next_elem))
    return curly_braces(result)


expr_to_2d_text_map["System`List"] = list_render_2d_text


def mathmlform_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    #  boxes = format_element(expr.elements[0], evaluation)
    boxes = Expression(
        Symbol("System`MakeBoxes"), expr.elements[0], SymbolStandardForm
    ).evaluate(evaluation)
    return TextBlock(boxes.boxes_to_mathml())  # type: ignore[union-attr]


expr_to_2d_text_map["System`MathMLForm"] = mathmlform_render_2d_text


def matrixform_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    # return parenthesize(tableform_render_2d_text(expr, evaluation, **kwargs))
    return tableform_render_2d_text(expr, evaluation, **kwargs)


expr_to_2d_text_map["System`MatrixForm"] = matrixform_render_2d_text


def plus_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    elements = expr.elements
    result = TEXTBLOCK_NULL
    tb_minus = join_blocks(TEXTBLOCK_SPACE, TEXTBLOCK_MINUS, TEXTBLOCK_SPACE)
    tb_plus = join_blocks(TEXTBLOCK_SPACE, TEXTBLOCK_PLUS, TEXTBLOCK_SPACE)
    for i, elem in enumerate(elements):
        if elem.has_form("Times", None):
            # If the first element is -1, remove it and use
            # a minus sign. Otherwise, if negative, do not add a sign.
            first = elem.elements[0]
            if isinstance(first, Integer):
                if first.value == -1:
                    result = join_blocks(
                        result,
                        tb_minus,
                        render_2d_text(
                            Expression(SymbolTimes, *elem.elements[1:]),
                            evaluation,
                            **kwargs,
                        ),
                    )
                    continue
                elif first.value < 0:
                    result = join_blocks(
                        result,
                        TEXTBLOCK_SPACE,
                        render_2d_text(elem, evaluation, **kwargs),
                    )
                    continue
            elif isinstance(first, Real):
                if first.value < 0:
                    result = join_blocks(
                        result,
                        TEXTBLOCK_SPACE,
                        render_2d_text(elem, evaluation, **kwargs),
                    )
                    continue
            result = join_blocks(
                result, tb_plus, render_2d_text(elem, evaluation, **kwargs)
            )
            ## TODO: handle complex numbers?
        else:
            elem_txt = render_2d_text(elem, evaluation, **kwargs)
            if (compare_precedence(elem, 310) or -1) < 0:
                elem_txt = parenthesize(elem_txt)
                result = join_blocks(result, tb_plus, elem_txt)
            elif i == 0 or (
                (isinstance(elem, Integer) and elem.value < 0)
                or (isinstance(elem, Real) and elem.value < 0)
            ):
                result = join_blocks(result, elem_txt)
            else:
                result = join_blocks(
                    result,
                    tb_plus,
                    render_2d_text(elem, evaluation, **kwargs),
                )
    return result


expr_to_2d_text_map["System`Plus"] = plus_render_2d_text


def power_render_2d_text(expr: Expression, evaluation: Evaluation, **kwargs):
    if len(expr.elements) != 2:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        base, exponent = (
            render_2d_text(elem, evaluation, **kwargs) for elem in expr.elements
        )
        if (compare_precedence(expr.elements[0], 590) or 1) == -1:
            base = parenthesize(base)
        return superscript(base, exponent)

    infix_form = Expression(
        SymbolInfix,
        ListExpression(*(expr.elements)),
        String("^"),
        Integer(590),
        SymbolRight,
    )
    return render_2d_text(infix_form, evaluation, **kwargs)


expr_to_2d_text_map["System`Power"] = power_render_2d_text


def pre_pos_fix_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    elements = expr.elements
    if not (0 <= len(elements) <= 4):
        raise _WrongFormattedExpression

    group = None
    precedence = 670
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
        ops_txt = [render_2d_text(ops, evaluation, **kwargs)]
    else:
        if head is SymbolPrefix:
            default_symb = TEXTBLOCK_ARROBA
            ops_txt = join_blocks(
                render_2d_text(head, evaluation, **kwargs), default_symb
            )
        else:  #  head is SymbolPostfix:
            default_symb = TEXTBLOCK_DOUBLESLASH
            ops_txt = join_blocks(
                default_symb, render_2d_text(head, evaluation, **kwargs)
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
    target_txt = render_2d_text(operand, evaluation, **kwargs)
    if cmp_precedence is not None and cmp_precedence != -1:
        target_txt = parenthesize(target_txt)

    return (
        join_blocks(ops_txt[0], target_txt)
        if head is SymbolPrefix
        else join_blocks(target_txt, ops_txt[0])
    )


expr_to_2d_text_map["System`Prefix"] = pre_pos_fix_render_2d_text
expr_to_2d_text_map["System`Postfix"] = pre_pos_fix_render_2d_text


def infix_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    elements = expr.elements
    if not (0 <= len(elements) <= 4):
        raise _WrongFormattedExpression

    group = None
    precedence = 670
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
            if ops.has_form("List", None):
                num_ops = len(ops.elements)
                ops_lst = [
                    render_2d_text(op, evaluation, **kwargs) for op in ops.elements
                ]
            else:
                ops_lst = [render_2d_text(ops, evaluation, **kwargs)]
        elif head in (SymbolPrefix, SymbolPostfix):
            ops_txt = [render_2d_text(ops, evaluation, **kwargs)]
    else:
        num_ops = 1
        default_symb = join_blocks(TEXTBLOCK_SPACE, TEXTBLOCK_TILDE, TEXTBLOCK_SPACE)
        ops_lst = [
            join_blocks(
                default_symb,
                render_2d_text(head, evaluation, **kwargs),
                default_symb,
            )
        ]

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

    parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
    for index, operand in enumerate(operands):
        operand_txt = render_2d_text(operand, evaluation, **kwargs)
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
            space = TEXTBLOCK_SPACE
            if str(ops_lst[index % num_ops]) != " ":
                result_lst = [
                    result,
                    space,
                    ops_lst[index % num_ops],
                    space,
                    operand_txt,
                ]
            else:
                result_lst = [result, space, operand_txt]

    return join_blocks(*result_lst)


expr_to_2d_text_map["System`Infix"] = infix_render_2d_text


def precedenceform_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    if len(expr.elements) == 2:
        return render_2d_text(expr.elements[0], evaluation, **kwargs)
    raise _WrongFormattedExpression


expr_to_2d_text_map["System`PrecedenceForm"] = precedenceform_render_2d_text


def rational_render_2d_text(
    n: Union[Rational, Expression], evaluation: Evaluation, **kwargs
):
    if n.has_form("Rational", 2):
        num, den = n.elements  # type: ignore[union-attr]
    else:
        num, den = n.numerator(), n.denominator()  # type: ignore[union-attr]
    return _divide(num, den, evaluation, **kwargs)


expr_to_2d_text_map["System`Rational"] = rational_render_2d_text


def real_render_2d_text(n: Real, evaluation: Evaluation, **kwargs):
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


expr_to_2d_text_map["System`Real"] = real_render_2d_text


def sqrt_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    if not 1 <= len(expr.elements) <= 2:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        return sqrt_block(
            *(render_2d_text(item, evaluation, **kwargs) for item in expr.elements)
        )
    raise _WrongFormattedExpression


expr_to_2d_text_map["System`Sqrt"] = sqrt_render_2d_text


def subscript_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    if len(expr.elements) != 2:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        return subscript(
            *(render_2d_text(item, evaluation, **kwargs) for item in expr.elements)
        )
    raise _WrongFormattedExpression


expr_to_2d_text_map["System`Subscript"] = subscript_render_2d_text


def subsuperscript_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    if len(expr.elements) != 3:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        return subsuperscript(
            *(render_2d_text(item, evaluation, **kwargs) for item in expr.elements)
        )
    raise _WrongFormattedExpression


expr_to_2d_text_map["System`Subsuperscript"] = subsuperscript_render_2d_text


def string_render_2d_text(expr: String, evaluation: Evaluation, **kwargs) -> TextBlock:
    lines = expr.value.split("\n")
    max_len = max([len(line) for line in lines])
    lines = [line + (max_len - len(line)) * " " for line in lines]
    return TextBlock("\n".join(lines))


expr_to_2d_text_map["System`String"] = string_render_2d_text


def stringform_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    strform = expr.elements[0]
    if not isinstance(strform, String):
        raise _WrongFormattedExpression

    items = list(
        render_2d_text(item, evaluation, **kwargs) for item in expr.elements[1:]
    )

    curr_indx = 0
    parts = strform.value.split("`")
    result = TextBlock(parts[0])
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
                result = join_blocks(
                    result, TEXTBLOCK_BACKQUOTE, part, TEXTBLOCK_BACKQUOTE
                )
                quote_open = False
                continue
        else:
            result = join_blocks(result, part)
            quote_open = True

    return result


expr_to_2d_text_map["System`StringForm"] = stringform_render_2d_text


def superscript_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    elements = expr.elements
    if len(elements) != 2:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        base, exponent = elements
        base_tb, exponent_tb = (
            render_2d_text(item, evaluation, **kwargs) for item in elements
        )
        precedence = compare_precedence(base, 590) or 1
        if precedence < 0:
            base_tb = parenthesize(base_tb)
        return superscript(base_tb, exponent_tb)
    infix_form = Expression(
        SymbolInfix,
        ListExpression(*(expr.elements)),
        String("^"),
        Integer(590),
        SymbolRight,
    )
    return render_2d_text(infix_form, evaluation, **kwargs)


expr_to_2d_text_map["System`Superscript"] = superscript_render_2d_text


def symbol_render_2d_text(symb: Symbol, evaluation: Evaluation, **kwargs):
    return TextBlock(evaluation.definitions.shorten_name(symb.name))


expr_to_2d_text_map["System`Symbol"] = symbol_render_2d_text


def tableform_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    return grid_render_2d_text(expr, evaluation)


expr_to_2d_text_map["System`TableForm"] = tableform_render_2d_text


def texform_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    #  boxes = format_element(expr.elements[0], evaluation)
    boxes = Expression(
        Symbol("System`MakeBoxes"), expr.elements[0], SymbolStandardForm
    ).evaluate(evaluation)
    return TextBlock(boxes.boxes_to_tex())  # type: ignore


expr_to_2d_text_map["System`TeXForm"] = texform_render_2d_text


def times_render_2d_text(
    expr: Expression, evaluation: Evaluation, **kwargs
) -> TextBlock:
    elements = expr.elements
    num: List[BaseElement] = []
    den: List[BaseElement] = []
    # First, split factors with integer, negative powers:
    for elem in elements:
        if elem.has_form("Power", 2):
            base, exponent = elem.elements
            if isinstance(exponent, Integer):
                if exponent.value == -1:
                    den.append(base)
                    continue
                elif exponent.value < 0:
                    den.append(Expression(SymbolPower, base, Integer(-exponent.value)))
                    continue
        elif isinstance(elem, Rational):
            num.append(elem.numerator())
            den.append(elem.denominator())
            continue
        elif elem.has_form("Rational", 2):
            elem_elements = elem.elements
            num.append(elem_elements[0])
            den.append(elem_elements[1])
            continue

        num.append(elem)

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
        return render_2d_text(num[0], evaluation, **kwargs)

    prefactor = 1
    result: TextBlock = TEXTBLOCK_NULL
    for i, elem in enumerate(num):
        if elem is IntegerM1:
            prefactor *= -1
            continue
        if isinstance(elem, Integer):
            prefactor *= -1
            elem = Integer(-elem.value)

        elem_txt = render_2d_text(elem, evaluation, **kwargs)
        if compare_precedence(elem, 400):
            elem_txt = parenthesize(elem_txt)
        if i == 0:
            result = elem_txt
        else:
            result = join_blocks(result, TEXTBLOCK_SPACE, elem_txt)
    if str(result) == "":
        result = TEXTBLOCK_ONE
    if prefactor == -1:
        result = join_blocks(TEXTBLOCK_MINUS, result)
    return result


expr_to_2d_text_map["System`Times"] = times_render_2d_text
