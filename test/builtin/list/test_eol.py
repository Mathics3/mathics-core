# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.list.constructing
"""
from test.helper import check_evaluation, check_evaluation_as_in_cli

import pytest


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        ("Append[a, b]", ("Nonatomic expression expected.",), "Append[a, b]", None),
        (
            "AppendTo[{}, 1]",
            ("{} is not a variable with a value, so its value cannot be changed.",),
            "AppendTo[{}, 1]",
            None,
        ),
        (
            "AppendTo[a, b]",
            ("a is not a variable with a value, so its value cannot be changed.",),
            "AppendTo[a, b]",
            None,
        ),
        ("Cases[1, 2]", None, "{}", None),
        ("Cases[f[1, 2], 2]", None, "{2}", None),
        ("Cases[f[f[1, 2], f[2]], 2]", None, "{}", None),
        ("Cases[f[f[1, 2], f[2]], 2, 2]", None, "{2, 2}", None),
        ("Cases[f[f[1, 2], f[2], 2], 2, Infinity]", None, "{2, 2, 2}", None),
        (
            "Cases[{1, f[2], f[3, 3, 3], 4, f[5, 5]}, f[x__] :> Plus[x]]",
            None,
            "{2, 9, 10}",
            None,
        ),
        (
            "Cases[{1, f[2], f[3, 3, 3], 4, f[5, 5]}, f[x__] -> Plus[x]]",
            None,
            "{2, 3, 3, 3, 5, 5}",
            None,
        ),
        ("z = f[x, y]; x = 1; Cases[z, _Symbol, Infinity]", None, "{y}", "Issue 531"),
        (
            "x=.;a=.;b=.;c=.;f=.; g=.;d=.;m=.;n=.;Delete[1 + x ^ (a + b + c), {2, 2, 3}]",
            None,
            "1 + x ^ (a + b)",
            "Faiing?",
        ),
        ("Delete[f[a, g[b, c], d], {{2}, {2, 1}}]", None, "f[a, d]", None),
        (
            "Delete[f[a, g[b, c], d], m + n]",
            (
                "The expression m + n cannot be used as a part specification. Use Key[m + n] instead.",
            ),
            "Delete[f[a, g[b, c], d], m + n]",
            None,
        ),
        (
            "Delete[{a, b, c, d}, {{1}, n}]",
            (
                "Position specification {n, {1}} in {a, b, c, d} is not a machine-sized integer or a list of machine-sized integers.",
            ),
            "Delete[{a, b, c, d}, {{1}, n}]",
            None,
        ),
        (
            "Delete[{a, b, c, d}, {{1}, {n}}]",
            (
                "Position specification n in {a, b, c, d} is not a machine-sized integer or a list of machine-sized integers.",
            ),
            "Delete[{a, b, c, d}, {{1}, {n}}]",
            None,
        ),
        ("z = {x, y}; x = 1; DeleteCases[z, _Symbol]", None, "{1}", "Issue 531"),
        ("x=.;z=.;", None, "Null", None),
        ("Drop[Range[10], {-2, -6, -3}]", None, "{1, 2, 3, 4, 5, 7, 8, 10}", None),
        ("Drop[Range[10], {10, 1, -3}]", None, "{2, 3, 5, 6, 8, 9}", None),
        (
            "Drop[Range[6], {-5, -2, -2}]",
            ("Cannot drop positions -5 through -2 in {1, 2, 3, 4, 5, 6}.",),
            "Drop[{1, 2, 3, 4, 5, 6}, {-5, -2, -2}]",
            None,
        ),
        (
            "First[a, b, c]",
            ("First called with 3 arguments; 1 or 2 arguments are expected.",),
            "First[a, b, c]",
            None,
        ),
        ('FirstPosition[{1, 2, 3}, _?StringQ, "NoStrings"]', None, "NoStrings", None),
        ("FirstPosition[a, a]", None, "{}", None),
        (
            "FirstPosition[{{{1, 2}, {2, 3}, {3, 1}}, {{1, 2}, {2, 3}, {3, 1}}},3]",
            None,
            "{1, 2, 2}",
            None,
        ),
        (
            'FirstPosition[{{1, {2, 1}}, {2, 3}, {3, 1}}, 2, Missing["NotFound"],2]',
            None,
            "{2, 1}",
            None,
        ),
        (
            'FirstPosition[{{1, {2, 1}}, {2, 3}, {3, 1}}, 2, Missing["NotFound"],4]',
            None,
            "{1, 2, 1}",
            None,
        ),
        (
            'FirstPosition[{{1, 2}, {2, 3}, {3, 1}}, 3, Missing["NotFound"], {1}]',
            None,
            "Missing[NotFound]",
            None,
        ),
        (
            'FirstPosition[{{1, 2}, {2, 3}, {3, 1}}, 3, Missing["NotFound"], 0]',
            None,
            "Missing[NotFound]",
            None,
        ),
        (
            'FirstPosition[{{1, 2}, {1, {2, 1}}, {2, 3}}, 2, Missing["NotFound"], {3}]',
            None,
            "{2, 2, 1}",
            None,
        ),
        (
            'FirstPosition[{{1, 2}, {1, {2, 1}}, {2, 3}}, 2, Missing["NotFound"], 3]',
            None,
            "{1, 2}",
            None,
        ),
        (
            'FirstPosition[{{1, 2}, {1, {2, 1}}, {2, 3}}, 2,  Missing["NotFound"], {}]',
            None,
            "{1, 2}",
            None,
        ),
        (
            'FirstPosition[{{1, 2}, {2, 3}, {3, 1}}, 3, Missing["NotFound"], {1, 2, 3}]',
            ("Level specification {1, 2, 3} is not of the form n, {n}, or {m, n}.",),
            "FirstPosition[{{1, 2}, {2, 3}, {3, 1}}, 3, Missing[NotFound], {1, 2, 3}]",
            None,
        ),
        (
            'FirstPosition[{{1, 2}, {2, 3}, {3, 1}}, 3, Missing["NotFound"], a]',
            ("Level specification a is not of the form n, {n}, or {m, n}.",),
            "FirstPosition[{{1, 2}, {2, 3}, {3, 1}}, 3, Missing[NotFound], a]",
            None,
        ),
        (
            'FirstPosition[{{1, 2}, {2, 3}, {3, 1}}, 3, Missing["NotFound"], {1, a}]',
            ("Level specification {1, a} is not of the form n, {n}, or {m, n}.",),
            "FirstPosition[{{1, 2}, {2, 3}, {3, 1}}, 3, Missing[NotFound], {1, a}]",
            None,
        ),
        ("A[x__] := 7 /; Length[{x}] == 3;Most[A[1, 2, 3, 4]]", None, "7", None),
        ("ClearAll[A];", None, "Null", None),
        ("a = {2,3,4}; i = 1; a[[i]] = 0; a", None, "{0, 3, 4}", None),
        ## Negative step
        ("{1,2,3,4,5}[[3;;1;;-1]]", None, "{3, 2, 1}", None),
        ("ClearAll[a]", None, "Null", None),
        (
            "Last[a, b, c]",
            ("Last called with 3 arguments; 1 or 2 arguments are expected.",),
            "Last[a, b, c]",
            None,
        ),
        ("Range[11][[-3 ;; 2 ;; -2]]", None, "{9, 7, 5, 3}", None),
        ("Range[11][[-3 ;; -7 ;; -3]]", None, "{9, 6}", None),
        ("Range[11][[7 ;; -7;; -2]]", None, "{7, 5}", None),
        (
            "{1, 2, 3, 4}[[1;;3;;-1]]",
            ("Cannot take positions 1 through 3 in {1, 2, 3, 4}.",),
            "{1, 2, 3, 4}[[1 ;; 3 ;; -1]]",
            None,
        ),
        (
            "{1, 2, 3, 4}[[3;;1]]",
            ("Cannot take positions 3 through 1 in {1, 2, 3, 4}.",),
            "{1, 2, 3, 4}[[3 ;; 1]]",
            None,
        ),
        (
            "a=.;b=.;Prepend[a, b]",
            ("Nonatomic expression expected.",),
            "Prepend[a, b]",
            "Prepend works with non-atomic expressions",
        ),
        (
            "PrependTo[{a, b}, 1]",
            ("{a, b} is not a variable with a value, so its value cannot be changed.",),
            "PrependTo[{a, b}, 1]",
            None,
        ),
        (
            "PrependTo[a, b]",
            ("a is not a variable with a value, so its value cannot be changed.",),
            "PrependTo[a, b]",
            None,
        ),
        (
            "x = 1 + 2;PrependTo[x, {3, 4}]",
            ("Nonatomic expression expected at position 1 in PrependTo[x, {3, 4}].",),
            "PrependTo[x, {3, 4}]",
            None,
        ),
        (
            "A[x__] := 31415 /; Length[{x}] == 3; Select[A[5, 2, 7, 1], OddQ]",
            None,
            "31415",
            None,
        ),
        ("ClearAll[A];", None, "Null", None),
        ## Parsing: 8 cases to consider
        ("a=.;b=.;c=.; a ;; b ;; c // FullForm", None, "Span[a, b, c]", None),
        ("  ;; b ;; c // FullForm", None, "Span[1, b, c]", None),
        ("a ;;   ;; c // FullForm", None, "Span[a, All, c]", None),
        ("  ;;   ;; c // FullForm", None, "Span[1, All, c]", None),
        ("a ;; b      // FullForm", None, "Span[a, b]", None),
        ("  ;; b      // FullForm", None, "Span[1, b]", None),
        ("a ;;        // FullForm", None, "Span[a, All]", None),
        ("  ;;        // FullForm", None, "Span[1, All]", None),
        ## Formatting
        ("a ;; b ;; c", None, "a ;; b ;; c", None),
        ("a ;; b", None, "a ;; b", None),
        # TODO: Rework this test
        ("{a ;; b ;; c ;; d}", None, "{a ;; b ;; c, 1 ;; d}", ";; association"),
        (
            "Select[a, True]",
            ("Nonatomic expression expected.",),
            "Select[a, True]",
            None,
        ),
        ("Take[Range[10], {8, 2, -1}]", None, "{8, 7, 6, 5, 4, 3, 2}", None),
        ("Take[Range[10], {-3, -7, -2}]", None, "{8, 6, 4}", None),
        (
            "Take[Range[6], {-5, -2, -2}]",
            ("Cannot take positions -5 through -2 in {1, 2, 3, 4, 5, 6}.",),
            "Take[{1, 2, 3, 4, 5, 6}, {-5, -2, -2}]",
            None,
        ),
        (
            "Take[l, {-1}]",
            ("Nonatomic expression expected at position 1 in Take[l, {-1}].",),
            "Take[l, {-1}]",
            None,
        ),
        ## Empty case
        ("Take[{1, 2, 3, 4, 5}, {-1, -2}]", None, "{}", None),
        ("Take[{1, 2, 3, 4, 5}, {0, -1}]", None, "{}", None),
        ("Take[{1, 2, 3, 4, 5}, {1, 0}]", None, "{}", None),
        ("Take[{1, 2, 3, 4, 5}, {2, 1}]", None, "{}", None),
        ("Take[{1, 2, 3, 4, 5}, {1, 0, 2}]", None, "{}", None),
        (
            "Take[{1, 2, 3, 4, 5}, {1, 0, -1}]",
            ("Cannot take positions 1 through 0 in {1, 2, 3, 4, 5}.",),
            "Take[{1, 2, 3, 4, 5}, {1, 0, -1}]",
            None,
        ),
    ],
)
def test_eol_edicates_private_doctests(
    str_expr, expected_messages, str_expected, assert_message
):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
        hold_expected=True,
    )


# To check expressions with has `Sequence` as output,
# we need to use ``check_evaluation_as_in_cli``
@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        ("Delete[{}, 0]", None, "Sequence[]", None),
        ("Delete[{1, 2}, 0]", None, "Sequence[1, 2]", None),
    ],
)
def test_as_in_cli(str_expr, expected_messages, str_expected, assert_message):
    check_evaluation_as_in_cli(
        str_expr, str_expected, expected_messages, assert_message
    )
