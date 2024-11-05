# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.diffeqns
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ## FIXME: sympy solves this as `Function[{x}, C[1] + Integrate[ArcSin[f[2 x]], x]]`
        #        (
        #            "Attributes[f] = {HoldAll}; DSolve[f[x + x] == Sin[f'[x]], f, x]",
        #            (
        #                (
        #                    "To avoid possible ambiguity, the arguments of the dependent "
        #                    "variable in f[x + x] == Sin[f'[x]] should literally match "
        #                    "the independent variables."
        #                ),
        #            ),
        #            "DSolve[f[x + x] == Sin[f'[x]], f, x]",
        #            "sympy solves this as `Function[{x}, C[1] + Integrate[ArcSin[f[2 x]], x]]`",
        #        ),
        #        """
        #        (
        #            "Attributes[f] = {}; DSolve[f[x + x] == Sin[f'[x]], f, x]",
        #            (
        #                (
        #                    "To avoid possible ambiguity, the arguments of the dependent "
        #                    "variable in f[2 x] == Sin[f'[x]] should literally match "
        #                    "the independent variables."
        #                ),
        #            ),
        #            "DSolve[f[2 x] == Sin[f'[x]], f, x]",
        #            None,
        #        ),
        (
            "DSolve[f'[x] == f[x], f, x] // FullForm",
            None,
            "{{Rule[f, Function[{x}, Times[C[1], Power[E, x]]]]}}",
            None,
        ),
        (
            "DSolve[f'[x] == f[x], f, x] /. {C[1] -> 1}",
            None,
            "{{f -> Function[{x}, 1 E ^ x]}}",
            None,
        ),
        (
            "DSolve[f'[x] == f[x], f, x] /. {C -> D}",
            None,
            "{{f -> Function[{x}, D[1] E ^ x]}}",
            None,
        ),
        (
            "DSolve[f'[x] == f[x], f, x] /. {C[1] -> C[0]}",
            None,
            "{{f -> Function[{x}, C[0] E ^ x]}}",
            None,
        ),
        (
            "DSolve[f[x] == 0, f, {}]",
            ("{} cannot be used as a variable.",),
            "DSolve[f[x] == 0, f, {}]",
            None,
        ),
        # # Order of arguments shoudn't matter
        (
            "DSolve[D[f[x, y], x] == D[f[x, y], y], f, {x, y}]",
            None,
            "{{f -> Function[{x, y}, C[1][-x - y]]}}",
            None,
        ),
        (
            "DSolve[D[f[x, y], x] == D[f[x, y], y], f[x, y], {x, y}]",
            None,
            "{{f[x, y] -> C[1][-x - y]}}",
            None,
        ),
        (
            "DSolve[D[f[x, y], x] == D[f[x, y], y], f[x, y], {y, x}]",
            None,
            "{{f[x, y] -> C[1][-x - y]}}",
            None,
        ),
        (
            "DSolve[\\[Gamma]'[x] == 0, \\[Gamma], x]",
            None,
            "{{γ -> Function[{x}, C[1]]}}",
            "sympy #11669 test",
        ),
    ],
)
def test_private_doctests_diffeqns(str_expr, msgs, str_expected, fail_msg):
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
