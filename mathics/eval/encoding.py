"""
Functions to format strings in a given encoding.

`encode_string_value` / `decode_bytes_value`: convert between the internal
Unicode string representation and a given target encoding.

`from_python_encoding` / `to_python_encoding`: translate between WMA and
Python character encoding names.

`get_encoding_table`: get the (Unicode ordinal -> byte) table for a given
character encoding, used to *encode* internal strings into that encoding.

`load_encoding_table`: load a custom encoding table from a WL encoding
file description (SystemFiles/CharacterEncodings/*.wl).

Design notes (see discussion that led to this rewrite):

- WL "8Bit" encoding files only list the *exceptions* to a plain Latin-1
  identity mapping; codes not listed pass through unchanged. So the
  decoding table always starts as `chr(i) for i in range(256)` and gets
  patched with the entries found in the file.
- Each entry can carry a third boolean, `invertible`. When it is `False`
  (used for entries that map to a WL *named character*, e.g. `\\[Cross]`,
  chosen as a safe visual stand-in rather than the "real" Unicode point
  for that byte) the mapping is only valid for *decoding* (byte -> str),
  never for *encoding* back (str -> byte). Omitted => `True` (bidirectional).
- We rely on `codecs.charmap_encode`/`charmap_decode`, the same primitives
  the Python stdlib uses to implement its own single-byte codecs
  (see Lib/encodings/iso8859_8.py, cp1252.py, etc). We build the encode
  table as a plain `dict[int, int]` rather than via `codecs.charmap_build`,
  because that helper can return an immutable, optimized `EncodingMap`
  when the table is (almost) bijective, and we need to *delete* the
  non-invertible entries from it.
- Because `.to_python(string_quotes=False)` is called on Strings already
  parsed by the WL tokenizer, `\\:UUUU` and `\\[Name]` are *already*
  resolved to real Unicode characters by the time we see them here — no
  separate named-character lookup table is needed in this context (unlike
  a standalone script parsing the .wl file as raw text).
"""

from __future__ import annotations

import codecs
from typing import Final

from mathics_scanner.characters import UNICODE_CHARACTER_TO_ASCII

from mathics.core.atoms import String
from mathics.core.convert.op import operator_to_unicode
from mathics.eval.wl_charmap_codec import (
    TAG_SIZES,
    Entry,
    assert_ascii_safe,
    build_charmap,
    build_substitution_table,
    escape_unrepresentable_char,
)
from mathics.settings import ROOT_DIR

# Map WMA encoding names to Python encoding names
# see https://docs.python.org/3/library/codecs.html#standard-encodings
CHARACTER_ENCODING_MAP: Final[dict[str, str]] = {
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

REVERSE_CHARACTER_ENCODING_MAP: Final[dict[str, str]] = {
    py: wl for wl, py in CHARACTER_ENCODING_MAP.items()
}

# This character is used in encoding in WMA, and differs from what we
# have in the mathics-scanner tables:
UNICODE_CHARACTER_TO_ASCII.update({operator_to_unicode["Times"]: r" x "})

# These encoding names correspond 1:1 to Python standard codec
# (see CHARACTER_ENCODING_MAP: "Unicode"->"utf_16", "UTF-8"/"UTF8"
# ->"utf_8"). There is no .wl file for them in WMA -- are the native representation
# so we delegate it to Python directly instead of looking for a table/file which could not exist.
NATIVE_PYTHON_ENCODINGS: Final[frozenset] = frozenset({"Unicode", "UTF-8", "UTF8"})


def _is_native_python_encoding(encoding: str) -> bool:
    return encoding in NATIVE_PYTHON_ENCODINGS


# Encode-direction tables (Unicode ordinal -> destination), used by
# `encode_string_value`. "ASCII" is a pseudo-encoding, not loaded from a
# .wl file, so it gets a substitution table instead of the int-keyed
# charmap tables built by `load_encoding_table`. "Unicode"/"UTF-8"/"UTF8"
# don't need an entry here at all -- see NATIVE_PYTHON_ENCODINGS.
# "ASCII" promise return pure ASCII; let's check instead assuming it
# (see assert_ascii_safe -- nothing in the substitution mechanism ensures it structurally,
# differently from the 8-bit charmap tables).
assert_ascii_safe(UNICODE_CHARACTER_TO_ASCII, table_name="ASCII")
_ASCII_SINGLE_TABLE, _ASCII_MULTI = build_substitution_table(UNICODE_CHARACTER_TO_ASCII)

WMA_UNICODE_CHARACTER_MAPS: dict[str, dict] = {
    "ASCII": _ASCII_SINGLE_TABLE,
}
# Substitutions whose key involves more than a single character (
# combination sequences), indexed by encoding name -- see build_substitution_table.
WMA_MULTI_CHAR_SUBSTITUTIONS: dict[str, object] = {"ASCII": _ASCII_MULTI}

# Decode-direction tables (256-char strings) for the real, file-loaded
# 8-bit charmap encodings only. If `encoding` has an entry here, it is a
# "real" charmap encoding and `encode_string_value`/`decode_bytes_value`
# use `codecs.charmap_encode`/`charmap_decode` on it.
WMA_DECODE_TABLES: dict[str, str] = {}


class EncodingNameError(Exception):
    pass


def encode_string_value(value: str, encoding: str) -> str:
    """
    Convert an Unicode string `value` to its representation under
    `encoding`, mirroring WMA's `ToString[expr, CharacterEncoding->encoding]`
    (OutputForm-style, see the $CharacterEncoding documentation):

    - A character already representable in `encoding` is left unchanged
      -- there is nothing to "convert", it's already valid raw form.
    - A character that is NOT representable is replaced by its Wolfram
      Language escape form (`\\[Name]` if it has one, else `\\:XXXX`),
      so the *entire result is always representable in `encoding`* --
      this NEVER returns raw bytes or a byte-per-character string.

    "Unicode"/"UTF-8"/"UTF8" can represent every character, so nothing
    ever needs escaping for them and `value` is returned as-is.
    """
    if encoding in ("Unicode", "UTF-8", "UTF8"):
        return value

    if encoding in WMA_DECODE_TABLES:
        # True encodings loaded from .wl files.
        encode_table = WMA_UNICODE_CHARACTER_MAPS[encoding]
        return "".join(
            ch if ord(ch) in encode_table else escape_unrepresentable_char(ch)
            for ch in value
        )

    # Pseudo-encodings substitutions (ej. "ASCII"): characters already representable
    # in this encoding (para ASCII: ord < 128) stay the same;
    # If not, use the approximate substitute if it exists (UNICODE_CHARACTER_TO_ASCII),
    # finally, if no substitute is avaliable, fall back to the WL escaped character name --
    # never leave a non-ascii character.
    table = get_encoding_table(encoding)
    multi = WMA_MULTI_CHAR_SUBSTITUTIONS.get(encoding)
    if multi is not None:
        value = multi.apply(value)

    result = []
    for ch in value:
        if ord(ch) < 128:
            result.append(ch)
            continue
        sub = table.get(ord(ch))
        result.append(
            sub.decode("utf-8") if sub is not None else escape_unrepresentable_char(ch)
        )
    return "".join(result)


def decode_bytes_value(value: bytes, encoding: str) -> str:
    """
    Convert raw bytes `value`, understood to be in `encoding`, to the
    internal Unicode string representation.

    For "Unicode"/"UTF-8"/"UTF8" delegates directly to Python's own
    codec. For file-loaded 8-bit charmap encodings, uses the table
    built by `load_encoding_table`.
    """
    if _is_native_python_encoding(encoding):
        return value.decode(to_python_encoding(encoding))

    if encoding not in WMA_DECODE_TABLES:
        raise EncodingNameError(f"No decode table available for {encoding!r}")
    decoded, _ = codecs.charmap_decode(value, "strict", WMA_DECODE_TABLES[encoding])
    return decoded


def from_python_encoding(encoding):
    """
    Return the name of a WMA character encoding name from
    the name of the equivalent Python character encoding.
    """
    return REVERSE_CHARACTER_ENCODING_MAP.get(encoding)


def get_encoding_table(encoding: str) -> dict:
    """
    Return the encode-direction table for `encoding`: for file-loaded
    8-bit charmap encodings this is `dict[int, int]` (Unicode ordinal ->
    byte), suitable for `codecs.charmap_encode`; for pseudo-encodings
    like "ASCII" it is `dict[int, bytes]` (see build_substitution_table).
    Returns `{}` for the native Python encodings (Unicode/UTF-8/UTF8),
    which don't use a table at all -- see NATIVE_PYTHON_ENCODINGS.
    """
    if _is_native_python_encoding(encoding):
        return {}
    try:
        return WMA_UNICODE_CHARACTER_MAPS[encoding]
    except KeyError:
        raise EncodingNameError(encoding)


def load_encoding_table(encoding, evaluation):
    """
    Load an encoding file when needed.

    Custom encodings are stored in SystemFiles/CharacterEncodings.
    These files store WL expressions of the form

    `{tag, {{code, repr, invertible__}, ...}}`

    with `tag` one of `"7Bit"` or `"8Bit"`, `code` a character code and
    `repr` the string representing that character code in the current
    encoding. If present, `invertible` (default `True`) indicates
    whether the mapping should also be used in the reverse (encode)
    direction; entries that alias a byte to a WL *named character* as a
    safe visual stand-in (rather than that byte's true Unicode point)
    are typically marked `False`.

    Codes not explicitly listed pass through as their own Latin-1
    codepoint (WL encoding files only list the *exceptions*).

    The file is loaded using `eval_Get`. If the file `{encoding}.wl` does
    not exist, or `eval_Get` returns an expression that doesn't match
    the expected format, this raises `EncodingNameError`.
    """
    from mathics.eval.files_io.files import eval_Get

    if (
        encoding in WMA_DECODE_TABLES
        or _is_native_python_encoding(encoding)
        or encoding in WMA_UNICODE_CHARACTER_MAPS
    ):
        # Already loaded. Do nothing.
        return

    etl = eval_Get(
        f"{ROOT_DIR}/SystemFiles/CharacterEncodings/{encoding}.wl",
        evaluation,
        "ASCII",
        None,
        None,
    )
    if etl is None or not etl.has_form("List", 2):
        evaluation.message("$CharacterEncoding", "charfile", String(encoding))
        raise EncodingNameError(encoding)

    tag = etl.elements[0].to_python(string_quotes=False)
    entries_expr = etl.elements[1]
    if tag not in TAG_SIZES or not entries_expr.has_form("List", None):
        evaluation.message("$CharacterEncoding", "charfile", String(encoding))
        raise EncodingNameError(encoding)
    if any(not entry.has_form("List", None) for entry in entries_expr.elements):
        evaluation.message("$CharacterEncoding", "charfile", String(encoding))
        raise EncodingNameError(encoding)

    entries = []
    try:
        for entry in entries_expr.elements:
            code, repr_str, *rest = (
                el.to_python(string_quotes=False) for el in entry.elements
            )
            invertible = rest[0] if rest else True
            entries.append(Entry(code=code, char=repr_str, invertible=invertible))
    except (IndexError, TypeError) as e:
        raise EncodingNameError(encoding) from e

    decoding_table, encode_table = build_charmap(tag, entries)

    WMA_DECODE_TABLES[encoding] = decoding_table
    WMA_UNICODE_CHARACTER_MAPS[encoding] = encode_table


def to_python_encoding(encoding) -> str:
    """
    Return the name of the equivalent Python encoding to a WMA
    character encoding name.
    """
    return CHARACTER_ENCODING_MAP.get(encoding)
