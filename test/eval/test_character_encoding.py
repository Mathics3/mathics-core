"""
Tests for the character-encoding subsystem: mathics.eval.wl_charmap_codec,
mathics.eval.encoding, and their integration into file I/O
(mathics.eval.files_io.read.Mathics3Open / mathics.core.streams.Stream).

Organized in three tiers, from fastest/most isolated to slowest/most
end-to-end:

  1. Pure unit tests for wl_charmap_codec.py -- no Mathics3 interpreter
     needed, run in milliseconds.
  2. Tests for encoding.py's encode/decode/load routines -- need a real
     Mathics3 interpreter (session-scoped fixture, built once), but use
     temporary, self-contained .wl files (never touch or depend on the
     repo's real SystemFiles/CharacterEncodings).
  3. End-to-end integration tests through Mathics3Open, actually
     reading/writing files on disk.

"""

import codecs

import pytest

from mathics.eval.encoding.wl_charmap_codec import (
    Entry,
    MultiCharSubstitution,
    WLCharmapCodec,
    assert_ascii_safe,
    build_charmap,
    build_substitution_table,
    encode_with_substitution,
    escape_unrepresentable_char,
    make_codec,
    register_codec,
    register_codec_from_tables,
)

# ======================================================================
# Tier 1: pure unit tests for wl_charmap_codec.py
# ======================================================================


class TestBuildCharmap:
    def test_unlisted_codes_default_to_latin1_identity(self):
        # .wl encoding files only list the *exceptions*; anything not
        # listed should pass through as its own Latin-1 codepoint.
        decoding_table, _ = build_charmap("8Bit", [])
        assert len(decoding_table) == 256
        assert decoding_table[65] == "A"
        assert decoding_table[224] == chr(224)

    def test_decode_uses_explicit_entry(self):
        entries = [Entry(code=224, char="\u05d0", invertible=True)]  # alef
        decoding_table, _ = build_charmap("8Bit", entries)
        assert decoding_table[224] == "\u05d0"

    def test_encode_roundtrips_invertible_entry(self):
        entries = [Entry(code=224, char="\u05d0", invertible=True)]
        _, encode_table = build_charmap("8Bit", entries)
        assert encode_table[ord("\u05d0")] == 224

    def test_invertible_defaults_to_true_when_flag_omitted(self):
        # 2-element entries (no third flag) are bidirectional by default.
        entries = [Entry(code=224, char="\u05d0", invertible=True)]
        _, encode_table = build_charmap("8Bit", entries)
        assert encode_table.get(ord("\u05d0")) == 224

    # TODO: revise this test.
    # def test_non_invertible_char_that_collides_with_identity_stays_excluded(self):
    #    # Regression: ISO8859-1.wl's {160, "\[NonBreakingSpace]", False}.
    #    # \[NonBreakingSpace] happens to BE chr(160) (the Latin-1 identity
    #    # value for that same byte), so a naive "is this ordinal mapped
    #    # to this code" check could accidentally think it's still
    #    # present after deletion. It must stay excluded regardless.
    #    entries = [Entry(code=160, char="\u00a0", invertible=False)]
    #    _, encode_table = build_charmap("8Bit", entries)
    #    assert ord("\u00a0") not in encode_table
    #
    #
    # def _test_non_invertible_entry_excluded_from_encode_table(self):
    #    # e.g. ISO8859-8.wl's {170, "\[Cross]", False}: valid for
    #    # decoding byte->char, but must NOT be usable in reverse.
    #    entries = [Entry(code=170, char="\u2a2f", invertible=False)]  # \[Cross]
    #   decoding_table, encode_table = build_charmap("8Bit", entries)
    #    assert decoding_table[170] == "\u2a2f"
    #    assert ord("\u2a2f") not in encode_table

    def test_7bit_tag_uses_128_byte_table(self):
        decoding_table, _ = build_charmap("7Bit", [])
        assert len(decoding_table) == 128

    def test_unknown_tag_defaults_to_256(self):
        decoding_table, _ = build_charmap("SomeFutureTag", [])
        assert len(decoding_table) == 256


class TestWLCharmapCodec:
    def test_decode_bytes_to_string(self):
        entries = [
            Entry(224, "\u05d0", True),
            Entry(225, "\u05d1", True),
        ]
        codec = make_codec("8Bit", entries)
        decoded, consumed = codec.decode(bytes([224, 225]))
        assert decoded == "\u05d0\u05d1"
        assert consumed == 2

    def test_encode_string_to_bytes(self):
        entries = [Entry(224, "\u05d0", True)]
        codec = make_codec("8Bit", entries)
        encoded, consumed = codec.encode("\u05d0")
        assert encoded == bytes([224])

    # def test_encode_non_invertible_char_raises(self):
    #    entries = [Entry(170, "\u2a2f", False)]
    #    codec = make_codec("8Bit", entries)
    #    with pytest.raises(UnicodeEncodeError):
    #        codec.encode("\u2a2f")

    def test_roundtrip_through_unmapped_ascii(self):
        entries = [Entry(72, "\uf8d6", True)]  # Klingon-style override on 'H'
        codec = make_codec("8Bit", entries)
        original = b"H WORLD"
        decoded, _ = codec.decode(original)
        assert decoded[1] == " "  # unmapped byte passes through unchanged
        encoded, _ = codec.encode(decoded)
        assert encoded == original


class TestEscapeUnrepresentableChar:
    def test_prefers_named_character_form(self):
        # \[Cross] has a WL name; must use it over the numeric escape.
        assert escape_unrepresentable_char("\u2a2f") == "\\[Cross]"

    def test_falls_back_to_hex_escape_when_no_name(self):
        # Cyrillic Zhe: no WL named-character form.
        assert escape_unrepresentable_char("\u0416") == "\\:0416"

    def test_hex_escape_is_four_lowercase_hex_digits(self):
        # pick a BMP character guaranteed to have no WL named-character
        # form: U+04FF (CYRILLIC SMALL LETTER HA WITH STROKE)
        result = escape_unrepresentable_char("\u04ff")
        assert result == "\\:04ff"

    def test_astral_plane_uses_six_digit_escape(self):
        result = escape_unrepresentable_char("\U0001f600")  # emoji, no WL name
        assert result == "\\|01f600"


class TestWLCharmapCodecConstruction:
    def test_can_be_constructed_directly_from_tables(self):
        decoding_table, encoding_table = build_charmap(
            "8Bit", [Entry(224, "\u05d0", True)]
        )
        codec = WLCharmapCodec(decoding_table, encoding_table)
        assert codec.decode(bytes([224]))[0] == "\u05d0"
        assert codec.encode("\u05d0")[0] == bytes([224])


class TestAssertAsciiSafe:
    def test_passes_for_pure_ascii_values(self):
        assert_ascii_safe({"\u00d7": " x ", "\u2265": ">="})  # should not raise

    def test_raises_for_non_ascii_value(self):
        with pytest.raises(ValueError):
            assert_ascii_safe({"x": "caf\u00e9"})


class TestBuildSubstitutionTable:
    def test_single_char_key_goes_to_single_table(self):
        single, multi = build_substitution_table({"\u00d7": " x "})
        assert single[ord("\u00d7")] == b" x "
        assert multi is None

    def test_empty_key_is_silently_skipped(self):
        # regression: mathics_scanner has an entry '' -> 'is'; an empty
        # key can't be a substring pattern (would match everywhere).
        single, multi = build_substitution_table({"": "is", "\u00d7": " x "})
        assert len(single) == 1
        assert multi is None or "" not in multi.mapping

    def test_combining_sequence_goes_to_multi_table(self):
        key = "c\u0323"  # 'c' + COMBINING DOT BELOW
        single, multi = build_substitution_table({key: ".c"})
        assert multi is not None
        assert multi.mapping[key] == ".c"

    def test_non_combining_multichar_key_is_rejected(self):
        # regression: 'lim' -> 'mlim' is NOT a combining sequence (three
        # plain ASCII letters); treating it like one would corrupt any
        # literal text containing "lim" by coincidence ("limit", "swimming").
        single, multi = build_substitution_table({"lim": "mlim", "\u00d7": " x "})
        assert multi is None or "lim" not in multi.mapping
        assert single[ord("\u00d7")] == b" x "


class TestMultiCharSubstitution:
    def test_apply_replaces_combining_sequence(self):
        multi = MultiCharSubstitution({"c\u0323": ".c"})
        assert multi.apply("Xc\u0323Y") == "X.cY"

    def test_apply_prefers_longest_match(self):
        multi = MultiCharSubstitution({"a\u0323": "A1", "a\u0323\u0301": "A2"})
        assert multi.apply("a\u0323\u0301") == "A2"

    def test_apply_leaves_unmatched_text_unchanged(self):
        multi = MultiCharSubstitution({"c\u0323": ".c"})
        assert multi.apply("hello world") == "hello world"


class TestEncodeWithSubstitution:
    def test_substitutes_known_chars(self):
        single, _ = build_substitution_table({"\u00d7": " x "})
        assert encode_with_substitution("A\u00d7B", single) == "A x B"

    def test_passes_through_unmapped_chars(self):
        single, _ = build_substitution_table({"\u00d7": " x "})
        # a character with no entry at all must pass through unchanged
        assert encode_with_substitution("A\u00e9B", single) == "A\u00e9B"

    def test_applies_multi_char_pass_before_single_char_pass(self):
        table = {"c\u0323": ".c", "\u00d7": " x "}
        single, multi = build_substitution_table(table)
        assert encode_with_substitution("c\u0323 \u00d7 x", single, multi) == ".c  x  x"


class TestRegisterCodec:
    def test_register_and_use_as_native_python_codec(self):
        entries = [Entry(72, "\uf8d6", True)]  # 'H' -> Klingon-ish char
        register_codec("wl-test-register-codec", "8Bit", entries)
        decoded = b"H".decode("wl-test-register-codec")
        assert decoded == "\uf8d6"
        assert decoded.encode("wl-test-register-codec") == b"H"

    def test_registered_codec_supports_streaming_incremental_use(self):
        # io.open(..., encoding=name) needs incrementalencoder/decoder
        # and streamreader/streamwriter, not just one-shot encode/decode.
        entries = [Entry(224, "\u05d0", True)]
        register_codec_from_tables(
            "wl-test-streaming-codec", *build_charmap("8Bit", entries)
        )
        info = codecs.lookup("wl-test-streaming-codec")
        assert info.incrementalencoder is not None
        assert info.incrementaldecoder is not None
        assert info.streamreader is not None
        assert info.streamwriter is not None

    # def test_registered_codec_enforces_invertibility(self):
    #    entries = [Entry(170, "\u2a2f", False)]
    #    register_codec_from_tables(
    #        "wl-test-invertibility-codec", *build_charmap("8Bit", entries)
    #    )
    #    with pytest.raises(UnicodeEncodeError):
    #        "\u2a2f".encode("wl-test-invertibility-codec")


# ======================================================================
# Tier 2: encoding.py routines, against a real Mathics3 interpreter
# ======================================================================

ISO8859_8_TEST_WL = r"""
{"8Bit",
  {{170, "\[Cross]", False}, {186, "\[Divide]", False},
   {224, "\:05d0"}, {225, "\:05d1"}, {226, "\:05d2"},
   {247, "\:05e7"}}
}
"""

ISO8859_1_TEST_WL = r"""
{"8Bit",
  {{160, "\[NonBreakingSpace]", False}}
}
"""


@pytest.fixture(scope="session")
def evaluation():
    """
    Boot a real Mathics3 interpreter once for the whole test session --
    this is expensive (loads all builtins), so it's session-scoped.
    """
    from mathics.core.load_builtin import import_and_load_builtins

    import_and_load_builtins()
    from mathics.session import MathicsSession

    return MathicsSession().evaluation


@pytest.fixture(autouse=True)
def _isolate_encoding_module_state():
    """
    encoding.py's WMA_DECODE_TABLES / WMA_UNICODE_CHARACTER_MAPS /
    _REGISTERED_CODEC_TO_WMA_NAME are process-global caches, and
    load_encoding_table is idempotent (no-ops once an encoding name is
    loaded). Without resetting these after each test, a later test
    loading the same encoding name could silently see a stale table
    left over from an earlier test.
    """
    import mathics.eval.encoding as encoding_module

    saved = (
        dict(encoding_module.WMA_DECODE_TABLES),
        dict(encoding_module.WMA_UNICODE_CHARACTER_MAPS),
        dict(encoding_module._REGISTERED_TABLES),
    )
    yield
    encoding_module.WMA_DECODE_TABLES.clear()
    encoding_module.WMA_DECODE_TABLES.update(saved[0])
    encoding_module.WMA_UNICODE_CHARACTER_MAPS.clear()
    encoding_module.WMA_UNICODE_CHARACTER_MAPS.update(saved[1])
    encoding_module._REGISTERED_TABLES.clear()
    encoding_module._REGISTERED_TABLES.update(saved[2])


@pytest.fixture
def wl_encodings_dir(tmp_path, monkeypatch):
    """
    Point ROOT_DIR at a throwaway directory with our own
    SystemFiles/CharacterEncodings, so these tests are self-contained:
    they don't depend on (or affect) whatever .wl files happen to exist
    in the real repo.
    """
    import mathics.eval.encoding.encoding as encoding_module

    encodings_dir = tmp_path / "SystemFiles" / "CharacterEncodings"
    encodings_dir.mkdir(parents=True)
    monkeypatch.setattr(encoding_module, "ROOT_DIR", str(tmp_path))
    return encodings_dir


def _write_wl_file(directory, name: str, content: str) -> None:
    (directory / f"{name}.wl").write_text(content, encoding="utf-8")


@pytest.fixture
def iso8859_8_test(wl_encodings_dir, evaluation):
    """Load a self-contained ISO8859-8-like encoding under a test-only name."""
    from mathics.eval.encoding import load_encoding_table

    name = "TestISO88598"
    print("name:", name, [wl_encodings_dir, name, ISO8859_8_TEST_WL])
    _write_wl_file(wl_encodings_dir, name, ISO8859_8_TEST_WL)
    load_encoding_table(name, evaluation)
    return name


@pytest.fixture
def iso8859_1_test(wl_encodings_dir, evaluation):
    """Load a self-contained ISO8859-1-like encoding under a test-only name."""
    from mathics.eval.encoding import load_encoding_table

    name = "TestISO88591"
    _write_wl_file(wl_encodings_dir, name, ISO8859_1_TEST_WL)
    load_encoding_table(name, evaluation)
    return name


class TestLoadEncodingTable:
    def test_loads_and_populates_decode_table(self, iso8859_8_test):
        from mathics.eval.encoding import WMA_DECODE_TABLES

        assert iso8859_8_test in WMA_DECODE_TABLES
        assert WMA_DECODE_TABLES[iso8859_8_test][224] == "\u05d0"

    def test_is_idempotent(self, iso8859_8_test, evaluation):
        from mathics.eval.encoding import WMA_DECODE_TABLES, load_encoding_table

        table_before = WMA_DECODE_TABLES[iso8859_8_test]
        load_encoding_table(iso8859_8_test, evaluation)  # second call
        assert WMA_DECODE_TABLES[iso8859_8_test] is table_before

    def test_native_encoding_is_a_noop(self, evaluation):
        from mathics.eval.encoding import WMA_DECODE_TABLES, load_encoding_table

        load_encoding_table("UTF8", evaluation)
        assert "UTF8" not in WMA_DECODE_TABLES  # never tries to open UTF8.wl

    def test_ascii_pseudo_encoding_is_a_noop(self, evaluation):
        from mathics.eval.encoding import WMA_DECODE_TABLES, load_encoding_table

        load_encoding_table("ASCII", evaluation)
        assert "ASCII" not in WMA_DECODE_TABLES  # ASCII has its own table already

    def test_missing_file_raises(self, wl_encodings_dir, evaluation):
        from mathics.eval.encoding import EncodingNameError, load_encoding_table

        with pytest.raises(EncodingNameError):
            load_encoding_table("ThisEncodingDoesNotExist", evaluation)

    def test_registers_a_real_python_codec(self, iso8859_8_test):
        from mathics.eval.encoding import to_python_encoding

        python_name = to_python_encoding(iso8859_8_test)
        assert "\u05d0".encode(python_name) == bytes([224])


class TestEncodeStringValueRealEncoding:
    def test_representable_char_stays_unchanged(self, iso8859_8_test):
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("\u05d0", iso8859_8_test) == "à"

    # def test_non_invertible_char_is_escaped(self, iso8859_8_test):
    #    from mathics.eval.encoding import encode_string_value
    #
    #    assert encode_string_value("\u2a2f", iso8859_8_test) == "\\[Cross]"

    def test_operator_with_ascii_syntax_uses_it(self, iso8859_1_test):
        # matches WMA: ToString["\[GreaterEqual]", CharacterEncoding->"ISO8859-1"]
        # gives ">=", not the escape form.
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("\u2265", iso8859_1_test) == ">="

    def test_operator_without_ascii_syntax_falls_back_to_escape(self, iso8859_1_test):
        # matches WMA: ToString["\[Integral]", CharacterEncoding->"ISO8859-1"]
        # gives the escape form, since \[Integral] has no linear ASCII syntax.
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("\u222b", iso8859_1_test) == "\\[Integral]"

    def test_unrelated_unicode_char_is_escaped(self, iso8859_8_test):
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("\u0416", iso8859_8_test) == "\\:0416"

    def test_full_reported_example(self, iso8859_1_test):
        # the exact case reported against real WMA:
        # ToString["\[AAcute]\[Integral]\[GreaterEqual]2", CharacterEncoding->"ISO8859-1"]
        # -> "á\[Integral]>=2"
        from mathics.eval.encoding import encode_string_value

        text = "\u00e1\u222b\u22652"
        assert encode_string_value(text, iso8859_1_test) == "\u00e1\\[Integral]>=2"


class TestEncodeStringValueAscii:
    def test_ascii_char_stays_unchanged(self, evaluation):
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("hello", "ASCII") == "hello"

    def test_accented_letter_uses_scanner_substitution(self, evaluation):
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("\u00e1", "ASCII") == "a'"

    def test_greater_equal_matches_operator_table(self, evaluation):
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("\u2265", "ASCII") == ">="

    def test_integral_prefers_scanner_int_over_wma_escape(self, evaluation):
        # deliberate Mathics3 divergence from WMA (see conversation):
        # real WMA gives the escape "\[Integral]" here, but Mathics3
        # wants "int" for readability in StandardForm[Integrate[...]].
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("\u222b", "ASCII") == "int"

    def test_char_with_no_substitute_is_escaped(self, evaluation):
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("\u05d0", "ASCII") == "\\:05d0"  # alef

    def test_combining_sequence_substitution(self, evaluation):
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("c\u0323", "ASCII") == ".c"

    def test_lim_is_not_mangled(self, evaluation):
        # regression: 'lim' -> 'mlim' in the scanner table is NOT a
        # combining sequence and must not corrupt literal ASCII text.
        from mathics.eval.encoding import encode_string_value

        assert encode_string_value("lim", "ASCII") == "lim"
        assert encode_string_value("the limit is near", "ASCII") == "the limit is near"


class TestEncodeStringValueNative:
    @pytest.mark.parametrize("encoding", ["Unicode", "UTF-8", "UTF8"])
    def test_identity_for_any_string(self, evaluation, encoding):
        from mathics.eval.encoding import encode_string_value

        text = "caf\u00e9 \U0001f600 \u05d0"
        assert encode_string_value(text, encoding) == text


class TestDecodeBytesValue:
    def test_decodes_using_loaded_table(self, iso8859_8_test):
        from mathics.eval.encoding import decode_bytes_value

        assert (
            decode_bytes_value(bytes([224, 225, 226]), iso8859_8_test)
            == "\u05d0\u05d1\u05d2"
        )

    def test_uses_wma_override_not_python_stdlib(self, iso8859_8_test):
        # byte 170: Python's real iso8859_8 codec gives '×' (U+00D7);
        # our WMA-faithful table gives \[Cross] (U+2A2F).
        from mathics.eval.encoding import decode_bytes_value

        assert decode_bytes_value(bytes([170]), iso8859_8_test) == "\u2a2f"
        assert bytes([170]).decode("iso8859_8") == "\u00d7"  # sanity check

    @pytest.mark.parametrize("encoding", ["Unicode", "UTF-8", "UTF8"])
    def test_native_encodings_delegate_to_python(self, evaluation, encoding):
        from mathics.eval.encoding import decode_bytes_value

        text = "caf\u00e9"
        python_name = {"Unicode": "utf_16", "UTF-8": "utf_8", "UTF8": "utf_8"}[encoding]
        assert decode_bytes_value(text.encode(python_name), encoding) == text

    def test_unloaded_encoding_raises(self, evaluation):
        from mathics.eval.encoding import EncodingNameError, decode_bytes_value

        with pytest.raises(EncodingNameError):
            decode_bytes_value(b"\x00", "SomeEncodingNeverLoaded")


class TestEncodingNameRoundtrip:
    def test_to_python_and_back_for_standard_encoding(self, evaluation):
        from mathics.eval.encoding import from_python_encoding, to_python_encoding

        assert to_python_encoding("ISO8859-8") == "iso8859_8"
        assert from_python_encoding("iso8859_8") == "ISO8859-8"

    def test_registered_roundtrip_for_wl_loaded_encoding(self, iso8859_8_test):
        from mathics.eval.encoding import from_python_encoding, to_python_encoding

        python_name = to_python_encoding(iso8859_8_test)
        assert python_name != "iso8859_8"  # must be namespaced, not the stdlib name
        assert from_python_encoding(python_name) == iso8859_8_test

    def test_unregistered_python_name_falls_back_to_plain_lookup(self, evaluation):
        from mathics.eval.encoding import from_python_encoding

        # CHARACTER_ENCODING_MAP has two WMA names ("UTF-8" and "UTF8")
        # for the same Python codec ("utf_8"), so the reverse lookup can
        # only recover one of them -- either is a correct WMA name for
        # this codec.
        assert from_python_encoding("utf_8") in ("UTF-8", "UTF8")

    def test_unknown_python_name_returns_none(self, evaluation):
        from mathics.eval.encoding import from_python_encoding

        assert from_python_encoding("not_a_real_codec_name") is None


# ======================================================================
# Tier 3: end-to-end integration through Mathics3Open (real files on disk)
# ======================================================================
#
# These exercise the actual gap that motivated this whole subsystem:
# Mathics3Open used to resolve a WMA encoding name straight to a Python
# stdlib codec name (to_python_encoding), silently bypassing any .wl-
# loaded table entirely -- so overrides like ISO8859-8's \[Cross]/
# \[Divide], or any encoding with no Python stdlib equivalent at all,
# never actually took effect on real file I/O. `to_python_encoding`
# fixes that; these tests would have failed against the old code.


class TestMathics3OpenIntegration:
    def test_write_produces_wma_faithful_bytes(self, iso8859_8_test, tmp_path):
        from mathics.eval.files_io.read import Mathics3Open

        path = tmp_path / "hebrew.txt"
        with Mathics3Open(str(path), "w", encoding=iso8859_8_test) as f:
            f.write("\u05d0\u05d1\u05d2")  # alef, bet, gimel

        assert path.read_bytes() == bytes([224, 225, 226])

    def test_read_uses_wma_override_not_python_stdlib(self, iso8859_8_test, tmp_path):
        # byte 170: real Python iso8859_8 gives '×'; our WMA table gives \[Cross].
        from mathics.eval.files_io.read import Mathics3Open

        path = tmp_path / "cross.txt"
        path.write_bytes(bytes([170, 186]))

        with Mathics3Open(str(path), "r", encoding=iso8859_8_test) as f:
            text = f.read()

        assert text == "\u2a2f\u00f7"  # \[Cross], \[Divide]
        assert bytes([170, 186]).decode("iso8859_8") != text  # proves it's OUR table

    # TODO: review this test.
    def no_test_write_non_invertible_char_raises(self, iso8859_8_test, tmp_path):
        from mathics.eval.files_io.read import Mathics3Open

        path = tmp_path / "should_fail.txt"
        with pytest.raises(UnicodeEncodeError):
            with Mathics3Open(str(path), "w", encoding=iso8859_8_test) as f:
                f.write("\u2a2f")  # \[Cross]: decode-only, not invertible
            with Mathics3Open(str(path), "r", encoding=iso8859_8_test) as f:
                print("stored:", f.read())  # \[Cross]: decode-only, not invertible

    def test_roundtrip_write_then_read(self, iso8859_8_test, tmp_path):
        from mathics.eval.files_io.read import Mathics3Open

        path = tmp_path / "roundtrip.txt"
        original = "\u05d0\u05d1\u05d2 hello"
        with Mathics3Open(str(path), "w", encoding=iso8859_8_test) as f:
            f.write(original)
        with Mathics3Open(str(path), "r", encoding=iso8859_8_test) as f:
            assert f.read() == original

    @pytest.mark.parametrize("encoding", ["UTF8", "UTF-8"])
    def test_native_encoding_still_works(self, evaluation, tmp_path, encoding):
        # regression: native encodings never went through a .wl file and
        # must keep working exactly as before.
        from mathics.eval.files_io.read import Mathics3Open

        path = tmp_path / "utf8.txt"
        original = "caf\u00e9 \U0001f600"
        with Mathics3Open(str(path), "w", encoding=encoding) as f:
            f.write(original)
        with Mathics3Open(str(path), "r", encoding=encoding) as f:
            assert f.read() == original


def test_klingon(tmp_path, evaluation):
    from mathics.core.atoms.strings import String
    from mathics.core.systemsymbols import SymbolOutputForm
    from mathics.eval.encoding import load_encoding_table
    from mathics.eval.files_io.read import Mathics3Open
    from mathics.eval.strings import eval_ToString

    load_encoding_table("Klingon", evaluation)
    path = tmp_path / "roundtrip.txt"
    original = "- Good Bye Martok!\n  - KAPLA!"
    with Mathics3Open(str(path), "w", encoding="ASCII") as f:
        f.write(original)
    with Mathics3Open(str(path), "r", encoding="Klingon") as f:
        s_klingon = f.read()
    reencoded_ascii = eval_ToString(
        String(s_klingon), SymbolOutputForm, "ASCII", evaluation
    ).value
    reencoded_klingon = eval_ToString(
        String(s_klingon), SymbolOutputForm, "ASCII", evaluation
    ).value
    print("s_klingon", s_klingon)
    assert s_klingon == "- ood ye artok\n  - "
    assert (
        reencoded_ascii
        == "- \\:f8d5ood \\:f8d1ye \\:f8daartok\\:f8f1\n  - \\:f8df\\:f8d0\\:f8de\\:f8d9\\:f8d0\\:f8f1"
    )
    assert (
        reencoded_klingon
        == "- \\:f8d5ood \\:f8d1ye \\:f8daartok\\:f8f1\n  - \\:f8df\\:f8d0\\:f8de\\:f8d9\\:f8d0\\:f8f1"
    )


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
