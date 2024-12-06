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
        u_val = u.to_python()
        v_val = v.to_python()
        u_abs = eval_Abs(u)
        if u_abs is None:
            return
        v_abs = eval_Abs(v)
        if v_abs is None:
            return
        distance = 1 - u_val * v_val.conjugate() / (u_abs.to_sympy() * v_abs.to_sympy())

        # If the input arguments were Integers, preserve that in the result
        if isinstance(u_val, int) and isinstance(v_val, int):
            try:
                if distance == int(distance):
                    distance = int(distance)
            except Exception:
                pass
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
