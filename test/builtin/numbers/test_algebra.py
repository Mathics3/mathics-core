# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.algebra and
mathics.builtins.numbers.integer
"""
from test.helper import check_evaluation

import pytest


def test_collect():
    for str_expr, str_expected in [
        ("Collect[q[x] + q[x] q[y],q[x]]", "q[x] (1 + q[y])"),
        ("Collect[ 1+ a x + b x^3 + Cos[t] x, x]", "1 + (a + Cos[t]) x + b x^3"),
        ("Collect[ q[0, x] q[0, y] + 1, q[0, x]]", "1 + q[0, x] q[0, y]"),  # Issue #285
        (
            "Collect[a x + b y + c x y^2 + p y x^2 + d x^2 y, {x, y}]",
            "a x + b y + c x y ^ 2 + x ^ 2 y (d + p)",
        ),
    ]:
        check_evaluation(str_expr, str_expected)


def test_coefficient():
    for str_expr, str_expected in (
        # Form 1: Coefficient[expr, form]
        (
            "Coefficient[(x + 2)/(y - 3) + (x + 3)/(y - 2), z, 0]",
            "(2 + x) / (-3 + y) + (3 + x) / (-2 + y)",
        ),
        (
            "Coefficient[y (x - 2)/((y^2 - 9)) + (x + 5)/(y + 2), x]",
            "y / (-9 + y ^ 2) + 1 / (2 + y)",
        ),
        # MMA returns better one: (-2 + x) / (-9 + y ^ 2)"
        (
            "Coefficient[y (x - 2)/((y^2 - 9)) + (x + 5)/(y + 2), y]",
            "x / (-9 + y ^ 2) - 2 / (-9 + y ^ 2)",
        ),
        (
            "Coefficient[y (x - 2)/((y - 3)(y + 3)) + (x + 5)/(y + 2), x]",
            "y / (-9 + y ^ 2) + 1 / (2 + y)",
        ),
        # MMA returns better one: (-2 + x) / ((-3 + y) (3 + y))
        (
            "Coefficient[y (x - 2)/((y - 3)(y + 3)) + (x + 5)/(y + 2), y]",
            "x / (-9 + y ^ 2) - 2 / (-9 + y ^ 2)",
        ),
        (
            "Coefficient[x^3 - 2 x/y + 3 x z, y]",
            "0",
        ),
        # Form 2: Coefficient[expr, form, n]
        (
            "Coefficient[x^2 + axy^2 - bSin[c], c]",
            "0",
        ),
    ):
        check_evaluation(str_expr, str_expected)


def test_coefficient_list():
    for str_expr, str_expected in (
        # Form 1: Coefficient[expr, form]
        (
            "CoefficientList[x^2 + a x y^2 - b Sin[c], y]",
            "{-b Sin[c] + x ^ 2, 0, a x}",
        ),
        (
            "CoefficientList[0, x]",
            "{}",
        ),
        (
            "CoefficientList[1, x]",
            "{1}",
        ),
        (
            "CoefficientList[x + 1, {}]",
            "1 + x",
        ),
        # Form 2 CoefficientList[poly, {var1, var2, ...}]
        (
            "CoefficientList[a x^2 + b y^3 + c x + d y + 5, {x}]",
            "{5 + b y ^ 3 + d y, c, a}",
        ),
        (
            "CoefficientList[a x^2 + b y^3 + c x + d y + 5, {}]",
            "5 + a x ^ 2 + b y ^ 3 + c x + d y",
        ),
        (
            "CoefficientList[a x^2 + b y^3 + c x + d y + 5, {x, y + 1}]",
            "{{5 + b y ^ 3 + d y}, {c}, {a}}",
        ),
        (
            "CoefficientList[a x^2 + b y^3 + c x + d y + 5, {x + 1, y}]",
            "{{5 + a x ^ 2 + c x, d, 0, b}}",
        ),
        (
            "CoefficientList[a x^2 + b y^3 + c x + d y + 5, {x + 1, y + 1}]",
            "{{5 + a x ^ 2 + b y ^ 3 + c x + d y}}",
        ),
        (
            "CoefficientList[y (x - 2)/((z - 3) (z + 3)) + (x + 5)/(z + 2), {x, y}]",
            "{{5 / (2 + z), -2 / (-9 + z ^ 2)}, {1 / (2 + z), 1 / (-9 + z ^ 2)}}",
        ),
        (
            "CoefficientList[0, {x, y}]",
            "{}",
        ),
        (
            "CoefficientList[1, {x, y}]",
            "{{1}}",
        ),
    ):
        check_evaluation(str_expr, str_expected)


def test_exponent():
    for str_expr, str_expected in (
        (
            "Exponent[(x^2 + 1)^3 - 1, x, List]",
            "{2, 4, 6}",
        ),
        (
            "Exponent[5 x^2 - 3 x + 7, x, List]",
            "{0, 1, 2}",
        ),
        (
            "Exponent[(x + 1) + (x + 1)^2, x, List]",
            "{0, 1, 2}",
        ),
        (
            "Exponent[(x + 3 y  - 2 z)^3 * (5 y + z), {x, y}, List]",
            "{{0, 1, 2, 3}, {0, 1, 2, 3, 4}}",
        ),
        (
            'Exponent[(x + 3 y - 2 z)^3*(5 y + z), {"x", "y"}, List]',
            "{{0}, {0}}",
        ),
        (
            "Exponent[(x + 3 y - 2 z)^3*(5 y + z), {}]",
            "{}",
        ),
        (
            "Exponent[x^a + b y^3 + c x + 2 y^e + 5, {x, y}, List]",
            "{{0, 1, a}, {0, 3, e}}",
        ),
        (
            "Exponent[x^2 / y^3, {x, y}]",
            "{2, -3}",
        ),
        (
            "Exponent[(x + 2)/(y - 3) + (x + 3)/(y - 2), {x, y, z}, List]",
            "{{0, 1}, {0}, {0}}",
        ),
        (
            "Exponent[x + 6 x^3 y^2 - 3/((x^2) (y^2)), {x, y}, List]",
            "{{-2, 1, 3}, {-2, 0, 2}}",
        ),
        (
            "Exponent[x^5 Sin[x^2] + x * x^3 Cos[x], x, List]",
            "{4, 5}",
        ),
        (
            "Exponent[x^5 Sin[x^2] + y Cos[y^2] + Log[x^3] + 6 y^4, {x, y}, List]",
            "{{0, 5}, {0, 1, 4}}",
        ),
    ):
        check_evaluation(str_expr, str_expected)


def test_factor_terms_list():
    for str_expr, str_expected in (
        (
            "f = 3 (-1 + 2 x) (-1 + y) (1 - a); FactorTermsList[f, y]",
            "{-3, 1 - a - 2 x + 2 a x, -1 + y}",
        ),
        (
            "FactorTermsList[f, {x, y}]",
            "{-3, -1 + a, -1 + y, -1 + 2 x}",
        ),
        (
            "FactorTermsList[f, {y, x}]",
            "{-3, -1 + a, -1 + 2 x, -1 + y}",
        ),
        (
            "FactorTermsList[f, {x, y, z}]",
            "{-3, -1 + a, 1, -1 + y, -1 + 2 x}",
        ),
        (
            "FactorTermsList[f, {x, y, z, t}]",
            "{-3, -1 + a, 1, 1, -1 + y, -1 + 2 x}",
        ),
        (
            "FactorTermsList[f, 3/5]",
            "{-3, -1 + a - 2 a x - a y + 2 x + y - 2 x y + 2 a x y}",
        ),
        (
            "FactorTermsList[f, {x, 3, y}]",
            "{-3, -1 + a, -1 + y, -1 + 2 x}",
        ),
        (
            "FactorTermsList[f/c]",
            "{-3, -1 / c + a / c - 2 a x / c - a y / c + 2 x / c + y / c - 2 x y / c + 2 a x y / c}",
        ),
        (
            "FactorTermsList[f/c, x] == FactorTermsList[f/c, {x, y}]",
            "True",
        ),
        (
            "g = Sin[x]*Cos[y]*(1 - 2 a)",
            "Cos[y] (1 - 2 a) Sin[x]",
        ),
        (
            "FactorTermsList[g]",
            "{-1, 2 a Cos[y] Sin[x] - Cos[y] Sin[x]}",
        ),
        (
            "FactorTermsList[g, x]",
            "{-1, 2 a Cos[y] Sin[x] - Cos[y] Sin[x]}",
        ),
        (
            "FactorTermsList[g, x] == FactorTermsList[g, y] == FactorTermsList[g, {x, y}]",
            "True",
        ),
        (
            "v = 3 * y * (1 - b) a^x",
            "3 y (1 - b) a ^ x",
        ),
        (
            "FactorTermsList[v]",
            "{-3, -y a ^ x + b y a ^ x}",
        ),
        (
            "FactorTermsList[v, x]",
            "{-3, -y a ^ x + b y a ^ x}",
        ),
        (
            "FactorTermsList[v, y]",
            "{-3, b a ^ x - a ^ x, y}",
        ),
        (
            "FactorTermsList[7]",
            "{7, 1}",
        ),
        (
            "FactorTermsList[0]",
            "{1, 0}",
        ),
        (
            "FactorTermsList[-3]",
            "{-3, 1}",
        ),
        (
            "FactorTermsList[7, {y, x}]",
            "{7, 1}",
        ),
        (
            "FactorTermsList[7, x]",
            "{7, 1}",
        ),
        (
            "FactorTermsList[7 - I, x]",
            "{7 - I, 1}",
        ),
        (
            "FactorTermsList[(x - 1) (1 + a), {c, d}]",
            "{1, -1 - a + x + a x}",
        ),
        (
            "FactorTermsList[(x - 1) (1 + a), {c, x}]",
            "{1, 1 + a, -1 + x, 1}",
        ),
        (
            "FactorTermsList[(x - 1) (1 + a), {}] == FactorTermsList[(x - 1) (1 + a)]",
            "True",
        ),
        (
            "FactorTermsList[x]",
            "{1, x}",
        ),
        (
            'FactorTermsList["x"]',
            "{1, x}",
        ),
    ):
        check_evaluation(str_expr, str_expected)


def test_polynomialq():
    for str_expr, str_expected in [
        ("PolynomialQ[1/x[1]^2]", "False"),
        ("PolynomialQ[x[1]^2]", "True"),
        ("PolynomialQ[y[1] ^ 3 / 6 + y[3] / 3 + y[1] y[2] / 2]", "True"),
    ]:
        check_evaluation(str_expr, str_expected)


def test_simplify():
    for str_expr, str_expected in (
        (
            "Simplify[a*x^2+b*x^2]",
            "x ^ 2 (a + b)",
        ),
        (
            "Simplify[2 Log[2]]",
            "Log[4]",
        ),
        (
            "Simplify[18 Log[2]]",
            "18 Log[2]",
        ),
        # triggers TypeError in sympy.simplify
        (
            "Clear[f]; x f[{y}] // Simplify",
            "x f[{y}]",
        ),
    ):
        check_evaluation(str_expr, str_expected)


skip_fullsimplify_test = True
try:
    import sympy
    from packaging import version

    skip_fullsimplify_test = version.parse(sympy.__version__) < version.parse("1.10.0")
except ImportError:
    pass


@pytest.mark.skipif(skip_fullsimplify_test, reason="requires sympy 1.10.10 or higher")
def test_fullsimplify():
    for str_expr, str_expected, failure_message in (
        (
            " a[x] + e f / (2 d) + c[x] // FullSimplify",
            "e f / (2 d) + a[x] + c[x]",
            "issue #214",
        ),
    ):
        check_evaluation(str_expr, str_expected, failure_message)


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Attributes[f] = {HoldAll}; Apart[f[x + x]]", None, "f[x + x]", None),
        ("Attributes[f] = {}; Apart[f[x + x]]", None, "f[2 x]", None),
        ## Errors:
        (
            "Coefficient[x + y + 3]",
            ("Coefficient called with 1 argument; 2 or 3 arguments are expected.",),
            "Coefficient[3 + x + y]",
            None,
        ),
        (
            "Coefficient[x + y + 3, 5]",
            ("5 is not a valid variable.",),
            "Coefficient[3 + x + y, 5]",
            None,
        ),
        # This is known bug of Sympy 1.0, next Sympy version will fix it by this commit
        # https://github.com/sympy/sympy/commit/25bf64b64d4d9a2dc563022818d29d06bc740d47
        ("Coefficient[x * y, z, 0]", None, "x y", "Sympy 1.0 returns 0"),
        # TODO: Support Modulus
        # ("Coefficient[(x + 2)^3 + (x + 3)^2, x, 0, {Modulus -> 3, Modulus -> 2, Modulus -> 10}]",
        # None,"{2, 1, 7}", None),
        (
            "CoefficientList[x + y, 5]",
            ("5 is not a valid variable.",),
            "CoefficientList[x + y, 5]",
            None,
        ),
        (
            "CoefficientList[(x - 2 y)^4, {x, 2}]",
            ("2 is not a valid variable.",),
            "CoefficientList[(x - 2 y) ^ 4, {x, 2}]",
            None,
        ),
        (
            "CoefficientList[x / y, {x, y}]",
            ("x / y is not a polynomial.",),
            "CoefficientList[x / y, {x, y}]",
            None,
        ),
        ("Expand[x, Modulus -> -1]  (* copy odd MMA behaviour *)", None, "0", None),
        (
            "Expand[x, Modulus -> x]",
            ("Value of option Modulus -> x should be an integer.",),
            "Expand[x, Modulus -> x]",
            None,
        ),
        ("a(b(c+d)+e) // Expand", None, "a b c + a b d + a e", None),
        ("(y^2)^(1/2)/(2x+2y)//Expand", None, "Sqrt[y ^ 2] / (2 x + 2 y)", None),
        (
            "2(3+2x)^2/(5+x^2+3x)^3 // Expand",
            None,
            "24 x / (5 + 3 x + x ^ 2) ^ 3 + 8 x ^ 2 / (5 + 3 x + x ^ 2) ^ 3 + 18 / (5 + 3 x + x ^ 2) ^ 3",
            None,
        ),
        ## Modulus option
        (
            "ExpandDenominator[1 / (x + y)^3, Modulus -> 3]",
            None,
            "1 / (x ^ 3 + y ^ 3)",
            None,
        ),
        (
            "ExpandDenominator[1 / (x + y)^6, Modulus -> 4]",
            None,
            "1 / (x ^ 6 + 2 x ^ 5 y + 3 x ^ 4 y ^ 2 + 3 x ^ 2 y ^ 4 + 2 x y ^ 5 + y ^ 6)",
            None,
        ),
        (
            "ExpandDenominator[2(3+2x)^2/(5+x^2+3x)^3]",
            None,
            "2 (3 + 2 x) ^ 2 / (125 + 225 x + 210 x ^ 2 + 117 x ^ 3 + 42 x ^ 4 + 9 x ^ 5 + x ^ 6)",
            None,
        ),
        ## errors:
        (
            "Exponent[x^2]",
            ("Exponent called with 1 argument; 2 or 3 arguments are expected.",),
            "Exponent[x ^ 2]",
            None,
        ),
        ## Issue659
        ("Factor[{x+x^2}]", None, "{x (1 + x)}", None),
        ("FactorTermsList[2 x^2 - 2, x]", None, "{2, 1, -1 + x ^ 2}", None),
        (
            "MinimalPolynomial[7a, x]",
            ("7 a is not an explicit algebraic number.",),
            "MinimalPolynomial[7 a, x]",
            None,
        ),
        (
            "MinimalPolynomial[3x^3 + 2x^2 + y^2 + ab, x]",
            ("ab + 2 x ^ 2 + 3 x ^ 3 + y ^ 2 is not an explicit algebraic number.",),
            "MinimalPolynomial[ab + 2 x ^ 2 + 3 x ^ 3 + y ^ 2, x]",
            None,
        ),
        ## PurePoly
        ("MinimalPolynomial[Sqrt[2 + Sqrt[3]]]", None, "1 - 4 #1 ^ 2 + #1 ^ 4", None),
        (
            "PolynomialQ[x, x, y]",
            ("PolynomialQ called with 3 arguments; 1 or 2 arguments are expected.",),
            "PolynomialQ[x, x, y]",
            None,
        ),
        ## Always return True if argument is Null
        (
            "PolynomialQ[x^3 - 2 x/y + 3xz, ]",
            None,
            "True",
            "Always return True if argument is Null",
        ),
        (
            "PolynomialQ[, {x, y, z}]",
            None,
            "True",
            "True if the expression is Null",
        ),
        (
            "PolynomialQ[, ]",
            None,
            "True",
            None,
        ),
        ## TODO: MMA and Sympy handle these cases differently
        ## #> PolynomialQ[x^(1/2) + 6xyz]
        ##  : No variable is not supported in PolynomialQ.
        ##  = True
        ## #> PolynomialQ[x^(1/2) + 6xyz, {}]
        ##  : No variable is not supported in PolynomialQ.
        ##  = True
        ## #> PolynomialQ[x^3 - 2 x/y + 3xz]
        ##  : No variable is not supported in PolynomialQ.
        ##  = False
        ## #> PolynomialQ[x^3 - 2 x/y + 3xz, {}]
        ##  : No variable is not supported in PolynomialQ.
        ##  = False
        ("f[x]/x+f[x]/x^2//Together", None, "f[x] (1 + x) / x ^ 2", None),
        ## failing test case from MMA docs
        ("Variables[E^x]", None, "{}", None),
    ],
)
def test_private_doctests_algebra(str_expr, msgs, str_expected, fail_msg):
    """doctests for algebra"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "FromDigits[x]",
            ("The input must be a string of digits or a list.",),
            "FromDigits[x, 10]",
            None,
        ),
    ],
)
def test_private_doctests_integer(str_expr, msgs, str_expected, fail_msg):
    """doctests for integer"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
