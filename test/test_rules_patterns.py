# -*- coding: utf-8 -*-
from .helper import check_evaluation


def test_downvalues():
    for str_expr, str_expected, message in (
        (
            "DownValues[foo]={x_^2:>y}",
            "{x_ ^ 2 :> y}",
            "Issue #1251 part 1",
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
        check_evaluation(str_expr, str_expected, message)


def test_blank():
    for str_expr, str_expected, message in (
        (
            "g[i] /. _[i] :> a",
            "a",
            "Issue #203",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_complex_rule():
    for str_expr, str_expected, message in (
        (
            "a == d b + d c /. a_ x_ + a_ y_ -> a (x + y)",
            "a == (b + c) d",
            "Issue #212",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)
