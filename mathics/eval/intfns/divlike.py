"""
Mathics3 builtins from mathics.builtin.intfns.divlike
"""

from typing import Optional

import sympy

import mathics.eval.tracing as tracing
from mathics.core.atoms import Integer, Integer0
from mathics.core.evaluation import Evaluation


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


def eval_PowerMod(a, b, m, evaluation: Evaluation) -> Integer:
    """
    All the variaous forms of handling module exponentiation.
    SymPy offers mod_inverse, nth_root_mod, sqrt_mod, and core.power.Pow. Python's
    `pow` is good for large ints.
    """

    if m == 0:
        evaluation.message("PowerMod", "divz", Integer0)
        return

    try:
        a_inverse = int(tracing.run_sympy(sympy.invert, a, m))
    except sympy.polys.polyerrors.NotInvertible:
        evaluation.message("PowerMod", "ninv", Integer(a), Integer(m))
        return

    # b == -1 is handled below.
    if b < 0 and b != -1:
        # Make `b` positive and invert `a`.
        a = a_inverse
        b = -b

    if isinstance(b, sympy.core.numbers.Half) or b == 0.5:
        # SymPy has a custom routine for square roots using sqrt_mod:
        return Integer(tracing.run_sympy(sympy.sqrt_mod, a, m))
    elif 0 < b < 1:
        # If we have an nth root (1/n) we can use sympy.nthroot
        if isinstance(b, sympy.core.numbers.Rational) and b.numerator == 1:
            return Integer(tracing.run_sympy(sympy.nthroot_mod, a, b.denominator, m))
    elif b == -1:
        # SymPy has a custom routine here using mod_inverse:
        try:
            result = tracing.run_sympy(sympy.mod_inverse, a, m)
        except sympy.polys.polyerrors.NotInvertible:
            evaluation.message("PowerMod", "ninv", Integer(a), Integer(m))
        return Integer(result)
    elif all(isinstance(x, int) for x in (a, b, m)) and b >= 1:
        # Standard Modular Exponentiation (b >= 1) using sympy.pow:
        # Use Python's builtin function `pow`.
        # this handles large int's better than SymPy's core.power.Pow:
        return Integer(pow(a, b, m))
    elif b > 1:
        # Standard Modular Exponentiation (b >= 1) using sympy.pow:
        result = tracing.run_sympy(sympy.core.power.Pow, a, b, m)
        return Integer(result)


def eval_Quotient(m, n, d) -> Integer:
    return Integer((m - d) // n)
