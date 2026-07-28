"test LaTex formatter"

# This test needs rewriting.
# It runs runs to_tex boxing on StandardForm
# when it should be pared with TeXForm instead.
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("testcase", "expected"),
    [
        (r"\[Alpha]", r"a"),  # In WMA, greek letters are encoded as its name
        (r"\[Pi]", "p"),  # character form.
        (r"\[AAcute]", "a'"),
        (r"\[Rule]", "->"),
        (r"\[RuleDelayed]", ":>"),
        (r"\[Or]", "||"),
        (r"\[And]", "&&"),
        (r"\[Not]", "!"),
        (r"\[Xor]", "xor"),
        (r"\[Equal]", "=="),
        (r"\[Equivalent]", "<=>"),
        (r"\[Implies]", "=>"),
        (r"\[GreaterEqual]", ">="),
    ],
)
def test_ascii_encodings(testcase, expected):
    expr = f'ToString["{testcase}", CharacterEncoding->"ASCII"]'
    check_evaluation(expr, expected, hold_expected=True)
    # FullForm always returns an ascii representation
    expr = f'"{testcase}"//FullForm'
    ff_expect = f'"{testcase}"'
    print(ff_expect)
    check_evaluation(expr, ff_expect, hold_expected=True)
