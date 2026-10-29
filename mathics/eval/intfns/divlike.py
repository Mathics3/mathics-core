b"""
Mathics3 builtins from mathics.builtin.intfns.divlike
"""

from collections.abc import Callable

import sympy

import mathics.eval.tracing as tracing  # noqa
from mathics.core.atoms import Complex, Integer, Integer0
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol


def combine_integer_arguments(builtin, ns, eval_fn: Callable) -> Expression | None:
    """
    Build the result of GCD or LCM from its arguments ns: the integer
    arguments are combined by eval_fn into a single Integer. If every
    argument is an integer, that Integer is returned; otherwise a new
    GCD[...] or LCM[...] expression is returned that holds the combined
    integer followed by the remaining arguments. None, meaning no change,
    is returned when there are fewer than two integers to combine.

    The rule pattern is ns___ (ns__) and not ns___Integer: the functions are
    Flat, and ns___Integer also matches a lone integer among other
    arguments. Rewriting it to itself made GCD[1/2, 3] or GCD[2.5, 5]
    evaluate until $IterationLimit.
    """
    ns = ns.get_sequence()
    integers = [n for n in ns if isinstance(n, Integer)]
    if len(integers) == len(ns):
        return eval_fn(ns)
    if len(integers) < 2:
        return None
    combined = eval_fn(integers)
    if combined is None:
        return None
    others = [n for n in ns if not isinstance(n, Integer)]
    return Expression(Symbol(builtin.get_name()), combined, *others)


def eval_ExtendedGCD(arguments: tuple) -> Integer | None:
    integers: list[int] = []
    for element in arguments.elements:
        if isinstance(element, Integer):
            integers.append(element.value)
        else:
            # Handle things other than Integers?
            return None
    coeffs, current_gcd = gcdex_list(integers)
    return ListExpression(
        Integer(current_gcd), to_mathics_list(*coeffs, elements_conversion_fn=Integer)
    )


def eval_GCD(ns: tuple) -> Integer | None:
    if len(ns) == 0:
        return Integer0
    if (result := ns[0].value) is None:
        return
    for n in ns[1:]:
        value = n.value
        if value is None:
            return
        result = tracing.run_sympy(sympy.gcd, result, value)
    return Integer(abs(result))


def eval_LCM(ns: tuple) -> Integer | None:
    if len(ns) == 0:
        return Integer0
    if (result := ns[0].value) is None:
        return
    for n in ns[1:]:
        value = n.value
        if value is None:
            return
        result = tracing.run_sympy(sympy.lcm, result, value)
    return Integer(abs(result))


def eval_ModularInverse(k: int, n: int) -> Integer | None:
    try:
        r = tracing.run_sympy(sympy.mod_inverse, k, n)
    except ValueError:
        return
    return Integer(r)


def eval_PowerMod(a, b, m, evaluation: Evaluation) -> Integer | Complex:
    """
    All the various forms of handling modular exponentiation.
    SymPy offers mod_inverse, nth_root_mod, sqrt_mod, and core.power.Pow. Python's
    `pow` is good for large ints.
    """

    if m == 0:
        evaluation.message(
            "PowerMod",
            "divz",
            evaluation.current_expression,
        )
        return

    # b == -1 is handled below.
    if b < 0 and b != -1:
        try:
            a_inverse = int(tracing.run_sympy(sympy.invert, a, m))
        except sympy.polys.polyerrors.NotInvertible:
            evaluation.message("PowerMod", "ninv", from_python(a), from_python(m))
        else:
            # Make `b` positive and invert `a`.
            a = a_inverse
            b = -b

    if isinstance(b, sympy.core.numbers.Half) or b == 0.5:
        # SymPy has a custom routine for square roots using sqrt_mod:
        return from_sympy(tracing.run_sympy(sympy.sqrt_mod, a, m))
    elif 0 < b < 1:
        # If we have an nth root (1/n) we can use sympy.nthroot
        is_unit_fraction = False
        if isinstance(b, sympy.core.numbers.Rational) and b.numerator == 1:
            is_unit_fraction = True
            b_inverse = b.denominator
        elif isinstance(b, float):
            b_inverse = get_unit_inverse(b)
            is_unit_fraction = b_inverse is not None
        if is_unit_fraction:
            return from_sympy(tracing.run_sympy(sympy.nthroot_mod, a, b_inverse, m))
    elif b == -1:
        # SymPy has a custom routine here using mod_inverse:
        try:
            result = tracing.run_sympy(sympy.mod_inverse, a, m)
        except (sympy.polys.polyerrors.NotInvertible, ValueError):
            evaluation.message("PowerMod", "ninv", from_python(a), from_python(m))
        else:
            return from_sympy(result)
    elif all(isinstance(x, int) for x in (a, b, m)) and b >= 1:
        # Standard Modular Exponentiation (b >= 1) using sympy.pow:
        # Use Python's builtin function `pow`.
        # This handles large int's better than SymPy's core.power.Pow:
        return Integer(pow(a, b, m))
    elif b > 1:
        # Standard Modular Exponentiation (b >= 1) using sympy.pow:
        result = tracing.run_sympy(sympy.core.power.Pow, a, b, m)
        return from_sympy(result)
    return None


def eval_Quotient(m, n, d) -> Integer:
    return Integer((m - d) // n)


def gcdex_list(numbers: list[int]) -> (list, int):
    """
    Return the extended GCD's coefficients and cumulative GCD for a list of numbers using
    SymPy's gcdex.
    If the list is empty,bbbbbbb we return [].

    """
    if not numbers:
        return [], 0
    if len(numbers) == 1:
        # Degenerate case.
        return [1], numbers[0]

    # Start with the first element...
    coeffs = [1]
    current_gcd = numbers[0]

    # and then chain through the remaining elements.
    for num in numbers[1:]:
        x, y, current_gcd = tracing.run_sympy(sympy.gcdex, current_gcd, num)
        # Scale all previously found coefficients by x
        coeffs = [c * x for c in coeffs]
        # Append the new coefficient y.
        coeffs.append(y)

    return coeffs, current_gcd


def get_unit_inverse(f: float) -> int | None:
    """
    If `f` is a unit inverse, that is, 1 / some_int,
    then some_int. Otherwise return None
    """
    if f <= 0:
        return None
    return int(inv) if (inv := 1.0 / f) else None
