"""
Linear algebra over the integers modulo a prime, used for the ``Modulus``
option of RowReduce, NullSpace, MatrixRank, Inverse and LinearSolve.

Matrices are plain Python lists of lists of ``int`` in the range 0..p-1.
"""

from typing import List, Optional, Tuple

import sympy

from mathics.core.atoms import Integer, Rational
from mathics.core.element import BaseElement
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolList

ModMatrix = List[List[int]]


def get_prime_modulus(modulus: Optional[BaseElement]) -> Optional[int]:
    """Return the value of a ``Modulus`` option.

    0 means ordinary arithmetic. None means the value is not a prime
    or 0, and is not supported.
    """
    if not isinstance(modulus, Integer):
        return None
    p = modulus.value
    if p == 0 or (p > 1 and sympy.isprime(p)):
        return p
    return None


def element_mod(element: BaseElement, p: int) -> Optional[int]:
    """Reduce an Integer or a Rational modulo p, or return None."""
    if isinstance(element, Integer):
        return element.value % p
    if isinstance(element, Rational):
        num, den = (int(x) for x in element.value.as_numer_denom())
        if den % p == 0:
            return None
        return num * pow(den, -1, p) % p
    return None


def vector_mod(vector: BaseElement, p: int) -> Optional[List[int]]:
    """Convert a List of rational numbers into a list of residues mod p."""
    if not vector.has_form(SymbolList, None):
        return None
    result = []
    for element in vector.elements:
        value = element_mod(element, p)
        if value is None:
            return None
        result.append(value)
    return result


def matrix_mod(matrix: BaseElement, p: int) -> Optional[ModMatrix]:
    """Convert a non-empty rectangular matrix of rational numbers into
    residues mod p, or return None."""
    if not matrix.has_form(SymbolList, None) or len(matrix.elements) == 0:
        return None
    rows = []
    for row in matrix.elements:
        values = vector_mod(row, p)
        if not values:
            return None
        rows.append(values)
    if any(len(row) != len(rows[0]) for row in rows):
        return None
    return rows


def to_mathics_matrix(rows: ModMatrix) -> ListExpression:
    return ListExpression(*(ListExpression(*(Integer(x) for x in row)) for row in rows))


def rref_mod(rows: ModMatrix, p: int) -> Tuple[ModMatrix, List[int]]:
    """Return the reduced row echelon form of ``rows`` mod p and the
    list of its pivot columns. ``rows`` is not modified."""
    rows = [list(row) for row in rows]
    nrows = len(rows)
    ncols = len(rows[0]) if rows else 0
    pivots: List[int] = []
    r = 0
    for c in range(ncols):
        if r == nrows:
            break
        pivot = next((i for i in range(r, nrows) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        inverse = pow(rows[r][c], -1, p)
        if inverse != 1:
            rows[r] = [x * inverse % p for x in rows[r]]
        pivot_row = rows[r]
        for i in range(nrows):
            factor = rows[i][c]
            if i != r and factor:
                rows[i] = [(x - factor * y) % p for x, y in zip(rows[i], pivot_row)]
        pivots.append(c)
        r += 1
    return rows, pivots


def nullspace_mod(rows: ModMatrix, p: int) -> ModMatrix:
    """Return a basis of the null space mod p.

    There is one vector for each column without a pivot; it has 1 there
    and 0 in the other columns without a pivot. As in WMA, the vectors
    come in decreasing order of that column.
    """
    reduced, pivots = rref_mod(rows, p)
    ncols = len(rows[0])
    pivot_set = set(pivots)
    basis = []
    for free in reversed(range(ncols)):
        if free in pivot_set:
            continue
        vector = [0] * ncols
        vector[free] = 1
        for i, c in enumerate(pivots):
            vector[c] = -reduced[i][free] % p
        basis.append(vector)
    return basis


def inverse_mod(rows: ModMatrix, p: int) -> Optional[ModMatrix]:
    """Return the inverse of a square matrix mod p, or None if it is
    singular mod p."""
    n = len(rows)
    augmented = [
        row + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(rows)
    ]
    reduced, pivots = rref_mod(augmented, p)
    if pivots[:n] != list(range(n)):
        return None
    return [row[n:] for row in reduced]


def linear_solve_mod(rows: ModMatrix, b: List[int], p: int) -> Optional[List[int]]:
    """Return one solution x of ``rows . x == b`` mod p, with 0 for the
    free variables, or None if there is no solution."""
    ncols = len(rows[0])
    augmented = [row + [v] for row, v in zip(rows, b)]
    reduced, pivots = rref_mod(augmented, p)
    if pivots and pivots[-1] == ncols:
        return None
    solution = [0] * ncols
    for i, c in enumerate(pivots):
        solution[c] = reduced[i][ncols]
    return solution
