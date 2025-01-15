# -*- coding: utf-8 -*-

"low-level Functions involving matrices"


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
