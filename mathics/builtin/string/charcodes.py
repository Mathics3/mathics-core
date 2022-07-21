# -*- coding: utf-8 -*-
"""
Character Codes
"""

import sys


from mathics.builtin.atomic.strings import to_python_encoding
from mathics.builtin.base import Builtin

from mathics.core.atoms import (
    Integer,
    Integer1,
    String,
)
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol

SymbolFromCharacterCode = Symbol("FromCharacterCode")
SymbolToCharacterCode = Symbol("ToCharacterCode")


def pack_bytes(codes):
    return bytes(codes)


def unpack_bytes(codes):
    return [int(code) for code in codes]


class ToCharacterCode(Builtin):
    """
    <dl>
    <dt>'ToCharacterCode["$string$"]'
      <dd>converts the string to a list of character codes (Unicode
      codepoints).
    <dt>'ToCharacterCode[{"$string1$", "$string2$", ...}]'
      <dd>converts a list of strings to character codes.
    </dl>

    >> ToCharacterCode["abc"]
     = {97, 98, 99}
    >> FromCharacterCode[%]
     = abc

    >> ToCharacterCode["\\[Alpha]\\[Beta]\\[Gamma]"]
     = {945, 946, 947}

    >> ToCharacterCode["ä", "UTF8"]
     = {195, 164}

    >> ToCharacterCode["ä", "ISO8859-1"]
     = {228}

    >> ToCharacterCode[{"ab", "c"}]
     = {{97, 98}, {99}}

    #> ToCharacterCode[{"ab"}]
     = {{97, 98}}

    #> ToCharacterCode[{{"ab"}}]
     : String or list of strings expected at position 1 in ToCharacterCode[{{ab}}].
     = ToCharacterCode[{{ab}}]

    >> ToCharacterCode[{"ab", x}]
     : String or list of strings expected at position 1 in ToCharacterCode[{ab, x}].
     = ToCharacterCode[{ab, x}]

    >> ListPlot[ToCharacterCode["plot this string"], Filling -> Axis]
     = -Graphics-

    #> ToCharacterCode[x]
     : String or list of strings expected at position 1 in ToCharacterCode[x].
     = ToCharacterCode[x]

    #> ToCharacterCode[""]
     = {}
    """

    messages = {
        "strse": "String or list of strings expected at position `1` in `2`.",
    }
    summary_text = "convert a string to a list of character codes"

    def _encode(self, string, encoding, evaluation):
        exp = Expression(SymbolToCharacterCode, string)

        if string.has_form("List", None):
            string = [substring.get_string_value() for substring in string.elements]
            if any(substring is None for substring in string):
                evaluation.message("ToCharacterCode", "strse", Integer1, exp)
                return None
        else:
            string = string.get_string_value()
            if string is None:
                evaluation.message("ToCharacterCode", "strse", Integer1, exp)
                return None

        if encoding == "Unicode":

            def convert(s):
                # FIXME: we can defined a custom conversion fn here
                return to_mathics_list(*[Integer(ord(code)) for code in s])

        else:
            py_encoding = to_python_encoding(encoding)
            if py_encoding is None:
                evaluation.message("General", "charcode", encoding)
                return

            def convert(s):
                # FIXME: we can defined a custom conversion fn here
                return to_mathics_list(
                    *[Integer(x) for x in unpack_bytes(s.encode(py_encoding))]
                )

        if isinstance(string, list):
            return to_mathics_list(*string, elements_conversion_fn=convert)
        elif isinstance(string, str):
            return convert(string)

    def apply_default(self, string, evaluation):
        "ToCharacterCode[string_]"
        return self._encode(string, "Unicode", evaluation)

    def apply(self, string, encoding, evaluation):
        "ToCharacterCode[string_, encoding_String]"
        return self._encode(string, encoding.get_string_value(), evaluation)


class _InvalidCodepointError(ValueError):
    pass


class FromCharacterCode(Builtin):
    """
    <dl>
    <dt>'FromCharacterCode[$n$]'
        <dd>returns the character corresponding to Unicode codepoint $n$.
    <dt>'FromCharacterCode[{$n1$, $n2$, ...}]'
        <dd>returns a string with characters corresponding to $n_i$.
    <dt>'FromCharacterCode[{{$n11$, $n12$, ...}, {$n21$, $n22$, ...}, ...}]'
        <dd>returns a list of strings.
    </dl>

    >> FromCharacterCode[100]
     = d

    >> FromCharacterCode[228, "ISO8859-1"]
     = ä

    >> FromCharacterCode[{100, 101, 102}]
     = def
    >> ToCharacterCode[%]
     = {100, 101, 102}

    >> FromCharacterCode[{{97, 98, 99}, {100, 101, 102}}]
     = {abc, def}

    >> ToCharacterCode["abc 123"] // FromCharacterCode
     = abc 123

    #> #1 == ToCharacterCode[FromCharacterCode[#1]] & [RandomInteger[{0, 65535}, 100]]
     = True

    #> FromCharacterCode[{}] // InputForm
     = ""

    #> FromCharacterCode[65536]
     : A character code, which should be a non-negative integer less than 65536, is expected at position 1 in {65536}.
     = FromCharacterCode[65536]
    #> FromCharacterCode[-1]
     : Non-negative machine-sized integer expected at position 1 in FromCharacterCode[-1].
     = FromCharacterCode[-1]
    #> FromCharacterCode[444444444444444444444444444444444444]
     : Non-negative machine-sized integer expected at position 1 in FromCharacterCode[444444444444444444444444444444444444].
     = FromCharacterCode[444444444444444444444444444444444444]

    #> FromCharacterCode[{100, 101, -1}]
     : A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, -1}.
     = FromCharacterCode[{100, 101, -1}]
    #> FromCharacterCode[{100, 101, 65536}]
     : A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, 65536}.
     = FromCharacterCode[{100, 101, 65536}]
    #> FromCharacterCode[{100, 101, x}]
     : A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, x}.
     = FromCharacterCode[{100, 101, x}]
    #> FromCharacterCode[{100, {101}}]
     : A character code, which should be a non-negative integer less than 65536, is expected at position 2 in {100, {101}}.
     = FromCharacterCode[{100, {101}}]

    #> FromCharacterCode[{{97, 98, 99}, {100, 101, x}}]
     : A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, x}.
     = FromCharacterCode[{{97, 98, 99}, {100, 101, x}}]
    #> FromCharacterCode[{{97, 98, x}, {100, 101, x}}]
     : A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {97, 98, x}.
     = FromCharacterCode[{{97, 98, x}, {100, 101, x}}]
    """

    messages = {
        "notunicode": (
            "A character code, which should be a non-negative integer less "
            "than 65536, is expected at position `2` in `1`."
        ),
        "intnm": (
            "Non-negative machine-sized integer expected at " "position `2` in `1`."
        ),
        "utf8": "The given codes could not be decoded as utf-8.",
    }
    summary_text = "convert from a list of character codes to a string"

    def _decode(self, n, encoding, evaluation):
        exp = Expression(SymbolFromCharacterCode, n)

        py_encoding = to_python_encoding(encoding)
        if py_encoding is None:
            evaluation.message("General", "charcode", encoding)
            return

        def convert_codepoint_list(li):
            if encoding == "Unicode":
                s = ""
                for i, ni in enumerate(li):
                    pyni = ni.get_int_value()
                    if not (pyni is not None and 0 <= pyni <= 0xFFFF):
                        evaluation.message(
                            "FromCharacterCode",
                            "notunicode",
                            ListExpression(*li),
                            Integer(i + 1),
                        )
                        raise _InvalidCodepointError
                    s += chr(pyni)
                return s
            else:
                codes = [x.get_int_value() & 0xFF for x in li]
                return pack_bytes(codes).decode(py_encoding)

        try:
            if n.has_form("List", None):
                if not n.elements:
                    return String("")
                # Mathematica accepts FromCharacterCode[{{100}, 101}],
                # so to match this, just check the first element to see
                # if we're dealing with nested lists.
                elif n.elements[0].has_form("List", None):
                    list_of_strings = []
                    for element in n.elements:
                        if element.has_form("List", None):
                            stringi = convert_codepoint_list(element.elements)
                        else:
                            stringi = convert_codepoint_list([element])
                        list_of_strings.append(String(stringi))
                    return ListExpression(*list_of_strings)
                else:
                    return String(convert_codepoint_list(n.elements))
            else:
                pyn = n.get_int_value()
                if not (isinstance(pyn, int) and pyn > 0 and pyn < sys.maxsize):
                    return evaluation.message(
                        "FromCharacterCode", "intnm", exp, Integer1
                    )
                return String(convert_codepoint_list([n]))
        except _InvalidCodepointError:
            return
        except UnicodeDecodeError:
            evaluation.message(self.get_name(), "utf8")
            return

        assert False, "can't get here"

    def apply_default(self, n, evaluation):
        "FromCharacterCode[n_]"
        return self._decode(n, "Unicode", evaluation)

    def apply(self, n, encoding, evaluation):
        "FromCharacterCode[n_, encoding_String]"
        return self._decode(n, encoding.get_string_value(), evaluation)
