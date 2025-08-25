# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.atomic.strings.

In particular, Alphabet
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg", "warnings"),
    [
        (
            'Complement[Alphabet["Swedish"], Alphabet["English"]]',
            r'{"à", "ä", "å", "é", "ö"}',
            "Alphabet test",
            tuple(),
        ),
        (
            'Alphabet["Elvish45"]',
            'Alphabet["Elvish45"]',
            "Alphabet for a made-up language",
            ("The alphabet Elvish45 is not known or not available.",),
        ),
    ],
)
def test_alphabet(str_expr, str_expected, fail_msg, warnings):
    check_evaluation(
        str_expr, str_expected, failure_message="", expected_messages=warnings
    )


@pytest.mark.parametrize(
    ("str_expr", "warnings", "str_expected"),
    [
        (
            "LetterNumber[4]",
            ("The argument 4 is not a string.",),
            "LetterNumber[4]",
        ),
        ('StringContainsQ["Hello", "o"]', None, "True"),
        ('StringContainsQ["a"]["abcd"]', None, "True"),
        ('StringContainsQ["Mathics", "ma", IgnoreCase -> False]', None, "False"),
        ('StringContainsQ["Mathics", "MA" , IgnoreCase -> True]', None, "True"),
        ('StringContainsQ["", "Empty String"]', None, "False"),
        ('StringContainsQ["", ___]', None, "True"),
        ('StringContainsQ["Empty Pattern", ""]', None, "True"),
        (
            'StringContainsQ[notastring, "n"]',
            (
                "String or list of strings expected at position 1 in StringContainsQ[notastring, n].",
            ),
            "StringContainsQ[notastring, n]",
        ),
        (
            'StringContainsQ["Welcome", notapattern]',
            (
                "Element notapattern is not a valid string or pattern element in notapattern.",
            ),
            "StringContainsQ[Welcome, notapattern]",
        ),
        ('StringContainsQ[{}, "list of string is empty"]', None, "{}"),
        ## special cases, Mathematica allows list of patterns
        (
            'StringContainsQ[{"A", "Galaxy", "Far", "Far", "Away"}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}]',
            None,
            "{False, False, True, True, False}",
        ),
        (
            'StringContainsQ[{"A", "Galaxy", "Far", "Far", "Away"}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}, IgnoreCase -> True]',
            None,
            "{False, False, True, True, True}",
        ),
        (
            'StringContainsQ[{"A", "Galaxy", "Far", "Far", "Away"}, {}]',
            None,
            "{False, False, False, False, False}",
        ),
        (
            'StringContainsQ[{"A", Galaxy, "Far", "Far", Away}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}]',
            (
                "String or list of strings expected at position 1 in StringContainsQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}].",
            ),
            "StringContainsQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}]",
        ),
        (
            'StringContainsQ[{"A", "Galaxy", "Far", "Far", "Away"}, {F ~~ __ ~~ "r", aw ~~ ___}]',
            (
                "Element F ~~ __ ~~ r is not a valid string or pattern element in {F ~~ __ ~~ r, aw ~~ ___}.",
            ),
            "StringContainsQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}]",
        ),
        # Mathematica can determine correct invalid element in the pattern, it reports error:
        # Element F is not a valid string or pattern element in {F ~~ __ ~~ r, aw ~~ ___}.
        (
            'StringRepeat["x", 0]',
            ("A positive integer is expected at position 2 in StringRepeat[x, 0].",),
            "StringRepeat[x, 0]",
        ),
        ('ToExpression["log(x)", InputForm]', None, "log x"),
        (
            'ToExpression["1+"]',
            (
                "Incomplete expression; more input is needed (line 1 of \"ToExpression['1+']\").",
            ),
            "$Failed",
        ),
        # ('ToExpression["log(x)", StandardForm]', None, "log x"),
    ],
)
def test_string(str_expr, warnings, str_expected):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message="",
        expected_messages=warnings,
        hold_expected=True,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "assert_fail_msg"),
    [
        (
            "ToExpression[]",
            (
                "ToExpression called with 0 arguments; between 1 and 3 arguments are expected.",
            ),
            "ToExpression argument error call",
        ),
    ],
)
def test_wrong_number_of_arguments(str_expr, msgs, assert_fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expr,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=assert_fail_msg,
        expected_messages=msgs,
    )
