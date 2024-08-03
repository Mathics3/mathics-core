import pytest
import sympy

from mathics.builtin.makeboxes import int_to_tuple_info, real_to_tuple_info
from mathics.core.atoms import Integer, Integer0, Integer1, IntegerM1, Real

# from packaging.version import Version


@pytest.mark.parametrize(
    ("integer", "expected", "exponent", "is_nonnegative"),
    [
        (Integer0, "0", 0, True),
        (Integer1, "1", 0, True),
        (IntegerM1, "1", 0, False),
        (Integer(999), "999", 2, True),
        (Integer(1000), "1000", 3, True),
        (Integer(-9999), "9999", 3, False),
        (Integer(-10000), "10000", 4, False),
    ],
)
def test_int_to_tuple_info(
    integer: Integer, expected: str, exponent: int, is_nonnegative: bool
):
    assert int_to_tuple_info(integer) == (expected, exponent, is_nonnegative)


@pytest.mark.parametrize(
    ("real", "digits", "expected", "exponent", "is_nonnegative"),
    [
        # Using older uncorrected version of Real()
        # (
        #     (Real(sympy.Float(0.0, 10)), 10, "0", -10, True)
        #     if Version(sympy.__version__) < Version("1.13.0")
        #     else (Real(sympy.Float(0.0, 10)), 10, "0000000000", -1, True)
        # ),
        (Real(sympy.Float(0.0, 10)), 10, "0", -10, True),
        (Real(0), 1, "0", 0, True),
        (Real(0), 2, "0", 0, True),
        (Real(0.1), 2, "1", -1, True),
        (Real(0.12), 2, "12", -1, True),
        (Real(-0.12), 2, "12", -1, False),
        (Real(3.141593), 10, "3141593", 0, True),
    ],
)
def test_real_to_tuple_info(
    real: Real, digits: int, expected: str, exponent: int, is_nonnegative: bool
):
    assert real_to_tuple_info(real, digits) == (expected, exponent, is_nonnegative)
