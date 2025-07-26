"""
Evaluation functions for built-in Hypergeometric functions
"""

from typing import Sequence, cast

import mpmath
import sympy

import mathics.eval.tracing as tracing
from mathics.core.atoms import Number
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.number import RECONSTRUCT_MACHINE_PRECISION_DIGITS, dps, min_prec
from mathics.core.systemsymbols import SymbolComplexInfinity
from mathics.eval.arithmetic import eval_mpmath_function


def eval_Hypergeometric2F1(a, b, c, z):
    """Hypergeometric2F1[a_, b_, c_, z_]

    Uses mpmath hyp2f1 if all args are numeric, otherwise,
    we use sympy's hyper and expand the symbolic result.
    """

    args = (a, b, c, z)
    sympy_args = []
    all_numeric = True
    for arg in args:
        if isinstance(arg, Number):
            sympy_arg = arg.value
        else:
            sympy_arg = arg.to_sympy()
            all_numeric = False

        sympy_args.append(sympy_arg)

    if all_numeric:
        args = cast(Sequence[Number], args)

        if any(arg.is_machine_precision() for arg in args):
            prec = None
        else:
            prec = min_prec(*args)
            if prec is None:
                prec = RECONSTRUCT_MACHINE_PRECISION_DIGITS
            d = dps(prec)
            args = tuple([arg.round(d) for arg in args])

        return eval_mpmath_function(
            mpmath.hyp2f1, *cast(Sequence[Number], args), prec=prec
        )
    else:
        sympy_result = tracing.run_sympy(
            sympy.hyper, [sympy_args[0], sympy_args[1]], [sympy_args[2]], sympy_args[3]
        )
        return from_sympy(sympy.hyperexpand(sympy_result))


def eval_HypergeometricPQF(a, b, z):
    "HypergeometricPFQ[a_, b_, z_]"
    try:
        a_sympy = [e.to_sympy() for e in a]
        b_sympy = [e.to_sympy() for e in b]
        result_sympy = tracing.run_sympy(sympy.hyper, a_sympy, b_sympy, z.to_sympy())
        return from_sympy(result_sympy)
    except Exception:
        return None


# FIXME, this should take a "prec" parameter?
def eval_N_HypergeometricPQF(a, b, z):
    "N[HypergeometricPFQ[a_, b_, z_]]"
    try:
        result_mpmath = tracing.run_mpmath(
            mpmath.hyper, a.to_python(), b.to_python(), z.to_python()
        )
        return from_mpmath(result_mpmath)
    except ZeroDivisionError:
        return SymbolComplexInfinity
    except Exception:
        return None
