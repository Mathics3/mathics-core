"""
Tests para wl_charmap_codec.py como toolkit puro: NO lee archivos .wl/.m
(esa responsabilidad es de encoding.load_encoding_table, via el
interprete real de Mathics3 -- ver test_encoding.py para tests de
integracion end-to-end contra los archivos reales). Aca las `Entry`
se arman a mano, con los mismos valores que ya verificamos que produce
el interprete real para Klingon.wl / ISO8859-1.m / ISO8859-8.m.

Correr con: python3 test_wl_charmap_codec.py
"""

from mathics.eval.wl_charmap_codec import Entry, make_codec, register_codec

# Subconjunto de Klingon.wl necesario para codificar "HELLO WORLD!"
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

# ISO8859-1.wl completo: una sola entrada
LATIN1_ENTRIES = [Entry(160, "\u00a0", False)]  # \[NonBreakingSpace]

# Subconjunto de ISO8859-8.wl usado en los tests
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
        "0x20",  # el espacio no esta en la tabla -> pasa por identidad
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


def test_latin1_encode_nbsp_is_not_invertible():
    # ISO8859-1.wl marca {160, "\[NonBreakingSpace]", False} -> no debe
    # poder volver a codificarse, aunque el caracter resultante sea
    # identico al de la identidad.
    codec = make_codec("8Bit", LATIN1_ENTRIES)
    try:
        codec.encode("A\u00a0B")
        assert False, "se esperaba UnicodeEncodeError"
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


def test_hebrew_cross_and_divide_not_invertible():
    codec = make_codec("8Bit", HEBREW_ENTRIES)
    for char in ("\u2a2f", "\u00f7"):  # Cross, Divide
        try:
            codec.encode(char)
            assert False, f"se esperaba UnicodeEncodeError para {char!r}"
        except UnicodeEncodeError:
            pass


def test_hebrew_alef_is_invertible():
    # las entradas de 2 elementos (sin flag) son invertibles por defecto
    codec = make_codec("8Bit", HEBREW_ENTRIES)
    encoded, _ = codec.encode("\u05d0")
    assert encoded == bytes([224])


def test_register_codec_native_python():
    register_codec("wl-klingon-test", "8Bit", KLINGON_ENTRIES)
    assert b"HELLO".decode("wl-klingon-test").encode("wl-klingon-test") == b"HELLO"


def test_ascii_substitution_empty_key_does_not_corrupt_output():
    # regresion: mathics_scanner.characters.UNICODE_CHARACTER_TO_ASCII
    # tiene una entrada con clave vacia ('' -> 'is'), que si no se filtra
    # rompe la regex del pre-paso multi-caracter (matchea en TODAS partes).
    from mathics.eval.wl_charmap_codec import (
        build_substitution_table,
        encode_with_substitution,
    )

    table_with_empty_key = {"": "is", "\u00d7": " x "}
    single, multi = build_substitution_table(table_with_empty_key)
    result = encode_with_substitution("A x B", single, multi)
    assert result == "A x B"  # no debe insertar 'is' en todos lados


def test_ascii_substitution_combining_sequence():
    # las claves de mas de 1 caracter (secuencias de combinacion) deben
    # resolverse via el pre-paso de substring, no via charmap_encode
    from mathics.eval.wl_charmap_codec import (
        build_substitution_table,
        encode_with_substitution,
    )

    table = {"c\u0323": ".c"}  # 'c' + COMBINING DOT BELOW
    single, multi = build_substitution_table(table)
    result = encode_with_substitution("c\u0323", single, multi)
    assert result == ".c"


def test_escape_unrepresentable_char_prefers_name():
    from mathics.eval.wl_charmap_codec import escape_unrepresentable_char

    assert escape_unrepresentable_char("\u2a2f") == "\\[Cross]"  # tiene nombre
    assert escape_unrepresentable_char("\u0416") == "\\:0416"  # sin nombre -> hex


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
    print(f"\n{len(tests) - failed}/{len(tests)} tests pasaron")
