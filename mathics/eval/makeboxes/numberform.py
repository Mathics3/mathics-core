"""
NumberForm related routines.
"""

from math import ceil
from typing import Optional, Tuple, Union

import mpmath

from mathics.core.atoms import Integer, MachineReal, PrecisionReal, Real, String
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.number import (
    LOG2_10,
    RECONSTRUCT_MACHINE_PRECISION_DIGITS,
    convert_base,
    dps,
)
from mathics.core.systemsymbols import (
    SymbolMakeBoxes,
    SymbolOutputForm,
    SymbolSubscriptBox,
)
from mathics.eval.makeboxes import _boxed_string, to_boxes


def int_to_tuple_info(integer: Integer) -> Tuple[str, int, bool]:
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
    s = str(value)
    exponent = len(s) - 1
    return s, exponent, is_nonnegative


def real_to_tuple_info(real: Real, digits: Optional[int]) -> Tuple[str, int, bool]:
    """
    Convert ``real`` to a tuple representing that value. The tuple consists of:
    * the string absolute value of ``integer`` with decimal point removed from the string;
      the position of the decimal point is determined by the exponent below,
    * the exponent, base 10, to be used, and
    * True if the value is nonnegative or False otherwise.

    If ``digits`` is None, we use the default precision.
    """
    if real.is_zero:
        s = "0"
        if real.is_machine_precision():
            exponent = 0
        else:
            p = real.get_precision()
            exponent = -dps(p)
        is_nonnegative = True
    else:
        if digits is None:
            if real.is_machine_precision():
                value = real.value
                s = repr(value)
            else:
                with mpmath.workprec(real.get_precision()):
                    value = real.to_mpmath()
                    s = mpmath.nstr(value, dps(real.get_precision()) + 1)
        else:
            with mpmath.workprec(real.get_precision()):
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
        # Set exponent. ``exponent`` is actual, ``pexp`` of ``NumberForm_to_string()`` is printed.
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
    return s, exponent, is_nonnegative


# FIXME: the return type should be a NumberForm, not a String.
# when this is fixed, rename the function.
def NumberForm_to_String(
    value: Union[Real, Integer],
    digits: Optional[int],
    digits_after_decimal_point: Optional[int],
    evaluation: Evaluation,
    options: dict,
) -> String:
    """
    Converts a Real or Integer value to a String.

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

    assert isinstance(digits, int) and digits > 0 or digits is None
    assert digits_after_decimal_point is None or (
        isinstance(digits_after_decimal_point, int) and digits_after_decimal_point >= 0
    )

    is_int = False
    if isinstance(value, Integer):
        assert digits is not None
        s, exp, is_nonnegative = int_to_tuple_info(value)
        if digits_after_decimal_point is None:
            is_int = True
    elif isinstance(value, Real):
        if digits is not None:
            digits = min(digits, dps(value.get_precision()) + 1)
        s, exp, is_nonnegative = real_to_tuple_info(value, digits)
        if digits is None:
            digits = len(s)
    else:
        raise ValueError("Expected Real or Integer.")

    assert isinstance(digits, int) and digits > 0

    sign_prefix = options["NumberSigns"][1 if is_nonnegative else 0]

    # round exponent to ExponentStep
    rexp = (exp // options["ExponentStep"]) * options["ExponentStep"]

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
        # TODO NumberPadding?
        s = s + "0" * (1 + exp - len(s))
    # pad left with '0'.
    if exp < 0:
        s = "0" * (-exp) + s
        exp = 0

    # left and right of NumberPoint
    left, right = s[: exp + 1], s[exp + 1 :]

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

    # pad with NumberPadding
    if digits_after_decimal_point is not None:
        if len(right) < digits_after_decimal_point:
            # pad right
            right = (
                right
                + (digits_after_decimal_point - len(right))
                * options["NumberPadding"][1]
            )
        elif len(right) > digits_after_decimal_point:
            # round right
            tmp = int(left + right)
            tmp = _round(tmp, digits_after_decimal_point - len(right))
            tmp = str(tmp)
            left, right = tmp[: exp + 1], tmp[exp + 1 :]

    def split_string(s, start, step):
        if start > 0:
            yield s[:start]
        for i in range(start, len(s), step):
            yield s[i : i + step]

    # insert NumberSeparator
    digit_block = options["DigitBlock"]
    if digit_block[0] != 0:
        left = split_string(left, len(left) % digit_block[0], digit_block[0])
        left = options["NumberSeparator"][0].join(left)
    if digit_block[1] != 0:
        right = split_string(right, 0, digit_block[1])
        right = options["NumberSeparator"][1].join(right)

    left_padding = 0
    max_sign_len = max(len(options["NumberSigns"][0]), len(options["NumberSigns"][1]))
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
        s = prefix + left
    else:
        s = prefix + left + options["NumberPoint"] + right

    # base
    base = "10"

    # build number
    method = options["NumberFormat"]
    if options["_Form"] in ("System`InputForm", "System`FullForm"):
        return method(
            _boxed_string(s, number_as_text=True),
            _boxed_string(base, number_as_text=True),
            _boxed_string(pexp, number_as_text=True),
            options,
        )
    else:
        return method(String(s), String(base), String(pexp), options)


def eval_baseform(self, expr, n, f, evaluation: Evaluation):
    base = n.value
    if base <= 0:
        evaluation.message("BaseForm", "intpm", expr, n)
        return None

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
        return to_boxes(Expression(SymbolMakeBoxes, expr, f), evaluation)

    try:
        val = convert_base(x, base, p)
    except ValueError:
        evaluation.message("BaseForm", "basf", n)
        return

    if f is SymbolOutputForm:
        return to_boxes(String("%s_%d" % (val, base)), evaluation)
    else:
        return to_boxes(
            Expression(SymbolSubscriptBox, String(val), String(base)), evaluation
        )
