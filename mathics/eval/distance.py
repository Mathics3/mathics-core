"""
Distance-related evaluation functions and exception classes
"""

from mathics.core.atoms import Complex, Integer, Integer0, Real
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import from_sympy, to_sympy_matrix


class IllegalDataPoint(Exception):
    pass


class IllegalDistance(Exception):
    def __init__(self, distance):
        self.distance = distance


def dist_repr(p) -> tuple:
    dist_p = repr_p = None
    if p.has_form("Rule", 2):
        if all(q.get_head_name() == "System`List" for q in p.elements):
            dist_p, repr_p = (q.elements for q in p.elements)
        elif (
            p.elements[0].get_head_name() == "System`List"
            and p.elements[1].get_name() == "System`Automatic"
        ):
            dist_p = p.elements[0].elements
            repr_p = [Integer(i + 1) for i in range(len(dist_p))]
    elif p.get_head_name() == "System`List":
        if all(q.get_head_name() == "System`Rule" for q in p.elements):
            dist_p, repr_p = ([q.elements[i] for q in p.elements] for i in range(2))
        else:
            dist_p = repr_p = p.elements
    return dist_p, repr_p


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
        distance = 1 - u_val * v_val.conjugate() / (abs(u_val) * abs(v_val))
        return from_python(distance)

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


def to_real_distance(d):
    if not isinstance(d, (Real, Integer)):
        raise IllegalDistance(d)

    mpd = d.to_mpmath()
    if mpd is None or mpd < 0:
        raise IllegalDistance(d)

    return mpd
