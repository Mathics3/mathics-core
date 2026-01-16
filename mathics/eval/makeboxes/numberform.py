"""
NumberForm related routines.
"""

import sys
from math import ceil
from typing import Any, Dict, Optional, Tuple, Union

import mpmath

from mathics.core.atoms import (
    Integer,
    Integer0,
    MachineReal,
    PrecisionReal,
    Real,
    String,
)
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.number import (
    LOG2_10,
    RECONSTRUCT_MACHINE_PRECISION_DIGITS,
    convert_base,
    dps,
)
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import (
    SymbolFullForm,
    SymbolMakeBoxes,
    SymbolOutputForm,
    SymbolSubscriptBox,
)
from mathics.eval.makeboxes import to_boxes

STR_DIGITS_CHECK_THRESHOLD = sys.int_info.str_digits_check_threshold


def default_numberformat_outputform(man, base, exp, opts):
    """Default number format function for OutputForm"""
    res = f"{man.value}{opts['NumberMultiplier']}{base.value}^{exp.value}"
    return String(res)


DEFAULT_NUMBERFORM_OPTIONS = {
    "DigitBlock": [0, 0],
    "ExponentFunction": lambda x: (SymbolNull if abs(x.value) <= 5 else x),
    "ExponentStep": 1,
    "NumberFormat": default_numberformat_outputform,
    "NumberMultiplier": "×",
    "NumberPadding": ["", "0"],
    "NumberPoint": ".",
    "NumberSeparator": [",", ""],
    "NumberSigns": ["-", ""],
    "SignPadding": False,
    "_Form": "System`FullForm",
}


def int_to_tuple_info(
    integer: Integer, digits: Optional[int] = None
) -> Tuple[str, int, bool, int]:
    """
    Convert ``integer`` to a tuple representing that value. The tuple consists of:
    * the string absolute value of ``integer``.
    * the exponent, base 10, to be used, and
    * True if the value is nonnegative or False otherwise.
    """
    value = integer.value
    if value < 0:
        is_nonnegative = False
        value = -value
    else:
        is_nonnegative = True
    try:
        s = str(value)
    except ValueError:
        # To large int values raise an error in Python when
        # converted into a string. Use in this case an
        # special function to process them:
        s = int_to_string_shorter_repr(value)

    digits = len(s) if digits is None else min(len(s), digits)
    exponent = len(s) - 1
    return s, exponent, is_nonnegative, digits


# STR_DIGITS_CHECK_THRESHOLD=640 is the maximum number of characters allowed by Python for an integer to be converted into a string.
def int_to_string_shorter_repr(
    value: int, max_digits: int = STR_DIGITS_CHECK_THRESHOLD
) -> str:
    """Convert value to a String, restricted to max_digits characters.

    if value has an n-digit decimal representation,
      value = d_1 *10^{n-1} d_2 * 10^{n-2} + d_3 10^{n-3} + ..... +
              d_{n-2}*100 +d_{n-1}*10 + d_{n}
    is represented as the string

    "d_1d_2d_3...d_{k}<<n-2k>>d_{n-k-1}...d_{n-2}d_{n-1}d_{n}"

    where n-2k digits are replaced by a placeholder.
    """
    if max_digits == 0:
        return str(value)

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
            return "-" + str(value)
        return str(value)

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
    return value_str


def real_to_tuple_info(
    real: Real, digits: Optional[int]
) -> Tuple[str, int, bool, int, int]:
    """
    Convert ``real`` to a tuple representing that value. The tuple consists of:
    * the string absolute value of ``integer`` with decimal point removed from the string;
      the position of the decimal point is determined by the exponent below,
    * the exponent, base 10, to be used, and
    * True if the value is nonnegative or False otherwise.
    * Updated value of digits, according to the number precision.
    * the decimal precision.

    If ``digits`` is None, we use the default precision.
    """
    binary_precision = real.get_precision()
    precision = dps(binary_precision)
    if digits is None:
        digits = precision + 1
    else:
        digits = min(digits, precision + 1)

    if real.is_zero:
        s = "0"
        if real.is_machine_precision():
            exponent = 0
        else:
            exponent = -precision
        is_nonnegative = True
        return s, exponent, is_nonnegative, digits, precision

    if digits is None:
        if real.is_machine_precision():
            value = real.value
            s = repr(value)
        else:
            with mpmath.workprec(binary_precision):
                value = real.to_mpmath()
                s = mpmath.nstr(value, precision + 1)
    else:
        with mpmath.workprec(binary_precision):
            value = real.to_mpmath()
            s = mpmath.nstr(value, digits)

    # Set sign prefix.
    if s[0] == "-":
        assert value < 0
        is_nonnegative = False
        s = s[1:]
    else:
        assert value >= 0
        is_nonnegative = True
    # Set exponent. ``exponent`` is actual, ``pexp`` of ``numberform_to_boxes()`` is printed.
    if "e" in s:
        s, exponent = s.split("e")
        exponent = int(exponent)
        if len(s) > 1 and s[1] == ".":
            # str(float) doesn't always include '.' if 'e' is present.
            s = s[0] + s[2:].rstrip("0")
    else:
        exponent = s.index(".") - 1
        s = s[: exponent + 1] + s[exponent + 2 :].rstrip("0")

        # Normalize exponent: remove leading '0's after the decimal point
        # and adjust the exponent accordingly.
        i = 0
        while i < len(s) and s[i] == "0":
            i += 1
            exponent -= 1
        s = s[i:]

    # Add trailing zeros for precision reals.
    if digits is not None and not real.is_machine_precision() and len(s) < digits:
        s = s + "0" * (digits - len(s))
    return s, exponent, is_nonnegative, digits, precision


def eval_baseform(
    expr: BaseElement, n: BaseElement, f: Symbol, evaluation: Evaluation
) -> BoxElementMixin:
    """
    Evaluate MakeBoxes[BaseForm[expr_, n_], f_]

    Parameters
    ----------
    expr : BaseElement
        the expression.
    n : BaseElement
        the base.
    f : Symbol
        Form (StandardForm/TraditionalForm).
    evaluation : Evaluation
        Evaluation object used for messages.

    Returns
    -------
    BoxElementMixin
        A String or a box expression representing `expr` in base `n`.

    """
    try:
        val, base = get_baseform_elements(expr, n, evaluation)
    except ValueError:
        return None
    if base is None:
        return to_boxes(Expression(SymbolMakeBoxes, expr, f), evaluation)
    if f is SymbolOutputForm:
        return to_boxes(String(f"{val}_{base}"), evaluation)

    return to_boxes(
        Expression(SymbolSubscriptBox, String(val), String(base)), evaluation
    )


def get_baseform_elements(
    expr: BaseElement, n: BaseElement, evaluation: Evaluation
) -> Dict[str, Any]:
    """
    Collect the options for BaseForm expressions.

    Parameters
    ----------
    expr : BaseElement
        Expression to be formatted.
    n : BaseElement
        The base of the numeration.
    evaluation : Evaluation
        Evaluation object used for show messages.

    Raises
    ------
    ValueError
        If some of the parameters is not valid.

    Returns
    -------
    Dict[str, Any]
        A dictionary with the option values.

    """

    if not isinstance(n, Integer):
        evaluation.message("BaseForm", "intpm", expr, n)
        raise ValueError

    base = n.value
    if base <= 0:
        evaluation.message("BaseForm", "intpm", expr, n)
        raise ValueError

    if isinstance(expr, PrecisionReal):
        x = expr.to_sympy()
        p = int(ceil(expr.get_precision() / LOG2_10) + 1)
    elif isinstance(expr, MachineReal):
        x = expr.value
        p = RECONSTRUCT_MACHINE_PRECISION_DIGITS
    elif isinstance(expr, Integer):
        x = expr.value
        p = 0
    else:
        return None, None
    try:
        return convert_base(x, base, p), base
    except ValueError:
        evaluation.message("BaseForm", "basf", n)
        raise


def get_numberform_parameters(
    full_expr, evaluation
) -> Tuple[BaseElement, BaseElement, Dict[str, Any]]:
    """Collect the parameters of a NumberForm[...] expression.
    Return a tuple with the expression, to be formatted,
    the precision especification and a dictionary of options
    with Python values
    """
    # Pick the
    num_form = full_expr.head
    elements = full_expr.elements
    form_name = num_form.get_name()
    full_expr = Expression(SymbolFullForm, full_expr)
    # This picks the builtin object used to do the option
    # checks...
    self = evaluation.definitions.builtin[form_name].builtin
    default_options: [str, BaseElement] = evaluation.definitions.get_options(form_name)
    options: Dict[str, BaseElement] = {}
    py_options: Dict = {}

    if len(elements) == 0:
        evaluation.message(form_name, "argm", num_form, Integer0)
        raise ValueError
    # Just one parameter. Silently return:
    if len(elements) == 1:
        py_options = self.check_and_convert_options(default_options, evaluation)
        if py_options is None:
            raise ValueError

        return elements[0], None, py_options
    # expr is now the target expression:
    expr, *elements = elements
    # Collect options
    pos = len(elements)
    options.update(default_options)
    for elem in elements[::-1]:
        pos = pos - 1
        if elem.has_form(("Rule", "RuleDelayed"), 2):
            key, val = elem.elements
            if isinstance(key, Symbol):
                key_name = key.get_name()
                if key_name not in options:
                    evaluation.message(form_name, "optx", key, num_form, *elements)
                    raise ValueError
                options[key_name] = val
            else:
                evaluation.message(form_name, "optx", key, num_form, *elements)
                raise ValueError
        else:
            break

    # To many non-option arguments
    if pos > 0:
        evaluation.message(form_name, "argct", num_form, Integer(len(elements) + 1))
        raise ValueError
    # Check for validity of the values:
    if pos == 0:
        precision_parms = elements[0]
    else:
        precision_parms = None

    py_options = self.check_and_convert_options(options, evaluation)

    if isinstance(precision_parms, Integer):
        val = precision_parms.value
        if val <= 0:
            evaluation.message(form_name, "iprf", precision_parms)
            precision_parms = None
    elif precision_parms.has_form("List", 2):
        if any(
            not isinstance(x, Integer) or x.value <= 0 for x in precision_parms.elements
        ):
            evaluation.message(form_name, "iprf", precision_parms)
            precision_parms = None
    else:
        evaluation.message(form_name, "iprf", precision_parms)
        precision_parms = None

    return expr, precision_parms, py_options


def numberform_to_boxes(
    value: Union[Real, Integer],
    digits: Optional[int],
    digits_after_decimal_point: Optional[int],
    evaluation: Optional[Evaluation],
    options: dict,
) -> BoxElementMixin:
    """
    Converts a Real or Integer value to a String or a BoxExpression.

    ``digits`` is the number of digits of precision and
    ``digits_after_decimal_point`` is the number of digits after the
    decimal point.  ``evaluation`` is used for messages.

    The allowed options are Python versions of the options permitted to
    NumberForm and must be supplied. See NumberForm or Real.make_boxes
    for correct option examples.

    If ``digits`` is None, use the default precision.  If
    ``digits_after_decimal_points`` is None, use all the digits we get
    from the converted number, that is, otherwise the number may be
    padded on the right-hand side with zeros.
    """

    # Ensure that all the options are valid options
    for key, val in DEFAULT_NUMBERFORM_OPTIONS.items():
        if options.get(key, None) is None:
            options[key] = val

    form = options["_Form"]

    # Get information about `value`
    is_int = False
    if isinstance(value, Integer):
        precision = None
        s, exp, is_nonnegative, digits = int_to_tuple_info(value, digits)
        if digits_after_decimal_point is None:
            is_int = True
    elif isinstance(value, Real):
        s, exp, is_nonnegative, digits, precision = real_to_tuple_info(value, digits)
    else:
        raise ValueError("Expected Real or Integer.")

    options["_digits_after_decimal_point"] = digits_after_decimal_point

    (
        left,
        right,
        exp,
        pexp,
    ) = _format_exponent(s, exp, is_int, evaluation, options)
    left, right = _do_pre_paddings(left, right, form, exp, options)

    digit_block = options["DigitBlock"]
    number_sep = options["NumberSeparator"]
    if digit_block[0]:
        left = _add_digit_block_separators(
            left, len(left) % digit_block[0], digit_block[0], number_sep[0]
        )
    if digit_block[1]:
        right = _add_digit_block_separators(right, 0, digit_block[1], number_sep[1])
    prefix, s = _do_padding(
        (
            left,
            right,
        ),
        digits,
        is_nonnegative,
        is_int,
        options,
    )
    s = _attach_precision(s, value, form, precision)

    # PrintForms attach the prefix to the number. FullForm and $BoxForms
    # put the prefix and the number in a RowBox:
    if form not in ("System`StandardForm", "System`TraditionalForm", "System`FullForm"):
        s = prefix + s
        prefix = ""

    # build number
    boxed_s = String(s)
    if pexp:
        # base
        boxed_s = options["NumberFormat"](
            boxed_s,
            String("10"),
            String(pexp),
            options,
        )
    if prefix:
        from mathics.builtin.box.layout import RowBox

        boxed_s = RowBox(String(prefix), boxed_s)
    return boxed_s


def _add_digit_block_separators(
    part: str, start: int, block_size: int, num_sep: str
) -> str:
    """Add the digit block separator"""

    def _split_string(s, start, step):
        if start > 0:
            yield s[:start]
        for i in range(start, len(s), step):
            yield s[i : i + step]

    part = _split_string(part, start, block_size)
    part = num_sep.join(part)
    return part


def _attach_precision(s: str, value, form: str, precision: float) -> str:
    """Add the precision mark if needed."""

    if isinstance(value, MachineReal):
        if form not in ("System`InputForm", "System`OutputForm"):
            s = s + "`"
    elif isinstance(value, PrecisionReal):
        if form not in ("System`OutputForm"):
            str_precision = str(precision)
            if "." not in str_precision:
                str_precision += "."
            s = s + "`" + str_precision
    return s


def _do_padding(
    parts: Tuple[str, str],
    digits: int,
    is_nonnegative: bool,
    is_int: bool,
    options: Dict[str, Any],
) -> Tuple[str, str]:
    """
    Rebuild the prefix and magnitud
    """
    left, right = parts
    left_padding = 0
    sign_prefix = options["NumberSigns"][1 if is_nonnegative else 0]
    max_sign_len = max(len(ns) for ns in options["NumberSigns"])

    i = len(sign_prefix) + len(left) + len(right) - max_sign_len
    if i < digits:
        left_padding = digits - i
    elif len(sign_prefix) < max_sign_len:
        left_padding = max_sign_len - len(sign_prefix)
    left_padding = left_padding * options["NumberPadding"][0]

    # insert NumberPoint
    if options["SignPadding"]:
        prefix = sign_prefix + left_padding
    else:
        prefix = left_padding + sign_prefix

    if is_int:
        s = left
    else:
        s = left + options["NumberPoint"] + right
    return prefix, s


def _do_pre_paddings(
    left: str, right: str, form: str, exp: int, options
) -> Tuple[str, str]:
    # pad with NumberPadding
    daadp = options["_digits_after_decimal_point"]
    if daadp is None:
        if form != "System`OutputForm":
            # Other forms strip trailing zeros:

            while len(right) > 0:
                if right[-1] == "0":
                    right = right[:-1]
                else:
                    break
    else:
        if len(right) < daadp:
            # pad right
            right = right + (daadp - len(right)) * options["NumberPadding"][1]
        elif len(right) > daadp:
            # round right
            tmp = int(left + right)
            tmp = _round(tmp, daadp - len(right))
            tmp = str(tmp)
            left, right = tmp[: exp + 1], tmp[exp + 1 :]
    return left, right


def _format_exponent(
    s: str, exp: int, is_int: bool, evaluation: Evaluation, options: Dict[str, Any]
) -> Tuple[str, str, int, str]:
    # round exponent to ExponentStep
    exponent_step = options["ExponentStep"]
    rexp = (exp // exponent_step) * exponent_step

    if is_int:
        # integer never uses scientific notation
        pexp = ""
    else:
        method = options["ExponentFunction"]
        pexp = method(Integer(rexp)).get_int_value()
        if pexp is not None:
            exp -= pexp
            pexp = str(pexp)
        else:
            pexp = ""

    # pad right with '0'.
    if len(s) < exp + 1:
        if evaluation is not None:
            evaluation.message("NumberForm", "sigz")

        # TODO NumberPadding instead 0?
        s = s + "0" * (1 + exp - len(s))
    # pad left with '0'.
    if exp < 0:
        s = "0" * (-exp) + s
        exp = 0

    # left and right of NumberPoint
    sleft, sright = s[: exp + 1], s[exp + 1 :]
    return sleft, sright, exp, pexp


def _round(number, ndigits):
    """
    python round() for integers but with correct rounding.
    e.g. `_round(14225, -1)` is `14230` not `14220`.
    """
    assert isinstance(ndigits, int)
    assert ndigits < 0
    assert isinstance(number, int)
    assert number >= 0
    number += 5 * int(10 ** -(1 + ndigits))
    number //= int(10**-ndigits)
    return number
