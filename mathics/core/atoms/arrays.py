"""
Mathics3 Array collections - ByteArray and NumericArray
"""
# Note: Python warns of ambiguity if we name this file this array.py
import base64
from typing import Optional, Tuple, Union

import numpy

from mathics.core.atoms.numerics import Integer
from mathics.core.atoms.strings import String
from mathics.core.element import ImmutableValueMixin
from mathics.core.keycomparable import (
    BASIC_ATOM_BYTEARRAY_ELT_ORDER,
    BASIC_ATOM_NUMERICARRAY_ELT_ORDER,
)
from mathics.core.symbols import Atom


class ByteArray(Atom, ImmutableValueMixin):
    _value: Union[bytes, bytearray]

    # Items is analogous to "elements" in Lists.
    # However the name is different because there is a concern
    # having these be distinct names may catch mistakes in coding
    # where an expanded or Normal[]'d value is used when it should
    # not be used.
    _items: Optional[tuple] = None

    class_head_name = "System`ByteArray"
    hash: int

    # We use __new__ here to ensure that two ByteArray's that have the same value
    # return the same object, and to set an object hash value.
    # Consider also @lru_cache, and mechanisms for limiting and
    # clearing the cache and the object store which might be useful in implementing
    # Builtin Share[].
    def __new__(cls, value):
        self = super().__new__(cls)
        if isinstance(value, (bytes, bytearray)):
            self._value = value
        elif isinstance(value, list):
            self._value = bytearray(value)
        elif isinstance(value, str):
            try:
                self._value = base64.b64decode(value)
            except Exception as e:
                raise TypeError(f"base64 string decode failed: {e}")
        else:
            raise TypeError("value does not belongs to a valid type")

        self.hash = hash(("ByteArray", str(self.value)))
        return self

    def __getitem__(self, index: int) -> int:
        """
        Support List index lookup without having to expand the entire bytearray into a Mathics3 list.
        """
        return self.value[index]

    def __getnewargs__(self) -> tuple:
        return (self.value,)

    def __hash__(self) -> int:
        return self.hash

    def __str__(self) -> str:
        return base64.b64encode(self.value).decode("utf8")

    # FIXME: the below does not use the "f" parameter to
    # change behavior between FullForm and OutputForm
    # Below we have the OutputForm behavior.
    # A refactoring should be done so that this routine
    # is removed and the form makes decisions, rather than
    # have this routine know everything about all forms.
    def atom_to_boxes(self, f, evaluation) -> "String":
        return String(f"ByteArray[<{len(self.value)}>]")

    def do_copy(self) -> "ByteArray":
        return ByteArray(self.value)

    def default_format(self, evaluation, form) -> str:
        value = self.value
        return '"' + value.__str__() + '"'

    @property
    def items(self) -> Tuple[Integer, ...]:
        """
        Return a tuple value of Mathics3 Integers for each element of the ByteArray.
        """
        if self._items is None:
            self._items = tuple([Integer(i) for i in self.value])
        return self._items

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return (
            BASIC_ATOM_BYTEARRAY_ELT_ORDER,
            self.value,
            "utf-8",
            0,
            1,
        )

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return super().pattern_precedence

    @property
    def is_literal(self) -> bool:
        """For a ByteArray, the value can't change and has a Python representation,
        i.e. a value is set and it does not depend on definition
        bindings. So we say it is a literal.
        """
        return True

    def sameQ(self, rhs) -> bool:
        """Mathics3 SameQ"""
        # FIX: check
        if isinstance(rhs, ByteArray):
            return self._value == rhs._value
        return False

    def get_string_value(self) -> Optional[str]:
        try:
            return self.value.decode("utf-8")
        except Exception:
            return None

    def to_sympy(self, **kwargs):
        return None

    def to_python(self, *args, **kwargs) -> Union[bytes, bytearray]:
        return self.value

    def user_hash(self, update):
        """
        returned untampered hash value.

        hashing a String is the one case where the user gets the untampered
        # hash value of the string's text. this corresponds to MMA behavior.
        """
        update(self.value)

    @property
    def value(self) -> Union[bytes, bytearray]:
        return self._value


#
# NumericArray
#

NUMERIC_ARRAY_TYPE_MAP = {
    "UnsignedInteger8": numpy.dtype("uint8"),
    "UnsignedInteger16": numpy.dtype("uint16"),
    "UnsignedInteger32": numpy.dtype("uint32"),
    "UnsignedInteger64": numpy.dtype("uint64"),
    "Integer8": numpy.dtype("int8"),
    "Integer16": numpy.dtype("int16"),
    "Integer32": numpy.dtype("int32"),
    "Integer64": numpy.dtype("int64"),
    "Real32": numpy.dtype("float32"),
    "Real64": numpy.dtype("float64"),
    "ComplexReal32": numpy.dtype("complex64"),
    "ComplexReal64": numpy.dtype("complex128"),
}

NUMERIC_ARRAY_DTYPE_TO_NAME = {
    dtype: name for name, dtype in NUMERIC_ARRAY_TYPE_MAP.items()
}


class NumericArray(Atom, ImmutableValueMixin):
    """
    NumericArray provides compact storage and efficient access for machine-precision numeric arrays,
    backed by NumPy arrays.
    """

    class_head_name = "NumericArray"

    def __init__(self, value, dtype=None):
        # compute value
        if not isinstance(value, numpy.ndarray):
            value = numpy.asarray(value, dtype=dtype)
        elif dtype is not None:
            value = value.astype(dtype)
        self.value = value

        # check type
        self._type_name = NUMERIC_ARRAY_DTYPE_TO_NAME.get(self.value.dtype, None)
        if not self._type_name:
            allowed = ", ".join(str(dtype) for dtype in NUMERIC_ARRAY_TYPE_MAP.values())
            message = f"Argument 'value' must be one of {allowed}; is {str(self.value.dtype)}."
            raise ValueError(message)

        # summary and hash
        shape_string = "×".join(str(dim) for dim in self.value.shape) or "0"
        self._summary_string = f"{self._type_name}, {shape_string}"
        self._hash = None

    def __hash__(self):
        if not self._hash:
            self._hash = hash(("NumericArray", self.value.shape, id(self.value)))
        return self._hash

    def __str__(self) -> str:
        return f"NumericArray[{self._summary_string}]"

    def atom_to_boxes(self, f, evaluation):
        return String(f"<{self._summary_string}>")

    def do_copy(self) -> "NumericArray":
        return NumericArray(self.value.copy())

    def default_format(self, evaluation, form) -> str:
        return f"NumericArray[<{self._summary_string}>]"

    @property
    def items(self) -> tuple:
        from mathics.core.convert.python import from_python

        if len(self.value.shape) == 1:
            return tuple(from_python(item.item()) for item in self.value)
        else:
            return tuple(NumericArray(array) for array in self.value)

    @property
    def element_order(self) -> tuple:
        return (
            BASIC_ATOM_NUMERICARRAY_ELT_ORDER,
            self.value.shape,
            self.value.dtype,
            id(self.value),
        )

    @property
    def pattern_precedence(self) -> tuple:
        return super().pattern_precedence

    def sameQ(self, rhs) -> bool:
        return isinstance(rhs, NumericArray) and numpy.array_equal(
            self.value, rhs.value
        )

    def to_sympy(self, **kwargs) -> None:
        return None

    # TODO: this returns a list instead of np.ndarray in keeping with
    # idea that to_python should return only "native" Python types.
    # Keep an eye on this because there is a slight risk that code may
    # naively call to_python and cause a performance issue due to
    # the cost of converting to a nested list structure for a large array.
    def to_python(self, *args, **kwargs) -> list:
        return self.value.tolist()

    def user_hash(self, update) -> None:
        update(self.value.tobytes())
