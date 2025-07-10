"""
String Tests
"""

import re

from mathics_scanner import SingleLineFeeder, SyntaxError

from mathics.builtin.atomic.strings import anchor_pattern
from mathics.core.atoms import Integer1, String
from mathics.core.attributes import A_LISTABLE, A_PROTECTED
from mathics.core.builtin import Builtin, Test
from mathics.core.convert.regex import to_regex
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.parser.util import parser
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolStringExpression, SymbolStringMatchQ
from mathics.eval.strings import eval_StringContainsQ


class DigitQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/DigitQ.html</url>

    <dl>
      <dt>'DigitQ'[$string$]
      <dd>yields 'True' if all the characters in the $string$ are \
          digits, and yields 'False' otherwise.

    </dl>

    >> DigitQ["9"]
     = True

    >> DigitQ["a"]
     = False

    >> DigitQ["01001101011000010111010001101000011010010110001101110011"]
     = True

    >> DigitQ["-123456789"]
     = False

    """

    rules = {
        "DigitQ[string_]": (
            "If[StringQ[string], StringMatchQ[string, DigitCharacter...], False, False]"
        ),
    }
    summary_text = "test whether all the characters are digits"


class LetterQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LetterQ.html</url>

    <dl>
      <dt>'LetterQ'[$string$]
      <dd> yields 'True' if all the characters in the $string$ are \
           letters, and yields 'False' otherwise.
    </dl>

    >> LetterQ["m"]
     = True

    >> LetterQ["9"]
     = False

    >> LetterQ["Mathics"]
     = True

    >> LetterQ["Welcome to Mathics"]
     = False
    """

    rules = {
        "LetterQ[string_]": (
            "If[StringQ[string], StringMatchQ[string, LetterCharacter...], False, False]"
        ),
    }
    summary_text = "test whether all the characters are letters"


class StringFreeQ(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/StringFreeQ.html</url>

    <dl>
      <dt>'StringFreeQ'["$string$", $patt$]
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

    options = {
        "IgnoreCase": "False",
    }

    rules = {
        "StringFreeQ[patt_][expr_]": "StringFreeQ[expr, patt]",
    }

    summary_text = "test whether a string is free of substrings matching a pattern"

    def eval(self, string, patt, evaluation: Evaluation, options: dict):
        "StringFreeQ[string_, patt_, OptionsPattern[%(name)s]]"
        return eval_StringContainsQ(
            self.__class__.__name__, string, patt, evaluation, options, False
        )


class StringMatchQ(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/StringMatchQ.html</url>

    <dl>
      <dt>'StringMatchQ'["string", $pattern$]
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


class StringQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/StringQ.html</url>
    <dl>
      <dt>'StringQ'[$expr$]
      <dd>returns 'True' if $expr$ is a 'String', or 'False' otherwise.
    </dl>

    >> StringQ["abc"]
     = True
    >> StringQ[1.5]
     = False
    >> Select[{"12", 1, 3, 5, "yz", x, y}, StringQ]
     = {12, yz}
    """

    summary_text = "test whether an expression is a string"

    def test(self, expr) -> bool:
        return isinstance(expr, String)


class SyntaxQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SyntaxQ.html</url>
    <dl>
      <dt>'SyntaxQ["string"]'
      <dd>returns 'True' if "string" corresponds to a syntactically correct input for a Mathics3 expression, or 'False' otherwise.
    </dl>

    >> SyntaxQ["a[b"]
     = False

    >> SyntaxQ["a[b]"]
     = True
    """

    # FIXME:
    # replace messages[string] with the below.
    # Better is to have this kind of thing done a function for doing this.
    # Same things for "noopt" message which does not exist yet.
    messages = {"string": "String expected at position `1` in `2`."}

    summary_text = (
        "test whether a string is a syntactically-correct a Mathics3 expression"
    )

    def eval(self, string, evaluation: Evaluation):
        "SyntaxQ[string_]"

        if not isinstance(string, String):
            evaluation.message(
                "SyntaxQ", "string", Integer1, Expression(Symbol("SyntaxQ"), string)
            )
            return

        feeder = SingleLineFeeder(string.value)
        try:
            parser.parse(feeder)
        except SyntaxError:
            return SymbolFalse
        else:
            return SymbolTrue
