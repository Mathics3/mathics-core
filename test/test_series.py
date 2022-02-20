# -*- coding: utf-8 -*-
"""
Unit tests from builtin ... calculus.py specific for Series
"""

from .helper import check_evaluation
import pytest


def test_seriesdata_product():
    for str_expr, str_expected, message in (
        (
            "3 * Series[F[x],{x,a,2}]//FullForm",
            "SeriesData[x, a, {3* F[a], 3* F'[a],3/2 F''[a]}, 0, 3,1]//FullForm",
            "Product of a series with a number",
        ),
        (
            "g[u] Series[F[x],{x,a,2}]//FullForm",
            "SeriesData[x, a, {g[u]* F[a], g[u]* F'[a], g[u]/2 F''[a]}, 0, 3,1]//FullForm",
            "Product of an expression free of x",
        ),
        (
            "Series[Exp[x], {x, 0, 5}] * Series[Exp[-x], {x, 0, 3}]//FullForm",
            "SeriesData[x, 0, {1}, 0, 4, 1]//FullForm",
            "product of series in the same variable, around the same neighbourhood",
        ),
        (
            "Series[Exp[x],{x,0,2}]*Series[Exp[y],{y,0,2}]//Normal//ExpandAll",
            "1 + y + y^2/2 + x^2*(1/2 + y/2 + y^2/4) + x*(1 + y + y^2/2)//ExpandAll",
            "product of series in different variables",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_seriesdata_operations_normal():
    for str_expr, str_expected, message in (
        (
            "Series[Exp[y], {y, 0, 2}] - 1 -y -y ^ 2 / 2 -10 y ^ 3//Normal",
            "0",
            "Difference of series with a polynomial",
        ),
        (
            "Series[Exp[y], {y, 0, 2}] - Exp[y] - a//Normal",
            "-a",
            "Difference of series with a function",
        ),
        (
            "Series[Exp[y],{y,0,2}]-Series[Exp[x],{x,0,3}]//Normal",
            "-x - x^2/2 - x^3/6 + y + y^2/2",
            "Difference of series in different variables",
        ),
        (
            "Series[Exp[x],{x,0,2}]-Series[Exp[x],{x,0,4}]//Normal",
            "0",
            "Difference of series in the same variable",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_derivatives():
    for str_expr, str_expected, message in (
        (
            "D[Series[F[x], {x, 0, 2}], x]//FullForm",
            "SeriesData[x, 0, List[Derivative[1][F][0], Derivative[2][F][0]], 0, 2, 1]//FullForm",
            "Derivative regarding x of a series in x around 0",
        ),
        (
            "D[Series[F[x],{x,0,2}], y]",
            "0",
            "Derivative regarding y for a series independent on y",
        ),
        (
            "D[Series[F[x],{x, g[y], 2}], y]//FullForm",
            "SeriesData[x, g[y], {}, 2, 2, 1]//FullForm",
            "Derivative regarding x of a series in x around g[y].",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_series_show():
    for str_expr, str_expected, message in (
        (
            "Series[Exp[x],{x,0,2}]",
            '"1 + x + 1 / 2 x ^ 2 + O[x] ^ 3"',
            "Series in one variable, around 0",
        ),
        (
            "Series[Exp[x],{x, 1, 2}]",
            '"E + E (x - 1) + E / 2 (x - 1) ^ 2 + O[x - 1] ^ 3"',
            "Series in one variable, around 1",
        ),
        (
            "Series[Exp[x],{x, a, 2}]",
            '"E ^ a + E ^ a (x - a) + E ^ a / 2 (x - a) ^ 2 + O[x - a] ^ 3"',
            "Series in one variable, around a",
        ),
        (
            "Series[F[x, y],{x, b, 2},{y, a, 1}]//FullForm",
            "SeriesData[x, b, {SeriesData[y, a, {F[b, a], Derivative[0, 1][F][b, a]}, 0, 2, 1], SeriesData[y, a, {Derivative[1, 0][F][b, a], Derivative[1, 1][F][b, a]}, 0, 2, 1], SeriesData[y, a, {Derivative[2, 0][F][b, a]/2, Derivative[2, 1][F][b, a]/2}, 0, 2, 1]}, 0, 3, 1]//FullForm",
            "Series in two variable, around a",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_seriesdata_operations():
    for str_expr, str_expected, message in (
        (
            "Series[Exp[y],{y,0,2}]-Series[Exp[x],{x,0,3}]//FullForm",
            "SeriesData[x, 0, {SeriesData[y, 0, {1, 1/2}, 1, 3, 1], -1, -1/2, -1/6}, 0, 4, 1]//FullForm",
            "Sum and difference of series",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


# To fix:


@pytest.mark.xfail
def test_todo_seriesdata():
    for str_expr, str_expected, message in (
        (
            "Series[F[x,z],{x, g[y], 2}, {z, a, 2}]//FullForm",
            "",
            "Iterated Series",
        ),
        (
            "D[Series[F[x,z],{x, g[y], 2}, {z, a, 2}], y]//FullForm",
            "SeriesData[x, g[y], {SeriesData[z, a, {}, 3, 3, 1], SeriesData[z, a, {}, 3, 3, 1]}, 0, 2, 1]//FullForm",
            "Derivative regarding x of an iterated series in x and z around (g[y], a).",
        ),
        (
            "Series[Exp[x], {x, 0, 2}] * (x ^ (1 / 3))",
            '"x ^ (1 / 3) + x ^ (2 / 3) + 1 / 2 x + O[x] ^ (10 / 3)"',
            "Product of a Series with a power of the variable",
        ),
        (
            "Series[Exp[x],{x,0,4}]Series[Exp[-x],{x,0,6}]",
            '"1 + O[x] ^ 5"',
            "Product of two series in the same variable.",
        ),
        (
            "Series[Exp[x],{x, 0, 2}]Series[Exp[-y],{y, 0,2}]",
            '"(1 + x + 1 / 2 x ^ 2 + O[x] ^ 3) (1 - y + 1 / 2 y ^ 2 + O[y] ^ 3)"',
            "Product of series in different variables",
        ),
        (
            "Series[Exp[x],{x, 0, 2}]Series[Exp[-y],{y, 0,2}]//Normal",
            "(1 + x + x ^ 2 / 2) (1 - y + y ^ 2 / 2)",
            "Product of series in two different variables, normal",
        ),
        (
            "Series[Exp[x-y],{x, 0, 3},{y, 0 , 3}]//FullForm",
            """SeriesData[x, 0, {
                  SeriesData[y, 0, {1, -1, 1/2, -1/6}, 0, 4, 1], 
                  SeriesData[y, 0, {1, -1, 1/2, -1/6}, 0, 4, 1], 
                  SeriesData[y, 0, {1/2, -1/2, 1/4, -1/12}, 0, 4, 1], 
                  SeriesData[y, 0, {1/6, -1/6, 1/12, -1/36}, 0, 4, 1]}, 0, 4, 1]//FullForm
            """,
            "Series in two variables",
        ),
        (
            "Series[Exp[x],{x,0,3}]-1-x-x^2",
            '"(-1 / 2) x ^ 2 + 1 / 6 x ^ 3 + O[x] ^ 4"',
            "Sum and difference of series",
        ),
        (
            "(Series[Exp[x-y],{x, 0, 2},{y, 0 , 2}]//Normal)-(1-(x-y))// ExpandAll",
            "1 + (x - y) + (x-y)^2 / 2 //ExpandAll",
            "Series in two variables, normal",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)
