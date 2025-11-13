import pytest

from mathics.core.atoms import Complex, Integer0, Integer1, Real, String


# Tests
@pytest.mark.parametrize(
    ("atom1", "atom2", "assert_msg"),
    [
        (
            Complex(Integer0, Integer1),
            Integer1,
            "Complex numbers come before Integers when numerically incompable",
        ),
        (
            Complex(Integer0, Integer1),
            Real(1.0),
            "Complex numbers come before Real Numbers when numerically incomparable",
        ),
        # FIXME: Fixing this breaks ColorNegate since RGBColor[1, 0, 0] != RGBColor[1.0, 0, 0]
        # (Integer1, Real(1.0), "Integers come before Real Numbers when equal value"),
        (Integer1, String("abc"), "Integers come before Real Numbers when equal value"),
    ],
)
def test_element_ordering_lt(atom1, atom2, assert_msg: str):
    assert atom1 < atom2, assert_msg
