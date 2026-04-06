"""
Functions to format strings in a given encoding.
"""

from typing import Dict, Final, Optional

from mathics_scanner.characters import UNICODE_CHARACTER_TO_ASCII

from mathics.core.convert.op import operator_to_unicode

CHARACTER_ENCODING_MAP: Final[Dict[str, str]] = {
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


def to_python_encoding(encoding) -> Optional[str]:
    return CHARACTER_ENCODING_MAP.get(encoding)


# Map WMA encoding names to Python encoding names

CHARACTER_ENCODING_MAP = {
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

REVERSE_CHARACTER_ENCODING_MAP = {py: wl for wl, py in CHARACTER_ENCODING_MAP.items()}


# These characters are used in encoding
# in WMA, and differs from what we have
# in Mathics3-scanner tables:
UNICODE_CHARACTER_TO_ASCII.update(
    {
        operator_to_unicode["Times"]: r" x ",
    }
)


class EncodingNameError(Exception):
    pass


def to_python_encoding(encoding):
    return CHARACTER_ENCODING_MAP.get(encoding)


def from_python_encoding(encoding):
    return REVERSE_CHARACTER_ENCODING_MAP.get(encoding)


def get_encoding_table(encoding: str) -> Dict[str, str]:
    """
    Return a dictionary with a map from
    character codes in the internal (Unicode)
    representation to the request encoding.
    """
    if encoding == "Unicode":
        return {}

    # In the final implementation, this should load the corresponding
    # json table or an encoding file as  in WMA
    # SystemFiles/CharacterEncodings/*.m
    # If the encoding is not available, raise an EncodingError
    try:
        return {
            "ASCII": UNICODE_CHARACTER_TO_ASCII,
            "UTF-8": {},
        }[encoding]
    except KeyError:
        raise EncodingNameError


def encode_string_value(value: str, encoding: str) -> str:
    """Convert an Unicode string `value` to the required `encoding`"""

    # In WMA, encodings are readed from SystemFiles/CharacterEncodings/*.m
    # on the fly. We should load them from Mathics3-Scanner tables.
    encoding_table = get_encoding_table(encoding)
    if not encoding_table:
        return value
    result = ""
    for ch in value:
        ch = encoding_table.get(ch, ch)
        result += ch
    return result
