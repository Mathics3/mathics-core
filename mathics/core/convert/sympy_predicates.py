"""
Converts expressions from Mathics3 expressions to SymPy Predicates.
These are used in the built-in functions Refine and Assumptions.
"""

from typing import Final

from sympy import And, Ne, Not, Or, Q
from sympy.assumptions.assume import AppliedPredicate
from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.relational import (
    Equality,
    GreaterThan,
    LessThan,
    Relational,
    StrictGreaterThan,
    StrictLessThan,
)
from sympy.sets.contains import Contains
from sympy.sets.fancysets import Complexes, Integers, Rationals, Reals

from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolElement,
    SymbolEqual,
    SymbolGreater,
    SymbolGreaterEqual,
    SymbolLess,
    SymbolLessEqual,
    SymbolNot,
    SymbolOr,
)

SYMPY_FALSE_PREDICATE: Final[AppliedPredicate] = Q.is_true(False)
SYMPY_TRUE_PREDICATE: Final[AppliedPredicate] = Q.is_true(True)


def sympy_expr_to_predicate(sympy_expr):
    """
    Converts SymPy expressions (relational, boolean, or predicates)
    into canonical SymPy Q AppliedPredicates for SymPy 1.14.0+.
    Note: Newer SymPy can use sask() and to_predicate()
    """
    # Already an AppliedPredicate (e.g., Q.positive(x)) or Boolean
    if isinstance(sympy_expr, AppliedPredicate):
        return sympy_expr

    # Boolean compound trees (And, Or, Not)
    if (
        isinstance(sympy_expr, Not)
        or hasattr(sympy_expr, "is_Not")
        and sympy_expr.is_Not
    ):
        return Not(sympy_expr_to_predicate(sympy_expr.args[0]))
    if (
        isinstance(sympy_expr, And)
        or hasattr(sympy_expr, "is_And")
        and sympy_expr.is_And
    ):
        return And(*[sympy_expr_to_predicate(arg) for arg in sympy_expr.args])
    if isinstance(sympy_expr, Or) or hasattr(sympy_expr, "is_Or") and sympy_expr.is_Or:
        return Or(*[sympy_expr_to_predicate(arg) for arg in sympy_expr.args])

    #  Domain membership checks (Element(x, Reals), Contains(x, Integers), etc.)
    # In SymPy, Element(x, S) constructs a Contains(x, S) object
    if isinstance(sympy_expr, Contains) or type(sympy_expr).__name__ in (
        "Element",
        "Contains",
    ):
        element, domain = sympy_expr.args[0], sympy_expr.args[1]

        # Map standard sets to their corresponding SymPy Q domain predicates.
        if hasattr(domain, "name") and domain.name in ("Booleans", "Boolean"):
            return Q.boolean(element)
        if isinstance(domain, Complexes) or (
            hasattr(domain, "name") and domain.name == "Complexes"
        ):
            return Q.complex(element)
        elif isinstance(domain, Integers) or (
            hasattr(domain, "name") and domain.name == "Integers"
        ):
            return Q.integer(element)
        elif isinstance(domain, Rationals) or (
            hasattr(domain, "name") and domain.name == "Rationals"
        ):
            return Q.rational(element)
        elif isinstance(domain, Reals) or (
            hasattr(domain, "name") and domain.name == "Reals"
        ):
            return Q.real(element)
        else:
            raise RuntimeError(f"Domain {domain} is not valid")

    # Relational expressions, canonicalizing the relation direction.
    if isinstance(sympy_expr, Relational):
        # Handle where the rhs is zero. For example: x > 0 -> Q.positive(x)
        # Handle zero-rhs explicit cases directly to preserve original symbol orientation
        if sympy_expr.rhs == 0:
            if isinstance(sympy_expr, StrictGreaterThan):
                return Q.positive(sympy_expr.lhs)
            elif isinstance(sympy_expr, StrictLessThan):
                return Q.negative(sympy_expr.lhs)
            elif isinstance(sympy_expr, GreaterThan):
                return Q.nonnegative(sympy_expr.lhs)
            elif isinstance(sympy_expr, LessThan):
                return Q.nonpositive(sympy_expr.lhs)
            elif isinstance(sympy_expr, Equality):
                return Q.zero(sympy_expr.lhs)
            elif isinstance(sympy_expr, Ne):
                return Q.nonzero(sympy_expr.lhs)

        # Handle where the lhs is zero. For example: 0 < x is the same as x > 0 -> Q.positive(x)
        if sympy_expr.lhs == 0:
            if isinstance(sympy_expr, StrictGreaterThan):  # 0 > x -> x < 0
                return Q.negative(sympy_expr.rhs)
            elif isinstance(sympy_expr, StrictLessThan):  # 0 < x -> x > 0
                return Q.positive(sympy_expr.rhs)
            elif isinstance(sympy_expr, GreaterThan):  # 0 >= x -> x <= 0
                return Q.nonpositive(sympy_expr.rhs)
            elif isinstance(sympy_expr, LessThan):  # 0 <= x -> x >= 0
                return Q.nonnegative(sympy_expr.rhs)
            elif isinstance(sympy_expr, Equality):
                return Q.zero(sympy_expr.rhs)
            elif isinstance(sympy_expr, Ne):
                return Q.nonzero(sympy_expr.rhs)

        lhs, rhs = sympy_expr.lhs, sympy_expr.rhs
        # Construct negated terms explicitly using Mul(-1, ...) to make type checking happy.
        neg_rhs = Mul(-1, rhs)
        neg_lhs = Mul(-1, lhs)

        # Non-zero general cases (algebraic reduction).
        if isinstance(sympy_expr, StrictGreaterThan):  # lhs > rhs -> lhs - rhs > 0
            return Q.positive(Add(lhs, neg_rhs))
        elif isinstance(sympy_expr, StrictLessThan):  # lhs < rhs -> rhs - lhs > 0
            return Q.positive(Add(rhs, neg_lhs))
        elif isinstance(sympy_expr, GreaterThan):  # lhs >= rhs -> lhs - rhs >= 0
            return Q.nonnegative(Add(lhs, neg_rhs))
        elif isinstance(sympy_expr, LessThan):  # lhs <= rhs -> rhs - lhs >= 0
            return Q.nonnegative(Add(rhs, neg_lhs))
        elif isinstance(sympy_expr, Equality):
            return Q.zero(Add(lhs, neg_rhs))
        elif isinstance(sympy_expr, Ne):
            return Q.nonzero(Add(lhs, neg_rhs))

    # None of the above conditions.
    # Fallback to a general boolean sympy_expression.
    return Q.is_true(sympy_expr)


def to_sympy_predicates(assumptions) -> AppliedPredicate:
    """Convert a Mathics3 assumptions expression to an
    AppliedPredicate used in SymPy's refine() or with_assumptions().
    """
    match assumptions:
        case val if val is SymbolTrue:
            return SYMPY_TRUE_PREDICATE
        case val if val is SymbolFalse:
            return SYMPY_FALSE_PREDICATE
        case val if isinstance(val, ListExpression):
            combined_predicate = SYMPY_TRUE_PREDICATE
            for elem in val.elements:
                sympy_assume = to_sympy_predicates(elem)
                if sympy_assume is not SYMPY_TRUE_PREDICATE:
                    if combined_predicate is SYMPY_TRUE_PREDICATE:
                        combined_predicate = sympy_assume
                    elif isinstance(sympy_assume, AppliedPredicate):
                        combined_predicate = AppliedPredicate("And", *sympy_assume.args)
                    else:
                        raise RuntimeError(
                            f"to_sympy_predicates returned whacky result {sympy_assume}"
                        )
            return combined_predicate

        case expr if isinstance(val, Expression):
            head = expr.head
            if head in (
                SymbolAnd,
                SymbolOr,
                SymbolNot,
                SymbolElement,
                SymbolEqual,
                SymbolGreater,
                SymbolGreaterEqual,
                SymbolLess,
                SymbolLessEqual,
            ):
                if (sympy_expr := expr.to_sympy()) is not None:
                    return sympy_expr_to_predicate(sympy_expr)

    return SYMPY_TRUE_PREDICATE
