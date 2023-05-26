# -*- coding: utf-8 -*-

"""
helper functions for arithmetic evaluation, which do not
depends on the evaluation context. Conversions to Sympy are
used just as a last resource.

Many of these do do depend on the evaluation context. Conversions to Sympy are
used just as a last resource.
"""

from functools import lru_cache
from typing import Callable, List, Optional, Tuple

import mpmath
import sympy

from mathics.core.atoms import (
    NUMERICAL_CONSTANTS,
    Complex,
    Integer,
    Integer0,
    Integer1,
    Integer2,
    IntegerM1,
    Number,
    Rational,
    RationalOneHalf,
    Real,
)
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement, ElementsProperties
from mathics.core.expression import Expression
from mathics.core.number import FP_MANTISA_BINARY_DIGITS, SpecialValueError, min_prec
from mathics.core.rules import Rule
from mathics.core.symbols import Atom, Symbol, SymbolPlus, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolAbs,
    SymbolComplexInfinity,
    SymbolExp,
    SymbolI,
    SymbolIndeterminate,
    SymbolLog,
    SymbolSign,
)

RationalMOneHalf = Rational(-1, 2)
RealM0p5 = Real(-0.5)
RealOne = Real(1.0)


# This cache might not be used that much.
@lru_cache()
def call_mpmath(
    mpmath_function: Callable, mpmath_args: tuple, precision: int
) -> Optional[BaseElement]:
    """
    A wrapper that calls
       mpmath_function(mpmath_args *mpmathargs)
    setting precision to the parameter ``precision``.

    The result is cached.
    """
    with mpmath.workprec(precision):
        try:
            result_mp = mpmath_function(*mpmath_args)
            if precision != FP_MANTISA_BINARY_DIGITS:
                return from_mpmath(result_mp, precision)
            return from_mpmath(result_mp)
        except ValueError as exc:
            text = str(exc)
            if text == "gamma function pole":
                return SymbolComplexInfinity
            else:
                raise
        except ZeroDivisionError:
            return
        except SpecialValueError as exc:
            return Symbol(exc.name)


def eval_Abs(expr: BaseElement) -> Optional[BaseElement]:
    """
    if expr is a number, return the absolute value.
    """

    if isinstance(expr, Number):
        return eval_Abs_number(expr)
    if expr.has_form("Power", 2):
        base, exp = expr.elements
        if exp.is_zero:
            return Integer1
        if test_arithmetic_expr(expr):
            abs_base = eval_Abs(base)
            if abs_base is None:
                abs_base = Expression(SymbolAbs, base)
            return Expression(SymbolPower, abs_base, exp)
    if expr.get_head() is SymbolTimes:
        return eval_multiply_numbers(*(eval_Abs(x) for x in expr.elements))
    if test_nonnegative_arithmetic_expr(expr):
        return expr
    if test_negative_arithmetic_expr(expr):
        return eval_multiply_numbers(IntegerM1, expr)
    return None


def eval_Abs_number(n: Number) -> Number:
    """
    Evals the absolute value of a number
    """
    if isinstance(n, Integer):
        n_val = n.value
        if n_val >= 0:
            return n
        return Integer(-n_val)
    if isinstance(n, Rational):
        n_num, n_den = n.value.as_numer_denom()
        if n_num >= 0:
            return n
        return Rational(-n_num, n_den)
    if isinstance(n, Real):
        n_val = n.value
        if n_val >= 0:
            return n
        return eval_multiply_numbers(IntegerM1, n)
    if isinstance(n, Complex):
        if n.real.is_zero:
            return eval_Abs_number(n.imag)
        sq_comp = tuple((eval_multiply_numbers(x, x) for x in (n.real, n.imag)))
        sq_abs = eval_add_numbers(*sq_comp)
        result = eval_Power_number(sq_abs, RationalOneHalf) or Expression(
            SymbolPower, sq_abs, RationalOneHalf
        )
        return result


def eval_Sign(expr: BaseElement) -> Optional[BaseElement]:
    """
    if expr is a number, return its sign.
    """
    if isinstance(expr, Atom):
        return eval_Sign_number(expr)
    if expr.has_form("Power", 2):
        base, exp = expr.elements
        if exp.is_zero:
            return Integer1
        if isinstance(exp, (Integer, Real, Rational)):
            sign = eval_Sign(base) or Expression(SymbolSign, base)
            return Expression(SymbolPower, sign, exp)
        if isinstance(exp, Complex):
            sign = eval_Sign(base) or Expression(SymbolSign, base)
            return Expression(SymbolPower, sign, exp.real)
        if test_arithmetic_expr(exp):
            sign = eval_Sign(base) or Expression(SymbolSign, base)
            return Expression(SymbolPower, sign, exp)
        return None
    if expr.has_form("Exp", 1):
        exp = expr.elements[0]
        if isinstance(exp, (Integer, Real, Rational)):
            return Integer1
        if isinstance(exp, Complex):
            return Expression(SymbolExp, exp.imag)
    if expr.get_head() is SymbolTimes:
        abs_value = eval_Abs(eval_multiply_numbers(*expr.elements))
        if abs_value is Integer1:
            return expr
        if abs_value is None:
            return None
        criteria = eval_add_numbers(abs_value, IntegerM1)
        if test_zero_arithmetic_expr(criteria, numeric=True):
            return expr
        return None
    if expr.get_head() is SymbolPlus:
        abs_value = eval_Abs(eval_add_numbers(*expr.elements))
        if abs_value is Integer1:
            return expr
        if abs_value is None:
            return None
        criteria = eval_add_numbers(abs_value, IntegerM1)
        if test_zero_arithmetic_expr(criteria, numeric=True):
            return expr
        return None
    if test_nonnegative_arithmetic_expr(expr):
        return Integer1
    if test_negative_arithmetic_expr(expr):
        return IntegerM1
    if test_zero_arithmetic_expr:
        return Integer0
    return None
    if isinstance(expr, Complex):
        re, im = expr.real, expr.imag
        sqabs = eval_add_numbers(eval_Times(re, re), eval_Times(im, im))
        norm = Expression(SymbolPower, sqabs, RationalMOneHalf)
        result = eval_Times(expr, norm)
        if result is None:
            return Expression(SymbolTimes, expr, norm)
        return result
    return None


def eval_Sign_number(n: Number) -> Number:
    """
    Evals the absolute value of a number.
    """
    if n.is_zero:
        return Integer0
    if isinstance(n, (Integer, Rational, Real)):
        return Integer1 if n.value > 0 else IntegerM1
    if isinstance(n, Complex):
        abs_sq = eval_add_numbers(
            *(eval_multiply_numbers(x, x) for x in (n.real, n.imag))
        )
        criteria = eval_add_numbers(abs_sq, IntegerM1)
        if test_zero_arithmetic_expr(criteria):
            return n
        if n.is_inexact():
            return eval_multiply_numbers(n, eval_Power_number(abs_sq, RealM0p5))
        if test_zero_arithmetic_expr(criteria, numeric=True):
            return n
        return eval_multiply_numbers(n, eval_Power_number(abs_sq, RationalMOneHalf))


def eval_mpmath_function(
    mpmath_function: Callable, *args: Number, prec: Optional[int] = None
) -> Optional[Number]:
    """
    Call the mpmath function `mpmath_function` with the arguments `args`
    working with precision `prec`. If `prec` is `None`, work with machine
    precision.

    Return a Mathics Number or None if the evaluation failed.
    """
    if prec is None:
        # if any argument has machine precision then the entire calculation
        # is done with machine precision.
        float_args = [arg.round().get_float_value(permit_complex=True) for arg in args]
        if None in float_args:
            return

        return call_mpmath(mpmath_function, tuple(float_args), FP_MANTISA_BINARY_DIGITS)
    else:
        with mpmath.workprec(prec):
            # to_mpmath seems to require that the precision is set from outside
            mpmath_args = [x.to_mpmath() for x in args]
            if None in mpmath_args:
                return
            return call_mpmath(mpmath_function, tuple(mpmath_args), prec)


def eval_Exponential(exp: BaseElement) -> BaseElement:
    """
    Eval E^exp
    """
    # If both base and exponent are exact quantities,
    # use sympy.

    if not exp.is_inexact():
        exp_sp = exp.to_sympy()
        if exp_sp is None:
            return None
        return from_sympy(sympy.Exp(exp_sp))

    prec = exp.get_precision()
    if prec is not None:
        if exp.is_machine_precision():
            number = mpmath.exp(exp.to_mpmath())
            result = from_mpmath(number)
            return result
        else:
            with mpmath.workprec(prec):
                number = mpmath.exp(exp.to_mpmath())
                return from_mpmath(number, prec)


def eval_Plus(*items: BaseElement) -> BaseElement:
    "evaluate Plus for general elements"
    numbers, items_tuple = segregate_numbers_from_sorted_list(*items)
    elements = []
    last_item = last_count = None
    number = eval_add_numbers(*numbers) if numbers else Integer0

    # This reduces common factors
    # TODO: Check if it possible to avoid the conversions back and forward to sympy.
    def append_last():
        if last_item is not None:
            if last_count == 1:
                elements.append(last_item)
            else:
                if last_item.has_form("Times", None):
                    elements.append(
                        Expression(
                            SymbolTimes, from_sympy(last_count), *last_item.elements
                        )
                    )
                else:
                    elements.append(
                        Expression(SymbolTimes, from_sympy(last_count), last_item)
                    )

    for item in items_tuple:
        count = rest = None
        if item.has_form("Times", None):
            for element in item.elements:
                if isinstance(element, Number):
                    count = element.to_sympy()
                    rest = item.get_mutable_elements()
                    rest.remove(element)
                    if len(rest) == 1:
                        rest = rest[0]
                    else:
                        rest.sort()
                        rest = Expression(SymbolTimes, *rest)
                    break
        if count is None:
            count = sympy.Integer(1)
            rest = item
        if last_item is not None and last_item == rest:
            last_count = last_count + count
        else:
            append_last()
            last_item = rest
            last_count = count
    append_last()

    # now elements contains the symbolic terms which can not be simplified.
    # by collecting common symbolic factors.
    if not elements:
        return number

    if number is not Integer0:
        elements.insert(0, number)
    elif len(elements) == 1:
        return elements[0]

    elements.sort()
    return Expression(
        SymbolPlus,
        *elements,
        elements_properties=ElementsProperties(False, False, True),
    )

    elements.sort()
    return Expression(
        SymbolPlus,
        *elements,
        elements_properties=ElementsProperties(False, False, True),
    )


def eval_Power_number(base: Number, exp: Number) -> Optional[Number]:
    """
    Eval base^exp for `base` and `exp` two numbers. If the expression
    remains the same, return None.
    """
    # If both base and exponent are exact quantities,
    # use sympy.
    # If base or exp are inexact quantities, use
    # the inexact routine.
    if base.is_inexact() or exp.is_inexact():
        return eval_Power_inexact(base, exp)

    # Trivial special cases
    if exp is Integer1:
        return base
    if exp is Integer0:
        return Integer1
    if base is Integer1:
        return Integer1

    def eval_Power_sympy() -> Optional[Number]:
        """
        Tries to compute x^p using sympy rules.
        If the answer is again x^p, return None.
        """
        # This function is called just if useful native rules
        # are available.
        result = from_sympy(sympy.Pow(base.to_sympy(), exp.to_sympy()))
        if result.has_form("Power", 2):
            # If the expression didn´t change, return None
            if result.elements[0].sameQ(base):
                return None
        return result

    # Rational exponent
    if isinstance(exp, Rational):
        exp_p, exp_q = exp.value.as_numer_denom()
        if abs(exp_p) > exp_q:
            exp_int, exp_num = divmod(exp_p, exp_q)
            exp_rem = Rational(exp_num, exp_q)
            factor_1 = eval_Power_number(base, Integer(exp_int))
            factor_2 = eval_Power_number(base, exp_rem) or Expression(
                SymbolPower, base, exp_rem
            )
            if factor_1 is Integer1:
                return factor_2
            return Expression(SymbolTimes, factor_1, factor_2)

    # Integer base
    if isinstance(base, Integer):
        base_value = base.value
        if base_value == -1:
            if isinstance(exp, Rational):
                if exp.sameQ(RationalOneHalf):
                    return SymbolI
                return None
            return eval_Power_sympy()
        elif base_value < 0:
            neg_base = eval_negate_number(base)
            candidate = eval_Power_number(neg_base, exp)
            if candidate is None:
                return None
            sign_factor = eval_Power_number(IntegerM1, exp)
            if candidate is Integer1:
                return sign_factor
            return Expression(SymbolTimes, candidate, sign_factor)

    # Rational base
    if isinstance(base, Rational):
        # If the exponent is an Integer or Rational negative value
        # restate as a positive power
        if (
            isinstance(exp, Integer)
            and exp.value < 0
            or isinstance(exp, Rational)
            and exp.value.p < 0
        ):
            base, exp = eval_inverse_number(base), eval_negate_number(exp)
            return eval_Power_number(base, exp) or Expression(SymbolPower, base, exp)

        p, q = (Integer(u) for u in base.value.as_numer_denom())
        p_eval, q_eval = (eval_Power_number(u, exp) for u in (p, q))
        # If neither p^exp or q^exp produced a new result,
        # leave it alone
        if q_eval is None and p_eval is None:
            return None
        # if q^exp == 1: return p_eval
        # (should not happen)
        if q_eval is Integer1:
            return p_eval
        if isinstance(q_eval, Integer):
            if isinstance(p_eval, Integer):
                return Rational(p_eval.value, q_eval.value)

        if p_eval is None:
            p_eval = Expression(SymbolPower, p, exp)

        if q_eval is None:
            q_eval = Expression(SymbolPower, q, exp)
        return Expression(
            SymbolTimes, p_eval, Expression(SymbolPower, q_eval, IntegerM1)
        )
    # Pure imaginary base case
    elif isinstance(base, Complex) and base.real.is_zero:
        base = base.imag
        if base.value < 0:
            base = eval_negate_number(base)
            phase = Expression(
                SymbolPower,
                IntegerM1,
                eval_multiply_numbers(IntegerM1, RationalOneHalf, exp),
            )
        else:
            phase = Expression(
                SymbolPower, IntegerM1, eval_multiply_numbers(RationalOneHalf, exp)
            )
        real_factor = eval_Power_number(base, exp)

        if real_factor is None:
            return None
        return Expression(SymbolTimes, real_factor, phase)

    # Generic case
    return eval_Power_sympy()


def eval_Power_inexact(base: Number, exp: Number) -> BaseElement:
    """
    Eval base^exp for `base` and `exp` inexact numbers
    """
    # If both base and exponent are exact quantities,
    # use sympy.
    prec = min_prec(base, exp)
    if prec is not None:
        is_machine_precision = base.is_machine_precision() or exp.is_machine_precision()
        if is_machine_precision:
            number = mpmath.power(base.to_mpmath(), exp.to_mpmath())
            return from_mpmath(number)
        else:
            with mpmath.workprec(prec):
                number = mpmath.power(base.to_mpmath(), exp.to_mpmath())
                return from_mpmath(number, prec)


def eval_Times(*items: BaseElement) -> BaseElement:
    elements = []
    numbers = []
    # find numbers and simplify Times -> Power
    numbers, symbolic_items = segregate_numbers_from_sorted_list(*(items))
    # This loop handles factors representing infinite quantities,
    # and factors which are powers of the same basis.

    for item in symbolic_items:
        if item is SymbolIndeterminate:
            return item
        # Process powers
        if elements:
            previous_elem = elements[-1]
            if item == previous_elem:
                elements[-1] = Expression(SymbolPower, previous_elem, Integer2)
                continue
            elif item.has_form("Power", 2):
                base, exp = item.elements
                if previous_elem.has_form("Power", 2) and base.sameQ(
                    previous_elem.elements[0]
                ):
                    exp = eval_Plus(exp, previous_elem.elements[1])
                    elements[-1] = Expression(
                        SymbolPower,
                        base,
                        exp,
                    )
                    continue
                if base.sameQ(previous_elem):
                    exp = eval_Plus(Integer1, exp)
                    elements[-1] = Expression(
                        SymbolPower,
                        base,
                        exp,
                    )
                    continue
            elif previous_elem.has_form("Power", 2) and previous_elem.elements[0].sameQ(
                item
            ):
                exp = eval_Plus(Integer1, previous_elem.elements[1])
                elements[-1] = Expression(
                    SymbolPower,
                    item,
                    exp,
                )
                continue
        else:
            item = item
        # Otherwise, just append the element...
        elements.append(item)

    number = eval_multiply_numbers(*numbers) if numbers else Integer1

    if len(elements) == 0 or number is Integer0:
        return number

    if number is IntegerM1 and elements and elements[0].has_form("Plus", None):
        elements[0] = Expression(
            elements[0].get_head(),
            *[
                Expression(SymbolTimes, IntegerM1, element)
                for element in elements[0].elements
            ],
        )
        number = Integer1

    if number is not Integer1:
        elements.insert(0, number)

    if len(elements) == 1:
        return elements[0]

    elements = sorted(elements)
    items_elements = items
    if len(elements) == len(items_elements) and all(
        elem.sameQ(item) for elem, item in zip(elements, items_elements)
    ):
        return None
    return Expression(
        SymbolTimes,
        *elements,
        elements_properties=ElementsProperties(False, False, True),
    )


# Here I used the convention of calling eval_* to functions that can produce a new expression, or None
# if the result can not be evaluated, or is trivial. For example, if we call eval_Power_number(Integer2, RationalOneHalf)
# it returns ``None`` instead of ``Expression(SymbolPower, Integer2, RationalOneHalf)``.
# The reason is that these functions are written to be part of replacement rules, to be applied during the evaluation process.
# In that process, a rule is considered applied if produces an expression that is different from the original one, or
# if the replacement function returns (Python's) ``None``.
#
# For example, when the expression ``Power[4, 1/2]`` is evaluated, a (Builtin) rule  ``Power[base_, exp_]->eval_repl_rule(base, expr)``
# is applied. If the rule matches, `repl_rule` is called with arguments ``(4, 1/2)`` and produces `2`. As `Integer2.sameQ(Power[4, 1/2])`
# is False, then no new rules for `Power` are checked, and a new round of evaluation is atempted.
#
# On the other hand, if ``Power[3, 1/2]``, ``repl_rule`` can do two possible things: one is return ``Power[3, 1/2]``. If it does,
# the rule is considered applied. Then, the evaluation method checks if `Power[3, 1/2].sameQ(Power[3, 1/2])`. In this case it is true,
# and then the expression is kept as it is.
# The other possibility is to return  (Python's) `None`. In that case, the evaluator considers that the rule failed to be applied,
# and look for another rule associated to ``Power``. To return ``None`` produces then a faster evaluation, since no ``sameQ`` call is needed,
# and do not prevent that other rules are attempted.
#
# The bad part of using ``None`` as a return is that I would expect that ``eval`` produces always a valid Expression, so if at some point of
# the code I call ``eval_Power_number(Integer3, RationalOneHalf)`` I get ``Expression(SymbolPower, Integer3, RationalOneHalf)``.
#
# From my point of view, it would make more sense to use the following convention:
#  * if the method has signature ``eval_method(...)->BaseElement:`` then use the prefix ``eval_``
#  * if the method has the siguature ``apply_method(...)->Optional[BaseElement]`` use the prefix ``apply_`` or maybe ``repl_``.
#
# In any case, let's keep the current convention.
#
#


def associate_powers(expr: BaseElement, power: BaseElement = Integer1) -> BaseElement:
    """
    base^a^b^c^...^power -> base^(a*b*c*...power)
    provided one of the following cases
    * `a`, `b`, ... `power` are all integer numbers
    * `a`, `b`,... are Rational/Real number with absolute value <=1,
      and the other powers are not integer numbers.
    * `a` is not a Rational/Real number, and b, c, ... power are all
      integer numbers.
    """
    powers = []
    base = expr
    if power is not Integer1:
        powers.append(power)

    while base.has_form("Power", 2):
        previous_base, outer_power = base, power
        base, power = base.elements
        if len(powers) == 0:
            if power is not Integer1:
                powers.append(power)
            continue
        if power is IntegerM1:
            powers.append(power)
            continue
        if isinstance(power, (Rational, Real)):
            if abs(power.value) < 1:
                powers.append(power)
                continue
        # power is not rational/real and outer_power is integer,
        elif isinstance(outer_power, Integer):
            if power is not Integer1:
                powers.append(power)
            if isinstance(power, Integer):
                continue
            else:
                break
        # in any other case, use the previous base and
        # exit the loop
        base = previous_base
        break

    if len(powers) == 0:
        return base
    elif len(powers) == 1:
        return Expression(SymbolPower, base, powers[0])
    result = Expression(SymbolPower, base, Expression(SymbolTimes, *powers))
    return result


def distribute_factor(expr: BaseElement, factor: BaseElement) -> BaseElement:
    """
    q * (a + b  + c) -> (q a  + q b + q c)
    """
    if not expr.has_form("Plus", None):
        return expr
    terms = (Expression(SymbolTimes, factor, term) for term in expr.elements)
    return Expression(SymbolPlus, *terms)


def distribute_powers(expr: BaseElement) -> BaseElement:
    """
    (a b c)^p -> (a^p b^p c^p)
    """
    if not expr.has_form("Power", 2):
        return expr
    base, exp = expr.elements
    if not base.has_form("Times", None):
        return expr
    factors = (Expression(SymbolPower, factor, exp) for factor in base.elements)
    return Expression(SymbolTimes, *factors)


def eval_add_numbers(
    *numbers: List[Number],
) -> Number:
    """
    Add the elements in ``numbers``.
    """
    if len(numbers) == 0:
        return Integer0
    if len(numbers) == 1:
        return numbers[0]

    is_machine_precision = any(number.is_machine_precision() for number in numbers)
    if is_machine_precision:
        terms = (item.to_mpmath() for item in numbers)
        number = mpmath.fsum(terms)
        return from_mpmath(number)

    prec = min_prec(*numbers)
    if prec is not None:
        # For a sum, what is relevant is the minimum accuracy of the terms
        with mpmath.workprec(prec):
            terms = (item.to_mpmath() for item in numbers)
            number = mpmath.fsum(terms)
            return from_mpmath(number, precision=prec)
    else:
        return from_sympy(sum(item.to_sympy() for item in numbers))


def eval_complex_conjugate(z: Number) -> Number:
    """
    Evaluates the complex conjugate of z.
    """
    if isinstance(z, Complex):
        re, im = z.real, z.imag
        return Complex(re, eval_negate_number(im))
    return z


def eval_inverse_number(n: Number) -> Number:
    """
    Eval 1/n
    """
    if isinstance(n, Integer):
        n_value = n.value
        if n_value == 1 or n_value == -1:
            return n
        return Rational(-1, -n_value) if n_value < 0 else Rational(1, n_value)
    if isinstance(n, Rational):
        n_num, n_den = n.value.as_numer_denom()
        if n_num < 0:
            n_num, n_den = -n_num, -n_den
        if n_num == 1:
            return Integer(n_den)
        return Rational(n_den, n_num)
    # Otherwise, use power....
    return eval_Power_number(n, IntegerM1)


def eval_multiply_numbers(*numbers: List[Number]) -> Number:
    """
    Multiply the elements in ``numbers``.
    """
    if len(numbers) == 0:
        return Integer1
    if len(numbers) == 1:
        return numbers[0]

    is_machine_precision = any(number.is_machine_precision() for number in numbers)
    if is_machine_precision:
        factors = (item.to_mpmath() for item in numbers)
        number = mpmath.fprod(factors)
        return from_mpmath(number)

    prec = min_prec(*numbers)
    if prec is not None:
        with mpmath.workprec(prec):
            factors = (item.to_mpmath() for item in numbers)
            number = mpmath.fprod(factors)
            return from_mpmath(number, prec)
    else:
        return from_sympy(sympy.Mul(*(item.to_sympy() for item in numbers)))


def eval_negate_number(n: Number) -> Number:
    """
    Changes the sign of n
    """
    if isinstance(n, Integer):
        return Integer(-n.value)
    if isinstance(n, Rational):
        n_num, n_den = n.value.as_numer_denom()
        return Rational(-n_num, n_den)
    # Otherwise, multiply by -1:
    return eval_multiply_numbers(IntegerM1, n)


def flat_arithmetic_operators(expr: Expression) -> Expression:
    """
    operation[a_number, b, operation[c_number, d], e]-> operation[a, c, b, c, d, e]
    """
    # items is a dict with two keys: True and False.
    # In True we store numeric items, and in False the symbolic ones.
    items = {True: [], False: []}
    head = expr.get_head()
    for element in expr.elements:
        # If the element is also head[elements],
        # take its elements, and append to the main expression.
        if element.get_head() is head:
            for item in flat_arithmetic_operators(element).elements:
                item[isinstance(item, Number)].append(item)
        item[isinstance(item, Number)].append(item)
    return Expression(head, *items[True], *items[False])


def segregate_numbers(
    *elements: BaseElement,
) -> Tuple[List[Number], List[BaseElement]]:
    """
    From a list of elements, produce two lists, one with the numeric items
    and the other with the remaining
    """
    items = {True: [], False: []}
    for element in elements:
        items[isinstance(element, Number)].append(element)
    return items[True], items[False]


# Note: we return:
#  Tuple[List[Number], List[BaseElement]]
#             ^^^^^
# But the mypy type checking system can't
# look into the loop and its condition and
# prove that the return type is List[Number].
# So we use the weaker type assertion
# which is the one on elements: List[BaseElement].
def segregate_numbers_from_sorted_list(
    *elements: BaseElement,
) -> Tuple[List[BaseElement], List[BaseElement]]:
    """
    From a list of elements, produce two lists, one with the numeric items
    and the other with the remaining. Different from `segregate_numbers`,
    this function assumes that elements are sorted with the numbers at
    the beginning.
    """
    for pos, element in enumerate(elements):
        if not isinstance(element, Number):
            return list(elements[:pos]), list(elements[pos:])
    return list(elements), []


def test_arithmetic_expr(expr: BaseElement, only_real: bool = True) -> bool:
    """
    Check if an expression `expr` is an arithmetic expression
    composed only by numbers and arithmetic operations.
    If only_real is set to True, then `I` is not considered a number.
    """
    if isinstance(expr, (Integer, Rational, Real)):
        return True
    if expr in NUMERICAL_CONSTANTS:
        return True
    if isinstance(expr, Complex) or expr is SymbolI:
        return not only_real
    if isinstance(expr, Symbol):
        return False

    head, elements = expr.head, expr.elements

    if head in (SymbolPlus, SymbolTimes):
        return all(test_arithmetic_expr(term, only_real) for term in elements)
    if expr.has_form("Exp", 1):
        return test_arithmetic_expr(elements[0], only_real)
    if head is SymbolLog:
        if len(elements) > 2:
            return False
        if len(elements) == 2:
            base = elements[0]
            if not test_positive_arithmetic_expr(base):
                return False
        return test_arithmetic_expr(elements[-1], only_real)
    if expr.has_form("Power", 2):
        base, exponent = elements
        if only_real:
            if isinstance(exponent, Integer):
                return test_arithmetic_expr(base)
        return all(test_arithmetic_expr(item, only_real) for item in elements)
    return False


def test_negative_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a negative value.
    """
    if isinstance(expr, (Integer, Rational, Real)):
        return expr.value < 0

    expr = eval_multiply_numbers(IntegerM1, expr)
    return test_positive_arithmetic_expr(expr)


def test_nonnegative_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a nonnegative number
    """
    if not test_arithmetic_expr(expr):
        return False

    if test_zero_arithmetic_expr(expr) or test_positive_arithmetic_expr(expr):
        return True


def test_nonpositive_arithetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a nonnegative number
    """
    if not test_arithmetic_expr(expr):
        return False

    if test_zero_arithmetic_expr(expr) or test_negative_arithmetic_expr(expr):
        return True
    return False


def test_positive_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a positive value.
    """
    if isinstance(expr, (Integer, Rational, Real)):
        return expr.value > 0
    if expr in NUMERICAL_CONSTANTS:
        return True
    if isinstance(expr, Atom):
        return False

    head, elements = expr.get_head(), expr.elements
    if head is SymbolPlus:
        positive_nonpositive_terms = {True: [], False: []}
        for term in elements:
            positive_nonpositive_terms[test_positive_arithmetic_expr(term)].append(term)

        if len(positive_nonpositive_terms[False]) == 0:
            return True
        if len(positive_nonpositive_terms[True]) == 0:
            return False

        pos, neg = (
            eval_add_numbers(*items) for items in positive_nonpositive_terms.values()
        )
        if neg.is_zero:
            return True
        if not test_arithmetic_expr(neg):
            return False

        total = eval_add_numbers(pos, neg)
        # Check positivity of the evaluated expression
        if isinstance(total, (Integer, Rational, Real)):
            return total.value > 0
        if isinstance(total, Complex):
            return False
        if total.sameQ(expr):
            return False
        return test_positive_arithmetic_expr(total)

    if head is SymbolTimes:
        nonpositive_factors = tuple(
            (item for item in elements if not test_positive_arithmetic_expr(item))
        )
        if len(nonpositive_factors) == 0:
            return True
        evaluated_expr = eval_multiply_numbers(*nonpositive_factors)
        if evaluated_expr.sameQ(expr):
            return False
        return test_positive_arithmetic_expr(evaluated_expr)
    if expr.has_form("Power", 2):
        base, exponent = elements
        if isinstance(exponent, Integer) and exponent.value % 2 == 0:
            return test_arithmetic_expr(base)
        return test_arithmetic_expr(exponent) and test_positive_arithmetic_expr(base)
    if expr.has_form("Exp", 1):
        return test_arithmetic_expr(expr.elements[0], only_real=True)
    if expr.has_form("Sqrt", 1):
        return test_positive_arithmetic_expr(expr.elements[0])
    if head is SymbolLog:
        if len(elements) > 2:
            return False
        if len(elements) == 2:
            if not test_positive_arithmetic_expr(elements[0]):
                return False
        arg = elements[-1]
        return test_positive_arithmetic_expr(eval_add_numbers(arg, IntegerM1))
    if expr.has_form("Abs", 1):
        arg = elements[0]
        return test_arithmetic_expr(
            arg, only_real=False
        ) and not test_zero_arithmetic_expr(arg)
    if head.has_form("DirectedInfinity", 1):
        return test_positive_arithmetic_expr(elements[0])

    return False


def test_zero_arithmetic_expr(expr: BaseElement, numeric: bool = False) -> bool:
    """
    return True if expr evaluates to a number compatible
    with 0
    """

    def is_numeric_zero(z: Number):
        if isinstance(z, Complex):
            if abs(z.real.value) + abs(z.imag.value) < 2.0e-10:
                return True
        if isinstance(z, Number):
            if abs(z.value) < 1e-10:
                return True
        return False

    if expr.is_zero:
        return True
    if numeric:
        if is_numeric_zero(expr):
            return True
        expr = to_inexact_value(expr)
    if expr.has_form("Times", None):
        if any(
            test_zero_arithmetic_expr(element, numeric=numeric)
            for element in expr.elements
        ) and not any(
            element.has_form("DirectedInfinity", None) for element in expr.elements
        ):
            return True
    if expr.has_form("Power", 2):
        base, exp = expr.elements

        if test_zero_arithmetic_expr(base, numeric):
            return test_nonnegative_arithmetic_expr(exp)
        if base.has_form("DirectedInfinity", None):
            return test_positive_arithmetic_expr(exp)
    if expr.has_form("Plus", None):
        result = eval_add_numbers(*expr.elements)
        if numeric:
            if isinstance(result, complex):
                if abs(result.real.value) + abs(result.imag.value) < 2.0e-10:
                    return True
            if isinstance(result, Number):
                if abs(result.value) < 1e-10:
                    return True
        return result.is_zero
    return False


def to_inexact_value(expr: BaseElement) -> BaseElement:
    """
    Converts an expression into an inexact expression.
    Replaces numerical constants by their numerical approximation,
    and then multiplies the expression by Real(1.)
    """
    if expr.is_inexact():
        return expr

    if isinstance(expr, Expression):
        for const, value in NUMERICAL_CONSTANTS.items():
            expr, success = expr.do_apply_rule(Rule(const, value))

    return eval_multiply_numbers(RealOne, expr)
