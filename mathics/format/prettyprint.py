"""
This module builts the 2D string associated to the OutputForm
"""

from typing import Any, Callable, Dict, List, Optional, Union

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
from mathics.eval.makeboxes import compare_precedence, do_format  # , format_element
from mathics.format.pane_text import (
    TextBlock,
    bracket,
    fraction,
    grid,
    integral_definite,
    integral_indefinite,
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


def expression_to_2d_text(
    expr: BaseElement, evaluation: Evaluation, form=SymbolStandardForm, **kwargs
):
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
        return expr_to_2d_text_map[lookup_name](format_expr, evaluation, form, **kwargs)
    except _WrongFormattedExpression:
        # If the key is not present, or the execution fails for any reason, use
        # the default
        pass
    except KeyError:
        pass
    return _default_expression_to_2d_text(format_expr, evaluation, form, **kwargs)


def _default_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    """
    Default representation of a function
    """
    expr_head = expr.head
    head = expression_to_2d_text(expr_head, evaluation, form, **kwargs)
    comma = TextBlock(", ")
    elements = [expression_to_2d_text(elem, evaluation) for elem in expr.elements]
    result = elements.pop(0) if elements else TextBlock(" ")
    while elements:
        result = result + comma + elements.pop(0)

    if form is SymbolTraditionalForm:
        return head + parenthesize(result)
    return head + bracket(result)


def _divide(num, den, evaluation, form, **kwargs):
    if kwargs.get("2d", False):
        return fraction(
            expression_to_2d_text(num, evaluation, form, **kwargs),
            expression_to_2d_text(den, evaluation, form, **kwargs),
        )
    infix_form = Expression(
        SymbolInfix, ListExpression(num, den), String("/"), Integer(400), SymbolLeft
    )
    return expression_to_2d_text(infix_form, evaluation, form, **kwargs)


def _strip_1_parm_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    if len(expr.elements) != 1:
        raise _WrongFormattedExpression
    return expression_to_2d_text(expr.elements[0], evaluation, form, **kwargs)


expr_to_2d_text_map["System`HoldForm"] = _strip_1_parm_expression_to_2d_text
expr_to_2d_text_map["System`InputForm"] = _strip_1_parm_expression_to_2d_text


def derivative_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    """Derivative operator"""
    head = expr.get_head()
    if head is SymbolDerivative:
        return _default_expression_to_2d_text(expr, evaluation, form, **kwargs)
    super_head = head.get_head()
    if super_head is SymbolDerivative:
        expr_elements = expr.elements
        if len(expr_elements) != 1:
            return _default_expression_to_2d_text(expr, evaluation, form, **kwargs)
        function_head = expression_to_2d_text(
            expr_elements[0], evaluation, form, **kwargs
        )
        derivatives = head.elements
        if len(derivatives) == 1:
            order_iv = derivatives[0]
            if order_iv == Integer1:
                return function_head + "'"
            elif order_iv == Integer2:
                return function_head + "''"

        if not kwargs["2d"]:
            return _default_expression_to_2d_text(expr, evaluation, form, **kwargs)

        superscript_tb = TextBlock(",").join(
            expression_to_2d_text(order, evaluation, form, **kwargs)
            for order in derivatives
        )
        superscript_tb = parenthesize(superscript_tb)
        return superscript(function_head, superscript_tb)

    # Full Function with arguments: delegate to the default conversion.
    # It will call us again with the head
    return _default_expression_to_2d_text(expr, evaluation, form, **kwargs)


expr_to_2d_text_map["System`Derivative"] = derivative_expression_to_2d_text


def divide_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    if len(expr.elements) != 2:
        raise _WrongFormattedExpression
    num, den = expr.elements
    return _divide(num, den, evaluation, form, **kwargs)


expr_to_2d_text_map["System`Divide"] = divide_expression_to_2d_text


def graphics(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    return TextBlock("-Graphics-")


expr_to_2d_text_map["System`Graphics"] = graphics


def graphics3d(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    return TextBlock("-Graphics3D-")


expr_to_2d_text_map["System`Graphics3D"] = graphics3d


def grid_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
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
                    expression_to_2d_text(item_elem, evaluation, form, **kwargs)
                    for item_elem in item.elements
                ]
            )
        else:
            rows.append(expression_to_2d_text(item, evaluation, form, **kwargs))

    return grid(rows)


expr_to_2d_text_map["System`Grid"] = grid_expression_to_2d_text


def integer_expression_to_2d_text(
    n: Integer, evaluation: Evaluation, form: Symbol, **kwargs
):
    return TextBlock(str(n.value))


expr_to_2d_text_map["System`Integer"] = integer_expression_to_2d_text


def integrate_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    elems = list(expr.elements)
    if len(elems) > 2 or not kwargs.get("2d", False):
        raise _WrongFormattedExpression

    integrand = elems.pop(0)
    result = expression_to_2d_text(integrand, evaluation, form, **kwargs)
    while elems:
        var = elems.pop(0)
        if var.has_form("List", 3):
            var_txt, a, b = (
                expression_to_2d_text(item, evaluation, form, **kwargs)
                for item in var.elements
            )
            result = integral_definite(result, var_txt, a, b)
        elif isinstance(var, Symbol):
            var_txt = expression_to_2d_text(var, evaluation, form, **kwargs)
            result = integral_indefinite(result, var_txt)
        else:
            break
    return result


expr_to_2d_text_map["System`Integrate"] = integrate_expression_to_2d_text


def list_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    return (
        TextBlock("{")
        + TextBlock(", ").join(
            [
                expression_to_2d_text(elem, evaluation, form, **kwargs)
                for elem in expr.elements
            ]
        )
        + TextBlock("}")
    )


expr_to_2d_text_map["System`List"] = list_expression_to_2d_text


def mathmlform_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    #  boxes = format_element(expr.elements[0], evaluation, form)
    boxes = Expression(
        Symbol("System`MakeBoxes"), expr.elements[0], SymbolStandardForm
    ).evaluate(evaluation)
    return TextBlock(boxes.boxes_to_mathml())  # type: ignore[union-attr]


expr_to_2d_text_map["System`MathMLForm"] = mathmlform_expression_to_2d_text


def matrixform_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    # return parenthesize(tableform_expression_to_2d_text(expr, evaluation, form, **kwargs))
    return tableform_expression_to_2d_text(expr, evaluation, form, **kwargs)


expr_to_2d_text_map["System`MatrixForm"] = matrixform_expression_to_2d_text


def plus_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    elements = expr.elements
    result = TextBlock("")
    for i, elem in enumerate(elements):
        if elem.has_form("Times", None):
            # If the first element is -1, remove it and use
            # a minus sign. Otherwise, if negative, do not add a sign.
            first = elem.elements[0]
            if isinstance(first, Integer):
                if first.value == -1:
                    result = (
                        result
                        + " - "
                        + expression_to_2d_text(
                            Expression(SymbolTimes, *elem.elements[1:]),
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
                        + expression_to_2d_text(elem, evaluation, form, **kwargs)
                    )
                    continue
            elif isinstance(first, Real):
                if first.value < 0:
                    result = (
                        result
                        + " "
                        + expression_to_2d_text(elem, evaluation, form, **kwargs)
                    )
                    continue
            result = (
                result + " + " + expression_to_2d_text(elem, evaluation, form, **kwargs)
            )
            ## TODO: handle complex numbers?
        else:
            elem_txt = expression_to_2d_text(elem, evaluation, form, **kwargs)
            if (compare_precedence(elem, 310) or -1) < 0:
                elem_txt = parenthesize(elem_txt)
                result = result + " + " + elem_txt
            elif i == 0 or (
                (isinstance(elem, Integer) and elem.value < 0)
                or (isinstance(elem, Real) and elem.value < 0)
            ):
                result = result + elem_txt
            else:
                result = (
                    result
                    + " + "
                    + expression_to_2d_text(elem, evaluation, form, **kwargs)
                )
    return result


expr_to_2d_text_map["System`Plus"] = plus_expression_to_2d_text


def power_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
):
    if len(expr.elements) != 2:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        base, exponent = (
            expression_to_2d_text(elem, evaluation, form, **kwargs)
            for elem in expr.elements
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
    return expression_to_2d_text(infix_form, evaluation, form, **kwargs)


expr_to_2d_text_map["System`Power"] = power_expression_to_2d_text


def pre_pos_infix_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
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

    if head in (SymbolPrefix, SymbolPostfix):
        if len(operands) != 1:
            raise _WrongFormattedExpression
    elif head is SymbolInfix:
        if len(operands) < 2:
            raise _WrongFormattedExpression
    else:
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
                    expression_to_2d_text(op, evaluation, form, **kwargs)
                    for op in ops.elements
                ]
            else:
                ops_lst = [expression_to_2d_text(ops, evaluation, form, **kwargs)]
        elif head in (SymbolPrefix, SymbolPostfix):
            ops_txt = [expression_to_2d_text(ops, evaluation, form, **kwargs)]
    else:
        if head is SymbolInfix:
            num_ops = 1
            default_symb = TextBlock(" ~ ")
            ops_lst = [
                default_symb
                + expression_to_2d_text(head, evaluation, form, **kwargs)
                + default_symb
            ]
        elif head is SymbolPrefix:
            default_symb = TextBlock(" @ ")
            ops_txt = (
                expression_to_2d_text(head, evaluation, form, **kwargs) + default_symb
            )
        elif head is SymbolPostfix:
            default_symb = TextBlock(" // ")
            ops_txt = default_symb + expression_to_2d_text(
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

    if head is SymbolPrefix:
        operand = operands[0]
        cmp_precedence = compare_precedence(operand, precedence)
        target_txt = expression_to_2d_text(operand, evaluation, form, **kwargs)
        if cmp_precedence is not None and cmp_precedence != -1:
            target_txt = parenthesize(target_txt)
        return ops_txt[0] + target_txt
    if head is SymbolPostfix:
        operand = operands[0]
        cmp_precedence = compare_precedence(operand, precedence)
        target_txt = expression_to_2d_text(operand, evaluation, form, **kwargs)
        if cmp_precedence is not None and cmp_precedence != -1:
            target_txt = parenthesize(target_txt)
        return target_txt + ops_txt[0]
    else:  # Infix
        parenthesized = group in (None, SymbolRight, SymbolNonAssociative)
        for index, operand in enumerate(operands):
            operand_txt = expression_to_2d_text(operand, evaluation, form, **kwargs)
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
                if ops_lst[index % num_ops].text != " ":
                    result = result + " " + ops_lst[index % num_ops] + " " + operand_txt
                else:
                    result = result + " " + operand_txt

        return result


expr_to_2d_text_map["System`Prefix"] = pre_pos_infix_expression_to_2d_text
expr_to_2d_text_map["System`Postfix"] = pre_pos_infix_expression_to_2d_text
expr_to_2d_text_map["System`Infix"] = pre_pos_infix_expression_to_2d_text


def precedenceform_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    if len(expr.elements) == 2:
        return expression_to_2d_text(expr.elements[0], evaluation, form, **kwargs)
    raise _WrongFormattedExpression


expr_to_2d_text_map["System`PrecedenceForm"] = precedenceform_expression_to_2d_text


def rational_expression_to_2d_text(
    n: Union[Rational, Expression], evaluation: Evaluation, form: Symbol, **kwargs
):
    if n.has_form("Rational", 2):
        num, den = n.elements  # type: ignore[union-attr]
    else:
        num, den = n.numerator(), n.denominator()  # type: ignore[union-attr]
    return _divide(num, den, evaluation, form, **kwargs)


expr_to_2d_text_map["System`Rational"] = rational_expression_to_2d_text


def real_expression_to_2d_text(n: Real, evaluation: Evaluation, form: Symbol, **kwargs):
    str_n = n.make_boxes("System`OutputForm").boxes_to_text()  # type: ignore[attr-defined]
    return TextBlock(str(str_n))


expr_to_2d_text_map["System`Real"] = real_expression_to_2d_text


def sqrt_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    if not 1 <= len(expr.elements) <= 2:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        return sqrt_block(
            *(
                expression_to_2d_text(item, evaluation, form, **kwargs)
                for item in expr.elements
            )
        )
    raise _WrongFormattedExpression


expr_to_2d_text_map["System`Sqrt"] = sqrt_expression_to_2d_text


def subscript_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    if len(expr.elements) != 2:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        return subscript(
            *(
                expression_to_2d_text(item, evaluation, form, **kwargs)
                for item in expr.elements
            )
        )
    raise _WrongFormattedExpression


expr_to_2d_text_map["System`Subscript"] = subscript_expression_to_2d_text


def subsuperscript_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    if len(expr.elements) != 3:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        return subsuperscript(
            *(
                expression_to_2d_text(item, evaluation, form, **kwargs)
                for item in expr.elements
            )
        )
    raise _WrongFormattedExpression


expr_to_2d_text_map["System`Subsuperscript"] = subsuperscript_expression_to_2d_text


def string_expression_to_2d_text(
    expr: String, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    return TextBlock(expr.value)


expr_to_2d_text_map["System`String"] = string_expression_to_2d_text


def stringform_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    strform = expr.elements[0]
    if not isinstance(strform, String):
        raise _WrongFormattedExpression

    items = list(
        expression_to_2d_text(item, evaluation, form, **kwargs)
        for item in expr.elements[1:]
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
                result = result + "`" + part + "`"
                quote_open = False
                continue
        else:
            result = result + part
            quote_open = True

    return result


expr_to_2d_text_map["System`StringForm"] = stringform_expression_to_2d_text


def superscript_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    elements = expr.elements
    if len(elements) != 2:
        raise _WrongFormattedExpression
    if kwargs.get("2d", False):
        base, exponent = elements
        base_tb, exponent_tb = (
            expression_to_2d_text(item, evaluation, form, **kwargs) for item in elements
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
    return expression_to_2d_text(infix_form, evaluation, form, **kwargs)


expr_to_2d_text_map["System`Superscript"] = superscript_expression_to_2d_text


def symbol_expression_to_2d_text(
    symb: Symbol, evaluation: Evaluation, form: Symbol, **kwargs
):
    return TextBlock(evaluation.definitions.shorten_name(symb.name))


expr_to_2d_text_map["System`Symbol"] = symbol_expression_to_2d_text


def tableform_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    return grid_expression_to_2d_text(expr, evaluation, form)


expr_to_2d_text_map["System`TableForm"] = tableform_expression_to_2d_text


def texform_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
) -> TextBlock:
    #  boxes = format_element(expr.elements[0], evaluation, form)
    boxes = Expression(
        Symbol("System`MakeBoxes"), expr.elements[0], SymbolStandardForm
    ).evaluate(evaluation)
    return TextBlock(boxes.boxes_to_tex())  # type: ignore


expr_to_2d_text_map["System`TeXForm"] = texform_expression_to_2d_text


def times_expression_to_2d_text(
    expr: Expression, evaluation: Evaluation, form: Symbol, **kwargs
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
        return _divide(num_expr, den_expr, evaluation, form, **kwargs)

    # there are no integer negative powers:
    if len(num) == 1:
        return expression_to_2d_text(num[0], evaluation, form, **kwargs)

    prefactor = 1
    result: TextBlock = TextBlock("")
    for i, elem in enumerate(num):
        if elem is IntegerM1:
            prefactor *= -1
            continue
        if isinstance(elem, Integer):
            prefactor *= -1
            elem = Integer(-elem.value)

        elem_txt = expression_to_2d_text(elem, evaluation, form, **kwargs)
        if compare_precedence(elem, 400):
            elem_txt = parenthesize(elem_txt)
        if i == 0:
            result = elem_txt
        else:
            result = result + " " + elem_txt
    if result.text == "":
        result = TextBlock("1")
    if prefactor == -1:
        result = TextBlock("-") + result
    return result


expr_to_2d_text_map["System`Times"] = times_expression_to_2d_text
