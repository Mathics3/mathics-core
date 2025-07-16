"""
evaluation functions for mathics.builtin.binary.io
"""

import struct

from mathics.core.list import ListExpression
from mathics.core.streams import Stream
from mathics.eval.files_io.read import SymbolEndOfFile


def eval_BinaryReadList(
    stream: Stream, readers: dict, kinds: list, return_list: bool, count: int
):
    """
    Evaluation function for BinaryRead[] and BinaryReadList[]

    Read binary data from stream. `kinds` is a list of kinds to read.
    If return_list is True, then the result is a list
    """

    result = []
    while count > 0 or count <= -1:
        count -= 1
        for t in kinds:
            try:
                result.append(readers[t](stream.io))
            except struct.error:
                result.append(SymbolEndOfFile)
        if len(result) > 0 and result[-1] == SymbolEndOfFile:
            break

    if return_list:
        # If we were doing BinaryReadList[], i.e. return_list is True,
        # then strip off the EndOfFile at the end
        if count < 0:
            result = result[:-1]

        return ListExpression(*result)
    elif len(result) == 1:
        return result[0]
    else:
        return ListExpression(*result)
