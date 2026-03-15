"""
String Tests
"""

import re
from typing import Optional, Tuple

from mathics_scanner import SingleLineFeeder, SyntaxError
from mathics_scanner.location import ContainerKind

from mathics.builtin.atomic.strings import anchor_pattern
from mathics.core.atoms import Integer1, String
from mathics.core.attributes import A_PROTECTED
from mathics.core.builtin import Builtin, Test
from mathics.core.convert.regex import to_regex
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.parser.util import parser
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolStringExpression, SymbolStringMatchQ
from mathics.eval.string_tests import eval_list_StringMatchQ, eval_StringMatchQ
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

    eval_error = Builtin.generic_argument_error
    expected_args = 1
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

    >> LetterQ["Mathematics"]
     = True

    >> LetterQ["Welcome to Mathics3"]
     = False
    """

    eval_error = Builtin.generic_argument_error
    expected_args = 1
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

      <dt>'StringFreeQ[$patt$]'
      <dd>represents an operator form of StringFreeQ that can be applied \
        to an expression.
    </dl>

    >> StringFreeQ["mathics3", "m" ~~ __ ~~ "s"]
     = False

    >> StringFreeQ["mathics3", "a" ~~ __ ~~ "m"]
     = True

    >> StringFreeQ["Mathics3", "MA" , IgnoreCase -> True]
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
      <dd> Returns True  if "string" matches $pattern$ and False otherwise.

      <dt>'StringMatchQ'[{$string_1$ $string_2$, ...}, $pattern$]
      <dd> produces a list of boolean values for each of the $string_i$

      <dt>'StringMatchQ'[$pattern$]
      <dd> represents an operator form of 'StringMatchQ' that can be applied \
      to an expression.
    </dl>

    >> StringMatchQ["abc", "abc"]
     = True

    >> StringMatchQ["abc", "abd"]
     = False

    >> StringMatchQ["15a94xcZ6", (DigitCharacter | LetterCharacter)..]
     = True

    Test a list of strings against a pattern:
    >> StringMatchQ[{"a", "b", "ab", "abcd", "bcde"}, "a" ~~ ___]
     = {True, False, True, True, False}

    Use StringMatchQ as an operator
    >> StringMatchQ[LetterCharacter]["a"]
     = True

    """

    attributes = A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = (1, 2)
    options = {
        "IgnoreCase": "False",
        "SpellingCorrection": "False",
    }

    rules = {
        "StringMatchQ[patt_][expr_]": "StringMatchQ[expr, patt]",
    }
    summary_text = "test whether a string matches a pattern"

    def validate_and_process_args(
        self, pattern: str, evaluation: Evaluation, options: dict
    ) -> Tuple[Optional[str], Optional[re.RegexFlag]]:
        """
        A common argument-checking and argument-conversion routine for StringMatchQ.
        Unless there is an error, we return pattern converted to a regular expression string
        (the string has not been compiled), and re.flags. If there was an error, return
        None, None
        """
        re_patt = to_regex(
            pattern, show_message=evaluation.message, abbreviated_patterns=True
        )
        if re_patt is None:
            evaluation.message(
                "StringExpression",
                "invld",
                pattern,
                Expression(SymbolStringExpression, pattern),
            )
            return None, None

        re_patt = anchor_pattern(re_patt)

        flags = re.MULTILINE
        if options["System`IgnoreCase"] is SymbolTrue:
            flags = flags | re.IGNORECASE

        return re_patt, flags

    def eval(self, string, patt, evaluation: Evaluation, options: dict):
        "StringMatchQ[string_, patt_, OptionsPattern[%(name)s]]"

        re_patt, flags = self.validate_and_process_args(patt, evaluation, options)

        if re_patt is None:
            return

        py_string = string.get_string_value()
        if py_string is None:
            evaluation.message(
                "StringMatchQ",
                "strse",
                Integer1,
                Expression(SymbolStringMatchQ, string, patt),
            )
            return

        return eval_StringMatchQ(re_patt, py_string, flags)

    def eval_list(
        self, strings: ListExpression, patt, evaluation: Evaluation, options: dict
    ):
        "StringMatchQ[strings_List, patt_, OptionsPattern[%(name)s]]"

        re_patt, flags = self.validate_and_process_args(patt, evaluation, options)

        if re_patt is None:
            return

        # The motivation for checking for literalness and for using a special
        # eval_list_StringMatchQ was discovered in looking at Mathics3 code
        # for doing a dictionary lookup. Here, there are lots of string items in
        # list. Unwrapping each is slow, especially when this has already been
        # done because the list is a list of literals.
        if strings.is_literal:
            strings = strings.value
            for string in strings:
                if not isinstance(string, str):
                    evaluation.message(
                        "StringMatchQ",
                        "strse",
                        Integer1,
                        evaluation.current_expression,
                    )
                    return

        else:
            strings = []
            for string in strings.elements:
                py_string = string.get_string_value()
                if py_string is None:
                    evaluation.message(
                        "StringMatchQ",
                        "strse",
                        Integer1,
                        evaluation.current_expression,
                    )
                    return
                strings.append(py_string)

        return eval_list_StringMatchQ(re_patt, strings, flags)


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

    eval_error = Builtin.generic_argument_error
    expected_args = 1
    summary_text = "test whether an expression is a string"

    def test(self, expr) -> bool:
        return isinstance(expr, String)


class SyntaxQ(Builtin):
    r"""
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SyntaxQ.html</url>
    <dl>
      <dt>'SyntaxQ["string"]'
      <dd>returns 'True' if "string" corresponds to a syntactically correct input for a \
      Mathics3 expression, or 'False' otherwise.
    </dl>

    >> SyntaxQ["a[b"]
     = False

    >> SyntaxQ["a[b]"]
     = True
    """

    eval_error = Builtin.generic_argument_error
    expected_args = (1, 2)

    # FIXME:
    # replace messages[string] with the below.
    # Better is to have this kind of thing done a function for doing this.
    # Same thing for "noopt" message which does not exist yet.
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

        feeder = SingleLineFeeder(string.value, "<SyntaxQ>", ContainerKind.STRING)
        try:
            parser.parse(feeder)
        except SyntaxError:
            return SymbolFalse
        else:
            return SymbolTrue
