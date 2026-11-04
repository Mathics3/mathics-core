"""
A builtin rule h[x___] binds x to all the elements without the pattern
matcher.
"""

from test.helper import check_evaluation, session

import pytest

from mathics.core.rules import all_elements_pattern


def _pattern(text):
    return session.evaluate(f"Hold[{text}]").elements[0]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("f[x___]", ("Global`f", "Global`x", 0)),
        ("f[x__]", ("Global`f", "Global`x", 1)),
        ("f[x_]", None),
        ("f[x___Integer]", None),
        ("f[x___, y_]", None),
        ("f[g[x___]]", None),
        ("f[x___][y___]", None),
        ("f[]", None),
    ],
)
def test_all_elements_pattern(text, expected):
    result = all_elements_pattern(_pattern(text))
    if expected is None:
        assert result is None
    else:
        head, name, least = result
        assert (head.get_name(), name, least) == expected


def test_builtin_rules_use_it():
    definition = session.definitions.get_definition("System`Plus")
    assert any(rule.all_elements for rule in definition.downvalues)


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
        ("Max[3, 1, 2]", "3"),
        ("StringJoin[]", '""'),
        ('StringJoin["a", "b", "c"]', '"abc"'),
        ("f426[1, Sequence[2, 3]]", "f426[1, 2, 3]"),
        ("CompoundExpression[]", "Null"),
    ],
)
def test_results_unchanged(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
