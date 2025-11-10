from mathics.core.atoms import Integer, NumericArray, String
from mathics.core.convert.python import from_python
from test.helper import check_evaluation, evaluate

import numpy as np
import pytest

#
# Python API tests
#

def test_numericarray_atom_preserves_array_reference():
    array = np.array([1, 2, 3], dtype=np.int64)
    atom = NumericArray(array)
    assert atom.value is array

def test_numericarray_atom_preserves_equality():
    array = np.array([1, 2, 3], dtype=np.int64)
    atom = NumericArray(array, dtype=np.float64)
    np.testing.assert_array_equal(atom.value, array)


def test_numericarray_expression_from_python_array():
    array = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    atom = from_python(array)
    assert isinstance(atom, NumericArray)
    assert atom.value is array

def test_numericarray_hash():
    a = [[1, 2], [3, 4]]
    array1a = np.array(a, dtype=np.float32)
    atom1a = from_python(array1a)
    array1b = np.array(a, dtype=np.float32)
    atom1b = from_python(array1a)
    array2 = np.array(a, dtype=np.float64)
    atom2 = from_python(array2)
    assert hash(atom1a) == hash(atom1b), "hashes of different arrays with same value should be same"
    assert hash(atom1a) != hash(atom2), "hashes of arrays with different values should be different"


#
# WL tests
#

@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # TODO: remove this - was temp to see if Normal still worked on ByteArray after changes
        #("Normal[ByteArray[{1,2}]]", "{1, 2}"),
        ("NumericArray[{{1,2},{3,4}}]", "<Integer64, 2×2>"),
        ("ToString[NumericArray[{{1,2},{3,4}}]]", "<Integer64, 2×2>"),
        ("Head[NumericArray[{1,2}]]", "NumericArray"),
        ("AtomQ[NumericArray[{1,2}]]", "True"),
        ("First[NumericArray[{1,2,3}]]", "1"),
        ("First[NumericArray[{{1,2}, {3,4}}]]", "<Integer64, 2>"),
        # TODO: these do not work yet
        # change was applied to First to make that work,
        # but did not want to change Last because it is awaiting DRYing
        #("Last[NumericArray[{1,2,3}]]", "3"),
        #("Last[NumericArray[{{1,2}, {3,4}}]]", "<Integer64, 2>"),
        ("Normal[NumericArray[{{1,2}, {3,4}}]]", "{{1, 2}, {3, 4}}"),
    ]
)
def test_basics(str_expr, str_expected):
    check_evaluation(str_expr, str_expected, hold_expected=True)

def test_type_conversion():
    expr = evaluate("NumericArray[{1,2}]")
    assert isinstance(expr, NumericArray)
    assert expr.value.dtype == np.int64
    expr = evaluate('NumericArray[{1,2}, "ComplexReal32"]')
    assert expr.value.dtype == np.complex64


