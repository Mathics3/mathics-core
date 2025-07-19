# -*- coding: utf-8 -*-

"""low-level Functions involving Matrices and Arrays"""

from typing import Optional

from sympy import Array, Matrix


def matrix_data(m):
    if not m.has_form("List", None):
        return None
    if all(element.has_form("List", None) for element in m.elements):
        result = [[item.to_sympy() for item in row.elements] for row in m.elements]
        if not any(None in row for row in result):
            return result
    elif not any(element.has_form("List", None) for element in m.elements):
        result = [item.to_sympy() for item in m.elements]
        if None not in result:
            return result
    return None


def to_sympy_array(m) -> Optional[Array]:
    """Converts a Mathics3 List of nested lists into a SymPy Array.
    If there is an problem in conversion return None.
    """
    if not m.has_form("List", None):
        return None
    if all(element.has_form("List", None) for element in m.elements):
        if m.is_literal and m.value is not None:
            return Array(m.value)
        result = [[item.to_sympy() for item in row.elements] for row in m.elements]
        if not any(None in row for row in result):
            return Array(result)
    elif not any(element.has_form("List", None) for element in m.elements):
        result = [item.to_sympy() for item in m.elements]
        if None not in result:
            return Array(result)
    return None


def to_sympy_matrix(m) -> Optional[Matrix]:
    """
    Converts a 2D Mathics3 List of Lists into a SymPy Matrix.
    (Matrices in SymPy are always 2D.)
    If there is an problem in conversion return None.
    """
    if not m.has_form("List", None):
        return None
    if all(element.has_form("List", None) for element in m.elements):
        result = [[item.to_sympy() for item in row.elements] for row in m.elements]
        if not any(None in row for row in result):
            return Matrix(result)
    elif not any(element.has_form("List", None) for element in m.elements):
        result = [item.to_sympy() for item in m.elements]
        if None not in result:
            return Matrix(result)
    return None
