"""
Functions to format strings in a given encoding.
"""

from typing import Dict

from mathics.core.convert.op import UNICODE_CHARACTER_TO_ASCII


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
    # TODO: implement the load of .m encodings.
    # Format:
    # (*name*)
    # {"7Bit"|"8Bit"|"16Bit",{{target_Integer,src_String}|{target_Integer, src_String, False},...}}
    #
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
