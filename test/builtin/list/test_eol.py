# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.list.constructing
"""

from test.helper import check_arg_counts, check_evaluation, check_evaluation_as_in_cli

import pytest


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        ("ClearAll[a];", None, "Null", None),
        (
            "Append[a, b]",
            ("Nonatomic expression expected at position 1 in Append[a, b].",),
            "Append[a, b]",
            None,
        ),
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
            "Failing?",
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
            ("Nonatomic expression expected at position 1 in Prepend[a, b].",),
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
            (
                "Nonatomic expression expected at position 1 in Select[a, True, Infinity].",
            ),
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
        ("Insert[{a, b, c}, new, -1]", None, "{a, b, c, new}", None),
        ("Insert[{a, b, c}, new, -4]", None, "{new, a, b, c}", None),
        ("Insert[{a, b, c}, new, 4]", None, "{a, b, c, new}", None),
        ("Insert[{}, new, -1]", None, "{new}", None),
        (
            "Insert[{a, b, c}, new, 0]",
            ("Cannot insert at position 0 in {a, b, c}.",),
            "Insert[{a, b, c}, new, 0]",
            None,
        ),
        (
            "Insert[{a, b, c}, new, 5]",
            ("Cannot insert at position 5 in {a, b, c}.",),
            "Insert[{a, b, c}, new, 5]",
            None,
        ),
        (
            "Insert[{a, b, c}, new, -5]",
            ("Cannot insert at position -5 in {a, b, c}.",),
            "Insert[{a, b, c}, new, -5]",
            None,
        ),
        (
            "Insert[]",
            ("Insert called with 0 arguments; 2 or 3 arguments are expected.",),
            "Insert[]",
            None,
        ),
        (
            "Insert[a]",
            ("Insert called with 1 argument; 2 or 3 arguments are expected.",),
            "Insert[a]",
            None,
        ),
        ("Insert[a, b]", None, "Insert[a, b]", None),
        (
            "Insert[a, b, c, d]",
            ("Insert called with 4 arguments; 2 or 3 arguments are expected.",),
            "Insert[a, b, c, d]",
            None,
        ),
    ],
)
def test_eol_edicates(str_expr, expected_messages, str_expected, assert_message):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
        hold_expected=True,
    )


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        (
            "First[a, b, c]",
            ("First called with 3 arguments; 1 or 2 arguments are expected.",),
            "First[a, b, c]",
            None,
        ),
        (
            "First[ByteArray[{5}]]",
            None,
            "5",
            None,
        ),
        (
            "Last[c, d, e]",
            ("Last called with 3 arguments; 1 or 2 arguments are expected.",),
            "Last[c, d, e]",
            None,
        ),
        (
            "Last[ByteArray[{6}]]",
            None,
            "6",
            None,
        ),
    ],
)
def test_First_and_Last(str_expr, expected_messages, str_expected, assert_message):
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


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected"),
    [
        ("Extract[{a[1], b[2]}, {2}, Hold]", None, "Hold[b[2]]"),
        (
            "Extract[{{1, 2}, {3, 4}}, {{1, 1}, {2, 2}}, Hold]",
            None,
            "{Hold[1], Hold[4]}",
        ),
        ("Extract[Hold[1 + 1, 2 + 2], {2}, Hold]", None, "Hold[2 + 2]"),
        ("Extract[Hold[1 + 1, 2 + 2], {1, -1}, Hold]", None, "Hold[1]"),
        ("Extract[Hold[1 + 1], {1, 0}, Hold]", None, "Hold[Plus]"),
        ("Extract[Hold[1 + 1], {{}}, Hold]", None, "{Hold[Hold[1 + 1]]}"),
        ("Extract[Hold[1 + 1], {}, Hold]", None, "{}"),
        ("Extract[{a, b, c}, 2, f]", None, "f[b]"),
        ("Extract[{{a, b}, {c, d}}, {All, 1}, Hold]", None, "Hold[{a, c}]"),
        ('Extract[<|"x" -> 1 + 1|>, {Key["x"]}, Hold]', None, "Hold[2]"),
        (
            "Extract[Hold[1 + 1], {1, 5}, Hold]",
            ("Part 5 of 1 + 1 does not exist.",),
            "Extract[Hold[1 + 1], {1, 5}, Hold]",
        ),
        (
            "Extract[{a, b}, notapos, Hold]",
            (
                "Position specification notapos in Extract[{a, b}, notapos, Hold] is not applicable.",
            ),
            "Extract[{a, b}, notapos, Hold]",
        ),
    ],
)
def test_extract_with_head(str_expr, expected_messages, str_expected):
    """Extract[expr, pos, h] wraps the parts in h before they are evaluated."""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        expected_messages=expected_messages,
    )


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected"),
    [
        ("Extract[{a, b}, {{}}]", None, "{{a, b}}"),
        # A single part selector other than an integer is a position too.
        ("Extract[{a, b, c}, All, Hold]", None, "Hold[{a, b, c}]"),
        ("Extract[{a, b, c}, 1 ;; 2, Hold]", None, "Hold[{a, b}]"),
        ("Extract[{a, b, c}, -1 ;; 1 ;; -1]", None, "{c, b, a}"),
        ('Extract[<|"x" -> 1 + 1|>, Key["x"], Hold]', None, "Hold[2]"),
        ('Extract[<|"x" -> 1, "y" -> 1 + 1|>, "y", Hold]', None, "Hold[2]"),
        ('Extract[<|"x" -> 1, "y" -> 2|>, {"y"}]', None, "2"),
        ("Extract[{{1, 2}, {3, 4}}, {All, 1}, Hold]", None, "Hold[{1, 3}]"),
        (
            "Extract[{{1, 2}, {3, 4}}, {{1, All}, {2, 2}}, Hold]",
            None,
            "{Hold[{1, 2}], Hold[4]}",
        ),
        (
            "Extract[{a, b, c}, xpos]",
            (
                "Position specification xpos in Extract[{a, b, c}, xpos] is not applicable.",
            ),
            "Extract[{a, b, c}, xpos]",
        ),
        ("Extract[{a, b}, {}]", None, "{}"),
        ("Extract[{1 + 1, 2}, {{1}, {2}}]", None, "{2, 2}"),
        ("Extract[ByteArray[{1, 2}], {-1}]", None, "2"),
        (
            "Extract[{1, 2}, {3}]",
            ("Part 3 of {1, 2} does not exist.",),
            "Extract[{1, 2}, {3}]",
        ),
        (
            "Extract[{a, b, c}, {{1}, {1, 1}}]",
            ("Part specification is longer than depth of object.",),
            "Extract[{a, b, c}, {{1}, {1, 1}}]",
        ),
        # Extract[pos] is the operator form.
        ("Extract[{2}][{a, b, c}]", None, "b"),
        ("Extract[{a}]", None, "Extract[{a}]"),
        ("Extract[f[a, b]]", None, "Extract[f[a, b]]"),
        (
            "Extract[{a}, 1, h, 4]",
            ("Extract called with 4 arguments; 2 or 3 arguments are expected.",),
            "Extract[{a}, 1, h, 4]",
        ),
    ],
)
def test_extract(str_expr, expected_messages, str_expected):
    """Extract[expr, pos]: an empty position is the whole expression, and a
    position that is not there leaves Extract unevaluated."""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        expected_messages=expected_messages,
    )


def test_extract_arg_errors():
    check_arg_counts("Extract", "2 or 3 arguments are")


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected"),
    [
        ("pa = Range[8]; pa[[{2, 5, 6}]] = {-1, -2, -3}; pa", None, "{1, -1, 3, 4, -2, -3, 7, 8}"),
        ("pa = Range[8]; pa[[{2, 3}]] = 0; pa", None, "{1, 0, 0, 4, 5, 6, 7, 8}"),
        ("pa = Range[8]; pa[[{-1, 1}]] = {p, q}; pa", None, "{q, 2, 3, 4, 5, 6, 7, p}"),
        # A right side of another length is assigned to each part whole.
        (
            "pa = Range[4]; pa[[{1, 2}]] = {u, v, w}; pa",
            None,
            "{{u, v, w}, {u, v, w}, 3, 4}",
        ),
        ("pa = Range[3]; pa[[All]] = 0; pa", None, "{0, 0, 0}"),
        ("pa = Range[5]; pa[[2 ;; 4]] = {a, b, c}; pa", None, "{1, a, b, c, 5}"),
        ("pa = Range[3]; pa[[-1]] = z; pa", None, "{1, 2, z}"),
        ("pm = {{1, 2}, {3, 4}}; pm[[All, 1]] = {a, b}; pm", None, "{{a, 2}, {b, 4}}"),
        ("pm = {{1, 2}, {3, 4}}; pm[[All, 1]] = z; pm", None, "{{z, 2}, {z, 4}}"),
        ("pm = {{1, 2}, {3, 4}}; pm[[{1, 2}, 2]] = {pax, pay}; pm", None, "{{1, pax}, {3, pay}}"),
        ("pm = {{1, 2}, {3, 4}}; pm[[2, All]] = {pax, pay}; pm", None, "{{1, 2}, {pax, pay}}"),
        (
            "pm = {{1, 2}, {3, 4}}; pm[[{2, 1}, {1}]] = {{a}, {b}}; pm",
            None,
            "{{b, 2}, {a, 4}}",
        ),
        ("pg = f[a, b, c]; pg[[{1, 3}]] = {pax, pay}; pg", None, "f[pax, b, pay]"),
        ("pg = f[a]; pg[[0]] = h; pg", None, "h[a]"),
        # A part that does not exist leaves the whole value unchanged.
        (
            "pa = Range[3]; pa[[{1, 5}]] = 0; pa",
            ("Part 5 of {1, 2, 3} does not exist.",),
            "{1, 2, 3}",
        ),
        (
            "pa = Range[3]; pa[[2 ;; 5]] = 0; pa",
            ("Part 4 of {1, 2, 3} does not exist.",),
            "{1, 2, 3}",
        ),
        ("pl = {1, 2, 3}; pl[[0]] = pf; pl", None, "pf[1, 2, 3]"),
        ("pm = {{1, 2}, {3, 4}}; pm[[2, 0]] = phg; pm", None, "{{1, 2}, phg[3, 4]}"),
        ("pm = {{1, 2}, {3, 4}}; pm[[All, 0]] = ph; pm", None, "{ph[1, 2], ph[3, 4]}"),
        ("pk = pf[1, 2]; pk[[0]] = List; pk", None, "{1, 2}"),
        (
            "pa = {0, 0, 0}; pa[[{2, pf[pq]}]] = 5; pa",
            ("The expression {2, pf[pq]} cannot be used as a part specification.",),
            "{0, 0, 0}",
        ),
        (
            "pm = {{1, 2}, {3, 4}}; pm[[1, 5]] = 0; pm",
            ("Part 5 of {1, 2} does not exist.",),
            "{{1, 2}, {3, 4}}",
        ),
        ("pm = {{1, 2}, {3, 4}, {5, 6}}; pm[[-2 ;; -1, 2]] = 0; pm", None, "{{1, 2}, {3, 0}, {5, 0}}"),
        ("pa = Range[5]; pa[[-1 ;; 1 ;; -2]] = 0; pa", None, "{0, 2, 0, 4, 0}"),
        ("pa = Range[5]; pa[[4 ;; 2 ;; -1]] = {u, v, w}; pa", None, "{1, w, v, u, 5}"),
        # The value assigned to may be shared: only the variable changes.
        ("pa = {1, {2}}; pb = pa; pb[[2, 1]] = 9; {pa, pb}", None, "{{1, {2}}, {1, {9}}}"),
        (
            "pa = {{1, 2}, {3, 4}}; pb = pa; pb[[All, 1]] = 0; {pa, pb}",
            None,
            "{{{1, 2}, {3, 4}}, {{0, 2}, {0, 4}}}",
        ),
        (
            "pkd[] := (pw = {1, {2}}; pw[[2, 1]] = 5; pw); "
            "{pkd[], pkd[], DownValues[pkd] === "
            "{HoldPattern[pkd[]] :> (pw = {1, {2}}; pw[[2, 1]] = 5; pw)}}",
            None,
            "{{1, {5}}, {1, {5}}, True}",
        ),
    ],
)
def test_part_assignment(str_expr, expected_messages, str_expected):
    """Assigning to parts given by a list of positions, All, a Span or a
    negative position, at any depth."""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        expected_messages=expected_messages,
    )
