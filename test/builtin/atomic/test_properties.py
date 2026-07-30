# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.atomic.properties
"""
from test.helper import check_evaluation


def test_downvalues():
    for str_expr, str_expected, assert_fail_message in (
        (
            "DownValues[foo]={x_^2:>y}",
            "{x_ ^ 2 :> y}",
            "Issue #1251 part 1",
        ),
        (
            "DownValues[foo]",
            "{HoldPattern[x_ ^ 2] :> y}",
            "Check that we get the DownValue just assigned.",
        ),
        (
            'DownValues["foo"]',
            "{HoldPattern[x_ ^ 2] :> y}",
            "A string is allowed in as a DownValues argument.",
        ),
        (
            "PrependTo[DownValues[foo], {x_^3:>z}]",
            "{{x_ ^ 3 :> z}, HoldPattern[x_ ^ 2] :> y}",
            "Issue #1251 part 2",
        ),
        (
            "DownValues[foo]={x_^3:>y}",
            "{x_ ^ 3 :> y}",
            "Issue #1251 part 3",
        ),
    ):
        check_evaluation(
            str_expr,
            str_expected,
            assert_fail_message,
            to_string_expr=False,
            to_string_expected=False,
        )
