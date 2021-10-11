# -*- coding: utf-8 -*-
"""
Unit tests from builtins ... algebra.py
"""
from .helper import check_evaluation


def test_error_msgs():
    # TODO: check also the message.
    for str_expr, str_expected, err_msg in (
        ["x[[2]]", "x[[2]]", "Part specification is longer than depth of object."],
        [
            "{1, 2, 3, 4}[[1;;3;;-1]]",
            "{1, 2, 3, 4}[[1 ;; 3 ;; -1]]",
            "Cannot take positions 1 through 3 in {1, 2, 3, 4}.",
        ],
        [
            "{1, 2, 3, 4}[[3;;1]]",
            "{1, 2, 3, 4}[[3 ;; 1]]",
            "Cannot take positions 3 through 1 in {1, 2, 3, 4}.",
        ],
    ):
        check_evaluation(
            str_expr,
            str_expected,
            err_msg,
            to_string_expr=False,
            to_string_expected=False,
        )


def test_read_access():
    for str_expr, str_expected, msg in (
        [
            "A = {a, b, c, d}; A[[3]]",
            "c",
            "",
        ],
        [
            "{a, b, c}[[-2]]",
            "b",
            "",
        ],
        [
            "(a + b + c)[[2]]",
            "b",
            "",
        ],
        [
            "(a + b + c)[[0]]",
            "Plus",
            "",
        ],
        [
            "M = {{a, b}, {c, d}}; M[[1, 2]]",
            "b",
            "",
        ],
        [
            "{1, 2, 3, 4}[[2;;4]]",
            "{2, 3, 4}",
            "",
        ],
        [
            "{1, 2, 3, 4}[[2;;-1]]",
            "{2, 3, 4}",
            "",
        ],
        [
            "{a, b, c, d}[[{1, 3, 3}]]",
            "{a, c, c}",
            "",
        ],
        [
            "B = {{a, b, c}, {d, e, f}, {g, h, i}}; B[[;;, 2]]",
            "{b, e, h}",
            "",
        ],
        [
            "B = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}; B[[{1, 3}, -2;;-1]]",
            "{{2, 3}, {8, 9}}",
            "",
        ],
        [
            "{{a, b, c}, {d, e, f}, {g, h, i}}[[All, 3]]",
            "{c, f, i}",
            "",
        ],
        [
            "(a+b+c+d)[[-1;;-2]]",
            "0",
            "",
        ],
        [
            "{1,2,3,4,5}[[3;;1;;-1]]",
            "{3, 2, 1}",
            "",
        ],
        # MMA bug
        [
            "{1, 2, 3, 4, 5}[[;; ;; -1]]",
            "{5, 4, 3, 2, 1}",
            "",
        ],
        [
            "Range[11][[-3 ;; 2 ;; -2]]",
            "{9, 7, 5, 3}",
            "",
        ],
        [
            "Range[11][[-3 ;; -7 ;; -3]]",
            "{9, 6}",
            "",
        ],
        [
            "Range[11][[7 ;; -7;; -2]]",
            "{7, 5}",
            "",
        ],
        [
            "A[[1]] + B[[2]] + C[[3]] // Hold // FullForm",
            "Hold[Plus[Part[A, 1], Part[B, 2], Part[C, 3]]]",
            "",
        ],
    ):
        print("\n\n", str_expr, "\n", str_expected, "\n", msg)
        check_evaluation(
            str_expr, str_expected, msg, to_string_expr=False, to_string_expected=False
        )


def test_weird():
    for str_expr, str_expected, msg in (
        # When an element is assigned, the element is what change, not the variable.
        ["B={a,b,c}; B[[1]]=3;{B,a}", "{{3, b, c}, a}", ""],
        ["B={a,b,c}; B={1,2,3};{B,a}", "{{1, 2, 3}, a}", ""],
        ["{a,b,c}[[1]]=3;a", "a", ""],
        ["{a,b,c}={1,2,3};a", "1", ""],
    ):
        print("\n\n", str_expr, "\n", str_expected, "\n")
        check_evaluation(str_expr, str_expected)


def test_write_access():
    for str_expr, str_expected, msg in (
        # The test that motivates all of this: this fails if Symbols are singletonized...
        ["B={a,b,c}; {B[[2]],B[[3]],B[[1]]}=B;B", "{c, a, b}", ""],
        # The test included in Parts
        [
            "B = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}; B[[;;, 2]] = {10, 11, 12}",
            "{10, 11, 12}",
            "",
        ],
        [
            "B",
            "{{1, 10, 3}, {4, 11, 6}, {7, 12, 9}}",
            "",
        ],
        [
            "B[[;;, 3]] = 13",
            "13",
            "",
        ],
        [
            "B",
            "{{1, 10, 13}, {4, 11, 13}, {7, 12, 13}}",
            "",
        ],
        [
            "B[[1;;-2]] = t",
            "t",
            "",
        ],
        [
            "B",
            "{t, t, {7, 12, 13}}",
            "",
        ],
        [
            "F = Table[i*j*k, {i, 1, 3}, {j, 1, 3}, {k, 1, 3}]; F[[;; All, 2 ;; 3, 2]] = t; F",
            "{{{1, 2, 3}, {2, t, 6}, {3, t, 9}}, {{2, 4, 6}, {4, t, 12}, {6, t, 18}}, {{3, 6, 9}, {6, t, 18}, {9, t, 27}}}",
            "",
        ],
        [
            "F[[;; All, 1 ;; 2, 3 ;; 3]] = k; F",
            "{{{1, 2, k}, {2, t, k}, {3, t, 9}}, {{2, 4, k}, {4, t, k}, {6, t, 18}}, {{3, 6, k}, {6, t, k}, {9, t, 27}}}",
            "",
        ],
        [
            "a = {2,3,4}; i = 1; a[[i]] = 0; a",
            "{0, 3, 4}",
            "",
        ],
        [
            "F=Table[Q[i,j,k],{i,3},{j,3},{k,3}]; F[[2;;,2;;,3]]=t; F",
            "{{{Q[1, 1, 1], Q[1, 1, 2], Q[1, 1, 3]}, {Q[1, 2, 1], Q[1, 2, 2], Q[1, 2, 3]}, {Q[1, 3, 1], Q[1, 3, 2], Q[1, 3, 3]}}, {{Q[2, 1, 1], Q[2, 1, 2], Q[2, 1, 3]}, {Q[2, 2, 1], Q[2, 2, 2], t}, {Q[2, 3, 1], Q[2, 3, 2], t}}, {{Q[3, 1, 1], Q[3, 1, 2], Q[3, 1, 3]}, {Q[3, 2, 1], Q[3, 2, 2], t}, {Q[3, 3, 1], Q[3, 3, 2], t}}}",
            "",
        ],
        [
            "F=Table[Q[i,j,k],{i,3},{j,3},{k,3}]; F[[2;;,2;;]]=t; F",
            "{{{Q[1, 1, 1], Q[1, 1, 2], Q[1, 1, 3]}, {Q[1, 2, 1], Q[1, 2, 2], Q[1, 2, 3]}, {Q[1, 3, 1], Q[1, 3, 2], Q[1, 3, 3]}}, {{Q[2, 1, 1], Q[2, 1, 2], Q[2, 1, 3]}, t, t}, {{Q[3, 1, 1], Q[3, 1, 2], Q[3, 1, 3]}, t, t}}",
            "",
        ],
    ):
        print("\n\n", str_expr, "\n", str_expected, "\n")
        check_evaluation(str_expr, str_expected, msg)


def test_sparse():
    for str_expr, str_expected in (
        ["SparseArray[{{0, a}, {b, 0}}]//Normal", "{{0,a},{b,0}}"],
    ):
        check_evaluation(
            str_expr, str_expected, to_string_expr=False, to_string_expected=False
        )
