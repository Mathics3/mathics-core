"""
Test builtin function Characters[]
"""

import time
from test.helper import check_evaluation, evaluate
from typing import Optional

import pytest

from mathics.core.atoms import String
from mathics.core.list import ListExpression
from mathics.session import MathicsSession

# Set up a Mathics session with definitions.
# For consistency set the character encoding ASCII which is
# the lowest common denominator available on all systems.
session = MathicsSession(character_encoding="ASCII")


def check_characters_evaluation(
    str_expr: str,
    expected: ListExpression,
    failure_message: Optional[str] = "",
):
    """
    Helper function to test Mathics expression against
    its results.

    Compares the expressions represented by ``str_expr`` and  ``str_expected`` by
    evaluating the first, and optionally, the second. If omitted, `str_expected`
    is assumed to be `"Null"`.

    str_expr: The expression to be tested. If its value is ``None``, the session is
              reset.
              At the beginning of each set of pytests, it is important to call
              ``check_evaluation(None)`` to avoid that definitions introduced by
              other tests affect the results.

    str_expected: The expected result. The value ``None`` is equivalent to ``"Null"``.

    failure_message: message shown in case of failure. Use "" for no failure message.
    """
    result = evaluate(str_expr)

    print(time.asctime())
    if failure_message:
        print(f"got: \n{result}\nexpect:\n{expected}\n -- {failure_message}")
        assert result == expected, failure_message
    else:
        print(f"got: \n{result}\nexpect:\n{expected}\n --")
        assert result == expected


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            r'Characters["\\\` "]',
            None,
            ListExpression(String("\\"), String(r"\`"), String(" ")),
            "Characters[] with an escape sequence that should be treated as one character",
        ),
    ],
)
def test_characters_with_escape_sequence(str_expr, msgs, str_expected, fail_msg):
    check_characters_evaluation(
        str_expr,
        str_expected,
        failure_message=fail_msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "Characters[]",
            ["Characters called with 0 arguments; 1 argument is expected."],
            "Characters[]",
            "Characters argument checking",
        ),
    ],
)
def test_characters(str_expr, msgs, str_expected, fail_msg):
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
