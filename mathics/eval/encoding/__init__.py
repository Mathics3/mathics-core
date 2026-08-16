"""
Character Encodings

This package contains the high-level and low-level functions used to work with different character encodings,
and contains two sub-modules:

* encoding: high-level interface to list, load and use Python-native and WL-custom character encodings.
* wl_charmap_codec: low-level interface to build and register Python codecs from information gathered
  from WL custom character encoding files, under SystemData/CharacterEncoding/*.wl

"""

from .encoding import (
    CHARACTER_ENCODING_MAP,
    ROOT_DIR,
    WMA_DECODE_TABLES,
    WMA_UNICODE_CHARACTER_MAPS,
    EncodingNameError,
    available_character_encodings,
    decode_bytes_value,
    encode_string_value,
    from_python_encoding,
    get_encoding_table,
    load_encoding_table,
    to_python_encoding,
)
from .wl_charmap_codec import _REGISTERED_TABLES, register_escape_error_handler

__all__ = [
    "CHARACTER_ENCODING_MAP",
    "EncodingNameError",
    "ROOT_DIR",
    "WMA_DECODE_TABLES",
    "WMA_UNICODE_CHARACTER_MAPS",
    "_REGISTERED_TABLES",
    "available_character_encodings",
    "decode_bytes_value",
    "encode_string_value",
    "from_python_encoding",
    "get_encoding_table",
    "load_encoding_table",
    "register_escape_error_handler",
    "to_python_encoding",
    "to_python_encoding",
]
