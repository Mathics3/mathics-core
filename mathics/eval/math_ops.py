from typing import Callable, Optional

from mathics.core.atoms import Integer, Real, String
from mathics.core.convert.sympy import from_sympy, to_sympy_matrix
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol


def eval_Norm(
    m: Expression, show_message: Optional[Callable] = None
) -> Optional[Expression]:
    """
    Norm[m] evaluation function - the 2-norm of matrix m
    """
    sympy_m = to_sympy_matrix(m)
    if sympy_m is None:
        if show_message:
            show_message("Norm", "nvm")
        return

    return from_sympy(sympy_m.norm())


def eval_Norm_p(
    m: Expression, p: Expression, show_message: Optional[Callable] = None
) -> Optional[Expression]:
    """
    Norm[m, p] evaluation function - the p-norm of matrix m.
    """
    if isinstance(p, Symbol):
        sympy_p = p.to_sympy()
    elif isinstance(p, String):
        sympy_p = p.value
        if sympy_p == "Frobenius":
            sympy_p = "fro"
    elif isinstance(p, (Real, Integer)) and p.to_python() >= 1:
        sympy_p = p.to_sympy()
    else:
        if show_message:
            show_message("Norm", "ptype", p)
        return

    if sympy_p is None:
        return
    matrix = to_sympy_matrix(m)

    if matrix is None:
        if show_message:
            show_message("Norm", "nvm")
        return
    if len(matrix) == 0:
        return

    try:
        res = matrix.norm(sympy_p)
    except NotImplementedError:
        if show_message:
            show_message("Norm", "normnotimplemented")
        return

    return from_sympy(res)
