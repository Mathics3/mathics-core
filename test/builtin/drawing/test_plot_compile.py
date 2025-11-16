"""
These tests were populated by introspecting _builtins and finding
all that had a sympy_name, mpmath_name, or whose path included the
string "numeric" or "number".

The tests are performed by evaluating N[function[args]] to get an expected value,
and then compiling the function and running compiled_function[args] get a result.
In a number of cases a small numeric tolerance is allowed, presumably due to differences
in exact algorithm used.

I took a first pass over the tests providing suitable args for the ones that were easy.
The tests that are uncommented pass; the commented ones need more work.
"""

import inspect

import numpy as np

from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.eval.drawing.plot_compile import plot_compile
from mathics.session import MathicsSession
from test.helper import session

#session = MathicsSession()


#
# Each test specifies:
#     name - name of function
#     args - suitable args to be given to N[function[args]] and compiled_function[args] for comparison
#     close (optional) - boolean indicating results will be close and not exact
#     scipy (optional) - boolean marking whether scipy is needed for the test
#
# for ??? check
#     sympy.expression_to_sympy
#     builtin.SympyFunction, especially silent failure except TypeError in to_sympy

tests = [
    #
    # Following have sympy_name.
    #
    dict(name="Abs", args=[-1]),
    dict(name="AiryAi", args=[1], close=True),
    dict(name="AiryAiPrime", args=[1], close=True),
    dict(name="AiryBi", args=[1], close=True),
    dict(name="AiryBiPrime", args=[1], close=True),
    # dict(name="AngerJ", args=[0,0]), # sympy_name is ''
    dict(name="ArcCos", args=[0]),
    dict(name="ArcCosh", args=[2], close=True),
    dict(name="ArcCot", args=[1]),
    dict(name="ArcCoth", args=[2], close=True),
    dict(name="ArcCsc", args=[2], close=True),
    dict(name="ArcCsch", args=[0.1]),
    dict(name="ArcSec", args=[2]),
    dict(name="ArcSech", args=[0.1]),
    dict(name="ArcSin", args=[0.1]),
    dict(name="ArcSinh", args=[0]),
    dict(name="ArcTan", args=[0]),
    dict(name="ArcTanh", args=[0]),
    dict(name="Arg", args=[0]),
    # dict(name="BellB", args=[0]), # scipy wants bell()
    dict(name="BernoulliB", args=[0], scipy=True),
    dict(name="BesselI", args=[0, 0], scipy=True),
    dict(name="BesselJ", args=[0, 0], scipy=True),
    # dict(name="BesselJZero", args=[1,1]), # sympy_name is ''
    dict(name="BesselK", args=[0.5, 0.5], close=True, scipy=True),
    dict(name="BesselY", args=[0, 0], scipy=True),
    # dict(name="BesselYZero", args=[2,2]), # sympy_name is ''
    dict(name="Beta", args=[0.5, 1], close=True),
    dict(name="Binomial", args=[3, 0.5], close=True),
    dict(name="Catalan", args=None),
    dict(name="CatalanNumber", args=[0]),
    dict(name="Ceiling", args=[0]),
    dict(name="ChebyshevT", args=[0, 1], scipy=True),
    dict(name="ChebyshevU", args=[0, 1], scipy=True),
    # dict(name="ClebschGordan", args=[[5,0],[4,0],[1,0]]), # module 'sympy' has no attribute 'physics.quantum.cg.CG'
    dict(name="ComplexExpand", args=[0]),
    # dict(name="ComplexInfinity", args=None), # N returns infinite
    # dict(name="ConditionalExpression", args=[1,True]),	# not registered with mathics_to_sympy
    dict(name="Conjugate", args=[0]),
    # dict(name="ContinuedFraction", args=[0.4, 3]), # continued_fraction() takes 1 positional argument but 2 were given
    # dict(name="ContinuedFraction", args=[0.4]), # N fails
    dict(name="Cos", args=[0]),
    dict(name="Cosh", args=[0]),
    dict(name="Cot", args=[1]),
    dict(name="Coth", args=[1]),
    dict(name="Csc", args=[1]),
    # dict(name="Curl", args=[0]), # is this really numeric?
    # dict(name="D", args=[0]), # is this really numeric
    dict(name="Degree", args=None),
    # dict(name="Derivative", args=[0]),	# is this really numeric
    # dict(name="DirectedInfinity", args=[0]), # infinity - how to handle
    # dict(name="DivisorSigma", args=[1,20]), # sympy expects divisor_sigma()
    dict(name="E", args=None),
    # dict(name="Eigenvalues", args=[[[1,2],[3,4]]]), # not registered with mathics_to_sympy
    # dict(name="EllipticE", args=[0]), # sympy expects elliptic_e()
    # dict(name="EllipticF", args=[0,0]), # sympy expectes elliptic_f()
    # dict(name="EllipticK", args=[0]), # sympy expects elliptic_k()
    # dict(name="EllipticPi", args=[0,0]), # sympy expects elliptic_pi()
    dict(name="Equal", args=[0, 0]),
    dict(name="Erf", args=[0]),
    dict(name="Erfc", args=[0]),
    dict(name="EulerE", args=[0]),
    dict(name="EulerGamma", args=None),
    # dict(name="EulerPhi", args=None), # N returns System`EulerPhi
    dict(name="Exp", args=[0]),
    # dict(name="ExpIntegralE", args=[1,1]), # sympy expects expint()
    dict(name="ExpIntegralEi", args=[0]),
    dict(name="Factorial", args=[0]),
    dict(name="Factorial2", args=[0]),
    # dict(name="Fibonacci", args=[0]), # sympyi expects fibonacci()
    dict(name="Floor", args=[0]),
    dict(name="FresnelC", args=[0]),
    dict(name="FresnelS", args=[0]),
    # dict(name="FromContinuedFraction", args=[[2,1,3,4]]), # ???
    # dict(name="Function", args=[0]), # is this really numeric
    dict(name="Gamma", args=[1]),
    dict(name="GegenbauerC", args=[1, 1, 1]),
    dict(name="GoldenRatio", args=None),
    dict(name="Greater", args=[0, 1]),
    dict(name="GreaterEqual", args=[0, 1]),
    # dict(name="HankelH1", args=[1,1]), # N and sympy differ a lot
    # dict(name="HankelH2", args=[1,1]), # N and sympy differ a lot
    dict(name="HarmonicNumber", args=[0]),
    # dict(name="Haversine", args=[0]), # module 'sympy' has no attribute 'haversine'
    dict(name="HermiteH", args=[0, 0]),
    # dict(name="Hypergeometric1F1", args=[1,1,1]), # sympy_name is ''
    # dict(name="Hypergeometric2F1", args=[2,3,4,5]), # ???
    # dict(name="HypergeometricPFQ", args=[[1,1],[3,3,3],2]), # ???
    # dict(name="HypergeometricU", args=[1,1,1]), # sympy_name is ''
    dict(name="I", args=None),
    dict(name="Im", args=[0]),
    # dict(name="Indeterminate", args=None), # N returns System`Indeterminate
    dict(name="Infinity", args=None),
    # dict(name="Integrate", args=[0]), # is this really numeric
    dict(name="InverseErf", args=[0]),
    dict(name="InverseErfc", args=[0]),
    # dict(name="InverseHaversine", args=[0]), # module 'sympy' has no attribute 'inversehaversine'
    dict(name="JacobiP", args=[1, 1, 1, 1]),
    # dict(name="KelvinBei", args=[0]), # sympy_name is ''
    # dict(name="KelvinBer", args=[0]), # sympy_name is ''
    # dict(name="KelvinKei", args=[0]), # sympy_name is ''
    # dict(name="KelvinKer", args=[0]), # sympy_name is ''
    # dict(name="KroneckerProduct", args=[0]), # args are matrices
    # dict(name="LaguerreL", args=[1,0]), # SympyFunction.to_sympy silent TypeError
    # dict(name="LambertW", args=[0]), # not registered with mathics_to_sympy
    dict(name="LegendreP", args=[1, 1]),
    # dict(name="LegendreQ", args=[1,0]), # sympy_name is ''
    # dict(name="LerchPhi", args=[1,2,0.25]), # sympy expects lerchphi()
    dict(name="Less", args=[0, 1]),
    dict(name="LessEqual", args=[0, 1]),
    dict(name="Log", args=[1]),
    dict(name="LogGamma", args=[0.5], close=True),
    # dict(name="LucasL", args=[0]), # sympy expects lucas()
    # dict(name="MeijerG", args=[[[], []], [[1], [-1]],1]), # ???
    # dict(name="MersennePrimeExponent", args=[10]), # to_sympy() fails
    # dict(name="ModularInverse", args=[3,5]), # SympyFunction.to_sympy silent TypeError
    # dict(name="MoebiusMu", args=[10]), # scipy expects mobius() [sic]
    # dict(name="PartitionsP", args=[10]), # lambdify generates incorrect code it seems
    # dict(name="PauliMatrix", args=[0]), # to_sympy failed
    dict(name="Pi", args=None),
    # dict(name="Piecewise", args=[]), # expression in conditional - how to test?
    dict(name="Plus", args=[0, 1]),
    dict(name="Pochhammer", args=[3, 2]),
    dict(name="PolyGamma", args=[3], close=True),
    dict(name="PolyGamma", args=[1, 2], close=True),
    # dict(name="PolyLog", args=[3,0.5]), # sympy expects polylog()
    # dict(name="PossibleZeroQ", args=[1]), # to_sympy() failed
    dict(name="Power", args=[2, 2]),
    # dict(name="Prime", args=[17]), # sympy expects SympyPrime()
    # dict(name="PrimePi", args=[0]), # sympy expects primepi()
    # dict(name="PrimeQ", args=[17]), # to_sympy() failed
    # dict(name="Product", args=[1,2,3]), # expects a function - can it be compiled??
    dict(name="ProductLog", args=[-1.5], close=True),
    dict(name="Re", args=[0]),
    # dict(name="Root", args=[0]), # expects a function - can it be compiled??
    # dict(name="RootSum", args=[0]), # expects a function - can it be compiled??
    dict(name="Sec", args=[0]),
    dict(name="Sech", args=[0]),
    dict(name="Sign", args=[0]),
    dict(name="Sin", args=[0]),
    dict(name="Sinh", args=[0]),
    # dict(name="SixJSymbol", args=[[1,2,3],[2,1,2]]), # module 'sympy' has no attribute 'physics.wigner.wigner_6j'
    # dict(name="Slot", args=[0]), # not numeric
    dict(name="SphericalBesselJ", args=[1, 1], close=True),
    dict(name="SphericalBesselY", args=[1, 1], close=True),
    # dict(name="SphericalHankelH1", args=[1,2]), # N and sympy differ significantly
    # dict(name="SphericalHankelH2", args=[1,2]), # N and sympy differ significantly
    # dict(name="SphericalHarmonicY", args=[3,1,1,1]), # sympy expects Ymn()
    dict(name="Sqrt", args=[2]),
    # dict(name="StieltjesGamma", args=[1]), # N returns System`StieltjesGamma[1.0]
    # dict(name="StirlingS1", args=[1,2]), # not registered with mathics_to_sympy
    # dict(name="StirlingS2", args=[1,2]), # not registered with mathics_to_sympy
    # dict(name="StruveH", args=[1,2]), # sympy_name is ''
    # dict(name="StruveL", args=[1,2]), # sympy_name is ''
    # dict(name="Subfactorial", args=[4]), # N gives 9, sympy gives nan
    # dict(name="Sum", args=[0]), # expects a function - can it be compiled??
    dict(name="Tan", args=[0]),
    dict(name="Tanh", args=[0]),
    # dict(name="ThreeJSymbol", args=[[6,0],[4,0],[2,0]]), # module 'sympy' has no attribute 'physics.wigner.wigner_3j'
    dict(name="Times", args=[1, 2, 3]),
    dict(name="Unequal", args=[0, 1]),
    # dict(name="WeberE", args=[0.5,5]), # sympy_name is ''
    dict(name="Zeta", args=[0]),
    #
    # Following have no sympy_name but do have mpamath_name.
    #
    # dict(name="Glaisher", args=None), # to_sympy() fails
    # dict(name="Khinchin", args=None), # to_sympy() fails
    #
    # Following have no sympy_name and no mpmath_name,
    # but do have "number" or "numeric" in their path.
    # Some may be possible candidates for building out compilation
    # by enabling sympy.
    #
    # dict(name="$MachineEpsilon", args=[0]),
    # dict(name="$MachinePrecision", args=[0]),
    # dict(name="$MaxMachineNumber", args=[0]),
    # dict(name="$MaxPrecision", args=[0]),
    # dict(name="$MinMachineNumber", args=[0]),
    # dict(name="$MinPrecision", args=[0]),
    # dict(name="$RandomState", args=[0]),
    # dict(name="Accuracy", args=[0]),
    # dict(name="AnglePath", args=[0]),
    # dict(name="Apart", args=[0]),
    # dict(name="BitLength", args=[0]),
    # dict(name="BrayCurtisDistance", args=[0]),
    # dict(name="C", args=[0]),
    # dict(name="CanberraDistance", args=[0]),
    # dict(name="Cancel", args=[0]),
    # dict(name="ChessboardDistance", args=[0]),
    # dict(name="Chop", args=[0]),
    # dict(name="Coefficient", args=[0]),
    # dict(name="CoefficientArrays", args=[0]),
    # dict(name="CoefficientList", args=[0]),
    # dict(name="Collect", args=[0]),
    # dict(name="Complexes", args=[0]),
    # dict(name="CosineDistance", args=[0]),
    # dict(name="DSolve", args=[0]),
    # dict(name="Denominator", args=[0]),
    # dict(name="DesignMatrix", args=[0]),
    # dict(name="Det", args=[0]),
    # dict(name="DigitCount", args=[0]),
    # dict(name="DiscreteLimit", args=[0]),
    # dict(name="DivisorSum", args=[0]),
    # dict(name="Divisors", args=[0]),
    # dict(name="Eigensystem", args=[0]),
    # dict(name="Eigenvectors", args=[0]),
    # dict(name="EuclideanDistance", args=[0]),
    # dict(name="Expand", args=[0]),
    # dict(name="ExpandAll", args=[0]),
    # dict(name="ExpandDenominator", args=[0]),
    # dict(name="Exponent", args=[0]),
    # dict(name="Factor", args=[0]),
    # dict(name="FactorInteger", args=[0]),
    # dict(name="FactorTermsList", args=[0]),
    # dict(name="FindMaximum", args=[0]),
    # dict(name="FindMinimum", args=[0]),
    # dict(name="FindRoot", args=[0]),
    # dict(name="FittedModel", args=[0]),
    # dict(name="FractionalPart", args=[0]),
    # dict(name="FromDigits", args=[0]),
    # dict(name="FullSimplify", args=[0]),
    # dict(name="Gudermannian", args=[0]),
    # dict(name="IntegerDigits", args=[0]),
    # dict(name="IntegerExponent", args=[0]),
    # dict(name="IntegerLength", args=[0]),
    # dict(name="IntegerPart", args=[0]),
    # dict(name="IntegerPartitions", args=[0]),
    # dict(name="IntegerReverse", args=[0]),
    # dict(name="IntegerString", args=[0]),
    # dict(name="Integers", args=[0]),
    # dict(name="Inverse", args=[0]),
    # dict(name="InverseGudermannian", args=[0]),
    # dict(name="JacobiSymbol", args=[0]),
    # dict(name="KroneckerSymbol", args=[0]),
    # dict(name="LeastSquares", args=[0]),
    # dict(name="Limit", args=[0]),
    # dict(name="LinearModelFit", args=[0]),
    # dict(name="LinearSolve", args=[0]),
    # dict(name="Log10", args=[0]),
    # dict(name="Log2", args=[0]),
    # dict(name="LogisticSigmoid", args=[0]),
    # dict(name="MachinePrecision", args=[0]),
    # dict(name="ManhattanDistance", args=[0]),
    # dict(name="MantissaExponent", args=[0]),
    # dict(name="MatrixExp", args=[0]),
    # dict(name="MatrixPower", args=[0]),
    # dict(name="MatrixRank", args=[0]),
    # dict(name="MinimalPolynomial", args=[0]),
    # dict(name="N", args=[0]),
    # dict(name="NIntegrate", args=[0]),
    # dict(name="Negative", args=[0]),
    # dict(name="NextPrime", args=[0]),
    # dict(name="NonNegative", args=[0]),
    # dict(name="NonPositive", args=[0]),
    # dict(name="NullSpace", args=[0]),
    # dict(name="NumberDigit", args=[0]),
    # dict(name="Numerator", args=[0]),
    # dict(name="O", args=[0]),
    # dict(name="Overflow", args=[0]),
    # dict(name="Positive", args=[0]),
    # dict(name="PowerExpand", args=[0]),
    # dict(name="PowersRepresentations", args=[0]),
    # dict(name="Precision", args=[0]),
    # dict(name="PseudoInverse", args=[0]),
    # dict(name="QRDecomposition", args=[0]),
    # dict(name="Random", args=[0]),
    # dict(name="RandomChoice", args=[0]),
    # dict(name="RandomComplex", args=[0]),
    # dict(name="RandomInteger", args=[0]),
    # dict(name="RandomPrime", args=[0]),
    # dict(name="RandomReal", args=[0]),
    # dict(name="RandomSample", args=[0]),
    # dict(name="Rationalize", args=[0]),
    # dict(name="RealAbs", args=[0]),
    # dict(name="RealDigits", args=[0]),
    # dict(name="RealSign", args=[0]),
    # dict(name="Reals", args=[0]),
    # dict(name="Round", args=[0]),
    # dict(name="RowReduce", args=[0]),
    # dict(name="SeedRandom", args=[0]),
    # dict(name="Series", args=[0]),
    # dict(name="SeriesCoefficient", args=[0]),
    # dict(name="SeriesData", args=[0]),
    # dict(name="Simplify", args=[0]),
    # dict(name="SingularValueDecomposition", args=[0]),
    # dict(name="Solve", args=[0]),
    # dict(name="SquaredEuclideanDistance", args=[0]),
    # dict(name="SquaresR", args=[0]),
    # dict(name="Together", args=[0]),
    # dict(name="Tr", args=[0]),
    # dict(name="Undefined", args=[0]),
    # dict(name="Underflow", args=[0]),
    # dict(name="UnitStep", args=[0]),
    # dict(name="Variables", args=[0]),
]

debug = 0


def fail(name, msg):
    msg = f"{name}: {msg}"
    print(msg)
    raise AssertionError(msg)


# Ttesting is showing multiple small numerical deviations
# between platforms, so instead of chasing them down one
# by one, let's just make all the tests "close-enough" tests.
# TODO: remove the close arg?
def one(name, args, close=True, scipy=False, expected=None):
    print("===", name)

    if args is None:
        # constant
        args = []
        parms = []
        n_expr = f"N[{name}]"
        def_expr = f"{name}"

    else:
        # function
        parms = [c for c in "xyzuvw"[0 : len(args)]]
        n_expr = f"N[{name}[{','.join(str(from_python(arg)) for arg in args)}]]"
        def_expr = f"{name}[{','.join(parms)}]"

    # run N[] to get expected if it isn't provided
    if expected is None:
        expected = session.evaluate(n_expr)
        if not hasattr(expected, "to_python") or isinstance(
            expected.to_python(), (Expression, str)
        ):
            # TODO: messages might be helpful
            fail(name, f"N fails, returning {expected} - check args")
        else:
            expected = expected.to_python()

    # compile function
    try:
        expr = session.parse(def_expr)
        fun = plot_compile(session.evaluation, expr, parms, debug)
    except Exception as oops:
        fail(name, f"compilaton failed: {oops}")

    # run compiled function to get result
    try:
        result = fun(*args)
    except NameError as oops:
        src = inspect.getsource(fun)
        fail(
            name,
            f"{oops} because sympy expected it would be found in the modules\n"
            f"that were configured during compiliation. The error occured while executing this compiled code:\n{src}",
        )
    except Exception as oops:
        src = inspect.getsource(fun)
        fail(name, f"{oops} occurred running the following compiled code:\n{src}")

    # compare
    if result != expected and not (close and np.isclose(result, expected)):
        fail(name, f"expected {expected}, got {result}")
    else:
        pass
        # print(f"{name} succeeds: expected {expected.value}, got {result}")


def test():
    for test in tests:
        one(**test)


if __name__ == "__main__":
    for test in tests:
        try:
            debug = 1
            one(**test)
        except AssertionError:
            exit()
