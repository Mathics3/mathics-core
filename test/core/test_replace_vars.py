# -*- coding: utf-8 -*-
"""
Expression.replace_vars keeps the subexpressions in which no variable occurs.
"""

import pytest

from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from test.helper import check_evaluation, session


def test_unchanged_subexpressions_are_kept():
    x, y, f = Symbol("Global`x"), Symbol("Global`y"), Symbol("Global`f")
    data = session.evaluate("Table[{i, i + 1}, {i, 10}]")
    expr = Expression(f, data, x)

    new = expr.replace_vars({"Global`x": y})
    assert new is not expr
    assert new.elements[1] is y
    # data has no x: it is the same object, with what is known about it.
    assert new.elements[0] is data
    assert new.elements[0].elements_properties is data.elements_properties

    # Nothing to replace anywhere: the expression itself comes back.
    assert expr.replace_vars({"Global`z": y}) is expr
    assert data.replace_vars({"Global`x": y}) is data


def test_function_parameters_still_renamed():
    x, y = Symbol("Global`x"), Symbol("Global`y")
    fn = Expression(
        Symbol("System`Function"),
        ListExpression(x),
        Expression(Symbol("System`Plus"), x, y),
    )
    new = fn.replace_vars({"Global`y": Symbol("Global`z")})
    assert new is not fn
    assert str(new.elements[0]) == "{Global`x$}"


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        # A list passed to a function and used in a loop inside Module.
        (
            "rvW[x_] := Module[{i = 0, s = 0}, While[i < 5, i++; s += x[[i]]]; s]; "
            "rvW[Range[10]]",
            "15",
            None,
        ),
        # Module renames its variables wherever they occur, next to
        # subexpressions that it keeps as they are.
        (
            "rvR = Module[{a = 1}, {a, {1, 2}, Hold[a + b]}]; "
            "{rvR[[1]], rvR[[2]], Extract[rvR, {3, 1, 1}, HoldForm] =!= HoldForm[a]}",
            "{1, {1, 2}, True}",
            None,
        ),
        # A right-hand side without pattern variables is shared by every
        # result; changing one result must not change the rule.
        (
            "rvG[_] := {1, 2, 3}; rvR = rvG[1]; rvR[[1]] = 5; {rvR, rvG[2]}",
            "{{5, 2, 3}, {1, 2, 3}}",
            None,
        ),
        (
            "rvH[_] := {{1, 2}, {3, 4}}; rvR = rvH[1]; rvR[[2, 1]] = 7; {rvR, rvH[2]}",
            "{{{1, 2}, {7, 4}}, {{1, 2}, {3, 4}}}",
            None,
        ),
        (
            "rvK[_] := {1, 2, 3}; rvR = rvK[1]; AppendTo[rvR, 4]; {rvR, rvK[2]}",
            "{{1, 2, 3, 4}, {1, 2, 3}}",
            None,
        ),
        # The right-hand side has no pattern variable in it, so it is shared;
        # the options of each call stay with that call, also when the same
        # rule is applied again with other options while it is evaluated.
        (
            "Options[rvOp] = {rvA -> 1}; rvN = 0; "
            "rvOp[_, OptionsPattern[]] := {OptionValue[rvA], rvNested[], OptionValue[rvA]}; "
            "rvNested[] := If[rvN++ < 1, rvOp[0, rvA -> 2], 0]; "
            "{rvOp[0], rvOp[0, rvA -> 3], rvOp[0]}",
            "{{1, {2, 0, 2}, 1}, {3, 0, 3}, {1, 0, 1}}",
            None,
        ),
    ],
)
def test_evaluation_with_kept_subexpressions(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)
    # The session is shared with the other test files.
    session.evaluate('ClearAll["Global`rv*"]')
