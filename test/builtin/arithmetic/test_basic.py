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
    (
        "str_expr",
        "str_expected",
        "msg",
    ),
    [
        ("2^0", "1", None),
        ("(2/3)^0", "1", None),
        ("2.^0", "1.", None),
        ("2^1", "2", None),
        ("(2/3)^1", "2 / 3", None),
        ("2.^1", "2.", None),
        ("2^(3)", "8", None),
        ("(1/2)^3", "1 / 8", None),
        ("2^(-3)", "1 / 8", None),
        ("(1/2)^(-3)", "8", None),
        ("(-7)^(5/3)", "-7 (-7) ^ (2 / 3)", None),
        ("3^(1/2)", "Sqrt[3]", None),
        # WMA do not rationalize numbers
        ("(1/5)^(1/2)", "Sqrt[5] / 5", None),
        # WMA do not rationalize numbers
        ("(3)^(-1/2)", "Sqrt[3] / 3", None),
        ("(1/3)^(-1/2)", "Sqrt[3]", None),
        ("(5/3)^(1/2)", "Sqrt[5 / 3]", None),
        ("(5/3)^(-1/2)", "Sqrt[3 / 5]", None),
        ("1/Sqrt[Pi]", "1 / Sqrt[Pi]", None),
        ("I^(2/3)", "(-1) ^ (1 / 3)", None),
        # In WMA, the next test would return ``-(-I)^(2/3)``
        # which is less compact and elegant...
        #        ("(-I)^(2/3)", "(-1) ^ (-1 / 3)", None),
        ("(2+3I)^3", "-46 + 9 I", None),
        ("(1.+3. I)^.6", "1.46069 + 1.35921 I", None),
        ("3^(1+2 I)", "3 ^ (1 + 2 I)", None),
        ("3.^(1+2 I)", "-1.75876 + 2.43038 I", None),
        ("3^(1.+2 I)", "-1.75876 + 2.43038 I", None),
        # In WMA, the following expression returns
        # ``(Pi/3)^I``. By now, this is handled by
        # sympy, which produces the result
        ("(3/Pi)^(-I)", "(3 / Pi) ^ (-I)", None),
        # Association rules
        #        ('(a^"w")^2', 'a^(2 "w")', "Integer power of a power with string exponent"),
        ('(a^2)^"w"', '(a ^ 2) ^ "w"', None),
        ('(a^2)^"w"', '(a ^ 2) ^ "w"', None),
        ("(a^2)^(1/2)", "Sqrt[a ^ 2]", None),
        ("(a^(1/2))^2", "a", None),
        ("(a^(1/2))^2", "a", None),
        ("(a^(3/2))^3.", "(a ^ (3 / 2)) ^ 3.", None),
        #        ("(a^(1/2))^3.", "a ^ 1.5", "Power associativity rational, real"),
        #        ("(a^(.3))^3.", "a ^ 0.9", "Power associativity for real powers"),
        ("(a^(1.3))^3.", "(a ^ 1.3) ^ 3.", None),
        # Exponentials involving expressions
        ("(a^(p-2 q))^3", "a ^ (3 p - 6 q)", None),
        ("(a^(p-2 q))^3.", "(a ^ (p - 2 q)) ^ 3.", None),
    ],
)
def test_power(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)


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
    check_evaluation(str_expr, str_expected, failure_message=msg)


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
