# -*- coding: utf-8 -*-
"""
This module contains basic low-level functions that combine an ``Expression``
with an ``Evaluation`` objects to produce ``BoxExpressions``, following
formatting rules.
"""


from typing import Any, Callable, Dict, List, Optional, Type

from mathics.core.atoms import Complex, Integer, Rational, String, SymbolI
from mathics.core.convert.expression import to_expression_with_specialization
from mathics.core.element import BaseElement, BoxElementMixin, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolDivide,
    SymbolFullForm,
    SymbolGraphics,
    SymbolGraphics3D,
    SymbolHoldForm,
    SymbolList,
    SymbolNumberForm,
    SymbolPlus,
    SymbolPostfix,
    SymbolRepeated,
    SymbolRepeatedNull,
    SymbolTimes,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolComplex,
    SymbolMinus,
    SymbolOutputForm,
    SymbolRational,
    SymbolStandardForm,
)

# An operator precedence value that will ensure that whatever operator
# this is attached to does not have parenthesis surrounding it.
# Operator precedence values are integers; If if an operator
# "op" is greater than the surrounding precedence, then "op"
# will be surrounded by parenthesis, e.g. ... (...op...) ...
# In named-characters.yml of mathics-scanner we start at 0.
# However, negative values would also work.
NEVER_ADD_PARENTHESIS = 0


# These Strings are used in Boxing output
StringElipsis = String("...")
StringLParen = String("(")
StringRParen = String(")")
StringRepeated = String("..")


# do_format_*

_element_formatters: Dict[
    Type[BaseElement],
    Callable[[BaseElement, Evaluation, Symbol], Optional[BaseElement]],
] = {}


# this temporarily replaces the _BoxedString class
def _boxed_string(string: str, **options):
    from mathics.builtin.box.layout import StyleBox

    return StyleBox(String(string), **options)


def compare_precedence(
    element: BaseElement, precedence: Optional[int] = None
) -> Optional[int]:
    """
    compare the precedence of the element regarding a precedence value.
    If both precedences are equal, return 0. If precedence of the
    first element is higher, return 1, otherwise -1.
    If precedences cannot be compared, return None.
    """
    while element.has_form("HoldForm", 1):
        element = element.elements[0]

    if precedence is None:
        return None
    if element.has_form(("Infix", "Prefix", "Postfix"), 3, None):
        element_prec = element.elements[2].value
    elif element.has_form("PrecedenceForm", 2):
        element_prec = element.elements[1].value
    # For negative values, ensure that the element_precedence is at least the precedence. (Fixes #332)
    elif isinstance(element, (Integer, Real)) and element.value < 0:
        element_prec = precedence
    else:
        element_prec = builtins_precedence.get(element.get_head_name())

    if element_prec is None:
        return None
    return 0 if element_prec == precedence else (1 if element_prec > precedence else -1)


# 640 = sys.int_info.str_digits_check_threshold.
# Someday when 3.11 is the minimum version of Python supported,
# we can replace the magic value 640 below with sys.int.str_digits_check_threshold.
def int_to_string_shorter_repr(value: int, form: Symbol, max_digits=640):
    """Convert value to a String, restricted to max_digits characters.

    if value has an n-digit decimal representation,
      value = d_1 *10^{n-1} d_2 * 10^{n-2} + d_3 10^{n-3} + ..... +
              d_{n-2}*100 +d_{n-1}*10 + d_{n}
    is represented as the string

    "d_1d_2d_3...d_{k}<<n-2k>>d_{n-k-1}...d_{n-2}d_{n-1}d_{n}"

    where n-2k digits are replaced by a placeholder.
    """
    if max_digits == 0:
        return String(str(value))

    # Normalize to positive quantities
    is_negative = value < 0
    if is_negative:
        value = -value
        max_digits = max_digits - 1

    # Estimate the number of decimal digits
    num_digits = int(value.bit_length() * 0.3)

    # If the estimated number is below the threshold,
    # return it as it is.
    if num_digits <= max_digits:
        if is_negative:
            return String("-" + str(value))
        return String(str(value))

    # estimate the size of the placeholder
    size_placeholder = len(str(num_digits)) + 6
    # Estimate the number of available decimal places
    avaliable_digits = max(max_digits - size_placeholder, 0)
    # how many most significative digits include
    len_msd = (avaliable_digits + 1) // 2
    # how many least significative digits to include:
    len_lsd = avaliable_digits - len_msd
    # Compute the msd.
    msd = str(value // 10 ** (num_digits - len_msd))
    if msd == "0":
        msd = ""

    # If msd has more digits than the expected, it means that
    # num_digits was wrong.
    extra_msd_digits = len(msd) - len_msd
    if extra_msd_digits > 0:
        # Remove the extra digit and fix the real
        # number of digits.
        msd = msd[:len_msd]
        num_digits = num_digits + 1

    lsd = ""
    if len_lsd > 0:
        lsd = str(value % 10 ** (len_lsd))
        # complete decimal positions in the lsd:
        lsd = (len_lsd - len(lsd)) * "0" + lsd

    # Now, compute the true number of hiding
    # decimal places, and built the placeholder
    remaining = num_digits - len_lsd - len_msd
    placeholder = f" <<{remaining}>> "
    # Check if the shorten string is actually
    # shorter than the full string representation:
    if len(placeholder) < remaining:
        value_str = f"{msd}{placeholder}{lsd}"
    else:
        value_str = str(value)

    if is_negative:
        value_str = "-" + value_str
    return String(value_str)


def eval_fullform_makeboxes(
    self, expr, evaluation: Evaluation, form=SymbolStandardForm
) -> Optional[BaseElement]:
    """
    This function takes the definitions provided by the evaluation
    object, and produces a boxed form for expr.

    Basically: MakeBoxes[expr // FullForm]
    """
    # This is going to be reimplemented.
    expr = Expression(SymbolFullForm, expr)
    return Expression(SymbolMakeBoxes, expr, form).evaluate(evaluation)


def eval_makeboxes(
    expr, evaluation: Evaluation, form=SymbolStandardForm
) -> Optional[BaseElement]:
    """
    This function takes the definitions provided by the evaluation
    object, and produces a boxed fullform for expr.

    Basically: MakeBoxes[expr // form]
    """
    # This is going to be reimplemented.
    return Expression(SymbolMakeBoxes, expr, form).evaluate(evaluation)


def make_output_form(expr, evaluation, form):
    """
    Build a 2D text representation of the expression.
    """
    from mathics.builtin.box.layout import InterpretationBox, PaneBox
    from mathics.format.prettyprint import expression_to_2d_text

    use_2d = (
        evaluation.definitions.get_ownvalues("System`$Use2DOutputForm")[0].replace
        is SymbolTrue
    )
    text2d = expression_to_2d_text(expr, evaluation, form, **{"2d": use_2d}).text

    if "\n" in text2d:
        text2d = "\n" + text2d
    elem1 = PaneBox(String(text2d))
    elem2 = Expression(SymbolOutputForm, expr)
    return InterpretationBox(elem1, elem2)


# do_format_*


def do_format(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
    do_format_method = _element_formatters.get(type(element), do_format_element)
    return do_format_method(element, evaluation, form)


def do_format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
    """
    Applies formats associated to the expression and removes
    superfluous enclosing formats.
    """
    from mathics.core.definitions import OutputForms

    evaluation.inc_recursion_depth()
    try:
        expr = element
        head = element.get_head()  # use element.head
        elements = element.get_elements()
        include_form = False
        # If the expression is enclosed by a Format
        # takes the form from the expression and
        # removes the format from the expression.
        if head in OutputForms and len(elements) == 1:
            expr = elements[0]
            if not form.sameQ(head):
                form = head
                include_form = True

        # If form is Fullform, return it without changes
        if form is SymbolFullForm:
            if include_form:
                expr = Expression(form, expr)
            return expr

        # Repeated and RepeatedNull confuse the formatter,
        # so we need to hardlink their format rules:
        if head is SymbolRepeated:
            if len(elements) == 1:
                return Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolPostfix,
                        ListExpression(elements[0]),
                        StringRepeated,
                        Integer(170),
                    ),
                )
            else:
                return Expression(SymbolHoldForm, expr)
        elif head is SymbolRepeatedNull:
            if len(elements) == 1:
                return Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolPostfix,
                        Expression(SymbolList, elements[0]),
                        StringElipsis,
                        Integer(170),
                    ),
                )
            else:
                return Expression(SymbolHoldForm, expr)

        # If expr is not an atom, looks for formats in its definition
        # and apply them.
        def format_expr(expr):
            if not (isinstance(expr, Atom)) and not (isinstance(expr.head, Atom)):
                # expr is of the form f[...][...]
                return None
            name = expr.get_lookup_name()
            format_rules = evaluation.definitions.get_formats(name, form.get_name())
            for rule in format_rules:
                result = rule.apply(expr, evaluation)
                if result is not None and result != expr:
                    return result.evaluate(evaluation)
            return None

        formatted = format_expr(expr) if isinstance(expr, EvalMixin) else None
        if formatted is not None:
            do_format_fn = _element_formatters.get(type(formatted), do_format_element)
            result = do_format_fn(formatted, evaluation, form)
            if include_form and result is not None:
                result = Expression(form, result)
            return result

        # If the expression is still enclosed by a Format,
        # iterate.
        # If the expression is not atomic or of certain
        # specific cases, iterate over the elements.
        head = expr.get_head()
        if head in OutputForms:
            # If the expression was of the form
            # Form[expr, opts]
            # then the format was not stripped. Then,
            # just return it as it is.
            if len(expr.get_elements()) != 1:
                return expr
            do_format_fn = _element_formatters.get(type(element), do_format_element)
            result = do_format_fn(expr, evaluation, form)
            if isinstance(result, Expression):
                expr = result

        elif (
            head is not SymbolNumberForm
            and not isinstance(expr, (Atom, BoxElementMixin))
            and head not in (SymbolGraphics, SymbolGraphics3D)
        ):
            new_elements = tuple(
                (
                    _element_formatters.get(type(element), do_format_element)(
                        element, evaluation, form
                    )
                    for element in expr.elements
                )
            )
            expr_head = expr.head
            do_format = _element_formatters.get(type(expr_head), do_format_element)
            head = do_format(expr_head, evaluation, form)
            expr = to_expression_with_specialization(head, *new_elements)

        if include_form:
            expr = Expression(form, expr)
        return expr
    finally:
        evaluation.dec_recursion_depth()


def do_format_rational(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
    if not isinstance(element, Rational):
        return None
    if form is SymbolFullForm:
        return do_format_expression(
            Expression(
                Expression(SymbolHoldForm, SymbolRational),
                element.numerator(),
                element.denominator(),
            ),
            evaluation,
            form,
        )
    else:
        numerator = element.numerator()
        minus = numerator.value < 0
        if minus:
            numerator = Integer(-numerator.value)
        result = Expression(SymbolDivide, numerator, element.denominator())
        if minus:
            result = Expression(SymbolMinus, result)
        result = Expression(SymbolHoldForm, result)
        result = do_format_expression(result, evaluation, form)
        return result


def do_format_complex(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
    if not isinstance(element, Complex):
        return None
    if form is SymbolFullForm:
        return do_format_expression(
            Expression(
                Expression(SymbolHoldForm, SymbolComplex), element.real, element.imag
            ),
            evaluation,
            form,
        )

    parts: List[Any] = []
    if element.is_machine_precision() or not element.real.is_zero:
        parts.append(element.real)
    if element.imag.sameQ(Integer(1)):
        parts.append(SymbolI)
    else:
        parts.append(Expression(SymbolTimes, element.imag, SymbolI))

    if len(parts) == 1:
        result = parts[0]
    else:
        result = Expression(SymbolPlus, *parts)

    return do_format_expression(Expression(SymbolHoldForm, result), evaluation, form)


def do_format_expression(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
    # # not sure how much useful is this format_cache
    # if element._format_cache is None:
    #    element._format_cache = {}

    # last_evaluated_time, expr = element._format_cache.get(form, (None, None))
    # if last_evaluated_time is not None and expr is not None:
    # if True
    #    symbolname = expr.get_name()
    #    if symbolname != "":
    #        if not evaluation.definitions.is_uncertain_final_value(
    #            last_evaluated_time, set((symbolname,))
    #        ):
    #            return expr
    expr = do_format_element(element, evaluation, form)
    # element._format_cache[form] = (evaluation.definitions.now, expr)
    return expr


_element_formatters[Rational] = do_format_rational
_element_formatters[Complex] = do_format_complex
_element_formatters[Expression] = do_format_expression
