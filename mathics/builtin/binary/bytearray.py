# -*- coding: utf-8 -*-
"""
ByteArrays
"""

from typing import Optional, Union

from mathics.core.atoms import ByteArrayAtom, Integer, String
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.systemsymbols import SymbolFailed


class ByteArray_(Builtin):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ByteArray.html</url>

    <dl>
      <dt>'ByteArray'[{$b_1$, $b_2$, ...}]
      <dd> Represents a sequence of Bytes $b_1$, $b_2$, ...

      <dt>'ByteArray'["$string$"]
      <dd> Constructs a byte array where bytes comes from decode a b64-encoded \
           String
    </dl>

    >> A=ByteArray[{1, 25, 3}]
     = ByteArray[<3>]
    >> A[[2]]
     = 25
    >> Normal[A]
     = {1, 25, 3}
    >> ToString[A]
     = ByteArray[<3>]
    >> ByteArray["ARkD"]
     = ByteArray[<3>]
    >> B=ByteArray["asy"]
     : The argument in ByteArray[asy] should be a vector of unsigned byte values or a Base64-encoded string.
     = $Failed

    A 'ByteArray" is a kind of Atom:

    >> AtomQ[ByteArray[{4, 2}]]
     = True
    """

    messages = {
        "batd": "Elements in `1` are not unsigned byte values.",
        "lend": (
            "The argument in ByteArray[`1`] should "
            "be a vector of unsigned byte values or a Base64-encoded string."
        ),
    }

    name = "ByteArray"
    summary_text = "array of bytes"

    def eval_str(self, string, evaluation) -> Union[ByteArrayAtom, SymbolFailed]:
        "ByteArray[string_String]"
        try:
            atom = ByteArrayAtom(string.value)
        except TypeError:
            evaluation.message("ByteArray", "lend", string)
            return SymbolFailed
        return atom

    def eval_to_str(self, baa, evaluation: Evaluation):
        "ToString[ByteArray[baa_ByteArrayAtom]]"
        return String(f"ByteArray[<{len(baa.value)}>]")

    def eval_normal(self, baa, evaluation: Evaluation):
        "System`Normal[ByteArray[baa_ByteArrayAtom]]"
        return to_mathics_list(*baa.value, elements_conversion_fn=Integer)

    def eval_list(self, values, evaluation) -> Optional[ByteArrayAtom]:
        "ByteArray[values_List]"
        try:
            ba = ByteArrayAtom(bytearray([b.get_int_value() for b in values.elements]))
        except Exception:
            evaluation.message("ByteArray", "batd", values)
            return None
        return ba


# TODO: BaseEncode, BaseDecode, ByteArrayQ, ByteArrayToString, StringToByteArray, ImportByteArray, ExportByteArray
