"""
Mathics3 builtins from mathics.builtin.intfns.divlike
"""

from typing import Optional, Union

import sympy

import mathics.eval.tracing as tracing
from mathics.core.atoms import Complex, Integer, Integer0
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluation import Evaluation


def get_unit_inverse(f: float) -> Optional[int]:
    """
    If `f` is a unit inverse, that is, 1 / some_int,
    then some_int. Otherwise return None
    """
    if f <= 0:
        return None
    return int(inv) if (inv := 1.0 / f) else None


def eval_GCD(ns: tuple) -> Optional[Integer]:
    if len(ns) == 0:
        return Integer0
    if (result := ns[0].value) is None:
        return
    for n in ns[1:]:
        value = n.value
        if value is None:
            return
        result = tracing.run_sympy(sympy.gcd, result, value)
    return Integer(result)


def eval_LCM(ns: tuple) -> Optional[Integer]:
    if len(ns) == 0:
        return Integer0
    if (result := ns[0].value) is None:
        return
    for n in ns[1:]:
        value = n.value
        if value is None:
            return
        result = tracing.run_sympy(sympy.lcm, result, value)
    return Integer(result)


def eval_ModularInverse(k: int, n: int) -> Optional[Integer]:
    try:
        r = tracing.run_sympy(sympy.mod_inverse, k, n)
    except ValueError:
        return
    return Integer(r)


def eval_PowerMod(a, b, m, evaluation: Evaluation) -> Union[Integer, Complex]:
    """
    All the variaous forms of handling module exponentiation.
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
        # this handles large int's better than SymPy's core.power.Pow:
        return Integer(pow(a, b, m))
    elif b > 1:
        # Standard Modular Exponentiation (b >= 1) using sympy.pow:
        result = tracing.run_sympy(sympy.core.power.Pow, a, b, m)
        return from_sympy(result)
    return None


def eval_Quotient(m, n, d) -> Integer:
    return Integer((m - d) // n)
