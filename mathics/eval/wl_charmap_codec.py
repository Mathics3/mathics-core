"""
wl_charmap_codec.py

Pure toolkit for building, from already parsed entries from a .wl
encoding file (with format {"8Bit", {{charcode, "repr",
invertible?}, ...}}), a real Python codec: a decode table
(byte -> str) and an encoding table (str -> byte), respecting the invertibility flag on each entry.

Construction primitives ('charmap_build', 'charmap_encode',
'charmap_decode') are the same used by the Pythons stdlib for implementing
its single byte codecs (see Lib/encodings/
iso8859_8.py, cp1252.py, mac_roman.py, etc.)
"""

from __future__ import annotations

import codecs
import re
from dataclasses import dataclass

from mathics_scanner.characters import CHARACTER_TO_NAME


@dataclass
class Entry:
    code: int
    char: str
    invertible: bool


TAG_SIZES = {"7Bit": 128, "8Bit": 256}


def build_charmap(tag: str, entries: list[Entry]) -> tuple[str, dict[int, int]]:
    """
    Build:
      - decoding_table: fixed length Python string (256 for 8Bit) for
        decodiding byte -> caracter. Undefined positions use
        '\\ufffe' (convention in codecs.charmap_* for "undefined").
      - encoding_table: dict character(ordinal) -> byte, built with
        codecs.charmap_build and then RESTRICTED to the invertible entries
        (in this way we replicate the WMA behavior: a non-invertible entry
        can be used for decoding but not for re-encoding).
    """
    size = TAG_SIZES.get(tag, 256)
    table = [chr(i) for i in range(size)]  # default: identity (Latin-1)
    for e in entries:
        if e.code < size:
            table[e.code] = e.char
    decoding_table = "".join(table)

    # Build the dict by hand (instead of of using codecs.charmap_build)
    # because that helper can return an optimizaded and immutable EncodingMap
    # when the table is (almost) biyective, and we need to erase
    # non-invertible entries.
    encoding_table: dict[int, int] = {
        ord(ch): code for code, ch in enumerate(decoding_table)
    }

    for e in entries:
        if not e.invertible and encoding_table.get(ord(e.char)) == e.code:
            del encoding_table[ord(e.char)]

    return decoding_table, encoding_table


def assert_ascii_safe(substitution: dict[str, str], table_name: str = "") -> None:
    """
    Check that all the values in a substitution table are pure ASCII.
    """
    offending = {
        ch: repl for ch, repl in substitution.items() if any(ord(c) > 127 for c in repl)
    }
    if offending:
        sample = dict(list(offending.items())[:5])
        raise ValueError(
            f"{table_name}: {len(offending)} valores de sustitucion no son "
            f"ASCII puro (ejemplos: {sample!r}) -- el resultado ya no seria "
            "seguro para tratarlo como bytes via .encode('latin-1')"
        )


def escape_unrepresentable_char(ch: str) -> str:
    """
    Represent a 1 position character -when is not representable in a
    given encoding- as a WL named character `\\[Name]` if the character
    has a name, or character code `\\:XXXX` (BMP, 4 hex digits) o
    `\\|XXXXXX` (out of BMP, 6 hex digits) if the name is not available.

    See  doc in $CharacterEncoding: "Unencodable characters can be
    input and will be output in standard \\[Name] and \\:nnnn form."
    """
    named = CHARACTER_TO_NAME.get(ch)
    if named is not None:
        return named
    code = ord(ch)
    return f"\\:{code:04x}" if code <= 0xFFFF else f"\\|{code:06x}"


class WLCharmapCodec(codecs.Codec):
    def __init__(self, decoding_table: str, encoding_table: dict[int, int]):
        self.decoding_table = decoding_table
        self.encoding_table = encoding_table

    def encode(self, input: str, errors: str = "strict"):
        return codecs.charmap_encode(input, errors, self.encoding_table)

    def decode(self, input: bytes, errors: str = "strict"):
        return codecs.charmap_decode(input, errors, self.decoding_table)


_PASSTHROUGH_ERROR_NAME = "wl_charmap_passthrough"


def _passthrough_error_handler(error: UnicodeEncodeError):
    unmapped = error.object[error.start : error.end]
    return unmapped.encode("utf-8"), error.end


def register_passthrough_error_handler(name: str = _PASSTHROUGH_ERROR_NAME) -> str:
    """
    Register (if needed) an error handler that allow pass without changes
    those characters without entries in the table, instead of failing.
    Return the name for using as `errors=` in codecs.charmap_encode.
    """
    try:
        codecs.lookup_error(name)
    except LookupError:
        codecs.register_error(name, _passthrough_error_handler)
    return name


def build_substitution_table(
    substitution: dict[str, str],
) -> tuple[dict[int, bytes], "MultiCharSubstitution | None"]:
    """
    Build a substitution table.
    Convert a Unicode->str substitution dict of variable length
    (ej. mathics_scanner.characters.UNICODE_CHARACTER_TO_ASCII) into:

      - single_table: dict[int, bytes], for entries associated to
        single character keys -- these are compatible with
        codecs.charmap_encode.
      - multi: a MultiCharSubstitution for entries associated to
        multiple character keys (ej. sequences base+diacritic
        combinant like 'c' + COMBINING DOT BELOW). codecs.charmap_encode
        process entries a single point at time and NEVER can match
        them. These are resulved by a pre-step of substrings replacement,
        before apply the charmap_encode.
    """
    single: dict[int, bytes] = {}
    multi: dict[str, str] = {}
    skipped_empty = 0
    for ch, repl in substitution.items():
        if len(ch) == 0:
            continue
        if len(ch) == 1:
            single[ord(ch)] = repl.encode("utf-8")
        else:
            multi[ch] = repl

    return single, (MultiCharSubstitution(multi) if multi else None)


class MultiCharSubstitution:
    """Replace many character substrings, longest first."""

    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping
        # longest first, to give precedence to the most specific rules.
        keys = sorted(mapping, key=len, reverse=True)
        self._pattern = re.compile("|".join(re.escape(k) for k in keys))

    def apply(self, text: str) -> str:
        return self._pattern.sub(lambda m: self.mapping[m.group(0)], text)


def encode_with_substitution(
    value: str,
    single_table: dict[int, bytes],
    multi: "MultiCharSubstitution | None" = None,
) -> str:
    """
    Apply a substitution table 1:many (see build_substitution_table)
    over `value`, allowing pass missing entry character without changes.
    Return a Python str normal (not the convention "1 char = 1 byte" used by
    WLCharmapCodec for 8-bit true encodings).
    """
    if multi is not None:
        value = multi.apply(value)
    errors = register_passthrough_error_handler()
    encoded, _ = codecs.charmap_encode(value, errors, single_table)
    return encoded.decode("utf-8")


def make_codec(tag: str, entries: list[Entry]) -> WLCharmapCodec:
    """
    Build a WLCharmapCodec from already parsed `entries`  (ej.
    by `load_encoding_table`, using the Mathics3 interpreter).
    """
    decoding_table, encoding_table = build_charmap(tag, entries)
    return WLCharmapCodec(decoding_table, encoding_table)


def register_codec(name: str, tag: str, entries: list[Entry]) -> None:
    """
    Register an encoding (defined by `tag`/`entries`, already parsed)
    under the name `name`, to be able to use
    'text'.encode(name) / bytes.decode(name) directly as any native
    Python codec.
    """
    codec = make_codec(tag, entries)
    # Python normaliza el nombre del encoding (minusculas, '-' -> '_')
    # antes de invocar las search functions registradas.
    normalized_name = name.lower().replace("-", "_")

    def search_function(encoding_name: str):
        if encoding_name != normalized_name:
            return None
        return codecs.CodecInfo(name=name, encode=codec.encode, decode=codec.decode)

    codecs.register(search_function)
