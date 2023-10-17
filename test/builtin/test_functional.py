# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.functional
"""

import sys
import time
from test.helper import check_evaluation, evaluate, session

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("ClearAll[f, g, h,x,y,a,b,c];", None, None, None),
        (
            "Apply[f, {a, b, c}, x+y]",
            ("Level specification x + y is not of the form n, {n}, or {m, n}.",),
            "Apply[f, {a, b, c}, x + y]",
            None,
        ),
        (
            "Map[f, expr, a+b, Heads->True]",
            ("Level specification a + b is not of the form n, {n}, or {m, n}.",),
            "Map[f, expr, a + b, Heads -> True]",
            None,
        ),
        (
            "MapIndexed[f, {1, 2}, a+b]",
            ("Level specification a + b is not of the form n, {n}, or {m, n}.",),
            "MapIndexed[f, {1, 2}, a + b]",
            None,
        ),
        (
            "MapThread[f, {{a, b}, {c, d}}, {1}]",
            (
                "Non-negative machine-sized integer expected at position 3 in MapThread[f, {{a, b}, {c, d}}, {1}].",
            ),
            "MapThread[f, {{a, b}, {c, d}}, {1}]",
            None,
        ),
        (
            "MapThread[f, {{a, b}, {c, d}}, 2]",
            (
                "Object {a, b} at position {2, 1} in MapThread[f, {{a, b}, {c, d}}, 2] has only 1 of required 2 dimensions.",
            ),
            "MapThread[f, {{a, b}, {c, d}}, 2]",
            None,
        ),
        (
            "MapThread[f, {{a}, {b, c}}]",
            (
                "Incompatible dimensions of objects at positions {2, 1} and {2, 2} of MapThread[f, {{a}, {b, c}}]; dimensions are 1 and 2.",
            ),
            "MapThread[f, {{a}, {b, c}}]",
            None,
        ),
        ("MapThread[f, {}]", None, "{}", None),
        ("MapThread[f, {a, b}, 0]", None, "f[a, b]", None),
        (
            "MapThread[f, {a, b}, 1]",
            (
                "Object a at position {2, 1} in MapThread[f, {a, b}, 1] has only 0 of required 1 dimensions.",
            ),
            "MapThread[f, {a, b}, 1]",
            None,
        ),
        (
            "MapThread[f, {{{a, b}, {c}}, {{d, e}, {f}}}, 2]",
            None,
            "{{f[a, d], f[b, e]}, {f[c, f]}}",
            "Behaviour extends MMA",
        ),
        (
            "Scan[Print, f[g[h[x]]], 2]",
            (
                "h[x]",
                "g[h[x]]",
            ),
            None,
            None,
        ),
        (
            "Scan[Print][{1, 2}]",
            (
                "1",
                "2",
            ),
            None,
            None,
        ),
        ("Scan[Return, {1, 2}]", None, "1", None),
    ],
)
def test_private_doctests_apply_fns_to_lists(str_expr, msgs, str_expected, fail_msg):
    """functional.apply_fns_to_lists"""

    def eval_expr(expr_str):
        query = session.evaluation.parse(expr_str)
        res = session.evaluation.evaluate(query)
        session.evaluation.stopped = False
        return res

    res = eval_expr(str_expr)
    if msgs is None:
        assert len(res.out) == 0
    else:
        assert len(res.out) == len(msgs)
        for li1, li2 in zip(res.out, msgs):
            assert li1.text == li2

    assert res.result == str_expected


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("g[x_,y_] := x+y;g[Sequence@@Slot/@Range[2]]&[1,2]", None, "#1 + #2", None),
        ("Evaluate[g[Sequence@@Slot/@Range[2]]]&[1,2]", None, "3", None),
        ("# // InputForm", None, "#1", None),
        ("#0 // InputForm", None, "#0", None),
        ("## // InputForm", None, "##1", None),
        ("Clear[g];", None, "Null", None),
    ],
)
def test_private_doctests_application(str_expr, msgs, str_expected, fail_msg):
    """functional.application"""
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
        ("FixedPoint[f, x, 0]", None, "x", None),
        (
            "FixedPoint[f, x, -1]",
            ("Non-negative integer expected.",),
            "FixedPoint[f, x, -1]",
            None,
        ),
        ("FixedPoint[Cos, 1.0, Infinity]", None, "0.739085", None),
        ("FixedPointList[f, x, 0]", None, "{x}", None),
        (
            "FixedPointList[f, x, -1]",
            ("Non-negative integer expected.",),
            "FixedPointList[f, x, -1]",
            None,
        ),
        ("Last[FixedPointList[Cos, 1.0, Infinity]]", None, "0.739085", None),
    ],
)
def test_private_doctests_functional_iteration(str_expr, msgs, str_expected, fail_msg):
    """functional.functional_iteration"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
