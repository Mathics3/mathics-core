from mpmath import mpc, mpf
from sympy import Float as SympyFloat

from mathics.core.atoms import (
    Complex,
    Integer0,
    Integer1,
    IntegerM1,
    MachineReal,
    PrecisionReal,
    Rational,
    Real,
)
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolDirectedInfinity, SymbolIndeterminate


def test_infinity():
    vals = [
        (mpf("+inf"), Expression(SymbolDirectedInfinity, Integer1)),
        (mpf("-inf"), Expression(SymbolDirectedInfinity, IntegerM1)),
        (
            mpc(1.0, "inf"),
            Expression(SymbolDirectedInfinity, Complex(Integer0, Integer1)),
        ),
        (
            mpc(1.0, "-inf"),
            Expression(SymbolDirectedInfinity, Complex(Integer0, IntegerM1)),
        ),
        (mpc("inf", 1), Expression(SymbolDirectedInfinity, Integer1)),
        (mpc("-inf", 1), Expression(SymbolDirectedInfinity, IntegerM1)),
        (mpf("nan"), SymbolIndeterminate),
    ]
    for val_in, val_out in vals:
        print([val_in, val_out, from_mpmath(val_in)])
        assert val_out.sameQ(from_mpmath(val_in))


def test_from_to_mpmath():
    vals = [
        (Integer1, MachineReal(1.0)),
        (Rational(1, 3), MachineReal(1.0 / 3.0)),
        (MachineReal(1.2), MachineReal(1.2)),
        (PrecisionReal(SympyFloat(1.3, 10)), PrecisionReal(SympyFloat(1.3, 10))),
        (PrecisionReal(SympyFloat(1.3, 30)), PrecisionReal(SympyFloat(1.3, 30))),
        (Complex(Integer1, IntegerM1), Complex(Integer1, IntegerM1)),
        (Complex(Integer1, Real(-1.0)), Complex(Integer1, Real(-1.0))),
        (Complex(Real(1.0), Real(-1.0)), Complex(Real(1.0), Real(-1.0))),
        (
            Complex(MachineReal(1.0), PrecisionReal(SympyFloat(-1.0, 10))),
            Complex(MachineReal(1.0), PrecisionReal(SympyFloat(-1.0, 10))),
        ),
        (
            Complex(MachineReal(1.0), PrecisionReal(SympyFloat(-1.0, 30))),
            Complex(MachineReal(1.0), PrecisionReal(SympyFloat(-1.0, 30))),
        ),
    ]
    for val1, val2 in vals:
        print((val1, val2))
        assert val2.sameQ(from_mpmath(val1.to_mpmath()))
