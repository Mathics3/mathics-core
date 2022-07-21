# -*- coding: utf-8 -*-
"""
Byte Arrays
"""

from mathics.builtin.base import Builtin
from mathics.core.atoms import (
    ByteArrayAtom,
    Integer,
    String,
)
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.systemsymbols import (
    SymbolByteArray,
    SymbolFailed,
)


class ByteArray(Builtin):
    r"""
    <dl>
      <dt>'ByteArray[{$b_1$, $b_2$, ...}]'
     <dd> Represents a sequence of Bytes $b_1$, $b_2$, ...

      <dt>'ByteArray["string"]'
     <dd> Constructs a byte array where bytes comes from decode a b64 encoded String
    </dl>

    >> A=ByteArray[{1, 25, 3}]
     = ByteArray["ARkD"]
    >> A[[2]]
     = 25
    >> Normal[A]
     = {1, 25, 3}
    >> ToString[A]
     = ByteArray["ARkD"]
    >> ByteArray["ARkD"]
     = ByteArray["ARkD"]
    >> B=ByteArray["asy"]
     : The first argument in Bytearray[asy] should be a B64 enconded string or a vector of integers.
     = $Failed
    """

    messages = {
        "aotd": "Elements in `1` are inconsistent with type Byte",
        "lend": "The first argument in Bytearray[`1`] should "
        + "be a B64 enconded string or a vector of integers.",
    }
    summary_text = "array of bytes"

    def apply_str(self, string, evaluation):
        "ByteArray[string_String]"
        try:
            atom = ByteArrayAtom(string.value)
        except Exception:
            evaluation.message("ByteArray", "lend", string)
            return SymbolFailed
        return Expression(SymbolByteArray, atom)

    def apply_to_str(self, baa, evaluation):
        "ToString[ByteArray[baa_ByteArrayAtom]]"
        return String('ByteArray["' + baa.__str__() + '"]')

    def apply_normal(self, baa, evaluation):
        "System`Normal[ByteArray[baa_ByteArrayAtom]]"
        return to_mathics_list(*baa.value, elements_conversion_fn=Integer)

    def apply_list(self, values, evaluation):
        "ByteArray[values_List]"
        if not values.has_form("List", None):
            return
        try:
            ba = bytearray([b.get_int_value() for b in values.elements])
        except Exception:
            evaluation.message("ByteArray", "aotd", values)
            return
        return Expression(SymbolByteArray, ByteArrayAtom(ba))


# TODO: BaseEncode, BaseDecode, ByteArrayQ, ByteArrayToString, StringToByteArray, ImportByteArray, ExportByteArray
