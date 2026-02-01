# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.messages.
"""


from test.helper import check_evaluation_as_in_cli

import pytest

print("\n***Rocky will address this soon.***")


@pytest.mark.skip(reason="Rocky will address this soon")
@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Check[1^0, err]", None, "1", None),
        (
            "Check[1 + 2]",
            ("Check called with 1 argument; 2 or more arguments are expected.",),
            "Check[1 + 2]",
            None,
        ),
        (
            "Check[1 + 2, err, 3 + 1]",
            (
                "Message name 3 + 1 is not of the form symbol::name or symbol::name::language.",
            ),
            "Check[1 + 2, err, 3 + 1]",
            None,
        ),
        (
            "Check[1 + 2, err, hello]",
            (
                "Message name hello is not of the form symbol::name or symbol::name::language.",
            ),
            "Check[1 + 2, err, hello]",
            None,
        ),
        (
            "Check[1/0, err, Compile::cpbool]",
            ("Infinite expression 1 / 0 encountered.",),
            "ComplexInfinity",
            None,
        ),
        (
            "Check[{0^0, 1/0}, err]",
            (
                "Indeterminate expression 0 ^ 0 encountered.",
                "Infinite expression 1 / 0 encountered.",
            ),
            "err",
            None,
        ),
        (
            "Check[0^0/0, err, Power::indet]",
            (
                "Indeterminate expression 0 ^ 0 encountered.",
                "Infinite expression 1 / 0 encountered.",
            ),
            "err",
            None,
        ),
        (
            "Check[{0^0, 3/0}, err, Power::indet]",
            (
                "Indeterminate expression 0 ^ 0 encountered.",
                "Infinite expression 1 / 0 encountered.",
            ),
            "err",
            None,
        ),
        (
            "Check[1 + 2, err, {a::b, 2 + 5}]",
            (
                "Message name 2 + 5 is not of the form symbol::name or symbol::name::language.",
            ),
            "Check[1 + 2, err, {a::b, 2 + 5}]",
            None,
        ),
        ("Off[Power::infy];Check[1 / 0, err]", None, "ComplexInfinity", None),
        (
            "On[Power::infy];Check[1 / 0, err]",
            ("Infinite expression 1 / 0 encountered.",),
            "err",
            None,
        ),
        (
            'Get["nonexistent_file.m"]',
            ("Cannot open nonexistent_file.m.",),
            "$Failed",
            None,
        ),
        (
            "Off[1]",
            (
                "Message name 1 is not of the form symbol::name or symbol::name::language.",
            ),
            None,
            None,
        ),
        ("Off[Message::name, 1]", None, None, None),
        (
            "On[Power::infy, Power::indet, Syntax::com];Quiet[expr, All, All]",
            ("Arguments 2 and 3 of Quiet[expr, All, All] should not both be All.",),
            "Quiet[expr, All, All]",
            None,
        ),
        (
            "{1,}",
            (
                'Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "").',
            ),
            "{1, Null}",
            None,
        ),
        (
            "{, 1}",
            (
                'Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "").',
            ),
            "{Null, 1}",
            None,
        ),
        (
            "{,,}",
            (
                'Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "").',
                'Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "").',
                'Warning: comma encountered with no adjacent expression. The expression will be treated as Null (line 1 of "").',
            ),
            "{Null, Null, Null}",
            None,
        ),
        # TODO:
        #  ("On[f::x]", ("Message f::x not found.",), None, None),
    ],
)
def test_private_doctests_messages(str_expr, msgs, str_expected, fail_msg):
    """These tests check the behavior the module messages"""
    check_evaluation_as_in_cli(str_expr, str_expected, fail_msg, msgs)
