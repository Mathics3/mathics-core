"""
wl_charmap_codec.py

Pure toolkit for building, from already parsed entries from a .wl
encoding file (with format {"8Bit", {{charcode, "repr",
invertible?}, ...}}), a real Python codec: a decode table
(byte -> str) and an encoding table (str -> byte).
Following the behavior observed in WMA, the field `invertible`
is not taken into account. If the entry "repr" is `None`,
then it is replaced by the unicode character with
code `0x0xF200 + charcode`.

Construction primitives ('charmap_build', 'charmap_encode',
'charmap_decode') are the same used by the Pythons stdlib for implementing
its single byte codecs (see Lib/encodings/
iso8859_8.py, cp1252.py, mac_roman.py, etc.)

Because 'codecs.charmap_encode'/'codecs.charmap_decode' only ever look
at one raw *byte* (0-255) of input at a time, everything built here
only works for genuinely single-byte encodings ("7Bit"/"8Bit" tags).
'register_codec_from_tables' enforces this with an explicit check --
see its docstring.
"""

from __future__ import annotations

import codecs
import re
import unicodedata
from dataclasses import dataclass

from mathics_scanner.characters import CHARACTER_TO_NAME


@dataclass
class Entry:
    code: int
    char: str
    invertible: bool


TAG_SIZES = {"7Bit": 128, "8Bit": 256, "16Bit": 512}


def build_charmap(tag: str, entries: list[Entry]) -> tuple[str, dict[int, int]]:
    """
    Build:
      - decoding_table: fixed length Python string (256 for 8Bit) for
        decoding byte -> character. Every position always has a real,
        round-trippable character: untouched positions default to
        Latin-1 identity, entries listing an explicit character
        override that position, and `{code, None}` entries (turned
        into `chr(0xF200 + code)` by the caller before this function
        ever sees them -- see load_encoding_table) place a
        Private-Use-Area placeholder there. There is no "undefined,
        raises on decode" sentinel: real Wolfram Mathematica always
        successfully decodes every byte (confirmed:
        `FromCharacterCode[142, "Symbol"]` -- byte 142 is `{142, None}`
        in Symbol.wl -- gives `"\\:f28e"`, i.e. exactly
        `chr(0xF200 + 142)`, not a decode failure).
      - encoding_table: dict character(ordinal) -> byte. Seeded with
        this tag's *native*-range identity (ord < size, e.g. plain
        ASCII/Latin-1 for "8Bit"), then overridden -- scanning bytes
        0..size-1 in order, so the highest matching byte code wins on
        a genuine multi-byte collision -- by whatever the decode table
        assigns each byte to. This reproduces, in a single unified
        rule, three behaviors confirmed against real Wolfram
        Mathematica:
          * A native-range character with NO explicit decode target
            anywhere still round-trips through its own byte (identity
            seed never gets overwritten for it): Klingon.wl reassigns
            byte 72 (0x48) away from "H" (to a pIqaD glyph, U+F8D6),
            yet plain "H" still encodes back to byte 72 -- confirmed
            via `ToString["Hola ...", CharacterEncoding->"Klingon"]`
            keeping "Hola" literal.
          * A character WITH an explicit decode target uses that byte,
            even when it's itself in the native range and even though
            the entry is marked `invertible -> False`: confirmed via
            `ToCharacterCode["\\[Divide]", "ISO8859-8"] -> {186}`
            (ISO8859-8.wl has `{186, "\\[Divide]", False}`; byte 247,
            the character's own Latin-1 identity position, is *itself*
            reassigned to Hebrew Qof in that file, so there is no
            competing identity mapping to worry about here -- but even
            where one could exist, the decode-table override always
            wins by construction, since it's applied after the seed).
          * `{code, None}` entries (-> PUA placeholder, see above) are
            just ordinary decode targets under this rule, so they
            participate in encoding too, and round-trip like anything
            else: confirmed via `ToCharacterCode["\\:f28e", "Symbol"]
            -> {142}`.
        The `invertible` field on `Entry` is intentionally NOT
        consulted anywhere in this function -- confirmed to have no
        effect on real WMA's encode direction (see the ISO8859-8
        example above). It's kept as parsed data on `Entry` only for
        callers that might want to inspect the table, not used here.
        NOTE: when two or more DIFFERENT bytes explicitly decode to
        the exact same character (e.g. Symbol.wl's duplicate
        `{210, "\\[RegisteredTrademark]"}` / `{226,
        "\\[RegisteredTrademark]", False}` pair), the highest-numbered
        byte wins for encoding under this rule. This specific tie-break
        is NOT verified against real WMA (we don't have a test case
        for it) -- but since all such bytes decode to the identical
        character, the two are functionally interchangeable for
        encoding purposes regardless of which one is picked.
    """
    size = TAG_SIZES.get(tag, 256)
    table = [chr(i) for i in range(size)]  # default: identity (Latin-1)
    for e in entries:
        if e.code < size:
            table[e.code] = e.char
    decoding_table = "".join(table)

    encoding_table: dict[int, int] = {i: i for i in range(size)}
    for code, ch in enumerate(decoding_table):
        encoding_table[ord(ch)] = code

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


def _is_combining_sequence(key: str) -> bool:
    """
    True if `key` is a base character followed by one or more Unicode
    combination code ('Mn'/'Mc' category) -- ej. 'c' + COMBINING DOT
    BELOW. These are the unique multicharacter keys for which a substring
    replacement makes sense: no single character in the sequence is
    meaningful by itself.
    Without this test, a multicharacter key resulting in a plain text
    (like  'lim' -> 'mlim' in  UNICODE_CHARACTER_TO_ASCII) spoils any
    literal text containint that string by chance ('limit', 'swimming', etc.),
    without any relation with the original motivation of the entry.
    """
    return len(key) > 1 and all(
        unicodedata.category(c) in ("Mn", "Mc") for c in key[1:]
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


_ESCAPE_ERROR_NAME = "wl_charmap_escape"


def _escape_error_handler(error: UnicodeEncodeError):
    r"""
    Encode error handler implementing $CharacterEncoding's documented
    output behavior: "Unencodable characters can be input and will be
    output in standard \[Name] and \:nnnn form." (see
    https://reference.wolfram.com/language/ref/$CharacterEncoding.html).

    Returns *bytes* (the escape text encoded as plain ASCII), not
    `str` -- if we returned `str`, codecs.charmap_encode would
    recursively try to re-encode that replacement through the SAME
    charmap, which can itself fail: a custom encoding may remap
    ordinary ASCII digits/punctuation too (e.g. "Klingon" remaps the
    digit '4'), so the escape text for one unencodable character could
    contain a character that is *also* unencodable in that charmap.
    Returning bytes directly sidesteps that entirely.
    """
    chars = error.object[error.start : error.end]
    escaped = "".join(escape_unrepresentable_char(ch) for ch in chars)
    return escaped.encode("ascii"), error.end


def register_escape_error_handler(name: str = _ESCAPE_ERROR_NAME) -> str:
    """
    Register (if needed) the encode error handler described above.
    Return the name for using as `errors=` in io.open()/str.encode()/
    codecs.charmap_encode.
    """
    try:
        codecs.lookup_error(name)
    except LookupError:
        codecs.register_error(name, _escape_error_handler)
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

    for ch, repl in substitution.items():
        if len(ch) == 0:
            continue
        if len(ch) == 1:
            single[ord(ch)] = repl.encode("utf-8")
        elif _is_combining_sequence(ch):
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


def canonicalize_codec_name(name: str) -> str:
    """
    Normalize `name` the same way CPython's own codec lookup machinery
    normalizes the name it hands to registered search functions (see
    Python/codecs.c:normalizestring, and codecs.register's docs: "the
    encoding name in all lower case letters with hyphens and spaces
    converted to underscores"): lowercase, with runs of spaces and/or
    hyphens collapsed to a single underscore.

    Both the registration side and the search function MUST apply this
    same transform, or a name containing a space (plausible for a
    user-authored encoding, e.g. "Mac Roman") silently fails to
    resolve: registering "Mac Roman" naively as "mac roman" (spaces
    left alone) while codecs.lookup("Mac Roman") invokes search
    functions with "mac_roman" means the two never match.
    """
    return re.sub(r"[-\s]+", "_", name.strip().lower())


# normalized codec name -> (decoding_table, encoding_table). Backing
# store for a *single* search function, registered once, rather than
# one new codecs.register() call (and one new closure) per encoding.
# codecs.register() has no "replace" or "unregister by name" semantics
# (pre-3.10 not even a general unregister existed), so accumulating a
# search function per custom encoding would mean every future
# codecs.lookup() of a name nobody has registered yet keeps scanning
# an ever-growing list of one-shot functions for the lifetime of the
# process.
_REGISTERED_TABLES: dict[str, tuple[str, dict[int, int]]] = {}
_SEARCH_FUNCTION_INSTALLED = False


def _build_codec_info(
    name: str, decoding_table: str, encoding_table: dict[int, int]
) -> codecs.CodecInfo:
    """
    Build the FULL codec machinery (incremental encoder/decoder,
    stream reader/writer), not just one-shot encode/decode -- required
    for `io.open(path, encoding=name)` to work in text/streaming mode.
    Follows the same pattern the Python stdlib itself uses for its
    charmap-based codecs (see Lib/encodings/iso8859_8.py, cp1252.py,
    etc: `encode`/`decode` there use `codecs.charmap_encode`/
    `charmap_decode` against module-level tables; here the tables are
    per-registration, so the nested classes close over them instead).
    """

    class _Codec(codecs.Codec):
        def encode(self, input: str, errors: str = "strict"):
            return codecs.charmap_encode(input, errors, encoding_table)

        def decode(self, input: bytes, errors: str = "strict"):
            return codecs.charmap_decode(input, errors, decoding_table)

    class _IncrementalEncoder(codecs.IncrementalEncoder):
        def encode(self, input: str, final: bool = False):
            return codecs.charmap_encode(input, self.errors, encoding_table)[0]

    class _IncrementalDecoder(codecs.IncrementalDecoder):
        def decode(self, input: bytes, final: bool = False):
            return codecs.charmap_decode(input, self.errors, decoding_table)[0]

    class _StreamWriter(_Codec, codecs.StreamWriter):
        pass

    class _StreamReader(_Codec, codecs.StreamReader):
        pass

    codec = _Codec()
    return codecs.CodecInfo(
        name=name,
        encode=codec.encode,
        decode=codec.decode,
        incrementalencoder=_IncrementalEncoder,
        incrementaldecoder=_IncrementalDecoder,
        streamreader=_StreamReader,
        streamwriter=_StreamWriter,
    )


def _wl_charmap_search_function(encoding_name: str):
    entry = _REGISTERED_TABLES.get(encoding_name)
    if entry is None:
        return None
    decoding_table, encoding_table = entry
    return _build_codec_info(encoding_name, decoding_table, encoding_table)


def _ensure_search_function_installed() -> None:
    global _SEARCH_FUNCTION_INSTALLED
    if not _SEARCH_FUNCTION_INSTALLED:
        codecs.register(_wl_charmap_search_function)
        _SEARCH_FUNCTION_INSTALLED = True


def register_codec_from_tables(
    name: str, decoding_table: str, encoding_table: dict[int, int]
) -> str:
    """
    Register a full Python codec directly from an already-built
    (decoding_table, encoding_table) pair -- e.g. the ones
    load_encoding_table already computes and stores, avoiding having to
    keep the raw Entry list around just to register a codec.

    Idempotent: calling this again with the same `name` and identical
    tables is a no-op; calling it with a *different* table for a name
    already registered replaces the entry (last write wins -- there is
    no concept of "unregistering" a stale mapping, so callers should
    only re-register when the underlying .wl file could plausibly have
    changed, e.g. between sessions, not on every lookup).

    Returns the *normalized* codec name that must actually be passed to
    io.open()/str.encode()/bytes.decode() to reach this codec -- e.g.
    register_codec_from_tables("Mac Roman", ...) returns "mac_roman",
    not "Mac Roman" (see canonicalize_codec_name).

    Raises ValueError if `decoding_table` has more than 256 entries:
    codecs.charmap_encode/charmap_decode only ever look at one input
    byte (0-255) at a time, so no charmap-based Python codec can
    represent an encoding whose external representation needs more
    than one byte per unit (e.g. a "16Bit"-tagged custom encoding,
    which build_charmap can happily construct a >256-entry table for,
    but which can never be turned into a working codec this way -- that
    would need a real stateful multi-byte codec instead).
    """
    if len(decoding_table) > 256:
        raise ValueError(
            f"{name!r}: decoding table has {len(decoding_table)} entries; "
            "codecs.charmap_encode/charmap_decode only ever look at one "
            "input byte (0-255) at a time, so no charmap-based Python "
            "codec can represent an encoding with more than 256 code "
            "points on the wire. This needs a real stateful multi-byte "
            "codec instead."
        )
    normalized_name = canonicalize_codec_name(name)
    _REGISTERED_TABLES[normalized_name] = (decoding_table, encoding_table)
    _ensure_search_function_installed()
    return normalized_name


def register_codec(name: str, tag: str, entries: list[Entry]) -> str:
    """
    Register an encoding (defined by `tag`/`entries`, already parsed)
    under the name `name`, to be able to use
    'text'.encode(name) / bytes.decode(name) directly as any native
    Python codec. Returns the normalized codec name (see
    register_codec_from_tables).
    """
    decoding_table, encoding_table = build_charmap(tag, entries)
    return register_codec_from_tables(name, decoding_table, encoding_table)
