"""
A builtin rule with a plain pattern, such as h[x___] or h[a_, b_Integer],
binds the names to the elements without the pattern matcher.
"""

from test.helper import check_evaluation, session

import pytest

from mathics.core.rules import simple_match, simple_pattern


def _pattern(text):
    return session.evaluate(f"HoldComplete[{text}]").elements[0]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("f[x___]", ("Global`f", (), ("Global`x", 0))),
        ("f[x__]", ("Global`f", (), ("Global`x", 1))),
        ("f[x_]", ("Global`f", (("Global`x", None),), None)),
        (
            "f[x_, y_Integer, z___]",
            (
                "Global`f",
                (("Global`x", None), ("Global`y", "System`Integer")),
                ("Global`z", 0),
            ),
        ),
        ("f[]", ("Global`f", (), None)),
        ("f[x___, y_]", None),
        ("f[x_, x_]", None),
        ("f[x_?EvenQ]", None),
        ("f[x_ /; x > 0]", None),
        ("f[x_:1]", None),
        ("f[g[x_]]", None),
        ("f[x_g[1]]", None),
        ("f[x___Integer]", None),
        ("f[x_][y_]", None),
        ("f[1]", None),
    ],
)
def test_simple_pattern(text, expected):
    result = simple_pattern(_pattern(text))
    if expected is None:
        assert result is None
        return
    head, singles, sequence = result
    singles = tuple(
        (name, None if blank_head is None else blank_head.get_name())
        for name, blank_head in singles
    )
    assert (head.get_name(), singles, sequence) == expected


@pytest.mark.parametrize(
    ("pattern", "expr", "expected"),
    [
        ("f[x___]", "f[1, 2]", {"Global`x": "Sequence[1, 2]"}),
        ("f[x___]", "f[1]", {"Global`x": "1"}),
        ("f[x___]", "f[]", {"Global`x": "Sequence[]"}),
        ("f[x__]", "f[]", None),
        ("f[x_, y_]", "f[1, 2]", {"Global`x": "1", "Global`y": "2"}),
        ("f[x_, y_]", "f[1, 2, 3]", None),
        ("f[x_, y_]", "g[1, 2]", None),
        ("f[x_Integer]", "f[1]", {"Global`x": "1"}),
        ("f[x_Integer]", "f[a]", None),
        ("f[x_, y___]", "f[1, 2, 3]", {"Global`x": "1", "Global`y": "Sequence[2, 3]"}),
    ],
)
def test_simple_match(pattern, expr, expected):
    vars = simple_match(simple_pattern(_pattern(pattern)), _pattern(expr))
    if expected is None:
        assert vars is None
        return
    assert {name: value for name, value in vars.items()}.keys() == expected.keys()
    for name, text in expected.items():
        assert vars[name].sameQ(_pattern(text)), (name, vars[name])


def test_builtin_rules_use_it():
    definition = session.definitions.get_definition("System`Plus")
    assert any(rule.simple for rule in definition.downvalues)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # Orderless and Flat heads: the elements come in their sorted order.
        ("Plus[c, a, b]", "a + b + c"),
        ("Plus[]", "0"),
        ("Plus[a]", "a"),
        ("Times[]", "1"),
        ("Times[3, a, 2]", "6 a"),
        ("Plus[Plus[a, b], c]", "a + b + c"),
        ("Max[]", "-Infinity"),
        # Fixed numbers of elements, with and without a head on the blank.
        ("Mod[17, 5]", "2"),
        ("Part[{a, b, c}, 2]", "b"),
        ('StringTake["abcd", 2]', '"ab"'),
        ("Mod[x, 5]", "Mod[x, 5]"),
        ("Max[3, 1, 2]", "3"),
        ("StringJoin[]", '""'),
        ('StringJoin["a", "b", "c"]', '"abc"'),
        ("f426[1, Sequence[2, 3]]", "f426[1, 2, 3]"),
        ("CompoundExpression[]", "Null"),
    ],
)
def test_results_unchanged(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
