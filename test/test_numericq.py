# -*- coding: utf-8 -*-
from .helper import check_evaluation, session
import pytest


@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
    ),
    [  # Numbers are numeric:
        ("2", "True"),
        ("3+2 I", "True"),
        ("2/9", "True"),
        # but Strings, not
        (""" "hi!" """, "False"),
        # Infinity is not numeric:
        ("Infinity", "False"),
        (
            "Pi",
            "True",
        ),
        (
            "E",
            "True",
        ),
        (
            "I",
            "True",
        ),
        # A detached symbol is not numeric
        (
            "a",
            "False",
        ),
        # If a symbol is assigned to a numeric downvalue,
        # NumericQ evaluates first its argument
        (
            "b=2;b",
            "True",
        ),
        (
            "$MachinePrecision",
            "True",
        ),
        # Also, an undefined symbol can be tagged as Numeric:
        (
            "NumericQ[a]=True; a",
            "True",
        ),
        # and also untagged as Numeric
        # (notice that as in WMA, `Protect` do not prevent the assignment):
        ("NumericQ[Pi]=False; Pi", False),
        # General builtin symbols are not numeric.
        (
            "Print",
            "False",
        ),
        # Head of numeric functions are not numeric
        (
            "Sin",
            "False",
        ),
    ],
)
def test_atomic_numericq(str_expr, str_expected):
    check_evaluation(f"NumericQ[{str_expr}]", str_expected)
    session.evaluate("ClearAll[a, b, Pi]")
    session.evaluate("NumericQ[a]=False;NumericQ[b]=False; NumericQ[Pi]=True;")


@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
    ),
    [
        # If an expression has a Head with attribute NumericFunction
        # and all their arguments are numeric, returns True
        (
            "Sin[1]",
            "True",
        ),
        (
            "a",
            "False",
        ),
        (
            "Sin[a]",
            "False",
        ),
        (
            "NumericQ[a]=True; Sin[a]",
            "True",
        ),
        (
            "Attributes[F]=NumericFunction; F[1]",
            "True",
        ),
        (
            "Attributes[F]=NumericFunction; F[Pi]",
            "True",
        ),
        (
            """Attributes[F]=NumericFunction; F["bla"]""",
            "False",
        ),
        (
            """F[1,l->2]""",
            "False",
        ),
        # NumericQ returs True for expressions that
        # cannot be evaluated to a number:
        ("1/(Sin[1]^2+Cos[1]^2-1)", "True"),
        ("Simplify[1/(Sin[1]^2+Cos[1]^2-1)]", "False"),
    ],
)
def test_expression_numericq(str_expr, str_expected):
    check_evaluation(f"NumericQ[{str_expr}]", str_expected)
    session.evaluate("ClearAll[a, F]")
    session.evaluate("NumericQ[a]=False;NumericQ[b]=False; NumericQ[Pi]=True;")


@pytest.mark.parametrize(
    (
        "str_expr",
        "str_expected",
    ),
    [
        # We can set that a symbol `a` is Numeric or not
        # by direct assign
        (
            "NumericQ[a]=True;NumericQ[a]",
            "True",
        ),
        (
            "NumericQ[a]=False;NumericQ[a]",
            "False",
        ),
        # In WMA, Clear does not reset the value of NumericQ
        # In Mathics, it does:
        ("NumericQ[a]=True; Clear[a]; NumericQ[a]", "True"),
        ("NumericQ[a]=True; ClearAll[a]; NumericQ[a]", "True"),
        ("NumericQ[a]=False", "False"),
        # We can only set True or False, otherwise the assignment fails:
        (
            "NumericQ[a]=37",
            "37",
        ),
        (
            "NumericQ[a]",
            "False",
        ),
        (
            "NumericQ[a]:=($MachinePrecision>10);NumericQ[a]",
            "False",
        ),
        # Assignment to NumericQ[expr] for expr expressions or patterns
        # does not show error messages, but does not have any effect:
        (
            "NumericQ[g[x]]=True;NumericQ[g[x]]",
            "False",
        ),
        (
            "NumericQ[g[x_]]=True;NumericQ[g[y]]",
            "False",
        ),
    ],
)
def test_assign_numericq(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
    session.evaluate("ClearAll[a, F, g]")
    session.evaluate("NumericQ[a]=False;NumericQ[b]=False; NumericQ[Pi]=True;")
