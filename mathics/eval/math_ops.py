from typing import Optional

from mathics.core.atoms import Integer, Real, String
from mathics.core.convert.sympy import from_sympy, to_sympy_matrix
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol


def eval_2_Norm(m: Expression, evaluation: Evaluation) -> Optional[Expression]:
    """
    2-Norm[] evaluation function
    """
    sympy_m = to_sympy_matrix(m)
    if sympy_m is None:
        evaluation.message("Norm", "nvm")
        return

    return from_sympy(sympy_m.norm())


def eval_p_norm(
    m: Expression, p: Expression, evaluation: Evaluation
) -> Optional[Expression]:
    """
    p2-Norm[] evaluation function
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
        evaluation.message("Norm", "ptype", p)
        return

    if sympy_p is None:
        return
    matrix = to_sympy_matrix(m)

    if matrix is None:
        evaluation.message("Norm", "nvm")
        return
    if len(matrix) == 0:
        return

    try:
        res = matrix.norm(sympy_p)
    except NotImplementedError:
        evaluation.message("Norm", "normnotimplemented")
        return

    return from_sympy(res)
