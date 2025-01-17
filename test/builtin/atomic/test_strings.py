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
    ("str_expr", "warnings", "str_expected", "fail_msg"),
    [
        (
            "LetterNumber[4]",
            ("The argument 4 is not a string.",),
            "LetterNumber[4]",
            None,
        ),
        ('StringContainsQ["Hello", "o"]', None, "True", None),
        ('StringContainsQ["a"]["abcd"]', None, "True", None),
        ('StringContainsQ["Mathics", "ma", IgnoreCase -> False]', None, "False", None),
        ('StringContainsQ["Mathics", "MA" , IgnoreCase -> True]', None, "True", None),
        ('StringContainsQ["", "Empty String"]', None, "False", None),
        ('StringContainsQ["", ___]', None, "True", None),
        ('StringContainsQ["Empty Pattern", ""]', None, "True", None),
        (
            'StringContainsQ[notastring, "n"]',
            (
                "String or list of strings expected at position 1 in StringContainsQ[notastring, n].",
            ),
            "StringContainsQ[notastring, n]",
            None,
        ),
        (
            'StringContainsQ["Welcome", notapattern]',
            (
                "Element notapattern is not a valid string or pattern element in notapattern.",
            ),
            "StringContainsQ[Welcome, notapattern]",
            None,
        ),
        ('StringContainsQ[{}, "list of string is empty"]', None, "{}", None),
        ## special cases, Mathematica allows list of patterns
        (
            'StringContainsQ[{"A", "Galaxy", "Far", "Far", "Away"}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}]',
            None,
            "{False, False, True, True, False}",
            None,
        ),
        (
            'StringContainsQ[{"A", "Galaxy", "Far", "Far", "Away"}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}, IgnoreCase -> True]',
            None,
            "{False, False, True, True, True}",
            None,
        ),
        (
            'StringContainsQ[{"A", "Galaxy", "Far", "Far", "Away"}, {}]',
            None,
            "{False, False, False, False, False}",
            None,
        ),
        (
            'StringContainsQ[{"A", Galaxy, "Far", "Far", Away}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}]',
            (
                "String or list of strings expected at position 1 in StringContainsQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}].",
            ),
            "StringContainsQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}]",
            None,
        ),
        (
            'StringContainsQ[{"A", "Galaxy", "Far", "Far", "Away"}, {F ~~ __ ~~ "r", aw ~~ ___}]',
            (
                "Element F ~~ __ ~~ r is not a valid string or pattern element in {F ~~ __ ~~ r, aw ~~ ___}.",
            ),
            "StringContainsQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}]",
            None,
        ),
        ## Mathematica can detemine correct invalid element in the pattern, it reports error:
        ## Element F is not a valid string or pattern element in {F ~~ __ ~~ r, aw ~~ ___}.
        (
            'StringRepeat["x", 0]',
            ("A positive integer is expected at position 2 in StringRepeat[x, 0].",),
            "StringRepeat[x, 0]",
            None,
        ),
        ('ToExpression["log(x)", InputForm]', None, "log x", None),
        (
            'ToExpression["1+"]',
            (
                "Incomplete expression; more input is needed (line 1 of \"ToExpression['1+']\").",
            ),
            "$Failed",
            None,
        ),
        (
            "ToExpression[]",
            (
                "ToExpression called with 0 arguments; between 1 and 3 arguments are expected.",
            ),
            "ToExpression[]",
            None,
        ),
        # ('ToExpression["log(x)", StandardForm]', None, "log x", None),
    ],
)
def test_private_doctests_string(str_expr, warnings, str_expected, fail_msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message="",
        expected_messages=warnings,
        hold_expected=True,
    )
