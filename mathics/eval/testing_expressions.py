from typing import Optional, Union

import sympy

from mathics.core.atoms import Complex, Integer, Integer0, Integer1, IntegerM1
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.rules import BasePattern
from mathics.core.symbols import BooleanType, SymbolFalse, SymbolTimes, SymbolTrue
from mathics.core.systemsymbols import SymbolDirectedInfinity, SymbolSparseArray


def do_cmp(x1, x2) -> Optional[int]:
    # don't attempt to compare complex numbers
    for x in (x1, x2):
        # TODO: Send message General::nord
        if isinstance(x, Complex) or (
            x.has_form("DirectedInfinity", 1) and isinstance(x.elements[0], Complex)
        ):
            return None

    s1 = x1.to_sympy()
    if s1 is None:
        return None
    s2 = x2.to_sympy()
    if s2 is None:
        return None

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
        delta = s1 - s2
        if delta.is_zero:
            return 0
        if delta.is_extended_negative:
            return -1
        if delta.is_extended_positive:
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


def expr_max(elements) -> Union[Expression, int]:
    result = Expression(SymbolDirectedInfinity, IntegerM1)
    for element in elements:
        c = do_cmp(element, result)
        if c is not None and c > 0:
            result = element
    return result


def expr_min(elements) -> Union[Expression, int]:
    result = Expression(SymbolDirectedInfinity, Integer1)
    for element in elements:
        c = do_cmp(element, result)
        if c is not None and c < 0:
            result = element
    return result


def is_number(sympy_value) -> bool:
    return hasattr(sympy_value, "is_number") or isinstance(sympy_value, sympy.Float)


def eval_ArrayQ(expr, pattern, test_condition, evaluation: Evaluation) -> BooleanType:
    "Check if expr is an Array which test yields true for each of its elements."

    pattern = BasePattern.create(pattern, evaluation=evaluation)

    dims = [len(expr.get_elements())]  # to ensure an atom is not an array

    def check(level, expr):
        if not expr.has_form("List", None):
            if test_condition is not None:
                test_expr = Expression(test_condition, expr)
                if test_expr.evaluate(evaluation) != SymbolTrue:
                    return False
            level_dim = None
        else:
            level_dim = len(expr.elements)

        if len(dims) > level:
            if dims[level] != level_dim:
                return False
        else:
            dims.append(level_dim)
        if level_dim is not None:
            for element in expr.elements:
                if not check(level + 1, element):
                    return False
        return True

    if not check(0, expr):
        return SymbolFalse

    depth = len(dims) - 1  # None doesn't count
    if not pattern.does_match(Integer(depth), {"evaluation": evaluation}):
        return SymbolFalse

    return SymbolTrue


def eval_SparseArrayQ(expr, pattern, test, evaluation: Evaluation) -> BooleanType:
    "Check if expr is a SparseArray which test yields true for each of its elements."

    if not expr.head.sameQ(SymbolSparseArray):
        return SymbolFalse

    pattern = BasePattern.create(pattern, evaluation=evaluation)
    dims, default_value, rules = expr.elements[1:]
    if not pattern.does_match(Integer(len(dims.elements)), {"evaluation": evaluation}):
        return SymbolFalse

    array_size = Expression(SymbolTimes, *dims.elements).evaluate(evaluation)
    if array_size.value > len(rules.elements):  # expr is not full
        test_expr = Expression(test, default_value)  # test default value
        if test_expr.evaluate(evaluation) != SymbolTrue:
            return SymbolFalse
    for rule in rules.elements:
        test_expr = Expression(test, rule.elements[-1])
        if test_expr.evaluate(evaluation) != SymbolTrue:
            return SymbolFalse

    return SymbolTrue
