import re
from typing import Iterable

from mathics.core.list import ListExpression
from mathics.core.symbols import BooleanType, SymbolFalse, SymbolTrue


def eval_StringMatchQ(re_pattern_str: str, string: str, flags) -> BooleanType:
    return (
        SymbolFalse if re.match(re_pattern_str, string, flags) is None else SymbolTrue
    )


def eval_list_StringMatchQ(
    re_pattern_str: str, strings: Iterable[str], flags
) -> BooleanType:
    """StringMatchQ when a list of strings has been given.

    The motivation for checking for literalness and for using a
    special eval_list_StringMatchQ as oppsed to iterated calls to
    eval_StringMatchQ was discovered in looking at Mathics3 code for
    doing a dictionary lookup. Here, there are lots of string items in
    list. Unwrapping each is slow, especially when this has already
    been done because the list is a list of literals.

    """
    # https://github.com/python/cpython/issues/89625 suggests compiling patterns is a win
    # even at 2. But we'll be pessimistic here.
    if len(strings) > 5:
        re_pattern = re.compile(re_pattern_str, flags)
        return ListExpression(
            *(
                SymbolTrue if re.match(re_pattern, string) else SymbolFalse
                for string in strings
            )
        )

    return ListExpression(
        *(
            SymbolTrue if re.match(re_pattern_str, string, flags) else SymbolFalse
            for string in strings
        )
    )
