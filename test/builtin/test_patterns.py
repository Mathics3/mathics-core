# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.patterns.
"""

from test.helper import check_evaluation

import pytest

# Clear all the variables


def test_blank():
    check_evaluation(None, None, None)
    for str_expr, str_expected, message in (
        (
            "g[i] /. _[i] :> a",
            "a",
            "Issue #203",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


def test_replace_all():
    check_evaluation(None, None, None)
    for str_expr, str_expected, message in (
        (
            "a == d b + d c /. a_ x_ + a_ y_ -> a (x + y)",
            "a == (b + c) d",
            "Issue #212",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            None,
            None,
            None,
            None,
        ),
        (
            "Dispatch[]",
            ("Dispatch called with 0 arguments; 1 argument is expected.",),
            "Dispatch[]",
            "dispatch with 0 arguments",
        ),
        ("Dispatch[a]", None, "Dispatch[a]", "A symbol. Keep unevaluated."),
        ("Dispatch[a -> b]", None, "Dispatch[<1>]", "single rule"),
        ("Dispatch[{}]", None, "{}", "empty rule"),
        ("Dispatch[{a -> 1}]", None, "Dispatch[<1>]", "single rule"),
        ("Dispatch[{a -> 1, b -> c}]", None, "Dispatch[<2>]", "two rules"),
        (
            "Dispatch[{a -> 1, b -> c, p}]",
            None,
            "Dispatch[{a ⇾ 1, b ⇾ c, p}]",
            "two rules and a symbol: keep unevaluated.",
        ),
        (
            "Dispatch[{a -> 1, {b -> c, p -> t}}]",
            None,
            "Dispatch[<3>]",
            "Flatten nested rules.",
        ),
        # TODO: handle 2 or more arguments.
    ],
)
def test_dispatch(str_expr, msgs, str_expected, fail_msg):
    """Test several cases for Dispatch"""
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
    ("str_expr", "str_expected", "fail_msg"),
    [
        ("ClearAll[f, g, o]; SetAttributes[f, Flat];", "Null", None),
        (
            "MatchQ[f[x, y, z], f[a_, z]]",
            "True",
            "A blank before a literal can take several elements",
        ),
        ("Replace[f[x, y, z], f[a_, z] :> {a}]", "{f[x, y]}", None),
        (
            "Replace[f[x, y, z], f[a_, z[_]] :> {a}]",
            "Replace[f[x, y, z], f[a_, z[_]] :> {a}]",
            None,
        ),
        ("Replace[f[x, y, z[1]], f[a_, z[_]] :> {a}]", "{f[x, y]}", None),
        ("f[x, y, z] /. f[a__, z] :> {a}", "{x, y}", "No element is lost"),
        ("f[x, y, z] /. f[a___, y, b___] :> {{a}, {b}}", "{{x}, {z}}", None),
        ("f[a, b, c, d, e] /. f[b, c, d] -> x", "f[a, x, e]", "WMA docs for Flat"),
        ("f[a, b, c, d, e] /. f[b, c, d] -> f[x, y]", "f[a, x, y, e]", None),
        ("f[a, b, c, d, e] /. f[b] -> x", "f[a, x, c, d, e]", None),
        ("f[a, b, c, d, e] /. f[d, b] -> x", "f[a, b, c, d, e]", "Order matters"),
        ("f[w, x, y, z] /. f[x, z] -> q", "f[w, x, y, z]", "Not contiguous"),
        (
            "SetAttributes[o, {Flat, OneIdentity}]; o[a_, 0] := 0; o[x, y, 0]",
            "0",
            None,
        ),
        ("SetAttributes[g, Flat]; g[a_, 0] := h[a]; g[x, y, 0]", "h[g[x, y]]", None),
        (
            "ClearAll[g]; SetAttributes[g, Flat]; g[l__, SameTest -> s_] := {{l}, s};"
            " g[{1, -1}, {2, 3}, SameTest -> t]",
            "{{{1, -1}, {2, 3}}, t}",
            "Issue #1381",
        ),
        ("ClearAll[f, g, o];", "Null", None),
    ],
)
def test_flat_patterns(str_expr, str_expected, fail_msg):
    """Pattern matching against expressions whose head is Flat"""
    check_evaluation(str_expr, str_expected, failure_message=fail_msg)


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("a + b /. x_ + y_ -> {x, y}", None, "{a, b}", None),
        (
            'StringReplace["h1d9a f483", DigitCharacter | WhitespaceCharacter -> ""]',
            None,
            "hdaf",
            None,
        ),
        (
            'StringReplace["abc DEF 123!", Except[LetterCharacter, WordCharacter] -> "0"]',
            None,
            "abc DEF 000!",
            None,
        ),
        ("a:b:c", None, "a : b : c", None),
        ("FullForm[a:b:c]", None, "Optional[Pattern[a, b], c]", None),
        ("(a:b):c", None, "a : b : c", None),
        ("a:(b:c)", None, "a : (b : c)", None),
        ('StringReplace["hello world!", _ -> "x"]', None, "xxxxxxxxxxxx", None),
        ("f[a, b, c, d] /. f[x__, c, y__] -> {{x},{y}}", None, "{{a, b}, {d}}", None),
        ("a + b + c + d /. Plus[x__, c] -> {x}", None, "{a, b, d}", None),
        (
            'StringReplace[{"ab", "abc", "abcd"}, "b" ~~ __ -> "x"]',
            None,
            "{ab, ax, ax}",
            None,
        ),
        ## This test hits infinite recursion
        ##
        ##The value captured by a named 'BlankNullSequence' pattern is a
        ##'Sequence' object, which can have no elements:
        ## ('f[] /. f[x___] -> x', None,
        ## 'Sequence[]', None),
        ("___symbol", None, "___symbol", None),
        ("___symbol //FullForm", None, "BlankNullSequence[symbol]", None),
        (
            'StringReplace[{"ab", "abc", "abcd"}, "b" ~~ ___ -> "x"]',
            None,
            "{ax, ax, ax}",
            None,
        ),
        ("1.. // FullForm", None, "Repeated[1]", None),
        (
            "8^^1.. // FullForm   (* Mathematica gets this wrong *)",
            None,
            "Repeated[1]",
            None,
        ),
        ('StringReplace["010110110001010", "01".. -> "a"]', None, "a1a100a0", None),
        (
            'StringMatchQ[#, "a" ~~ ("b"..) ~~ "a"] &/@ {"aa", "aba", "abba"}',
            None,
            "{False, True, True}",
            None,
        ),
        ("1... // FullForm", None, "RepeatedNull[1]", None),
        (
            "8^^1... // FullForm   (* Mathematica gets this wrong *)",
            None,
            "RepeatedNull[1]",
            None,
        ),
        (
            'StringMatchQ[#, "a" ~~ ("b"...) ~~ "a"] &/@ {"aa", "aba", "abba"}',
            None,
            "{True, True, True}",
            None,
        ),
        ("{opt -> b} /. OptionsPattern[{}] -> t", None, "t", None),
        ("Clear[f]", None, None, None),
        (
            "Options[f] = {Power -> 2}; f[x_, OptionsPattern[f]] := x ^ OptionValue[Power];",
            None,
            None,
            None,
        ),
        ("f[10]", None, "100", None),
        ("f[10, Power -> 3]", None, "1000", None),
        ("Clear[f]", None, None, None),
        ("Options[f] = {Power -> 2};", None, None, None),
        ("f[x_, OptionsPattern[]] := x ^ OptionValue[Power];", None, None, None),
        ("f[10]", None, "100", None),
        ("f[10, Power -> 3]", None, "1000", None),
        ("Clear[f]", None, None, None),
        # Orderless literal pattern mixing an atom and an expression
        ("f[2 x[3]] = 1; f[2 x[3]]", None, "1", None),
        ("Clear[f]", None, None, None),
    ],
)
def test_pattern(str_expr, msgs, str_expected, fail_msg):
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
    ("str_expr", "str_expected", "fail_msg"),
    [
        (
            "MatchQ[Table[{k, k}, {k, 3000}], {{_Integer, _Integer}..}]",
            "True",
            "a long sequence does not run out of Python stack",
        ),
        (
            "MatchQ[Append[Table[{k, k}, {k, 3000}], {x, 1}], {{_Integer, _Integer}..}]",
            "False",
            "a long sequence that fails at its end",
        ),
        ("MatchQ[Table[1, {3000}], {(x_)..}]", "True", None),
        ("MatchQ[{1, 1, 2}, {(x_)..}]", "False", "the same x in every repetition"),
        ("f[1, 2, 3] /. f[x:(_Integer|_Real)...] :> {x}", "{1, 2, 3}", None),
        (
            "Cases[{{1, 1}, {1, 2}, {3, 3, 3}}, {(x_)..}]",
            "{{1, 1}, {3, 3, 3}}",
            None,
        ),
        (
            "{a, b, a, b} /. {x:Repeated[a|b, {2, 3}], y__} :> {{x}, {y}}",
            "{{a, b}, {a, b}}",
            "as in WMA, the shortest split of the rest wins",
        ),
    ],
)
def test_repeated(str_expr, str_expected, fail_msg):
    check_evaluation(str_expr, str_expected, fail_msg)
