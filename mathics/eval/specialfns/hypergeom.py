"""
Evaluation functions for built-in Hypergeometric functions
"""

from typing import Sequence, cast

import mpmath
import sympy

import mathics.eval.tracing as tracing
from mathics.core.atoms import Complex, Number
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.number import RECONSTRUCT_MACHINE_PRECISION_DIGITS, dps, min_prec
from mathics.core.systemsymbols import SymbolComplexInfinity
from mathics.eval.arithmetic import eval_mpmath_function


def eval_Hypergeometric1F1(a, b, z):
    """Hypergeometric2F1[a_, b_, z_]

    We use SymPy's hyper and expand the symbolic result.
    But if that fails to expand and all arugments are numeric, use mpmath hyp1f1.

    We prefer SymPy because it preserves constants like E whereas mpmath will
    convert E to a precisioned number.
    """

    args = (a, b, z)

    sympy_args = []
    all_numeric = True
    for arg in args:
        if isinstance(arg, Number):
            # FIXME: in the future, .value
            # should work on Complex numbers.
            if isinstance(arg, Complex):
                sympy_arg = arg.to_python()
            else:
                sympy_arg = arg.value
        else:
            sympy_arg = arg.to_sympy()
            all_numeric = False

        sympy_args.append(sympy_arg)

    sympy_result = tracing.run_sympy(
        sympy.hyper, [sympy_args[0]], [sympy_args[1]], sympy_args[2]
    )
    expanded_result = sympy.hyperexpand(sympy_result)

    # Oddly, expansion sometimes doesn't work for when complex arguments are given.
    # However mpmath can handle this.
    # I imagine at some point in the future this will be fixed.
    if isinstance(expanded_result, sympy.hyper) and all_numeric:
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
            mpmath.hyp1f1, *cast(Sequence[Number], args), prec=prec
        )
    else:
        return from_sympy(expanded_result)


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
            if isinstance(arg, Complex):
                sympy_arg = arg.to_python()
            else:
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
        return run_sympy_hyper(
            [sympy_args[0], sympy_args[1]], [sympy_args[2]], sympy_args[3]
        )


def eval_HypergeometricPQF(a, b, z):
    "HypergeometricPFQ[a_, b_, z_]"
    try:
        a_sympy = [e.to_sympy() for e in a]
        b_sympy = [e.to_sympy() for e in b]
        return run_sympy_hyper(a_sympy, b_sympy, z.to_sympy())
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


def run_sympy_hyper(a, b, z):
    sympy_result = tracing.run_sympy(sympy.hyper, a, b, z)
    result = sympy.hyperexpand(sympy_result)
    return from_sympy(result)
