# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.arithmetic.basic
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("1. + 2. + 3.", "6.", None),
        ("1 + 2/3 + 3/5", "34 / 15", None),
        ("1 - 2/3 + 3/5", "14 / 15", None),
        ("1. - 2/3 + 3/5", "0.933333", None),
        ("1 - 2/3 + 2 I", "1 / 3 + 2 I", None),
        ("1. - 2/3 + 2 I", "0.333333 + 2. I", None),
        (
            "a + 2 a + 3 a q",
            "3 a + 3 a q",
            "WMA do not collect the common factor `a` in the last expression neither",
        ),
        ("a - 2 a + 3 a q", "-a + 3 a q", None),
        ("a - (5+ a+ 2 b) + 3 a q", "-5 + 3 a q - 2 b", "WMA distribute the sign (-)"),
        (
            "a - 2 (5+ a+ 2 b) + 3 a q",
            "a + 3 a q - 2 (5 + a + 2 b)",
            "WMA do not distribute neither in the general case",
        ),
    ],
)
def test_add(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg, hold_expected=True)


@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
    ),
    [
        ("E^(3+I Pi)", "-E ^ 3"),
        ("E^(I Pi/2)", "I"),
        ("E^1", "E"),
        ("log2=Log[2.]; E^log2", "2."),
        ("log2=Log[2.]; Chop[E^(log2+I Pi)]", "-2."),
        ("log2=.; E^(I Pi/4)", "E ^ (I / 4 Pi)"),
        ("E^(.25 I Pi)", "0.707107 + 0.707107 I"),
    ],
)
def test_exponential(str_expr, str_expected):
    check_evaluation(str_expr, str_expected, hold_expected=True)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("1.  2.  3.", "6.", None),
        ("1 * 2/3 * 3/5", "2 / 5", None),
        ("1 (- 2/3) ( 3/5)", "-2 / 5", None),
        ("1. (- 2/3) ( 3 / 5)", "-0.4", None),
        ("1 (- 2/3) (2 I)", "-4 I / 3", None),
        ("1. (- 2/3) (2 I)", "0. - 1.33333 I", None),
        ("a ( 2 a) ( 3 a q)", "6 a ^ 3 q", None),
        ("a (- 2 a) ( 3 Sqrt[a] q)", "-6 a ^ (5 / 2) q", None),
        (
            "a (5+ a+ 2 b) (3 a q)",
            "3 a ^ 2 q (5 + a + 2 b)",
            "WMA distribute the sign (-)",
        ),
        (
            "a (- 2 (5+ a+ 2 b)) * (3 a q)",
            "-6 a ^ 2 q (5 + a + 2 b)",
            "WMA do not distribute neither in the general case",
        ),
        (
            "a  b a^2 / (2 a)^(3/2)",
            "Sqrt[2] a ^ (3 / 2) b / 4",
            "WMA do not distribute neither in the general case",
        ),
        (
            "a  b a^2 / (a)^(3/2)",
            "a ^ (3 / 2) b",
            "WMA do not distribute neither in the general case",
        ),
        (
            "a  b a^2 / (a b)^(3/2)",
            "a ^ 3 b / (a b) ^ (3 / 2)",
            "WMA do not distribute neither in the general case",
        ),
        (
            "a  b a ^ 2  (a b)^(-3 / 2)",
            "a ^ 3 b / (a b) ^ (3 / 2)",
            "Goes to the previous case because of the rule in Power",
        ),
        (
            "a  b Infinity",
            "a b Infinity",
            "Goes to the previous case because of the rule in Power",
        ),
        (
            "a  b 0 * Infinity",
            "Indeterminate",
            "Goes to the previous case because of the rule in Power",
        ),
        (
            "a  b ComplexInfinity",
            "ComplexInfinity",
            "Goes to the previous case because of the rule in Power",
        ),
        (
            "HoldForm[Times[]]",
            "Times[]",
            "Times without arguments is nor formatted",
        ),
        (
            "HoldForm[Times[x]]",
            "Times[x]",
            "Times with a single argument is nor formatted",
        ),
    ],
)
def test_multiply(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=msg,
        hold_expected=True,
        to_string_expr=True,
    )


@pytest.mark.skip("DirectedInfinity Precedence needs going over")
@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
        "msg",
    ),
    [
        (
            "DirectedInfinity[1+I]+DirectedInfinity[2+I]",
            "(2 / 5 + I / 5) Sqrt[5] Infinity + (1 / 2 + I / 2) Sqrt[2] Infinity",
            None,
        ),
        ("DirectedInfinity[Sqrt[3]]", "Infinity", None),
        (
            "a  b  DirectedInfinity[1. + 2. I]",
            "a b ((0.447214 + 0.894427 I) Infinity)",
            "symbols times floating point complex directed infinity",
        ),
        ("a  b  DirectedInfinity[I]", "a b (I Infinity)", ""),
        (
            "a  b (-1 + 2 I) Infinity",
            "a b ((-1 / 5 + 2 I / 5) Sqrt[5] Infinity)",
            "symbols times algebraic exact factor times infinity",
        ),
        (
            "a  b (-1 + 2 Pi I) Infinity",
            "a b (Infinity (-1 + 2 I Pi) / Sqrt[1 + 4 Pi ^ 2])",
            "complex irrational exact",
        ),
        (
            "a  b  DirectedInfinity[(1 + 2 I)/ Sqrt[5]]",
            "a b ((1 / 5 + 2 I / 5) Sqrt[5] Infinity)",
            "symbols times algebraic complex directed infinity",
        ),
        ("a  b  DirectedInfinity[q]", "a b (q Infinity)", ""),
        # Failing tests
        # Problem with formatting. Parenthezise are missing...
        #        ("a  b  DirectedInfinity[-I]", "a b (-I Infinity)",  ""),
        #        ("a  b  DirectedInfinity[-3]", "a b (-Infinity)",  ""),
    ],
)
def test_directed_infinity_precedence(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=msg,
        hold_expected=True,
        to_string_expr=True,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "expected_message", "fail_msg"),
    [
        ("2^0", "1", None, None),
        ("(2/3)^0", "1", None, None),
        ("2.^0", "1.", None, None),
        ("2^1", "2", None, None),
        ("(2/3)^1", "2 / 3", None, None),
        ("2.^1", "2.", None, None),
        ("2^(3)", "8", None, None),
        ("(1/2)^3", "1 / 8", None, None),
        ("2^(-3)", "1 / 8", None, None),
        ("(1/2)^(-3)", "8", None, None),
        ("(-7)^(5/3)", "-7 (-7) ^ (2 / 3)", None, None),
        ("3^(1/2)", "Sqrt[3]", None, None),
        # WMA do not rationalize numbers
        ("(1/5)^(1/2)", "Sqrt[5] / 5", None, None),
        # WMA do not rationalize numbers
        ("(3)^(-1/2)", "Sqrt[3] / 3", None, None),
        ("(1/3)^(-1/2)", "Sqrt[3]", None, None),
        ("(5/3)^(1/2)", "Sqrt[5 / 3]", None, None),
        ("(5/3)^(-1/2)", "Sqrt[3 / 5]", None, None),
        ("1/Sqrt[Pi]", "1 / Sqrt[Pi]", None, None),
        ("I^(2/3)", "(-1) ^ (1 / 3)", None, None),
        # In WMA, the next test would return ``-(-I)^(2/3)``
        # which is less compact and elegant...
        #        ("(-I)^(2/3)", "(-1) ^ (-1 / 3)", None),
        ("(2+3I)^3", "-46 + 9 I", None, None),
        ("(1.+3. I)^.6", "1.46069 + 1.35921 I", None, None),
        ("3^(1+2 I)", "3 ^ (1 + 2 I)", None, None),
        ("3.^(1+2 I)", "-1.75876 + 2.43038 I", None, None),
        ("3^(1.+2 I)", "-1.75876 + 2.43038 I", None, None),
        # In WMA, the following expression returns
        # ``(Pi/3)^I``. By now, this is handled by
        # sympy, which produces the result
        ("(3/Pi)^(-I)", "(3 / Pi) ^ (-I)", None, None),
        # Association rules
        #        ('(a^"w")^2', 'a^(2 "w")', "Integer power of a power with string exponent"),
        ('(a^2)^"w"', '(a ^ 2) ^ "w"', None, None),
        ('(a^2)^"w"', '(a ^ 2) ^ "w"', None, None),
        ("(a^2)^(1/2)", "Sqrt[a ^ 2]", None, None),
        ("(a^(1/2))^2", "a", None, None),
        ("(a^(1/2))^2", "a", None, None),
        ("(a^(3/2))^3.", "(a ^ (3 / 2)) ^ 3.", None, None),
        #        ("(a^(1/2))^3.", "a ^ 1.5", "Power associativity rational, real"),
        #        ("(a^(.3))^3.", "a ^ 0.9", "Power associativity for real powers"),
        ("(a^(1.3))^3.", "(a ^ 1.3) ^ 3.", None, None),
        # Exponentials involving expressions
        ("(a^(p-2 q))^3", "a ^ (3 p - 6 q)", None, None),
        ("(a^(p-2 q))^3.", "(a ^ (p - 2 q)) ^ 3.", None, None),
        # Indefinite / ComplexInfinity / Complex powers
        ("1/0", "ComplexInfinity", "Infinite expression 1 / 0 encountered.", None),
        (
            "0 ^ -2",
            "ComplexInfinity",
            "Infinite expression 1 / 0 ^ 2 encountered.",
            None,
        ),
        (
            "0 ^ (-1/2)",
            "ComplexInfinity",
            "Infinite expression 1 / Sqrt[0] encountered.",
            None,
        ),
        (
            "0 ^ -Pi",
            "ComplexInfinity",
            "Infinite expression 1 / 0 ^ 3.14159 encountered.",
            None,
        ),
        (
            "0 ^ (2 I E)",
            "Indeterminate",
            "Indeterminate expression 0 ^ (0. + 5.43656 I) encountered.",
            None,
        ),
        (
            "0 ^ - (Pi + 2 E I)",
            "ComplexInfinity",
            "Infinite expression 0 ^ (-3.14159 - 5.43656 I) encountered.",
            None,
        ),
        ("0 ^ 0", "Indeterminate", "Indeterminate expression 0 ^ 0 encountered.", None),
        ("Sqrt[-3+2. I]", "0.550251 + 1.81735 I", None, None),
        ("(3/2+1/2I)^2", "2 + 3 I / 2", None, None),
        ("I ^ I", "(-1) ^ (I / 2)", None, None),
        ("2 ^ 2.0", "4.", None, None),
        ("Pi ^ 4.", "97.4091", None, None),
        ("a ^ b", "a ^ b", None, None),
    ],
)
def test_power(str_expr, str_expected, expected_message, fail_msg):
    if expected_message is None:
        check_evaluation(str_expr, str_expected, failure_message=fail_msg)
    else:
        check_evaluation(
            str_expr,
            str_expected,
            failure_message=fail_msg,
            expected_messages=[expected_message],
        )


@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
        "msg",
    ),
    [
        (None, None, None),
        # Private tests from mathics.arithmetic.Complex
        ("Complex[1, Complex[0, 1]]", "0", "Iterated Complex (1 , I)"),
        ("Complex[1, Complex[1, 0]]", "1 + I", "Iterated Complex  (1, 1) "),
        ("Complex[1, Complex[1, 1]]", "I", "Iterated Complex, (1, 1 + I)"),
        ("Complex[0., 0.]", "0. + 0. I", "build complex 0.+0. I"),
        ("Complex[10, 0.]", "10. + 0. I", "build complex"),
        ("Complex[10, 0]", "10", "build complex"),
        ("1 + 0. I", "1. + 0. I", None),
        # Mathics produces "0."
        # For some weird reason, the following tests
        # pass if we run this unit test alone, but not
        # if we run it together all the tests
        ("0. + 0. I//FullForm", "Complex[0., 0.]", "WMA compatibility"),
        ("0. I//FullForm", "Complex[0., 0.]", None),
        ("1. + 0. I//FullForm", "Complex[1., 0.]", None),
        ("0. + 1. I//FullForm", "Complex[0., 1.]", None),
        ("1. + 0. I//OutputForm", "1. + 0. I", "Formatted"),
        ("0. + 1. I//OutputForm", "0. + 1. I", "Formatting 1. I"),
        ("-2/3-I//FullForm", "Complex[Rational[-2, 3], -1]", "Adding a rational"),
    ],
)
def test_complex(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=msg,
        to_string_expected=True,
        # to_string_expr=True,
        hold_expected=True,
    )


@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
        "msg",
    ),
    [
        (None, None, None),
        ("{Conjugate[Pi], Conjugate[E]}", "{Pi, E}", "Issue #272"),
        ("-2/3", "-2 / 3", "Rational"),
        ("-2/3//Head", "Rational", "Rational"),
        (
            "(-1 + a^n) Sum[a^(k n), {k, 0, m-1}] // Simplify",
            "-1 + (a ^ n) ^ m",
            "according to WMA. Now it fails",
        ),
        ("1 / 4.0", "0.25", None),
        ("10 / 3 // FullForm", "Rational[10, 3]", None),
        ("a / b // FullForm", "Times[a, Power[b, -1]]", None),
        # Plus
        ("-2a - 2b", "-2 a - 2 b", None),
        ("-4+2x+2*Sqrt[3]", "-4 + 2 Sqrt[3] + 2 x", None),
        ("2a-3b-c", "2 a - 3 b - c", None),
        ("2a+5d-3b-2c-e", "2 a - 3 b - 2 c + 5 d - e", None),
        ("1 - I * Sqrt[3]", "1 - I Sqrt[3]", None),
        ("Head[3 + 2 I]", "Complex", None),
        # Times
        ("Times[]// FullForm", "1", None),
        ("Times[-1]// FullForm", "-1", None),
        ("Times[-5]// FullForm", "-5", None),
        ("Times[-5, a]// FullForm", "Times[-5, a]", None),
        ("-a*b // FullForm", "Times[-1, a, b]", None),
        ("-(x - 2/3)", "2 / 3 - x", None),
        ("-x*2", "-2 x", None),
        ("-(h/2) // FullForm", "Times[Rational[-1, 2], h]", None),
        ("x / x", "1", None),
        ("2x^2 / x^2", "2", None),
        ("3. Pi", "9.42478", None),
        ("Head[3 * I]", "Complex", None),
        ("Head[Times[I, 1/2]]", "Complex", None),
        ("Head[Pi * I]", "Times", None),
        ("3 * a //InputForm", "3*a", None),
        ("3 * a //OutputForm", "3 a", None),
        ("-2.123456789 x", "-2.12346 x", None),
        ("-2.123456789 I", "0. - 2.12346 I", None),
        ("N[Pi, 30] * I", "3.14159265358979323846264338328 I", None),
        ("N[I Pi, 30]", "3.14159265358979323846264338328 I", None),
        ("N[Pi * E, 30]", "8.53973422267356706546355086955", None),
        ("N[Pi, 30] * N[E, 30]", "8.53973422267356706546355086955", None),
        (
            "N[Pi, 30] * E//{#1, Precision[#1]}&",
            "{8.53973422267356706546355086955, 30.}",
            None,
        ),
        # Precision
        (
            "N[Pi, 30] + N[E, 30]//{#1, Precision[#1]}&",
            "{5.85987448204883847382293085463, 30.}",
            None,
        ),
        (
            "N[Sqrt[2], 50]",
            "1.4142135623730950488016887242096980785696718753769",
            "N[Sqrt[...]]",
        ),
        (
            "Sum[i / Log[i], {i, 1, Infinity}]",
            "Sum[i / Log[i], {i, 1, Infinity}]",
            "Issue #302",
        ),
        (
            "Sum[Cos[Pi i], {i, 1, Infinity}]",
            "Sum[Cos[i Pi], {i, 1, Infinity}]",
            "Issue #302",
        ),
        (
            "Sum[x^k*Sum[y^l,{l,0,4}],{k,0,4}]",
            "1 + x (1 + y + y ^ 2 + y ^ 3 + y ^ 4) + x ^ 2 (1 + y + y ^ 2 + y ^ 3 + y ^ 4) + x ^ 3 (1 + y + y ^ 2 + y ^ 3 + y ^ 4) + x ^ 4 (1 + y + y ^ 2 + y ^ 3 + y ^ 4) + y + y ^ 2 + y ^ 3 + y ^ 4",
            "Iterated sum",
        ),
    ],
)
def test_miscelanea_private_tests(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg, hold_expected=True)


@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
        "msg",
    ),
    [
        (
            "Product[1 + 1 / i ^ 2, {i, Infinity}]",
            "1 / ((-I)! I!)",
            (
                "Used to be a bug in sympy, but now it is solved exactly!\n"
                "Again a bug in sympy - regressions between 0.7.3 and 0.7.6 (and 0.7.7?)"
            ),
        ),
    ],
)
@pytest.mark.xfail
def test_miscelanea_private_tests_xfail(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
        "msgs",
        "failmsg",
    ),
    [
        ("CubeRoot[-5]", "-5 ^ (1 / 3)", None, None),
        ("CubeRoot[-510000]", "-10 510 ^ (1 / 3)", None, None),
        ("CubeRoot[-5.1]", "-1.7213", None, None),
        ("CubeRoot[b]", "b ^ (1 / 3)", None, None),
        ("CubeRoot[-0.5]", "-0.793701", None, None),
        (
            "CubeRoot[3 + 4 I]",
            "(3 + 4 I) ^ (1 / 3)",
            ["The parameter 3 + 4 I should be real valued."],
            None,
        ),
    ],
)
def test_cuberoot(str_expr, str_expected, msgs, failmsg):
    check_evaluation(
        str_expr, str_expected, expected_messages=msgs, failure_message=failmsg
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ## Issue #302
        ## The sum should not converge since the first term is 1/0.
        (
            "Sum[i / Log[i], {i, 1, Infinity}]",
            None,
            "Sum[i / Log[i], {i, 1, Infinity}]",
            None,
        ),
        (
            "Sum[Cos[Pi i], {i, 1, Infinity}]",
            None,
            "Sum[Cos[i Pi], {i, 1, Infinity}]",
            None,
        ),
    ],
)
def test_private_doctests_arithmetic(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
