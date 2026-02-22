# -*- coding: utf-8 -*-
"""
Characters in Strings
"""
# FIXME: Redo: this is part of a Tech note, not a guide section.

from mathics.core.atoms import String
from mathics.core.attributes import A_LISTABLE, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin, Test
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.eval.string.characters import eval_Characters


class Characters(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Characters.html</url>

    <dl>
      <dt>'Characters'["$string$"]
      <dd>returns a list of the characters in $string$.
    </dl>

    >> Characters["abc"]
     = {a, b, c}
    """

    attributes = A_LISTABLE | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = 1
    summary_text = "list the characters in a string"

    def eval(self, string: String, evaluation: Evaluation) -> ListExpression:
        "Characters[string_String]"

        return eval_Characters(string.value)


class CharacterRange(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/CharacterRange.html</url>

    <dl>
      <dt>'CharacterRange'["$a$", "$b$"]
      <dd>returns a list of the Unicode characters from $a$ to $b$ inclusive.
    </dl>

    >> CharacterRange["a", "e"]
     = {a, b, c, d, e}
    >> CharacterRange["b", "a"]
     = {}
    """

    attributes = A_PROTECTED | A_READ_PROTECTED

    messages = {
        "argtype": "Arguments `1` and `2` are not both strings of length 1.",
    }

    summary_text = "range of characters with successive character codes"

    def eval(self, start, stop, evaluation: Evaluation):
        "CharacterRange[start_String, stop_String]"

        if len(start.value) != 1 or len(stop.value) != 1:
            evaluation.message("CharacterRange", "argtype", start, stop)
            return
        start = ord(start.value[0])
        stop = ord(stop.value[0])
        return ListExpression(*[String(chr(code)) for code in range(start, stop + 1)])


class LowerCaseQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/LowerCaseQ.html</url>

    <dl>
      <dt>'LowerCaseQ'[$s$]
      <dd>returns True if $s$ consists wholly of lower case characters.
    </dl>

    >> LowerCaseQ["abc"]
     = True

    An empty string returns True.
    >> LowerCaseQ[""]
     = True
    """

    summary_text = "test whether all the characters are lower-case letters"

    def test(self, expr) -> bool:
        return isinstance(expr, String) and all(
            c.islower() for c in expr.get_string_value()
        )


class ToLowerCase(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ToLowerCase.html</url>

    <dl>
      <dt>'ToLowerCase'[$s$]
      <dd>returns $s$ in all lower case.
    </dl>

    >> ToLowerCase["New York"]
     = new york
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "turn all the letters into lower case"

    def eval(self, s, evaluation: Evaluation):
        "ToLowerCase[s_String]"
        return String(s.get_string_value().lower())


class ToUpperCase(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ToUpperCase.html</url>

    <dl>
      <dt>'ToUpperCase'[$s$]
      <dd>returns $s$ in all upper case.
    </dl>

    >> ToUpperCase["New York"]
     = NEW YORK
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "turn all the letters into upper case"

    def eval(self, s, evaluation: Evaluation):
        "ToUpperCase[s_String]"
        return String(s.get_string_value().upper())


class UpperCaseQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/UpperCaseQ.html</url>

    <dl>
     <dt>'UpperCaseQ'[$s$]
     <dd>returns True if $s$ consists wholly of upper case characters.
    </dl>

    >> UpperCaseQ["ABC"]
     = True

    An empty string returns True.
    >> UpperCaseQ[""]
     = True
    """

    summary_text = "test whether all the characters are upper-case letters"

    def test(self, expr) -> bool:
        return isinstance(expr, String) and all(
            c.isupper() for c in expr.get_string_value()
        )
