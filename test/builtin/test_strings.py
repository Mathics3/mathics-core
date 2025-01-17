# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.string.
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            'StringInsert["abcdefghijklm", "X", 15]',
            ("Cannot insert at position 15 in abcdefghijklm.",),
            "StringInsert[abcdefghijklm, X, 15]",
            None,
        ),
        (
            'StringInsert[abcdefghijklm, "X", 4]',
            (
                "String or list of strings expected at position 1 in StringInsert[abcdefghijklm, X, 4].",
            ),
            "StringInsert[abcdefghijklm, X, 4]",
            None,
        ),
        (
            'StringInsert["abcdefghijklm", X, 4]',
            ("String expected at position 2 in StringInsert[abcdefghijklm, X, 4].",),
            "StringInsert[abcdefghijklm, X, 4]",
            None,
        ),
        (
            'StringInsert["abcdefghijklm", "X", a]',
            (
                "Position specification a in StringInsert[abcdefghijklm, X, a] is not a machine-sized integer or a list of machine-sized integers.",
            ),
            "StringInsert[abcdefghijklm, X, a]",
            None,
        ),
        (
            'StringInsert["abcdefghijklm", "X", 0]',
            ("Cannot insert at position 0 in abcdefghijklm.",),
            "StringInsert[abcdefghijklm, X, 0]",
            None,
        ),
        (
            'StringInsert["abcdefghijklm", "X", -15]',
            ("Cannot insert at position -15 in abcdefghijklm.",),
            "StringInsert[abcdefghijklm, X, -15]",
            None,
        ),
        (
            'StringInsert["abcdefghijklm", "X", {1, -1, 14, -14}]',
            None,
            "XXabcdefghijklmXX",
            None,
        ),
        (
            'StringInsert["abcdefghijklm", "X", {1, 0}]',
            ("Cannot insert at position 0 in abcdefghijklm.",),
            "StringInsert[abcdefghijklm, X, {1, 0}]",
            None,
        ),
        ('StringInsert["", "X", {1}]', None, "X", None),
        ('StringInsert["", "X", {1, -1}]', None, "XX", None),
        ('StringInsert["", "", {1}]', None, "", None),
        (
            'StringInsert["", "X", {1, 2}]',
            ("Cannot insert at position 2 in .",),
            "StringInsert[, X, {1, 2}]",
            None,
        ),
        (
            'StringInsert["abcdefghijklm", "", {1, 2, 3, 4 ,5, -6}]',
            None,
            "abcdefghijklm",
            None,
        ),
        ('StringInsert["abcdefghijklm", "X", {}]', None, "abcdefghijklm", None),
        (
            'StringInsert[{"abcdefghijklm", "Mathics"}, "X", 13]',
            ("Cannot insert at position 13 in Mathics.",),
            "{abcdefghijklXm, StringInsert[Mathics, X, 13]}",
            None,
        ),
        ('StringInsert[{"", ""}, "", {1, 1, 1, 1}]', None, "{, }", None),
        (
            'StringInsert[{"abcdefghijklm", "Mathics"}, "X", {0, 2}]',
            (
                "Cannot insert at position 0 in abcdefghijklm.",
                "Cannot insert at position 0 in Mathics.",
            ),
            "{StringInsert[abcdefghijklm, X, {0, 2}], StringInsert[Mathics, X, {0, 2}]}",
            None,
        ),
        (
            'StringInsert[{"abcdefghijklm", Mathics}, "X", {1, 2}]',
            (
                "String or list of strings expected at position 1 in StringInsert[{abcdefghijklm, Mathics}, X, {1, 2}].",
            ),
            "StringInsert[{abcdefghijklm, Mathics}, X, {1, 2}]",
            None,
        ),
        (
            'StringInsert[{"", "Mathics"}, "X", {1, 1, -1}]',
            None,
            "{XXX, XXMathicsX}",
            None,
        ),
        (
            'StringPosition["123ABCxyABCzzzABCABC", "ABC", -1]',
            (
                "Non-negative integer or Infinity expected at position 3 in StringPosition[123ABCxyABCzzzABCABC, ABC, -1].",
            ),
            "StringPosition[123ABCxyABCzzzABCABC, ABC, -1]",
            None,
        ),
        ## Overlaps
        (
            'StringPosition["1231221312112332", RegularExpression["[12]+"]]',
            None,
            "{{1, 2}, {2, 2}, {4, 7}, {5, 7}, {6, 7}, {7, 7}, {9, 13}, {10, 13}, {11, 13}, {12, 13}, {13, 13}, {16, 16}}",
            None,
        ),
        (
            'StringPosition["1231221312112332", RegularExpression["[12]+"], Overlaps -> False]',
            None,
            "{{1, 2}, {4, 7}, {9, 13}, {16, 16}}",
            None,
        ),
        (
            'StringPosition["1231221312112332", RegularExpression["[12]+"], Overlaps -> x]',
            None,
            "{{1, 2}, {4, 7}, {9, 13}, {16, 16}}",
            None,
        ),
        (
            'StringPosition["1231221312112332", RegularExpression["[12]+"], Overlaps -> All]',
            ("Overlaps -> All option is not currently implemented in Mathics.",),
            "{{1, 2}, {2, 2}, {4, 7}, {5, 7}, {6, 7}, {7, 7}, {9, 13}, {10, 13}, {11, 13}, {12, 13}, {13, 13}, {16, 16}}",
            None,
        ),
        (
            'StringPosition["21211121122", {"121", "11"}]',
            None,
            "{{2, 4}, {4, 5}, {5, 6}, {6, 8}, {8, 9}}",
            None,
        ),
        (
            'StringPosition["21211121122", {"121", "11"}, Overlaps -> False]',
            None,
            "{{2, 4}, {5, 6}, {8, 9}}",
            None,
        ),
        (
            'StringPosition[{"abc", "abcda"}, "a"]',
            None,
            "{{{1, 1}}, {{1, 1}, {5, 5}}}",
            None,
        ),
        ('StringPosition[{"abc"}, "a", Infinity]', None, "{{{1, 1}}}", None),
        ('StringPosition["abc"]["123AabcDEabc"]', None, "{{5, 7}, {10, 12}}", None),
        ('StringRiffle[{a, b, c, "d", e, "f"}]', None, "a b c d e f", None),
        ## 1st is not a list
        (
            'StringRiffle["abcdef"]',
            (
                "List expected at position 1 in StringRiffle[abcdef].",
                "StringRiffle called with 1 argument; 2 or more arguments are expected.",
            ),
            "StringRiffle[abcdef]",
            None,
        ),
        ('StringRiffle[{"", "", ""}] // FullForm', None, '"  "', None),
        ## This form is not supported
        (
            'StringRiffle[{{"a", "b"}, {"c", "d"}}]',
            ("Sublist form in position 1 is is not implemented yet.",),
            "StringRiffle[{{a, b}, {c, d}}]",
            None,
        ),
        (
            'StringRiffle[{"a", "b", "c", "d", "e"}, sep]',
            ("String expected at position 2 in StringRiffle[{a, b, c, d, e}, sep].",),
            "StringRiffle[{a, b, c, d, e}, sep]",
            None,
        ),
        (
            'StringRiffle[{"a", "b", "c", "d", "e"}, {" ", ")"}]',
            (
                "String expected at position 2 in StringRiffle[{a, b, c, d, e}, { , )}].",
            ),
            "StringRiffle[{a, b, c, d, e}, { , )}]",
            None,
        ),
        (
            'StringRiffle[{"a", "b", "c", "d", "e"}, {left, " ", "."}]',
            (
                "String expected at position 2 in StringRiffle[{a, b, c, d, e}, {left,  , .}].",
            ),
            "StringRiffle[{a, b, c, d, e}, {left,  , .}]",
            None,
        ),
        ## This form is not supported
        (
            'StringRiffle[{"a", "b", "c"}, "+", "-"]',
            ("Multiple separators form is not implemented yet.",),
            "StringRiffle[{a, b, c}, +, -]",
            "## Mathematica result: a+b+c, but we are not support multiple separators",
        ),
        (
            "StringSplit[x]",
            ("String or list of strings expected at position 1 in StringSplit[x].",),
            "StringSplit[x, Whitespace]",
            None,
        ),
        (
            'StringSplit["x", x]',
            ("Element x is not a valid string or pattern element in x.",),
            "StringSplit[x, x]",
            None,
        ),
        ('StringTake["abcd", 0] // InputForm', None, '""', None),
        ('StringTake["abcd", {3, 2}] // InputForm', None, '""', None),
        ('StringTake["", {1, 0}] // InputForm', None, '""', None),
        (
            'StringTake["abc", {0, 0}]',
            ('Cannot take positions 0 through 0 in "abc".',),
            "StringTake[abc, {0, 0}]",
            None,
        ),
        (
            "StringTake[{2, 4},2]",
            ("String or list of strings expected at position 1.",),
            "StringTake[{2, 4}, 2]",
            None,
        ),
        (
            'StringTake["kkkl",Graphics[{}]]',
            ("Integer or a list of sequence specifications expected at position 2.",),
            "StringTake[kkkl, -Graphics-]",
            None,
        ),
    ],
)
def test_private_doctests_operations(str_expr, msgs, str_expected, fail_msg):
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ('StringMatchQ["123245a6", DigitCharacter..]', None, "False", None),
        (
            'StringCases["abc-abc xyz-uvw", Shortest[x : WordCharacter .. ~~ "-" ~~ x : LetterCharacter] -> x]',
            (
                "Ignored restriction given for x in x : LetterCharacter as it does not match previous occurrences of x.",
            ),
            "{abc}",
            None,
        ),
        ('"a" ~~ "b" ~~ "c" // FullForm', None, '"abc"', None),
        ("a ~~ b", None, "a ~~ b", None),
        ('StringFreeQ["Hello", "o"]', None, "False", None),
        ('StringFreeQ["a"]["abcd"]', None, "False", None),
        ('StringFreeQ["Mathics", "ma", IgnoreCase -> False]', None, "True", None),
        ('StringFreeQ["", "Empty String"]', None, "True", None),
        ('StringFreeQ["", ___]', None, "False", None),
        ('StringFreeQ["Empty Pattern", ""]', None, "False", None),
        (
            'StringFreeQ[notastring, "n"]',
            (
                "String or list of strings expected at position 1 in StringFreeQ[notastring, n].",
            ),
            "StringFreeQ[notastring, n]",
            None,
        ),
        (
            'StringFreeQ["Welcome", notapattern]',
            (
                "Element notapattern is not a valid string or pattern element in notapattern.",
            ),
            "StringFreeQ[Welcome, notapattern]",
            None,
        ),
        ('StringFreeQ[{}, "list of string is empty"]', None, "{}", None),
        (
            'StringFreeQ[{"A", "Galaxy", "Far", "Far", "Away"}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}]',
            None,
            "{True, True, False, False, True}",
            None,
        ),
        (
            'StringFreeQ[{"A", "Galaxy", "Far", "Far", "Away"}, {}]',
            None,
            "{True, True, True, True, True}",
            None,
        ),
        (
            'StringFreeQ[{"A", Galaxy, "Far", "Far", Away}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}]',
            (
                "String or list of strings expected at position 1 in StringFreeQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}].",
            ),
            "StringFreeQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}]",
            None,
        ),
        (
            'StringFreeQ[{"A", "Galaxy", "Far", "Far", "Away"}, {F ~~ __ ~~ "r", aw ~~ ___}]',
            (
                "Element F ~~ __ ~~ r is not a valid string or pattern element in {F ~~ __ ~~ r, aw ~~ ___}.",
            ),
            "StringFreeQ[{A, Galaxy, Far, Far, Away}, {F ~~ __ ~~ r, aw ~~ ___}]",
            None,
        ),
        ## Mathematica can detemine correct invalid element in the pattern, it reports error:
        ## Element F is not a valid string or pattern element in {F ~~ __ ~~ r, aw ~~ ___}.
        ('StringMatchQ["abc1", LetterCharacter]', None, "False", None),
        ('StringMatchQ["abc", "ABC"]', None, "False", None),
        ('StringMatchQ["abc", "ABC", IgnoreCase -> True]', None, "True", None),
        ## Words containing nonword characters
        (
            'StringMatchQ[{"monkey", "don \'t", "AAA", "S&P"}, ___ ~~ Except[WordCharacter] ~~ ___]',
            None,
            "{False, True, False, True}",
            None,
        ),
        ## Try to match a literal number
        (
            "StringMatchQ[1.5, NumberString]",
            (
                "String or list of strings expected at position 1 in StringMatchQ[1.5, NumberString].",
            ),
            "StringMatchQ[1.5, NumberString]",
            None,
        ),
        ## Abbreviated string patterns Issue #517
        ('StringMatchQ["abcd", "abc*"]', None, "True", None),
        ('StringMatchQ["abc", "abc*"]', None, "True", None),
        (r'StringMatchQ["abc\\", "abc\\"]', None, "True", None),
        (r'StringMatchQ["abc*d", "abc\\*d"]', None, "True", None),
        (r'StringMatchQ["abc*d", "abc\\**"]', None, "True", None),
        ('StringMatchQ["abcde", "a*f"]', None, "False", None),
        ('StringMatchQ["abcde", "a@e"]', None, "True", None),
        ('StringMatchQ["aBCDe", "a@e"]', None, "False", None),
        ('StringMatchQ["ae", "a@e"]', None, "False", None),
    ],
)
def test_private_doctests_patterns(str_expr, msgs, str_expected, fail_msg):
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ('ToCharacterCode[{"ab"}]', None, "{{97, 98}}", None),
        (
            'ToCharacterCode[{{"ab"}}]',
            (
                "String or list of strings expected at position 1 in ToCharacterCode[{{ab}}].",
            ),
            "ToCharacterCode[{{ab}}]",
            None,
        ),
        (
            "ToCharacterCode[x]",
            (
                "String or list of strings expected at position 1 in ToCharacterCode[x].",
            ),
            "ToCharacterCode[x]",
            None,
        ),
        ('ToCharacterCode[""]', None, "{}", None),
        (
            "#1 == ToCharacterCode[FromCharacterCode[#1]] & [RandomInteger[{0, 65535}, 100]]",
            None,
            "True",
            None,
        ),
        ("FromCharacterCode[{}] // InputForm", None, '""', None),
        (
            "FromCharacterCode[65536]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 1 in {65536}.",
            ),
            "FromCharacterCode[65536]",
            None,
        ),
        (
            "FromCharacterCode[-1]",
            (
                "Non-negative machine-sized integer expected at position 1 in FromCharacterCode[-1].",
            ),
            "FromCharacterCode[-1]",
            None,
        ),
        (
            "FromCharacterCode[444444444444444444444444444444444444]",
            (
                "Non-negative machine-sized integer expected at position 1 in FromCharacterCode[444444444444444444444444444444444444].",
            ),
            "FromCharacterCode[444444444444444444444444444444444444]",
            None,
        ),
        (
            "FromCharacterCode[{100, 101, -1}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, -1}.",
            ),
            "FromCharacterCode[{100, 101, -1}]",
            None,
        ),
        (
            "FromCharacterCode[{100, 101, 65536}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, 65536}.",
            ),
            "FromCharacterCode[{100, 101, 65536}]",
            None,
        ),
        (
            "FromCharacterCode[{100, 101, x}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, x}.",
            ),
            "FromCharacterCode[{100, 101, x}]",
            None,
        ),
        (
            "FromCharacterCode[{100, {101}}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 2 in {100, {101}}.",
            ),
            "FromCharacterCode[{100, {101}}]",
            None,
        ),
        (
            "FromCharacterCode[{{97, 98, 99}, {100, 101, x}}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, x}.",
            ),
            "FromCharacterCode[{{97, 98, 99}, {100, 101, x}}]",
            None,
        ),
        (
            "FromCharacterCode[{{97, 98, x}, {100, 101, x}}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {97, 98, x}.",
            ),
            "FromCharacterCode[{{97, 98, x}, {100, 101, x}}]",
            None,
        ),
        # These tests are commented out due to the bug reported in issue #906
        # Octal and hexadecimal notation works alone, but fails
        # as a part of another expression. For example,
        # F[\.78\.79\.7A]   or "\.78\.79\.7A" produces a syntax error in Mathics.
        # Here, this is put inside a ToString[...] and hence, it does not work.
        # (r"\.78\.79\.7A=37; xyz", None, '37', "Octal characters. check me."),
        # (r"\:0078\:0079\:007A=38;xyz", None, '38', "Hexadecimal characters. Check me."),
        # (r"\101\102\103\061\062\063=39;ABC123", None, "39", None),
        (r"xyz=.;ABC123=.;\[Alpha]\[Beta]\[Gamma]", None, "\u03B1\u03B2\u03B3", None),
        ('LetterQ[""]', None, "True", None),
        (
            'LetterQ["\\[Alpha]\\[Beta]\\[Gamma]\\[Delta]\\[Epsilon]\\[Zeta]\\[Eta]\\[Theta]"]',
            None,
            "True",
            None,
        ),
    ],
)
def test_private_doctests_characters(str_expr, msgs, str_expected, fail_msg):
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


# These tests are separated due to the bug reported in issue #906


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        (r"\.78\.79\.7A", "xyz", "variable name using hexadecimal characters"),
        (r"\:0078\:0079\:007A", "xyz", "variable name using hexadecimal characters"),
        (
            r"\101\102\103\061\062\063",
            "ABC123",
            "variable name using hexadecimal characters",
        ),
    ],
)
def test_private_doctests_characters(str_expr, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=False,
        to_string_expected=False,
        hold_expected=False,
        failure_message=fail_msg,
    )
