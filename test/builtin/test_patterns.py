# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.patterns.
"""

from test.helper import check_evaluation


def test_blank():
    for str_expr, str_expected, message in (
        (
            "g[i] /. _[i] :> a",
            "a",
            "Issue #203",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_replace_all():
    for str_expr, str_expected, message in (
        (
            "a == d b + d c /. a_ x_ + a_ y_ -> a (x + y)",
            "a == (b + c) d",
            "Issue #212",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_rule_repl_cond():
    for str_expr, str_expected, message in (
        # For Rules, replacement is not evaluated
        (
            "f[x]/.(f[u_]->u^2/; u>3/; u>2)",
            "x^2/; x>3/; x>2",
            "conditions are not evaluated in Rule",
        ),
        (
            "f[4]/.(f[u_]->u^2/; u>3/; u>2)",
            "16 /; 4 > 3 /; 4 > 2",
            "still not evaluated, even if values are provided, due to the HoldAll attribute.",
        ),
        # However, for delayed rules, the behavior is different:
        # Conditions defines if the rule is applied
        # and do not appears in the result.
        ("f[x]/.(f[u_]:>u^2/; u>3/; u>2)", "f[x]", "conditions are not evaluated"),
        ("f[4]/.(f[u_]:>u^2/; u>3/; u>2)", "16", "both conditions are True"),
        (
            "f[2.5]/.(f[u_]:>u^2/; u>3/; u>2)",
            "f[2.5]",
            "just the first condition is True",
        ),
        ("f[1.]/.(f[u_]:>u^2/; u>3/; u>2)", "f[1.]", "Both conditions are False"),
    ):
        check_evaluation(str_expr, str_expected, message)
