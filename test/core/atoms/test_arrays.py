# -*- coding: utf-8 -*-


import numpy as np

from mathics.core.atoms import NumericArray
from mathics.core.convert.python import from_python
from mathics.core.definitions import Definitions
from mathics.core.load_builtin import import_and_load_builtins

import_and_load_builtins()

definitions = Definitions(add_builtin=True)

#
# NumericArray tests
#


def test_numericarray_atom_preserves_array_reference():
    array = np.array([1, 2, 3], dtype=np.int64)
    atom = NumericArray(array)
    assert atom.value is array, "NumericArray.value should be a NumPy array"


def test_numericarray_atom_preserves_equality():
    array = np.array([1, 2, 3], dtype=np.int64)
    atom = NumericArray(array, dtype=np.float64)
    np.testing.assert_array_equal(atom.value, array)


def test_numericarray_expression_from_python_array():
    array = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    atom = from_python(array)
    assert isinstance(
        atom, NumericArray
    ), "from_python() conversion of a NumPy Array should yield a NumericArray"
    assert atom.value is array
