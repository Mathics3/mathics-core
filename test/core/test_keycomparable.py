import pytest
from sympy import Float

from mathics.core.atoms import (
    Complex,
    Integer0,
    Integer1,
    PrecisionReal,
    Rational,
    Real,
    String,
)

print("creating representations")
ZERO_REPRESENTATIONS = {
    "Integer": Integer0,
    "MachineReal": Real(0.0),
    "PrecisionReal`2": PrecisionReal(Float(0, 2)),
    "PrecisionReal`5": PrecisionReal(Float(0, 5)),
    "PrecisionReal`10": PrecisionReal(Float(0, 10)),
    "PrecisionReal`20": PrecisionReal(Float(0, 20)),
    "PrecisionReal`22": PrecisionReal(Float(0, 22)),
    "PrecisionReal`40": PrecisionReal(Float(0, 40)),
}
ZERO_REPRESENTATIONS["Complex"] = Complex(
    ZERO_REPRESENTATIONS["MachineReal"], ZERO_REPRESENTATIONS["MachineReal"]
)
ZERO_REPRESENTATIONS["Complex`20"] = Complex(
    ZERO_REPRESENTATIONS["PrecisionReal`20"], ZERO_REPRESENTATIONS["PrecisionReal`20"]
)

ONE_REPRESENTATIONS = {
    "Integer": Integer1,
    "MachineReal": Real(1.0),
    "PrecisionReal`2": PrecisionReal(Float(1, 2)),
    "PrecisionReal`5": PrecisionReal(Float(1, 5)),
    "PrecisionReal`10": PrecisionReal(Float(1, 10)),
    "PrecisionReal`20": PrecisionReal(Float(1, 20)),
    "PrecisionReal`22": PrecisionReal(Float(1, 22)),
}


# Add some complex cases
ONE_REPRESENTATIONS["Complex Integer"] = Complex(
    Integer1, ZERO_REPRESENTATIONS["PrecisionReal`10"]
)
ONE_REPRESENTATIONS["Complex"] = Complex(
    ONE_REPRESENTATIONS["MachineReal"], ZERO_REPRESENTATIONS["MachineReal"]
)
ONE_REPRESENTATIONS["Complex`5"] = Complex(
    ONE_REPRESENTATIONS["PrecisionReal`5"], ZERO_REPRESENTATIONS["PrecisionReal`5"]
)


ONE_FIFTH_REPRESENTATIONS = {
    "Rational": Rational(1, 5),
    "MachineReal": Real(0.2),
    "PrecisionReal`20": PrecisionReal(Float(".2", 20)),
    "PrecisionReal`22": PrecisionReal(Float(".2", 22)),
}
ONE_FIFTH_REPRESENTATIONS["Complex"] = Complex(
    ONE_FIFTH_REPRESENTATIONS["MachineReal"], ZERO_REPRESENTATIONS["MachineReal"]
)
ONE_FIFTH_REPRESENTATIONS["Complex`20"] = Complex(
    ONE_FIFTH_REPRESENTATIONS["PrecisionReal`20"],
    ZERO_REPRESENTATIONS["PrecisionReal`20"],
)


def test_sorting_numbers():
    """
    In WMA, canonical order for numbers with the same value in different representations:
    * Integer
    * Complex[Integer, PrecisionReal]
    * MachineReal
    * Complex[MachineReal, MachineReal]
    * PrecisionReal, Complex[PrecisionReal, PrecisionReal] if precision of the real parts are equal,
    * otherwise, sort by precision of the real part.
    * Rational
    Example: {1, 1 + 0``10.*I, 1., 1. + 0.*I, 1.`4., 1.`4. + 0``4.*I, 1.`4. + 0``3.*I, 1.`6.}
    and
             {0.2, 0.2 + 0.*I, 0.2`4., 0.2`10., 1/5}
    are lists in canonical order.

    If the numbers are in different representations, numbers are sorted by their real parts,
    and then the imaginary part is considered:
    {0.2, 0.2 - 1.*I, 0.2 + 1.*I, 1/5}
    """
    zero_canonical_order = (
        "Integer",
        "MachineReal",
        "Complex",
        "PrecisionReal`20",
        "Complex`20",
        "PrecisionReal`22",
    )
    one_canonical_order = (
        "Integer",
        "MachineReal",
        "Complex",
        "Complex Integer",
        "PrecisionReal`2",
        "PrecisionReal`5",
        "Complex`5",
        "PrecisionReal`20",
    )
    one_fifth_canonical_order = (
        "MachineReal",
        "Complex",
        "PrecisionReal`20",
        "Complex`20",
        "PrecisionReal`22",
        "Rational",
    )

    # Canonical order
    for order_equiv_forms in [
        [ZERO_REPRESENTATIONS[pos] for pos in zero_canonical_order],
        [ONE_REPRESENTATIONS[pos] for pos in one_canonical_order],
        [ONE_FIFTH_REPRESENTATIONS[pos] for pos in one_fifth_canonical_order],
    ]:
        for elem, nelem in zip(order_equiv_forms[:-1], order_equiv_forms[1:]):
            e_order, ne_order = elem.element_order, nelem.element_order
            print("-------")
            print(type(elem), f"{elem}", e_order)
            print("vs", type(nelem), f"{nelem}", ne_order)
            assert e_order < ne_order and not (
                ne_order <= e_order
            ), "wrong order or undefined."
            assert (
                elem == nelem
            ), f"elements are not equal {elem} ({type(elem)}[{e_order}]) != {nelem}({type(nelem)}[{ne_order}])"
            assert (
                nelem == elem
            ), f"elements are not equal {elem} ({type(elem)}[{e_order}]) != {nelem}({type(nelem)}[{ne_order}])"


def test_sorting_complex():
    one_fifth_rational = ONE_FIFTH_REPRESENTATIONS["Rational"]
    one_fifth_mr = ONE_FIFTH_REPRESENTATIONS["MachineReal"]
    one_fifth_pr = ONE_FIFTH_REPRESENTATIONS["PrecisionReal`20"]
    one_fifth_cplx_i = Complex(one_fifth_mr, ONE_REPRESENTATIONS["MachineReal"])
    one_fifth_cplx_mi = Complex(one_fifth_mr, -ONE_REPRESENTATIONS["MachineReal"])
    canonical_sorted = [
        one_fifth_mr,
        one_fifth_cplx_mi,
        one_fifth_cplx_i,
        one_fifth_pr,
        one_fifth_rational,
    ]
    for elem, nelem in zip(canonical_sorted[:-1], canonical_sorted[1:]):
        e_order, ne_order = elem.element_order, nelem.element_order
        print("-------")
        print(type(elem), f"{elem}", e_order)
        print("vs", type(nelem), f"{nelem}", ne_order)
        assert e_order < ne_order and not (
            ne_order <= e_order
        ), f"{e_order}, {ne_order}"


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
