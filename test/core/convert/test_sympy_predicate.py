import pytest
from sympy import (
    Abs,
    And,
    Contains,
    Eq,
    Ge,
    Gt,
    Le,
    Lt,
    Ne,
    Not,
    Or,
    Q,
    S,
    Symbol as SymPySymbol,
    refine,
)
from sympy.assumptions.assume import AppliedPredicate

from mathics.core.convert.sympy import sympy_expr_to_predicate
from mathics.core.symbols import Symbol

Symbol_a = Symbol("Global`a")
Symbol_b = Symbol("Global`b")
Symbol_x = Symbol("Global`x")
Symbol_y = Symbol("Global`y")
Symbol_F = Symbol("Global`F")
Symbol_G = Symbol("Global`G")

SymPySymbol_x = SymPySymbol("x")


@pytest.fixture
def x():
    return SymPySymbol("x")


@pytest.fixture
def y():
    return SymPySymbol("y")


@pytest.mark.parametrize(
    "domain, expected_predicate",
    [
        (S.Reals, Q.real(SymPySymbol_x)),
        (S.Integers, Q.integer(SymPySymbol_x)),
        (S.Rationals, Q.rational(SymPySymbol_x)),
        (S.Complexes, Q.complex(SymPySymbol_x)),
        # (S.Booleans, Q.boolean(SymPySymbol_x)),
    ],
)
def test_domain_membership(domain, expected_predicate):
    """SymPy Domain (Real, Integers, Rationals) Membership Checks"""
    expr = Contains(SymPySymbol_x, domain)
    sympy_predicate = sympy_expr_to_predicate(expr)
    print(f"Predicate test: {sympy_predicate}")
    assert (
        sympy_predicate == expected_predicate
    ), f"Predicate test; got: {sympy_predicate}, expected {expected_predicate}"
    assert isinstance(sympy_predicate, AppliedPredicate)


def test_relational_zero_rhs(x):
    """Relational Normalization & Directional Alignment"""
    assert sympy_expr_to_predicate(x > 0) == Q.positive(x)
    assert sympy_expr_to_predicate(x < 0) == Q.negative(x)
    assert sympy_expr_to_predicate(x >= 0) == Q.nonnegative(x)
    assert sympy_expr_to_predicate(x <= 0) == Q.nonpositive(x)
    assert sympy_expr_to_predicate(Eq(x, 0)) == Q.zero(x)
    assert sympy_expr_to_predicate(Ne(x, 0)) == Q.nonzero(x)


def test_relational_zero_lhs(x):
    """Ensures 0 < x maps to Q.positive(x) and not Q.negative(-x)"""
    assert sympy_expr_to_predicate(0 < x) == Q.positive(x)
    assert sympy_expr_to_predicate(0 > x) == Q.negative(x)
    assert sympy_expr_to_predicate(0 <= x) == Q.nonnegative(x)
    assert sympy_expr_to_predicate(0 >= x) == Q.nonpositive(x)
    assert sympy_expr_to_predicate(Eq(0, x)) == Q.zero(x)
    assert sympy_expr_to_predicate(Ne(0, x)) == Q.nonzero(x)


def test_relational_general_expressions(x, y):
    """Tests relational expressions not including 0."""
    assert sympy_expr_to_predicate(x > y) == Q.positive(x - y)
    assert sympy_expr_to_predicate(x < y) == Q.positive(y - x)
    assert sympy_expr_to_predicate(x >= y) == Q.nonnegative(x - y)
    assert sympy_expr_to_predicate(x <= y) == Q.nonnegative(y - x)
    assert sympy_expr_to_predicate(Eq(x, y)) == Q.zero(x - y)
    assert sympy_expr_to_predicate(Ne(x, y)) == Q.nonzero(x - y)


def test_boolean_trees(x, y):
    """Test And, Or, and Not"""
    expr_and = (x > 0) & Q.integer(y)
    # Also try: (x > 0) & Contains(y, Integers) ?
    res_and = sympy_expr_to_predicate(expr_and)
    assert res_and == And(
        Q.positive(x), Q.integer(y)
    ), "Converting to SymPy Boolean And() got: {res_and}"

    expr_or = (x < 0) | (y > 0)
    res_or = sympy_expr_to_predicate(expr_or)
    assert res_or == Or(
        Q.negative(x), Q.positive(y)
    ), "Converting to SymPy Boolean Or() got: {res_and}"

    expr_not = ~(x <= 0)
    res_not = sympy_expr_to_predicate(expr_not)
    assert res_not == Q.positive(
        x
    ), "Converting to SymPy Boolean Not() should change relation got: {res_not}"


def test_already_applied_predicate(x):
    """Test Not relational with zero, domain or Element test, or Boolean compound, so
    fallback boolean test"""
    pred = Q.positive(x)
    assert sympy_expr_to_predicate(pred) is pred


def test_refine_compatibility(x):
    """Test that generated predicates work directly with SymPy's refine()"""
    pred_real = sympy_expr_to_predicate(Contains(x, S.Reals))
    pred_pos = sympy_expr_to_predicate(x > 0)

    combined = And(pred_real, pred_pos)
    assert (
        refine(Abs(x), combined) == x
    ), "Abs(x) should simpify to x when real and positive"
