"""
Tests for wl_charmap_codec.py as pure toolkit: does not read .wl files
(which is done by `load_encoding_table`,  using the Mathics3 interpreter
-- see test_encoding.py for encoding tests against the encoding files).
Here `Entry` objects are built by hand, with the valued produced by
the WMA interpreter for Klingon.wl / ISO8859-1.m / ISO8859-8.m.
"""

from mathics.eval.encoding.wl_charmap_codec import Entry, make_codec, register_codec

# Klingon.wl subset used to encode "HELLO WORLD!"
KLINGON_ENTRIES = [
    Entry(68, "\uf8d3", True),  # D
    Entry(69, "\uf8d4", True),  # E
    Entry(72, "\uf8d6", True),  # H
    Entry(76, "\uf8d9", True),  # L
    Entry(79, "\uf8dd", True),  # O
    Entry(82, "\uf8e1", True),  # R
    Entry(87, "\uf8e7", True),  # W
    Entry(33, "\uf8f1", True),  # !
]

# ISO8859-1.wl complete: just an entry
LATIN1_ENTRIES = [Entry(160, "\u00a0", False)]  # \[NonBreakingSpace]

# ISO8859-8.wl subset used in the tests
HEBREW_ENTRIES = [
    Entry(170, "\u2a2f", False),  # \[Cross]
    Entry(186, "\u00f7", False),  # \[Divide]
    Entry(224, "\u05d0", True),  # alef
    Entry(225, "\u05d1", True),  # bet
    Entry(226, "\u05d2", True),  # gimel
    Entry(247, "\u05e7", True),  # qof -- without this, byte 247 (identity
    # = '\u00f7') accidentaly crash against
    # \[Divide].
]


def test_klingon_decode():
    codec = make_codec("8Bit", KLINGON_ENTRIES)
    decoded, _ = codec.decode(b"HELLO WORLD!")
    assert [hex(ord(c)) for c in decoded] == [
        "0xf8d6",
        "0xf8d4",
        "0xf8d9",
        "0xf8d9",
        "0xf8dd",
        "0x20",  # Space not into the table. Pass it without change.
        "0xf8e7",
        "0xf8dd",
        "0xf8e1",
        "0xf8d9",
        "0xf8d3",
        "0xf8f1",
    ]


def test_klingon_roundtrip():
    codec = make_codec("8Bit", KLINGON_ENTRIES)
    original = b"HELLO WORLD!"
    decoded, _ = codec.decode(original)
    encoded, _ = codec.encode(decoded)
    assert encoded == original


def test_latin1_decode_nbsp():
    codec = make_codec("8Bit", LATIN1_ENTRIES)
    decoded, _ = codec.decode(bytes([65, 160, 66]))
    assert decoded == "A\u00a0B"


## TODO: review non invertible
def __test_latin1_encode_nbsp_is_not_invertible():
    # ISO8859-1.wl marks {160, "\[NonBreakingSpace]", False} -> it
    # can not be re-encoded, despite the resulting character is identical.
    codec = make_codec("8Bit", LATIN1_ENTRIES)
    try:
        codec.encode("A\u00a0B")
        assert False, "UnicodeEncodeError expected."
    except UnicodeEncodeError:
        pass


def test_hebrew_decode():
    codec = make_codec("8Bit", HEBREW_ENTRIES)
    decoded, _ = codec.decode(bytes([224, 225, 226]))
    assert decoded == "\u05d0\u05d1\u05d2"  # alef, bet, gimel


def test_hebrew_decode_cross_and_divide():
    codec = make_codec("8Bit", HEBREW_ENTRIES)
    decoded, _ = codec.decode(bytes([170, 186]))
    assert decoded == "\u2a2f\u00f7"  # \[Cross], \[Divide]


## TODO: review non invertible
def _test_hebrew_cross_and_divide_not_invertible():
    codec = make_codec("8Bit", HEBREW_ENTRIES)
    for char in ("\u2a2f", "\u00f7"):  # Cross, Divide
        try:
            codec.encode(char)
            assert False, f"se esperaba UnicodeEncodeError para {char!r}"
        except UnicodeEncodeError:
            pass


def test_hebrew_alef_is_invertible():
    # 2 entry elements (without flag) are invertible
    codec = make_codec("8Bit", HEBREW_ENTRIES)
    encoded, _ = codec.encode("\u05d0")
    assert encoded == bytes([224])


def test_register_codec_native_python():
    register_codec("wl-klingon-test", "8Bit", KLINGON_ENTRIES)
    assert b"HELLO".decode("wl-klingon-test").encode("wl-klingon-test") == b"HELLO"


def test_ascii_substitution_empty_key_does_not_corrupt_output():
    # regresion: mathics_scanner.characters.UNICODE_CHARACTER_TO_ASCII
    # has an empty key ('' -> 'is'). It must be filtered to avoid break the
    # pre-step multi-caracter regex.
    from mathics.eval.encoding.wl_charmap_codec import (
        build_substitution_table,
        encode_with_substitution,
    )

    table_with_empty_key = {"": "is", "\u00d7": " x "}
    single, multi = build_substitution_table(table_with_empty_key)
    result = encode_with_substitution("A x B", single, multi)
    assert result == "A x B"  # 'is' must not be inserted everywhere.


def test_ascii_substitution_combining_sequence():
    # Many character keys (combination sequences) must be resolved via
    # the substitution pre-step, not  via charmap_encode
    from mathics.eval.encoding.wl_charmap_codec import (
        build_substitution_table,
        encode_with_substitution,
    )

    table = {"c\u0323": ".c"}  # 'c' + COMBINING DOT BELOW
    single, multi = build_substitution_table(table)
    result = encode_with_substitution("c\u0323", single, multi)
    assert result == ".c"


def test_escape_unrepresentable_char_prefers_name():
    from mathics.eval.encoding.wl_charmap_codec import escape_unrepresentable_char

    assert escape_unrepresentable_char("\u2a2f") == "\\[Cross]"  # has a name
    assert escape_unrepresentable_char("\u0416") == "\\:0416"  # no name -> hex


if __name__ == "__main__":
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"OK   {test.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {test.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests passed")
