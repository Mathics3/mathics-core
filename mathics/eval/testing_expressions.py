"""
Evaluation routines for mathics.builtin.testing_expressions
"""

from collections.abc import Callable, Iterator, Sequence
from typing import Final, Literal, TypeVar

import sympy

from mathics.core.atoms import (
    Complex,
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    Number,
    Rational,
    String,
)
from mathics.core.convert.expression import to_numeric_args
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.number import is_inexact
from mathics.core.rules import BasePattern
from mathics.core.symbols import (
    BooleanType,
    Symbol,
    SymbolFalse,
    SymbolTimes,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolDirectedInfinity,
    SymbolEqual,
    SymbolGreater,
    SymbolGreaterEqual,
    SymbolLess,
    SymbolLessEqual,
    SymbolList,
    SymbolMaxExtraPrecision,
    SymbolSparseArray,
    SymbolUnequal,
)
from mathics.eval.nevaluator import eval_N

T = TypeVar("T")

# An annotation type for any number of Literal argument counts -1, 0, 1.
# In reality we'll have one or two of these, but we use ellipsis anyway.
ComparisonTuple = tuple[Literal[-1, 0, 1], ...]

OPERATOR_TO_ARGUMENT_MAP: Final[dict[Symbol, ComparisonTuple]] = {
    SymbolLess: (-1,),
    SymbolLessEqual: (-1, 0),
    SymbolEqual: (0,),
    SymbolGreaterEqual: (0, 1),
    SymbolGreater: (1,),
    SymbolUnequal: (-1, 1),
}


def do_cmp(x1, x2) -> int | None:
    # Exact numbers compare as Python numbers: going through SymPy (a
    # subtraction and its assumptions) costs more than the whole step of a
    # loop that tests its counter.
    if isinstance(x1, (Integer, Rational)) and isinstance(x2, (Integer, Rational)):
        v1, v2 = x1.value, x2.value
        return 0 if v1 == v2 else (-1 if v1 < v2 else 1)

    # don't attempt to compare complex numbers
    for x in (x1, x2):
        # TODO: Send message General::nord
        if isinstance(x, Complex) or (
            x.has_form(SymbolDirectedInfinity, 1) and isinstance(x.elements[0], Complex)
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
    # SymPy for everything else.
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


def do_cplx_equal(x, y) -> bool | None:
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
            return c == 0
        else:
            c = do_cmp(x.imag, Integer0)
            if c is None:
                return
            if c != 0:
                return False
            c = do_cmp(x.real, y.real)
            if c is None:
                return
            return c == 0
    c = do_cmp(x, y)
    if c is None:
        return None
    return c == 0


def expr_max(elements) -> Expression | int:
    result = Expression(SymbolDirectedInfinity, IntegerM1)
    for element in elements:
        c = do_cmp(element, result)
        if c is not None and c > 0:
            result = element
    return result


def expr_min(elements) -> Expression | int:
    result = Expression(SymbolDirectedInfinity, Integer1)
    for element in elements:
        c = do_cmp(element, result)
        if c is not None and c < 0:
            result = element
    return result


def get_adjacent_pairs(args: Sequence[T]) -> Iterator[tuple[T, T]]:
    """Yield adjacent pairs: args[i], args[i + 1]."""
    for i in range(len(args) - 1):
        yield (args[i], args[i + 1])


def get_gt_pairs(args: Sequence[T]) -> Iterator[tuple[T, T]]:
    """Yield all pairs, args[i, j] where 0 <= j < i < len(args)"""
    for i in range(len(args)):
        for j in range(i):
            yield (args[i], args[j])


def is_number(sympy_value) -> bool:
    return hasattr(sympy_value, "is_number") or isinstance(sympy_value, sympy.Float)


def eval_ArrayQ(expr, pattern, test_condition, evaluation: Evaluation) -> BooleanType:
    "Check if expr is an Array which test yields true for each of its elements."

    pattern = BasePattern.create(pattern, evaluation=evaluation)

    dims = [len(expr.get_elements())]  # to ensure an atom is not an array

    def check(level, expr):
        if not expr.has_form(SymbolList, None):
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


def eval_comparison_operator(
    symbol: Symbol, elements, evaluation: Evaluation
) -> BooleanType | None:
    elements_sequence = elements.get_sequence()
    if len(elements_sequence) <= 1:
        return SymbolTrue

    elements = numerify_args(elements, evaluation)
    wanted = OPERATOR_TO_ARGUMENT_MAP[symbol]
    if isinstance(elements[-1], String):
        return None

    for i in range(len(elements) - 1):
        x = elements[i]
        if isinstance(x, String):
            return None
        y = elements[i + 1]
        c = do_cmp(x, y)
        if c is None:
            return None
        if c not in wanted:
            return SymbolFalse
    return SymbolTrue


def eval_equality_operator(
    symbol: Symbol,
    elements,
    evaluation: Evaluation,
    *,
    eval_other: Callable | None = None,
    operator_sense: Callable | None = None,
) -> BooleanType | None:
    """
    Standalone equality/inequality helper.

    The symbol is passed explicitly so this function does not depend on a
    particular _EqualityOperator instance. Instance-specific behavior is
    supplied through the optional hooks when needed.
    """
    elements_sequence = elements.get_sequence()
    n = len(elements_sequence)
    if n <= 1:
        return SymbolTrue

    if operator_sense is None:
        operator_sense = bool

    if not all(
        isinstance(arg, Number) and not arg.is_inexact for arg in elements_sequence
    ):
        if eval_other is not None:
            return eval_other(elements, evaluation)
        return SymbolTrue

    args = numerify_args(elements, evaluation)
    for x, y in get_adjacent_pairs(args):
        c = do_cplx_equal(x, y)
        if c is None:
            return None
        if not operator_sense(c):
            return SymbolFalse
    return SymbolTrue


def numerify_args(elements, evaluation: Evaluation) -> list | tuple:
    """Process elements into a tuple or list for comparison."""
    element_sequence = elements.get_sequence()
    all_numeric = all(is_inexact(element) for element in element_sequence)

    if all_numeric and any(not isinstance(item, Number) for item in element_sequence):
        # All elements are numeric, but they are not all numbers.
        # Here, apply N[] (or eval_N()).
        n_items = []
        for item in element_sequence:
            if not isinstance(item, Number):
                item = eval_N(item, evaluation, SymbolMaxExtraPrecision)
            n_items.append(item)
        return n_items

    # For mixed values, rely on to_numeric_args.
    return to_numeric_args(elements, evaluation)
