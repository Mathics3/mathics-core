"""
Evaluation functions for built-in Hypergeometric functions
"""

from typing import Sequence, Tuple, cast

import mpmath
import sympy

import mathics.eval.tracing as tracing
from mathics.core.atoms import Complex, Integer1, MachineReal1, Number
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

    # SymPy returns E ^ z for Hypergeometric1F1[0,0,z], but
    # WMA gives 1.  Therefore, we add the below code to give the WMA
    # behavior. If SymPy switches, this code be eliminated.
    if hasattr(a, "is_zero") and a.is_zero:
        return (
            MachineReal1
            if a.is_machine_precision()
            or hasattr(z, "machine_precision")
            and z.is_machine_precision()
            else Integer1
        )

    args = (a, b, z)
    sympy_args, all_numeric = to_sympy_with_classification(args)
    sympy_result = tracing.run_sympy(
        sympy.hyper, [sympy_args[0]], [sympy_args[1]], sympy_args[2]
    )
    expanded_result = sympy.hyperexpand(sympy_result)

    # Oddly, SymPy expansion sometimes doesn't work when complex arguments are given.
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

    Uses mpmath hyp2f1 if all args are numeric. Otherwise,
    we use SymPy's hyper and expand the symbolic result.
    """

    args = (a, b, c, z)
    sympy_args, all_numeric = to_sympy_with_classification(args)
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
        return run_sympy_hyper_and_expand(
            [sympy_args[0], sympy_args[1]], [sympy_args[2]], sympy_args[3]
        )


def eval_HypergeometricPQF(a, b, z):
    "HypergeometricPFQ[a_, b_, z_]"

    # SymPy returns E for HypergeometricPFQ[{0},{0},Number], but
    # WMA gives 1.  Therefore, we add the below code to give the WMA
    # behavior. If SymPy switches, this code be eliminated.
    if (
        len(a.elements) > 0
        and hasattr(a[0], "is_zero")
        and a[0].is_zero
        and isinstance(z, Number)
    ):
        return MachineReal1 if a[0].is_machine_precision() else Integer1

    # FIXME: This isn't complete. If parameters "a" or "b" contain MachineReal
    # numbers then the results should be MachineReal as well.
    if z.is_machine_precision():
        return eval_N_HypergeometricPQF(a, b, z)

    try:
        a_sympy = [e.to_sympy() for e in a]
        b_sympy = [e.to_sympy() for e in b]
        return run_sympy_hyper_and_expand(a_sympy, b_sympy, z.to_sympy())
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


def eval_MeijerG(a, b, z):
    """
    Use sympy.meijerg to compute MeijerG(a, b, z)
    """
    try:
        a_sympy = [[e2.to_sympy() for e2 in e1] for e1 in a]
        b_sympy = [[e2.to_sympy() for e2 in e1] for e1 in b]
        result_sympy = tracing.run_sympy(sympy.meijerg, a_sympy, b_sympy, z.to_sympy())
        # For now, we don't allow simplification and conversion
        # to other functions like Bessel, because this can introduce
        # SymPy's exp_polar() function for which we don't have a
        # Mathics3 equivalent for yet.
        # return from_sympy(sympy.hyperexpand(result_sympy))
        return from_sympy(result_sympy)
    except Exception:
        return None


# FIXME: ADDING THIS causes test/doc/test_common.py to fail! It reports that Hypergeometric has been included more than once
# Weird!

# def eval_N_MeijerG(a, b, z):
#     "N[MeijerG[a_, b_, z_], prec_]"
#     try:
#         result_mpmath = tracing.run_mpmath(
#             mpmath.meijerg, a.to_python(), b.to_python(), z.to_python()
#         )
#         return from_mpmath(result_mpmath)
#     except ZeroDivisionError:
#         return SymbolComplexInfinity
#     except Exception:
#         return None


def run_sympy_hyper_and_expand(a, b, z):
    """Ruy SymPy's hyper function and expand the result."""
    sympy_result = tracing.run_sympy(sympy.hyper, a, b, z)
    result = sympy.hyperexpand(sympy_result)
    return from_sympy(result)


def to_sympy_with_classification(args: tuple) -> Tuple[list, bool]:
    """Converts `args` to its corresponding SymPy form.  However, if
    all elements of args are numeric, then we detect and report that.
    We do this so that the caller can decide whether to use mpmath if
    SymPy fails. One might expect SymPy to do this automatically, but
    it doesn't catch all opportunites.
    """
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
    return sympy_args, all_numeric
