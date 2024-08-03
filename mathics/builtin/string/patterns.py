# -*- coding: utf-8 -*-
"""
String Patterns
"""

import re

from mathics.builtin.atomic.strings import (
    _evaluate_match,
    _parallel_match,
    _pattern_search,
    _StringFind,
    anchor_pattern,
    to_regex,
)
from mathics.core.atoms import Integer1, String
from mathics.core.attributes import A_FLAT, A_LISTABLE, A_ONE_IDENTITY, A_PROTECTED
from mathics.core.builtin import BinaryOperator, Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue

SymbolStringMatchQ = Symbol("StringMatchQ")
SymbolStringExpression = Symbol("StringExpression")


class DigitCharacter(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/DigitCharacter.html</url>

    <dl>
      <dt>'DigitCharacter'
      <dd>represents the digits 0-9.
    </dl>

    >> StringMatchQ["1", DigitCharacter]
     = True
    >> StringMatchQ["a", DigitCharacter]
     = False
    >> StringMatchQ["12", DigitCharacter]
     = False

    >> StringMatchQ["123245", DigitCharacter..]
     = True
    """

    summary_text = "digit 0-9"


class EndOfLine(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/EndOfLine.html</url>

    <dl>
      <dt>'EndOfLine'
      <dd>represents the end of a line in a string.
    </dl>

    >> StringReplace["aba\nbba\na\nab", "a" ~~ EndOfLine -> "c"]
     = abc
     . bbc
     . c
     . ab

    >> StringSplit["abc\ndef\nhij", EndOfLine]
     = {abc,
     . def,
     . hij}
    """
    summary_text = "a string pattern matching EOF"


class EndOfString(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/EndOfString.html</url>

    <dl>
      <dt>'EndOfString'
      <dd>represents the end of a string.
    </dl>

    Test whether strings end with "e":
    >> StringMatchQ[#, __ ~~ "e" ~~ EndOfString] &/@ {"apple", "banana", "artichoke"}
     = {True, False, True}

    >> StringReplace["aab\nabb", "b" ~~ EndOfString -> "c"]
     = aab
     . abc
    """

    summary_text = "end of the whole string"


class LetterCharacter(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/LetterCharacter.html</url>

    <dl>
      <dt>'LetterCharacter'
      <dd>represents letters.
    </dl>

    >> StringMatchQ[#, LetterCharacter] & /@ {"a", "1", "A", " ", "."}
     = {True, False, True, False, False}

    LetterCharacter also matches unicode characters.
    >> StringMatchQ["\\[Lambda]", LetterCharacter]
     = True
    """

    summary_text = "letter"


class StartOfLine(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/StartOfLine.html</url>

    <dl>
      <dt>'StartOfLine'
      <dd>represents the start of a line in a string.
    </dl>

    >> StringReplace["aba\nbba\na\nab", StartOfLine ~~ "a" -> "c"]
     = cba
     . bba
     . c
     . cb

    >> StringSplit["abc\ndef\nhij", StartOfLine]
     = {abc
     . , def
     . , hij}
    """

    summary_text = "start of a line"


class StartOfString(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/StartOfString.html</url>

    <dl>
      <dt>'StartOfString'
      <dd>represents the start of a string.
    </dl>

    Test whether strings start with "a":
    >> StringMatchQ[#, StartOfString ~~ "a" ~~ __] &/@ {"apple", "banana", "artichoke"}
     = {True, False, True}

    >> StringReplace["aba\nabb", StartOfString ~~ "a" -> "c"]
     = cba
     . abb
    """
    summary_text = "start of a whole string"


class StringCases(_StringFind):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/StringCases.html</url>

    <dl>
      <dt>'StringCases["$string$", $pattern$]'
      <dd>gives all occurrences of $pattern$ in $string$.

      <dt>'StringReplace["$string$", $pattern$ -> $form$]'
      <dd>gives all instances of $form$ that stem from occurrences of $pattern$ in $string$.

      <dt>'StringCases["$string$", {$pattern1$, $pattern2$, ...}]'
      <dd>gives all occurrences of $pattern1$, $pattern2$, ....

      <dt>'StringReplace["$string$", $pattern$, $n$]'
      <dd>gives only the first $n$ occurrences.

      <dt>'StringReplace[{"$string1$", "$string2$", ...}, $pattern$]'
      <dd>gives occurrences in $string1$, $string2$, ...
    </dl>

    >> StringCases["axbaxxb", "a" ~~ x_ ~~ "b"]
     = {axb}

    >> StringCases["axbaxxb", "a" ~~ x__ ~~ "b"]
     = {axbaxxb}

    >> StringCases["axbaxxb", Shortest["a" ~~ x__ ~~ "b"]]
     = {axb, axxb}

    >> StringCases["-abc- def -uvw- xyz", Shortest["-" ~~ x__ ~~ "-"] -> x]
     = {abc, uvw}

    >> StringCases["-öhi- -abc- -.-", "-" ~~ x : WordCharacter .. ~~ "-" -> x]
     = {öhi, abc}

    >> StringCases["abc-abc xyz-uvw", Shortest[x : WordCharacter .. ~~ "-" ~~ x_] -> x]
     = {abc}

    >> StringCases["abba", {"a" -> 10, "b" -> 20}, 2]
     = {10, 20}

    >> StringCases["a#ä_123", WordCharacter]
     = {a, ä, 1, 2, 3}

    >> StringCases["a#ä_123", LetterCharacter]
     = {a, ä}
    """

    rules = {
        "StringCases[rule_][string_]": "StringCases[string, rule]",
    }
    summary_text = "occurrences of string patterns in a string"

    def _find(self, py_stri, py_rules, py_n, flags, evaluation: Evaluation):
        def cases():
            for match, form in _parallel_match(py_stri, py_rules, flags, py_n):
                if form is None:
                    yield String(match.group(0))
                else:
                    yield _evaluate_match(form, match, evaluation)

        return ListExpression(*list(cases()))

    def eval(self, string, rule, n, evaluation: Evaluation, options: dict):
        "%(name)s[string_, rule_, OptionsPattern[%(name)s], n_:System`Private`Null]"
        # this pattern is a slight hack to get around missing Shortest/Longest.
        return self._apply(string, rule, n, evaluation, options, True)


class StringExpression(BinaryOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/StringExpression.html</url>

    <dl>
    <dt>'StringExpression[s_1, s_2, ...]'
      <dd>represents a sequence of strings and symbolic string objects $s_i$.
    </dl>

    >> "a" ~~ "b" // FullForm
     = "ab"
    """

    attributes = A_FLAT | A_ONE_IDENTITY | A_PROTECTED
    operator = "~~"
    precedence = 135

    messages = {
        "invld": "Element `1` is not a valid string or pattern element in `2`.",
        "cond": "Ignored restriction given for `1` in `2` as it does not match previous occurrences of `1`.",
    }
    summary_text = "an arbitrary string expression"

    def eval(self, args, evaluation: Evaluation):
        "StringExpression[args__String]"
        args = args.get_sequence()
        args = [arg.get_string_value() for arg in args]
        if None in args:
            return
        return String("".join(args))


class StringFreeQ(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/StringFreeQ.html</url>

    <dl>
      <dt>'StringFreeQ["$string$", $patt$]'
      <dd>returns True if no substring in $string$ matches the string \
      expression $patt$, and returns False otherwise.

      <dt>'StringFreeQ[{"s1", "s2", ...}, patt]'
      <dd>returns the list of results for each element of string list.

      <dt>'StringFreeQ["string", {p1, p2, ...}]'
      <dd>returns True if no substring matches any of the $pi$.

      <dt>'StringFreeQ[patt]'
      <dd>represents an operator form of StringFreeQ that can be applied \
        to an expression.
    </dl>

    >> StringFreeQ["mathics", "m" ~~ __ ~~ "s"]
     = False

    >> StringFreeQ["mathics", "a" ~~ __ ~~ "m"]
     = True

    >> StringFreeQ["Mathics", "MA" , IgnoreCase -> True]
     = False

    >> StringFreeQ[{"g", "a", "laxy", "universe", "sun"}, "u"]
     = {True, True, True, False, False}


    >> StringFreeQ["e" ~~ ___ ~~ "u"] /@ {"The Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"}
     = {False, False, False, True, True, True, True, True, False}

    >> StringFreeQ[{"A", "Galaxy", "Far", "Far", "Away"}, {"F" ~~ __ ~~ "r", "aw" ~~ ___}, IgnoreCase -> True]
     = {True, True, False, False, False}

    """

    messages = {
        "strse": "String or list of strings expected at position `1` in `2`.",
    }

    options = {
        "IgnoreCase": "False",
    }

    rules = {
        "StringFreeQ[patt_][expr_]": "StringFreeQ[expr, patt]",
    }

    summary_text = "test whether a string is free of substrings matching a pattern"

    def eval(self, string, patt, evaluation: Evaluation, options: dict):
        "StringFreeQ[string_, patt_, OptionsPattern[%(name)s]]"
        return _pattern_search(
            self.__class__.__name__, string, patt, evaluation, options, False
        )


class StringMatchQ(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/StringMatchQ.html</url>

    <dl>
      <dt>'StringMatchQ["string", $pattern$]'
      <dd> checks  is "string" matches $pattern$
    </dl>

    >> StringMatchQ["abc", "abc"]
     = True

    >> StringMatchQ["abc", "abd"]
     = False

    >> StringMatchQ["15a94xcZ6", (DigitCharacter | LetterCharacter)..]
     = True

    Use StringMatchQ as an operator
    >> StringMatchQ[LetterCharacter]["a"]
     = True
    """

    attributes = A_LISTABLE | A_PROTECTED

    options = {
        "IgnoreCase": "False",
        "SpellingCorrections": "None",
    }

    messages = {
        "strse": "String or list of strings expected at position `1` in `2`.",
    }

    rules = {
        "StringMatchQ[patt_][expr_]": "StringMatchQ[expr, patt]",
    }
    summary_text = "test whether a string matches a pattern"

    def eval(self, string, patt, evaluation: Evaluation, options: dict):
        "StringMatchQ[string_, patt_, OptionsPattern[%(name)s]]"
        py_string = string.get_string_value()
        if py_string is None:
            evaluation.message(
                "StringMatchQ",
                "strse",
                Integer1,
                Expression(SymbolStringMatchQ, string, patt),
            )
            return

        re_patt = to_regex(
            patt, show_message=evaluation.message, abbreviated_patterns=True
        )
        if re_patt is None:
            evaluation.message(
                "StringExpression",
                "invld",
                patt,
                Expression(SymbolStringExpression, patt),
            )
            return

        re_patt = anchor_pattern(re_patt)

        flags = re.MULTILINE
        if options["System`IgnoreCase"] is SymbolTrue:
            flags = flags | re.IGNORECASE

        if re.match(re_patt, py_string, flags=flags) is None:
            return SymbolFalse
        else:
            return SymbolTrue


class WhitespaceCharacter(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/WhitespaceCharacter.html</url>

    <dl>
      <dt>'WhitespaceCharacter'
      <dd>represents a single whitespace character.
    </dl>

    >> StringMatchQ["\n", WhitespaceCharacter]
     = True

    >> StringSplit["a\nb\r\nc\rd", WhitespaceCharacter]
     = {a, b, , c, d}

    For sequences of whitespace characters use 'Whitespace':
    >> StringMatchQ[" \n", WhitespaceCharacter]
     = False
    >> StringMatchQ[" \n", Whitespace]
     = True
    """

    summary_text = "space, newline, tab, or other whitespace character"


# strings.to_regex() seems to have the implementation here.
class WordBoundary(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/WordBoundary.html</url>

    <dl>
      <dt>'WordBoundary'
      <dd>represents the boundary between words.
    </dl>

    >> StringReplace["apple banana orange artichoke", "e" ~~ WordBoundary -> "E"]
     = applE banana orangE artichokE
    """

    summary_text = "boundary between word characters and others"


class WordCharacter(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/WordCharacter.html</url>

    <dl>
      <dt>'WordCharacter'
      <dd>represents a single letter or digit character.
    </dl>

    >> StringMatchQ[#, WordCharacter] &/@ {"1", "a", "A", ",", " "}
     = {True, True, True, False, False}

    Test whether a string is alphanumeric:
    >> StringMatchQ["abc123DEF", WordCharacter..]
     = True
    >> StringMatchQ["$b;123", WordCharacter..]
     = False
    """
    summary_text = "letter or digit"
