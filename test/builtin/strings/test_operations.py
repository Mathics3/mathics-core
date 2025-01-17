"""
Test Operations on Strings
"""

import re
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            'StringReplace["abcabc", "a" -> "b", -1]',
            (
                re.compile(
                    "Non-negative integer or Infinity expected at position 3 in StringReplace\\[abcabc, a (->)|[→] b, -1\\]"
                ),
            ),
            re.compile("StringReplace\\[abcabc, a (->)|[→] b, -1\\]"),
            None,
        ),
        ('StringReplace["abc", "b" -> 4]', ("String expected.",), "a <> 4 <> c", None),
        ('StringReplace["01101100010", "01" .. -> "x"]', None, "x1x100x0", None),
        ('StringReplace["abc abcb abdc", "ab" ~~ _ -> "X"]', None, "X Xb Xc", None),
        (
            'StringReplace["abc abcd abcd",  WordBoundary ~~ "abc" ~~ WordBoundary -> "XX"]',
            None,
            "XX abcd abcd",
            None,
        ),
        (
            'StringReplace["abcd acbd", RegularExpression["[ab]"] -> "XX"]',
            None,
            "XXXXcd XXcXXd",
            None,
        ),
        (
            'StringReplace["abcd acbd", RegularExpression["[ab]"] ~~ _ -> "YY"]',
            None,
            "YYcd YYYY",
            None,
        ),
        (
            'StringReplace["abcdabcdaabcabcd", {"abc" -> "Y", "d" -> "XXX"}]',
            None,
            "YXXXYXXXaYYXXX",
            None,
        ),
        (
            'StringReplace["  Have a nice day.  ", (StartOfString ~~ Whitespace) | (Whitespace ~~ EndOfString) -> ""] // FullForm',
            None,
            '"Have a nice day."',
            None,
        ),
        ('StringReplace["xyXY", "xy" -> "01"]', None, "01XY", None),
        ('StringReplace["xyXY", "xy" -> "01", IgnoreCase -> True]', None, "0101", None),
        ('StringReplace["abcabc", "a" -> "b", Infinity]', None, "bbcbbc", None),
        (
            'StringReplace[x, "a" -> "b"]',
            (
                re.compile(
                    "String or list of strings expected at position 1 in StringReplace\\[x, a (->)|[→] b\\]."
                ),
            ),
            re.compile("StringReplace\\[x, a (->)|[→] b"),
            None,
        ),
        (
            'StringReplace["xyzwxyzwaxyzxyzw", x]',
            ("x is not a valid string replacement rule.",),
            "StringReplace[xyzwxyzwaxyzxyzw, x]",
            None,
        ),
        (
            'StringReplace["xyzwxyzwaxyzxyzw", x -> y]',
            ("Element x is not a valid string or pattern element in x.",),
            re.compile("StringReplace\\[xyzwxyzwaxyzxyzw, x (->)|[→] y"),
            None,
        ),
    ],
)
def test_string_replace_errors(str_expr, msgs, str_expected, fail_msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=None,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
