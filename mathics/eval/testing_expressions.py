from typing import Optional

import sympy

from mathics.core.atoms import Complex, Integer0, Integer1, IntegerM1
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolDirectedInfinity


def cmp(a, b) -> int:
    "Returns 0 if a == b, -1 if a < b and 1 if a > b"
    return (a > b) - (a < b)


def do_cmp(x1, x2) -> Optional[int]:

    # don't attempt to compare complex numbers
    for x in (x1, x2):
        # TODO: Send message General::nord
        if isinstance(x, Complex) or (
            x.has_form("DirectedInfinity", 1) and isinstance(x.elements[0], Complex)
        ):
            return None

    s1 = x1.to_sympy()
    s2 = x2.to_sympy()

    # Use internal comparisons only for Real which is uses
    # WL's interpretation of equal (which allows for slop
    # in the least significant digit of precision), and use
    # use sympy for everything else
    if s1.is_Float and s2.is_Float:
        if x1 == x2:
            return 0
        if x1 < x2:
            return -1
        return 1

    # we don't want to compare anything that
    # cannot be represented as a numeric value
    if s1.is_number and s2.is_number:
        if s1 == s2:
            return 0
        if s1 < s2:
            return -1
        return 1

    return None


def do_cplx_equal(x, y) -> Optional[int]:
    if isinstance(y, Complex):
        x, y = y, x
    if isinstance(x, Complex):
        if isinstance(y, Complex):
            c = do_cmp(x.real, y.real)
            if c is None:
                return
            if c != 0:
                return False
            c = do_cmp(x.imag, y.imag)
            if c is None:
                return
            if c != 0:
                return False
            else:
                return True
        else:
            c = do_cmp(x.imag, Integer0)
            if c is None:
                return
            if c != 0:
                return False
            c = do_cmp(x.real, y.real)
            if c is None:
                return
            if c != 0:
                return False
            else:
                return True
    c = do_cmp(x, y)
    if c is None:
        return None
    return c == 0


def expr_max(elements):
    result = Expression(SymbolDirectedInfinity, IntegerM1)
    for element in elements:
        c = do_cmp(element, result)
        if c > 0:
            result = element
    return result


def expr_min(elements):
    result = Expression(SymbolDirectedInfinity, Integer1)
    for element in elements:
        c = do_cmp(element, result)
        if c < 0:
            result = element
    return result


def is_number(sympy_value) -> bool:
    return hasattr(sympy_value, "is_number") or isinstance(sympy_value, sympy.Float)
