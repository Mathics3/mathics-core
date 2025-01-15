# -*- coding: utf-8 -*-
"""
String Manipulation
"""

import io
import re
import unicodedata
from abc import ABC
from binascii import unhexlify
from heapq import heappop, heappush
from typing import Any, List

from mathics_scanner import TranslateError

from mathics.core.atoms import Integer, Integer0, Integer1, String
from mathics.core.attributes import A_LISTABLE, A_PROTECTED
from mathics.core.builtin import Builtin, Predefined, PrefixOperator
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.parser import MathicsFileLineFeeder, parse
from mathics.core.systemsymbols import (
    SymbolFailed,
    SymbolInputForm,
    SymbolNone,
    SymbolOutputForm,
    SymbolToExpression,
)
from mathics.eval.strings import eval_StringContainsQ, eval_ToString
from mathics.settings import SYSTEM_CHARACTER_ENCODING

# covers all of the variations. Here we just give some minimal basics

# Data taken from:
#   https://unicode-org.github.io/cldr-staging/charts/37/summary/root.html
# The uppercase letters often don't have the accents that lower-case
# letters have. I don't understand, or I may have interpreted the charts wrong.
#
alphabet_descriptions = {
    "Cyrillic": {
        "Lowercase": r"абвгґдђѓеёєжзѕиіїйјклљмнњопрстћќуўфхцчџшщъыьэюя",
        "Uppercase": r"АБВГҐДЂЃЕЁЄЖЗЅИІЇЙЈКЛЉМНЊОПРСТЋЌУЎФХЦЧЏШЩЪЫЬЭЮЯ",
    },
    "English": {
        "Lowercase": r"abcdefghijklmnopqrstuvwxyz",
        "Uppercase": r"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    },
    "French": {
        "Lowercase": r"aàâæbcçdeéèêëfghiîïjklmnoôœpqrstuùûüvwxyÿz",
        "Uppercase": r"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    },
    "German": {
        "Lowercase": r"aäbcdefghijklmnoöpqrsßtuüvwxyz",
        "Uppercase": r"AÄBCDEFGHIJKLMNOÖPQRSTUÜVWXYZ",
    },
    "Greek": {
        "Lowercase": "αβγδεζηθικλμνξοπρστυφχψω",
        "Uppercase": "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ",
    },
    "Italian": {
        "Lowercase": "aàbcdeéèfghiìjklmnoóòpqrstuùvwxyz",
        "Uppercase": r"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    },
    "Spanish": {
        "Lowercase": "aábcdeéfghiíjklmnñoópqrstuúüvwxyz",
        "Uppercase": "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ",
    },
    "Swedish": {
        "Lowercase": "aàbcdeéfghijklmnopqrstuvwxyzåäö",
        "Uppercase": "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ",
    },
    "Turkish": {
        "Lowercase": "abcçdefgğhıiİjklmnoöprsştuüvyz",
        "Uppercase": "ABCÇDEFGHIİJKLMNOÖPQRSŞTUÜVWXYZ",
    },
}

alphabet_alias = {
    "Russian": "Cyrillic",
}


def _decode_pname(name):
    return unhexlify(name[1:]).decode("utf8")


def _evaluate_match(s, m, evaluation):
    replace = dict(
        (_decode_pname(name), String(value)) for name, value in m.groupdict().items()
    )
    return s.replace_vars(replace, in_scoping=False).evaluate(evaluation)


def _parallel_match(text, rules, flags, limit):
    heap = []

    def push(i, iter, form):
        m = None
        try:
            m = next(iter)
        except StopIteration:
            pass
        if m is not None:
            heappush(heap, (m.start(), i, m, form, iter))

    for i, (patt, form) in enumerate(rules):
        push(i, re.finditer(patt, text, flags=flags), form)

    k = 0
    n = 0

    while heap:
        start, i, match, form, iter = heappop(heap)

        if start >= k:
            yield match, form

            n += 1
            if n >= limit > 0:
                break

            k = match.end()

        push(i, iter, form)


def anchor_pattern(patt):
    """
    anchors a regex in order to force matching against an entire string.
    """
    if not patt.endswith(r"\Z"):
        patt = patt + r"\Z"
    if not patt.startswith(r"\A"):
        patt = r"\A" + patt
    return patt


# FIXME: Generalize string.lower() and ord()
def letter_number(chars: List[str], start_ord) -> List["Integer"]:
    # Note caller has verified that everything isalpha() and
    # each char has length 1.
    return [Integer(ord(char.lower()) - start_ord) for char in chars]


def mathics_split(patt, string, flags):
    """
    Python's re.split includes the text of groups if they are capturing.

    Furthermore, you can't split on empty matches. Trying to do this returns
    the original string for Python < 3.5, raises a ValueError for
    Python >= 3.5, <= X and works as expected for Python >= X, where 'X' is
    some future version of Python (> 3.6).

    For these reasons we implement our own split.
    """
    # (start, end) indices of splits
    indices = list((m.start(), m.end()) for m in re.finditer(patt, string, flags))

    # (start, end) indices of stuff to keep
    indices = [(None, 0)] + indices + [(len(string), None)]
    indices = [(indices[i][1], indices[i + 1][0]) for i in range(len(indices) - 1)]

    # slice up the string
    return [string[start:stop] for start, stop in indices]


_encodings = {
    # see https://docs.python.org/2/library/codecs.html#standard-encodings
    "ASCII": "ascii",
    "CP949": "cp949",
    "CP950": "cp950",
    "EUC-JP": "euc_jp",
    "IBM-850": "cp850",
    "ISOLatin1": "iso8859_1",
    "ISOLatin2": "iso8859_2",
    "ISOLatin3": "iso8859_3",
    "ISOLatin4": "iso8859_4",
    "ISOLatinCyrillic": "iso8859_5",
    "ISO8859-1": "iso8859_1",
    "ISO8859-2": "iso8859_2",
    "ISO8859-3": "iso8859_3",
    "ISO8859-4": "iso8859_4",
    "ISO8859-5": "iso8859_5",
    "ISO8859-6": "iso8859_6",
    "ISO8859-7": "iso8859_7",
    "ISO8859-8": "iso8859_8",
    "ISO8859-9": "iso8859_9",
    "ISO8859-10": "iso8859_10",
    "ISO8859-13": "iso8859_13",
    "ISO8859-14": "iso8859_14",
    "ISO8859-15": "iso8859_15",
    "ISO8859-16": "iso8859_16",
    "koi8-r": "koi8_r",
    "MacintoshCyrillic": "mac_cyrillic",
    "MacintoshGreek": "mac_greek",
    "MacintoshIcelandic": "mac_iceland",
    "MacintoshRoman": "mac_roman",
    "MacintoshTurkish": "mac_turkish",
    "ShiftJIS": "shift_jis",
    "Unicode": "utf_16",
    "UTF-8": "utf_8",
    "UTF8": "utf_8",
    "WindowsANSI": "cp1252",
    "WindowsBaltic": "cp1257",
    "WindowsCyrillic": "cp1251",
    "WindowsEastEurope": "cp1250",
    "WindowsGreek": "cp1253",
    "WindowsTurkish": "cp1254",
}


def to_python_encoding(encoding):
    return _encodings.get(encoding)


class Alphabet(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Alphabet.html</url>
    <dl>
      <dt>'Alphabet'[]
      <dd>gives the list of lowercase letters a-z in the English alphabet .

      <dt>'Alphabet[$type$]'
      <dd> gives the alphabet for the language or class $type$.
    </dl>

    >> Alphabet[]
     = {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z}
    >> Alphabet["German"]
     = {a, ä, b, c, d, e, f, g, h, i, j, k, l, m, n, o, ö, p, q, r, s, ß, t, u, ü, v, w, x, y, z}

    Some languages are aliases. "Russian" is the same letter set as "Cyrillic"
    >> Alphabet["Russian"] == Alphabet["Cyrillic"]
     = True
    """

    messages = {
        "nalph": "The alphabet `` is not known or not available.",
    }

    rules = {
        "Alphabet[]": """Alphabet["English"]""",
    }

    summary_text = "lowercase letters in an alphabet"

    def eval(self, alpha, evaluation):
        """Alphabet[alpha_String]"""
        alphakey = alpha.value
        alphakey = alphabet_alias.get(alphakey, alphakey)
        if alphakey is None:
            evaluation.message("Alphabet", "nalph", alpha)
            return
        alphabet = alphabet_descriptions.get(alphakey, None)
        if alphabet is None:
            evaluation.message("Alphabet", "nalph", alpha)
            return
        return to_mathics_list(*alphabet["Lowercase"], elements_conversion_fn=String)


class CharacterEncoding(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/$CharacterEncoding.html</url>

    <dl>
      <dt>'$CharacterEncoding'
      <dd>specifies the default raw character encoding to use for input and \
      output when no encoding is explicitly specified. \
      Initially this is set to '$SystemCharacterEncoding'.
    </dl>

    See the character encoding current is in effect and used in input and \
    output functions functions like 'OpenRead[]':

    >> $CharacterEncoding
     = ...

    By setting its value to one of the values in '$CharacterEncodings', \
    operators are formatted differently. For example,

    >> $CharacterEncoding = "ASCII"; a -> b
     = ...
    >> $CharacterEncoding = "UTF-8"; a -> b
     = ...

    Setting its value to 'None' restore the value to \
    '$SystemCharacterEncoding':
    >> $CharacterEncoding = None;
    >> $SystemCharacterEncoding == $CharacterEncoding
     = True

    See also <url>
    :$SystemCharacterEncoding:
    /doc/reference-of-built-in-symbols/atomic-elements-of-expressions/string-manipulation/$systemcharacterencoding/</url>.
    """

    name = "$CharacterEncoding"
    messages = {
        "charcode": "`1` is not a valid character encoding. Possible settings are the names given by $CharacterEncodings or None."
    }
    value = f'"{SYSTEM_CHARACTER_ENCODING}"'
    rules = {
        "$CharacterEncoding": value,
    }

    summary_text = "default character encoding"

    def eval_set(self, value, evaluation):
        """Set[$CharacterEncoding, value_]"""
        if value is SymbolNone:
            value = String(SYSTEM_CHARACTER_ENCODING)
        if isinstance(value, String) and value.value in _encodings.keys():
            evaluation.definitions.set_ownvalue("System`$CharacterEncoding", value)
        else:
            evaluation.message("$CharacterEncoding", "charcode", value)
        return value


class CharacterEncodings(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/$CharacterEncodings.html</url>

    <dl>
      <dt>'$CharacterEncodings'
      <dd>stores the list of available character encodings.
    </dl>

    >> $CharacterEncodings[[;;9]]
     = ...
    """

    name = "$CharacterEncodings"
    value = "{%s}" % ",".join(map(lambda s: '"%s"' % s, _encodings.keys()))
    rules = {
        "$CharacterEncodings": value,
    }
    summary_text = "available character encodings"


class HexadecimalCharacter(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/HexadecimalCharacter.html</url>

    <dl>
      <dt>'HexadecimalCharacter'
      <dd>represents the characters 0-9, a-f and A-F.
    </dl>

    >> StringMatchQ[#, HexadecimalCharacter] & /@ {"a", "1", "A", "x", "H", " ", "."}
     = {True, True, True, False, False, False, False}
    """

    summary_text = "hexadecimal digits"


# This isn't your normal Box class. We'll keep this here rather than
# in mathics.builtin.box for now.
# mmatera commenct: This does not even exist in WMA. \! should be associated
# to `ToExpression`, but it was not  properly implemented by now...
class InterpretedBox(PrefixOperator):
    r"""
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/InterpretationBox.html</url>

    <dl>
      <dt>'InterpretedBox[$box$]'
      <dd>is the ad hoc fullform for \! $box$. just for internal use...
    </dl>

    >> \! \(2+2\)
     = 4
    """

    summary_text = "interpret boxes as an expression"

    def eval(self, boxes, evaluation: Evaluation):
        """InterpretedBox[boxes_]"""
        # TODO: the following is a very raw and dummy way to
        # handle these expressions.
        # In the first place, this should handle different kind
        # of boxes in different ways.
        reinput = boxes.boxes_to_text()
        return Expression(SymbolToExpression, String(reinput)).evaluate(evaluation)


class LetterNumber(Builtin):
    r"""
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LetterNumber.html</url>
    <dl>
      <dt>'LetterNumber'[$c$]
      <dd>returns the position of the character $c$ in the English alphabet.

      <dt>'LetterNumber["string"]'
      <dd>returns a list of the positions of characters in string.
      <dt>'LetterNumber["string", $alpha$]'
      <dd>returns a list of the positions of characters in string, regarding the alphabet $alpha$.
    </dl>

    >> LetterNumber["b"]
     = 2

    LetterNumber also works with uppercase characters
    >> LetterNumber["B"]
     = 2

    >> LetterNumber["ss2!"]
     = {19, 19, 0, 0}

    Get positions of each of the letters in a string:
    >> LetterNumber[Characters["Peccary"]]
    = {16, 5, 3, 3, 1, 18, 25}

    >> LetterNumber[{"P", "Pe", "P1", "eck"}]
    = {16, {16, 5}, {16, 0}, {5, 3, 11}}

    >> LetterNumber["\[Beta]", "Greek"]
     = 2

    """
    # FIXME: put the right unicode characters in a way that the
    # following test works...
    r"""
    # #> LetterNumber["\[CapitalBeta]", "Greek"]
    #  = 2

    """

    messages = {
        "nalph": "The alphabet `` is not known or not available.",
        "nas": ("The argument `1` is not a string."),
    }

    summary_text = "position of a letter in an alphabet"

    def eval_alpha_str(self, chars: List[Any], alpha: String, evaluation):
        "LetterNumber[chars_, alpha_String]"
        alphakey = alpha.value
        alphakey = alphabet_alias.get(alphakey, alphakey)
        if alphakey is None:
            evaluation.message("LetterNumber", "nalph", alpha)
            return
        if alphakey == "English":
            return self.apply(chars, evaluation)
        alphabet = alphabet_descriptions.get(alphakey, None)
        if alphabet is None:
            evaluation.message("LetterNumber", "nalph", alpha)
            return
        # TODO: handle Uppercase
        if isinstance(chars, String):
            py_chars = chars.value
            if len(py_chars) == 1:
                # FIXME generalize ord("a")
                res = alphabet["Lowercase"].find(py_chars) + 1
                if res == -1:
                    res = alphabet["Uppercase"].find(py_chars) + 1
                return Integer(res)
            else:
                r = []
                for c in py_chars:
                    cp = alphabet["Lowercase"].find(c) + 1
                    if cp == -1:
                        cp = alphabet["Uppercase"].find(c) + 1
                    r.append(cp)
                return ListExpression(*r)
        elif chars.has_form("List", 1, None):
            result = []
            for element in chars.elements:
                result.append(self.eval_alpha_str(element, alpha, evaluation))
            return ListExpression(*result)
        else:
            evaluation.message(self.__class__.__name__, "nas", chars)
            return
        return None

    def eval(self, chars: List[Any], evaluation):
        "LetterNumber[chars_]"

        start_ord = ord("a") - 1
        if isinstance(chars, String):
            py_chars = chars.value
            if len(py_chars) == 1:
                # FIXME generalize ord("a")
                return letter_number([py_chars[0]], start_ord)[0]
            else:
                r = [
                    letter_number(c, start_ord)[0] if c.isalpha() else 0
                    for c in py_chars
                ]
                return to_mathics_list(*r)
        elif chars.has_form("List", 1, None):
            result = []
            for element in chars.elements:
                result.append(self.eval(element, evaluation))
            return ListExpression(*result)
        else:
            evaluation.message(self.__class__.__name__, "nas", chars)
        return None


class NumberString(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/NumberString.html</url>
    <dl>
      <dt>'NumberString'
      <dd>represents the characters in a number.
    </dl>

    >> StringMatchQ["1234", NumberString]
     = True

    >> StringMatchQ["1234.5", NumberString]
    = True

    >> StringMatchQ["1.2`20", NumberString]
     = False
    """

    summary_text = "characters in string representation of a number"


class RemoveDiacritics(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RemoveDiacritics.html</url>
    <dl>
      <dt>'RemoveDiacritics[$s$]'
      <dd>returns a version of $s$ with all diacritics removed.
    </dl>

    >> RemoveDiacritics["en prononçant pêcher et pécher"]
     = en prononcant pecher et pecher

    >> RemoveDiacritics["piñata"]
     = pinata
    """

    summary_text = "remove diacritics"

    def eval(self, s, evaluation: Evaluation):
        "RemoveDiacritics[s_String]"
        return String(
            unicodedata.normalize("NFKD", s.value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )


class _StringFind(Builtin, ABC):
    options = {
        "IgnoreCase": "False",
        "MetaCharacters": "None",
    }

    messages = {
        "srep": "`1` is not a valid string replacement rule.",
    }

    def _find(py_stri, py_rules, py_n, flags):
        raise NotImplementedError()


class String_(Builtin, ABC):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/String.html</url>
    <dl>
      <dt>'String'
      <dd>is the head of strings.
    </dl>

    >> Head["abc"]
     = String
    >> "abc"
     = abc

    Use 'InputForm' to display quotes around strings:
    >> InputForm["abc"]
     = "abc"

    'FullForm' also displays quotes:
    >> FullForm["abc" + 2]
     = Plus[2, "abc"]
    """

    name = "String"
    summary_text = "head for strings"


class StringContainsQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/StringContainsQ.html</url>
    <dl>
      <dt>'StringContainsQ["$string$", $patt$]'
      <dd>returns True if any part of $string$ matches $patt$, and returns False otherwise.

      <dt>'StringContainsQ[{"s1", "s2", ...}, patt]'
      <dd>returns the list of results for each element of string list.

      <dt>'StringContainsQ[patt]'
      <dd>represents an operator form of StringContainsQ that can be applied to an expression.
    </dl>

    >> StringContainsQ["mathics", "m" ~~ __ ~~ "s"]
     = True

    >> StringContainsQ["mathics", "a" ~~ __ ~~ "m"]
     = False

    >> StringContainsQ[{"g", "a", "laxy", "universe", "sun"}, "u"]
     = {False, False, False, True, True}


    >> StringContainsQ["e" ~~ ___ ~~ "u"] /@ {"The Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"}
     = {True, True, True, False, False, False, False, False, True}
    """

    options = {
        "IgnoreCase": "False",
    }

    rules = {
        "StringContainsQ[patt_][expr_]": "StringContainsQ[expr, patt]",
    }

    summary_text = "test whether a pattern matches with a substring"

    def eval(self, string, patt, evaluation: Evaluation, options: dict):
        "StringContainsQ[string_, patt_, OptionsPattern[%(name)s]]"
        return eval_StringContainsQ(
            self.__class__.__name__, string, patt, evaluation, options, True
        )


class StringRepeat(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/StringRepeat.html</url>
    <dl>
      <dt>'StringRepeat["$string$", $n$]'
      <dd>gives $string$ repeated $n$ times.

      <dt>'StringRepeat["$string$", $n$, $max$]'
      <dd>gives $string$ repeated $n$ times, but not more than $max$ characters.

    </dl>

    >> StringRepeat["abc", 3]
     = abcabcabc

    >> StringRepeat["abc", 10, 7]
     = abcabca
    """

    messages = {
        "intp": "A positive integer is expected at position `1` in `2`.",
    }

    summary_text = "build a string by concatenating repetitions"

    def eval(self, expression, s, n, evaluation):
        "expression: StringRepeat[s_String, n_]"
        py_n = n.value if isinstance(n, Integer) else 0
        if py_n < 1:
            evaluation.message("StringRepeat", "intp", 2, expression)
        else:
            return String(s.value * py_n)

    def eval_truncated(self, expression, s, n, m, evaluation):
        "expression: StringRepeat[s_String, n_Integer, m_Integer]"
        # The above rule insures that n and m are boht Integer type
        py_n = n.value
        py_m = m.value

        if py_n < 1:
            evaluation.message("StringRepeat", "intp", 2, expression)
        elif py_m < 1:
            evaluation.message("StringRepeat", "intp", 3, expression)
        else:
            py_s = s.value
            py_n = min(1 + py_m // len(py_s), py_n)

            return String((py_s * py_n)[:py_m])


class SystemCharacterEncoding(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/$SystemCharacterEncoding.html</url>
    <dl>
      <dt>$SystemCharacterEncoding
      <dd>gives the default character encoding of the system.

      On startup, the value of environment variable 'MATHICS_CHARACTER_ENCODING' \
      sets this value. However if that environment variable is not set, set the value \
      is set in Python using 'sys.getdefaultencoding()'.
    </dl>

    >> $SystemCharacterEncoding
     = ...
    """

    name = "$SystemCharacterEncoding"

    rules = {
        "$SystemCharacterEncoding": '"' + SYSTEM_CHARACTER_ENCODING + '"',
    }

    summary_text = "system's character encoding"


class ToExpression(Builtin):
    r"""
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ToExpression.html</url>
    <dl>
      <dt>'ToExpression[$input$]'
      <dd>interprets a given string as Mathics input.

      <dt>'ToExpression[$input$, $form$]'
      <dd>reads the given input in the specified $form$.

      <dt>'ToExpression[$input$, $form$, $h$]'
      <dd>applies the head $h$ to the expression before evaluating it.

    </dl>

    >> ToExpression["1 + 2"]
     = 3

    >> ToExpression["{2, 3, 1}", InputForm, Max]
     = 3

    >> ToExpression["2 3", InputForm]
     = 6

    Note that newlines are like semicolons, not blanks. So so the return value is the \
    second-line value.
    >> ToExpression["2\[NewLine]3"]
     = 3
    """

    # TODO: Other forms
    """
    >> ToExpression["log(x)", TraditionalForm]
     = Log[x]
    >> ToExpression["log(x)", TraditionalForm]
     = Log[x]
    """
    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "argb": (
            "`1` called with `2` arguments; "
            "between `3` and `4` arguments are expected."
        ),
        "interpfmt": (
            "`1` is not a valid interpretation format. "
            "Valid interpretation formats include InputForm "
            "and any member of $BoxForms."
        ),
        "notstr": "The format type `1` is valid only for string input.",
    }
    summary_text = "build an expression from formatted text"

    def eval(self, seq, evaluation: Evaluation):
        "ToExpression[seq__]"

        # Organise Arguments
        py_seq = seq.get_sequence()
        if len(py_seq) == 1:
            (inp, form, head) = (py_seq[0], SymbolInputForm, None)
        elif len(py_seq) == 2:
            (inp, form, head) = (py_seq[0], py_seq[1], None)
        elif len(py_seq) == 3:
            (inp, form, head) = (py_seq[0], py_seq[1], py_seq[2])
        else:
            assert len(py_seq) > 3  # 0 case handled by apply_empty
            evaluation.message(
                "ToExpression",
                "argb",
                "ToExpression",
                Integer(len(py_seq)),
                Integer1,
                Integer(3),
            )
            return

        # Apply the different forms
        if form is SymbolInputForm:
            if isinstance(inp, String):
                # TODO: turn the below up into a function and call that.
                s = inp.value
                short_s = s[:15] + "..." if len(s) > 16 else s
                with io.StringIO(s) as f:
                    f.name = """ToExpression['%s']""" % short_s
                    feeder = MathicsFileLineFeeder(f)
                    while not feeder.empty():
                        try:
                            query = parse(evaluation.definitions, feeder)
                        except TranslateError:
                            return SymbolFailed
                        finally:
                            feeder.send_messages(evaluation)
                        if query is None:  # blank line / comment
                            continue
                        result = query.evaluate(evaluation)

            else:
                result = inp
        else:
            evaluation.message("ToExpression", "interpfmt", form)
            return

        # Apply head if present
        if head is not None:
            result = Expression(head, result).evaluate(evaluation)

        return result

    def eval_empty(self, evaluation: Evaluation):
        "ToExpression[]"
        evaluation.message(
            "ToExpression", "argb", "ToExpression", Integer0, Integer1, Integer(3)
        )
        return


class ToString(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ToString.html</url>
    <dl>
      <dt>'ToString[$expr$]'
      <dd>returns a string representation of $expr$.

      <dt>'ToString[$expr$, $form$]'
      <dd>returns a string representation of $expr$ in the form $form$.
    </dl>

    >> ToString[2]
     = 2
    >> ToString[2] // InputForm
     = "2"
    >> ToString[a+b]
     = a + b
    >> "U" <> 2
     : String expected.
     = U <> 2
    >> "U" <> ToString[2]
     = U2
    >> ToString[Integrate[f[x],x], TeXForm]
     = \\int f\\left[x\\right] \\, dx

    """

    options = {
        "CharacterEncoding": '"Unicode"',
        "FormatType": "OutputForm",
        "NumberMarks": "$NumberMarks",
        "PageHeight": "Infinity",
        "PageWidth": "Infinity",
        "TotalHeight": "Infinity",
        "TotalWidth": "Infinity",
    }

    summary_text = "format an expression and produce a string"

    def eval_default(self, value, evaluation: Evaluation, options: dict):
        "ToString[value_, OptionsPattern[ToString]]"
        return self.eval_form(value, SymbolOutputForm, evaluation, options)

    def eval_form(self, expr, form, evaluation: Evaluation, options: dict):
        "ToString[expr_, form_, OptionsPattern[ToString]]"
        encoding = options["System`CharacterEncoding"]
        return eval_ToString(expr, form, encoding.value, evaluation)


class Transliterate(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Transliterate.html</url>
    <dl>
      <dt>'Transliterate[$s$]'
      <dd>transliterates a text in some script into an ASCII string.
    </dl>

    ASCII translateration examples:
    <ul>
      <li><url>:Russian language:
          https://en.wikipedia.org/wiki/Russian_language#Transliteration</url>
      <li><url>:Hiragana: https://en.wikipedia.org/wiki/Hiragana#Table_of_hiragana</url>
    </ul>
    """

    # Causes XeTeX to barf. Put this inside a unit test.
    # >> Transliterate["つかう"]
    #  = tsukau

    # >> Transliterate["Алекса́ндр Пу́шкин"]
    #  = Aleksandr Pushkin

    # > Transliterate["μήτηρ γάρ τέ μέ φησι θεὰ Θέτις ἀργυρόπεζα"]
    # = meter gar te me phesi thea Thetis arguropeza

    requires = ("unidecode",)
    summary_text = "transliterate an UTF string in different alphabets to ASCII"

    def eval(self, s, evaluation: Evaluation):
        "Transliterate[s_String]"
        from unidecode import unidecode

        return String(unidecode(s.value))


class Whitespace(Builtin):
    r"""
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Whitespace.html</url>
    <dl>
      <dt>'Whitespace'
      <dd>represents a sequence of whitespace characters.
    </dl>

    >> StringMatchQ["\r \n", Whitespace]
     = True

    >> StringSplit["a  \n b \r\n c d", Whitespace]
     = {a, b, c, d}

    >> StringReplace[" this has leading and trailing whitespace \n ", (StartOfString ~~ Whitespace) | (Whitespace ~~ EndOfString) -> ""] <> " removed" // FullForm
     = "this has leading and trailing whitespace removed"
    """
    summary_text = "sequence of whitespace characters"
