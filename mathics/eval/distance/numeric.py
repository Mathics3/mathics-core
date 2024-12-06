from sympy.core.power import Mul, Pow

from mathics.core.atoms import Complex, Integer, Integer0, Real
from mathics.core.convert.sympy import from_sympy, to_sympy_matrix
from mathics.eval.arithmetic import eval_Abs


def eval_CosineDistance(u, v):
    "CosineDistance[u_, v_]"

    # We follow pretty much what is done in Symja in ClusteringFunctions.java for this:
    # https://github.com/axkr/symja_android_library/blob/master/symja_android_library/matheclipse-core/src/main/java/org/matheclipse/core/builtin/ClusteringFunctions.java#L377-L386
    # Some extensions for degenerate cases have been added.

    # Handle some degenerate cases
    if isinstance(u, (Complex, Integer, Real)) and isinstance(
        v, (Complex, Integer, Real)
    ):
        u_abs = eval_Abs(u)
        if u_abs is None:
            return
        v_abs = eval_Abs(v)
        if v_abs is None:
            return

        # Do the following, but using SymPy expressions:
        #   distance = 1 - (u * v.conjugate()) / (abs(u) * abs(v))
        numerator = Mul(u.to_sympy(), v.to_sympy().conjugate())
        divisor_product = Mul(u_abs.to_sympy(), v_abs.to_sympy())
        distance = 1 - numerator * Pow(divisor_product, -1)
        return from_sympy(distance)

    sym_u = to_sympy_matrix(u)
    if sym_u is None:
        return
    sym_v = to_sympy_matrix(v)
    if sym_v is None:
        return
    u_norm = sym_u.norm()
    if u_norm == 0:
        return Integer0
    v_norm = sym_v.norm()
    if v_norm == 0:
        return Integer0

    return from_sympy(1 - sym_u.dot(sym_v.conjugate()) / (u_norm * v_norm))
