"""
Distance-related evaluation functions and exception classes
"""
from mathics.core.atoms import Integer, Real


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


def to_real_distance(d):
    if not isinstance(d, (Real, Integer)):
        raise IllegalDistance(d)

    mpd = d.to_mpmath()
    if mpd is None or mpd < 0:
        raise IllegalDistance(d)

    return mpd
