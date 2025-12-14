# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.compilation.
"""

from test.helper import check_evaluation

import pytest

from mathics.compile import has_llvmlite


@pytest.mark.skipif(
    not has_llvmlite,
    reason="requires llvmlite",
)
@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "cf = Compile[{{x, _Real}}, Sin[x]]",
            None,
            "CompiledFunction[{x}, Sin[x], -CompiledCode-]",
            None,
        ),
        ("cf[1/2]", None, "0.479426", None),
        ("cf[4]", None, "-0.756802", None),
        (
            "cf[x]",
            ("Invalid argument x should be Integer, Real or boolean.",),
            "CompiledFunction[{x}, Sin[x], -CompiledCode-][x]",
            None,
        ),
        (
            "cf = Compile[{{x, _Real}, {x, _Integer}}, Sin[x + y]]",
            ("Duplicate parameter x found in {{x, _Real}, {x, _Integer}}.",),
            "Compile[{{x, _Real}, {x, _Integer}}, Sin[x + y]]",
            None,
        ),
        (
            "cf = Compile[{{x, _Real}, {y, _Integer}}, Sin[x + z]]",
            None,
            "CompiledFunction[{x, y}, Sin[x + z], -PythonizedCode-]",
            None,
        ),
        (
            "cf = Compile[{{x, _Real}, {y, _Integer}}, Sin[x + y]]",
            None,
            "CompiledFunction[{x, y}, Sin[x + y], -CompiledCode-]",
            None,
        ),
        ("cf[1, 2]", None, "0.14112", None),
        (
            "cf[x + y]",
            None,
            "CompiledFunction[{x, y}, Sin[x + y], -CompiledCode-][x + y]",
            None,
        ),
        (
            "cf = Compile[{{x, _Real}, {y, _Integer}}, If[x == 0.0 && y <= 0, 0.0, Sin[x ^ y] + 1 / Min[x, 0.5]] + 0.5];cf[0, -2]",
            None,
            "0.5",
            None,
        ),
        ("ClearAll[cf];", None, None, None),
    ],
)
def test_private_doctests_compilation(str_expr, msgs, str_expected, fail_msg):
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
