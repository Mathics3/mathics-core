from test.helper import check_evaluation, evaluate, session

import pytest

from mathics.core.convert.regex import to_regex


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Blank[]", r"(.|\n)", "Blank"),
        ("A", None, "an undefined symbol"),
        ("WhitespaceCharacter", r"\s", "white space"),
        ("LetterCharacter", r"[^\W_0-9]", "a letter or a character"),
    ],
)
def test_to_regex(str_expr, str_expected, msg):
    expr = evaluate(str_expr)
    if msg:
        assert to_regex(expr) == str_expected, msg
    else:
        assert to_regex(expr) == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure", "msg"),
    [
        (None, None, None, None),
        #
        (
            'StringSplit["ab23c", RegularExpression[2]]',
            "StringSplit[ab23c, RegularExpression[2]]",
            (
                "Element RegularExpression[2] is not a valid string or pattern "
                "element in RegularExpression[2]."
            ),
            "an integer is not a valid argument for RegularExpression",
        ),
        #
        (
            'StringSplit["ab23c", RegularExpression["[0-9]++)"]]',
            "StringSplit[ab23c, RegularExpression[[0-9]++)]]",
            (
                "Element RegularExpression[[0-9]++)] is not a valid string "
                "or pattern element in RegularExpression[[0-9]++)]."
            ),
            "wrong regex",
        ),
        #
    ],
)
def test_regex_err_msg(str_expr, str_expected, failure, msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        hold_expected=True,
        to_string_expected=True,
        expected_messages=[failure],
        failure_message=msg,
    )
