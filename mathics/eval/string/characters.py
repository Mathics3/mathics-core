"""
Evaluation functions for builtins in mathics.builtin.string.
"""

from mathics_scanner.characters import replace_box_unicode_with_ascii

from mathics.core.atoms import String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.list import ListExpression


def eval_Characters(string: str) -> ListExpression:
    "Characters[string_String]"

    return to_mathics_list(
        *(replace_box_unicode_with_ascii(s) for s in string),
        elements_conversion_fn=String,
    )
