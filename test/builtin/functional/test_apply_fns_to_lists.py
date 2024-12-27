# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.functional.apply_fns_to_lists
"""

from test.helper import check_evaluation_as_in_cli

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
def test_apply_fns_to_lists(str_expr, msgs, str_expected, fail_msg):
    """functional.apply_fns_to_lists"""
    check_evaluation_as_in_cli(str_expr, str_expected, fail_msg, msgs)


def test_map_at():
    """functional.apply_fns_to_lists"""
    for str_expr, msgs, str_expected, fail_msg in (
        (
            "MapAt[f, {a, b, c, d}, 10]",
            ("Part {10} of {a, b, c, d} does not exist.",),
            "MapAt[f, {a, b, c, d}, 10]",
            "Indexing beyond the end of a list",
        ),
        (
            "MapAt[f, {a, b, c, d}, -9]",
            ("Part {-9} of {a, b, c, d} does not exist.",),
            "MapAt[f, {a, b, c, d}, -9]",
            "Indexing before the beginning of a list",
        ),
        (
            "MapAt[f, {a, b, c, d}, {1, 1}]",
            ("Part {1, 1} of {a, b, c, d} does not exist.",),
            "MapAt[f, {a, b, c, d}, {1, 1}]",
            "Indexing a dimension beyond the level of a list",
        ),
    ):
        check_evaluation_as_in_cli(str_expr, str_expected, fail_msg, msgs)
