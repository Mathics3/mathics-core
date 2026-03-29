"""
Functions to format strings in a given encoding.
"""

from typing import Dict

from mathics_scanner.characters import UNICODE_CHARACTER_TO_ASCII

from mathics.core.convert.op import operator_to_ascii, operator_to_unicode

# Map WMA encoding names to Python encoding names
ENCODING_WMA_TO_PYTHON = {
    "WindowsEastEurope": "cp1250",
    "WindowsCyrillic": "cp1251",
    "WindowsANSI": "cp1252",
    "WindowsGreek": "cp1252",
    "WindowsTurkish": "cp1254",
}


# These characters are used in encoding
# in WMA, and differs from what we have
# in Mathics3-scanner tables:
UNICODE_CHARACTER_TO_ASCII.update(
    {
        operator_to_unicode["Times"]: r" x ",
        "": r"\[DifferentialD]",
    }
)
# Some printable ASCII characters appears in the name
# table. We should remove them:
for raw_char_code in range(32, 127):
    char = chr(raw_char_code)
    if char in UNICODE_CHARACTER_TO_ASCII:
        del UNICODE_CHARACTER_TO_ASCII[char]


class EncodingNameError(Exception):
    pass


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
