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
from test.helper import session

import numpy as np

from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.eval.drawing.plot_compile import plot_compile

#
# Each test specifies:
#     name - name of function
#     args - suitable args to be given to N[function[args]] and compiled_function[args] for comparison
#     scipy (optional) - boolean marking whether scipy is needed for the test
#     fail (optional) - if test is known to fail, is string that is expected in the failure message
#
# common failures
#     N fails                 N did not give numeric result.
#                              Check test case args, or test may be more complicated
#     sympy_name is ''        Builtin has .sympy_name = ''
#                             Look into whether sympy in fact has an equivalent to use here.
#     not registered          Bultin is not registered
#                             Try making it a subclass of SympyFunction.
#     '...' is not defined    Sympy expects function '...' to be defined.
#                             Look into adding it in plot_compile.py
#     TypeError               Look into builtin.to_sympy where it catches TypeError

# common test case for Round, Floor, Ceiling, IntegerPart, FractionalPart
rounding=[[-1.7, -1.5, -1.2, -1, 1, 1.2, 1.5, 1.7]]

tests = [
    #
    # Following have sympy_name.
    # fmt: off
    #
    dict(name="Abs", args=[-1]),
    dict(name="AiryAi", args=[1]),
    dict(name="AiryAiPrime", args=[1]),
    dict(name="AiryBi", args=[1]),
    dict(name="AiryBiPrime", args=[1]),
    dict(name="AngerJ", args=[0,0], fail="sympy_name is ''"),
    dict(name="ArcCos", args=[0]),
    dict(name="ArcCosh", args=[2]),
    dict(name="ArcCot", args=[1]),
    dict(name="ArcCoth", args=[2]),
    dict(name="ArcCsc", args=[2]),
    dict(name="ArcCsch", args=[0.1]),
    dict(name="ArcSec", args=[2]),
    dict(name="ArcSech", args=[0.1]),
    dict(name="ArcSin", args=[0.1]),
    dict(name="ArcSinh", args=[0]),
    dict(name="ArcTan", args=[0]),
    dict(name="ArcTanh", args=[0]),
    dict(name="Arg", args=[0]),
    dict(name="BellB", args=[0], fail="'bell' is not defined"),
    dict(name="BernoulliB", args=[0], scipy=True),
    dict(name="BesselI", args=[0, 0], scipy=True),
    dict(name="BesselJ", args=[0, 0], scipy=True),
    dict(name="BesselJZero", args=[1,1], fail="sympy_name is ''"),
    dict(name="BesselK", args=[0.5, 0.5], scipy=True),
    dict(name="BesselY", args=[0, 0], scipy=True),
    dict(name="BesselYZero", args=[2,2], fail="sympy_name is ''"),
    dict(name="Beta", args=[0.5, 1]),
    dict(name="Binomial", args=[3, 0.5]),
    dict(name="Catalan", args=None),
    dict(name="CatalanNumber", args=[0]),
    dict(name="Ceiling", args=rounding),
    dict(name="ChebyshevT", args=[0, 1], scipy=True),
    dict(name="ChebyshevU", args=[0, 1], scipy=True),
    dict(name="ClebschGordan", args=[[5,0],[4,0],[1,0]], fail="physics.quantum.cg.CG"),
    dict(name="ComplexExpand", args=[0]),
    dict(name="ComplexInfinity", args=None, fail="N fails"),
    dict(name="ConditionalExpression", args=[1,True], fail="not registered"),
    dict(name="Conjugate", args=[0]),
    dict(name="ContinuedFraction", args=[0.4, 3], fail="2 were given"),
    dict(name="ContinuedFraction", args=[0.4], fail="N fails"),
    dict(name="Cos", args=[0]),
    dict(name="Cosh", args=[0]),
    dict(name="Cot", args=[1]),
    dict(name="Coth", args=[1]),
    dict(name="Csc", args=[1]),
    dict(name="Curl", args=[0], fail="N fails"), # takes function - compilable?
    dict(name="D", args=[0], fail="N fails"), # takes function - compilable?
    dict(name="Degree", args=None),
    dict(name="Derivative", args=[0], fail="N fails"),
    dict(name="DirectedInfinity", args=[0], fail="N fails"),
    dict(name="DivisorSigma", args=[1,20], fail="'divisor_sigma' is not defined"),
    dict(name="E", args=None),
    dict(name="Eigenvalues", args=[[[1,2],[3,4]]], fail="not registered"),
    dict(name="EllipticE", args=[0], fail="'elliptic_e' is not defined"),
    dict(name="EllipticF", args=[0,0], fail="'elliptic_f' is not defined"),
    dict(name="EllipticK", args=[0], fail="'elliptic_k' is not defined"),
    dict(name="EllipticPi", args=[0,0], fail="'elliptic_pi' is not defined"),
    dict(name="Equal", args=[0, 0]),
    dict(name="Erf", args=[0]),
    dict(name="Erfc", args=[0]),
    dict(name="EulerE", args=[0]),
    dict(name="EulerGamma", args=None),
    dict(name="EulerPhi", args=None, fail="N fail"),
    dict(name="Exp", args=[0]),
    dict(name="ExpIntegralE", args=[1,1], fail="'expint' is not defined"),
    dict(name="ExpIntegralEi", args=[0]),
    dict(name="Factorial", args=[0]),
    dict(name="Factorial2", args=[0]),
    dict(name="Fibonacci", args=[0], fail="'fibonacci' is not defined"),
    dict(name="Floor", args=rounding),
    dict(name="FresnelC", args=[0]),
    dict(name="FresnelS", args=[0]),
    dict(name="FromContinuedFraction", args=[[2,1,3,4]], fail="TypeError"),
    # dict(name="Function", args=[], fail=True), # compilable?
    dict(name="Gamma", args=[1]),
    dict(name="GegenbauerC", args=[1, 1, 1]),
    dict(name="GoldenRatio", args=None),
    dict(name="Greater", args=[0, 1]),
    dict(name="GreaterEqual", args=[0, 1]),
    dict(name="HankelH1", args=[1,1], fail="N and sympy differ"),
    dict(name="HankelH2", args=[1,1], fail="N and sympy differ"),
    dict(name="HarmonicNumber", args=[0]),
    dict(name="Haversine", args=[1]),
    dict(name="HermiteH", args=[0, 0]),
    dict(name="Hypergeometric1F1", args=[1,1,1], fail="List not registered"),
    dict(name="Hypergeometric2F1", args=[2,3,4,5], fail="List not registered"),
    dict(name="HypergeometricPFQ", args=[[1,1],[3,3,3],2], fail="TypeError"),
    dict(name="HypergeometricU", args=[1,1,1], fail="sympy_name is ''"),
    dict(name="I", args=None),
    dict(name="Im", args=[0]),
    dict(name="Indeterminate", args=None, fail="N fails"),
    dict(name="Infinity", args=None),
    dict(name="Integrate", args=[0], fail="N fails"), # takes function - compilable?
    dict(name="InverseErf", args=[0]),
    dict(name="InverseErfc", args=[0]),
    dict(name="InverseHaversine", args=[0.1]),
    dict(name="JacobiP", args=[1, 1, 1, 1]),
    dict(name="KelvinBei", args=[0], fail="sympy_name is ''"),
    dict(name="KelvinBer", args=[0], fail="sympy_name is ''"),
    dict(name="KelvinKei", args=[0], fail="sympy_name is ''"),
    dict(name="KelvinKer", args=[0], fail="sympy_name is ''"),
    dict(name="KroneckerProduct", args=[0], fail="N fails"),
    dict(name="LaguerreL", args=[1,0], fail="TypeError"),
    dict(name="LambertW", args=[1]),
    dict(name="LegendreP", args=[1, 1]),
    dict(name="LegendreQ", args=[1,0], fail="sympy_name is ''"),
    dict(name="LerchPhi", args=[1,2,0.25], fail="'lerchphi' is not defined"),
    dict(name="Less", args=[0, 1]),
    dict(name="LessEqual", args=[0, 1]),
    dict(name="Log", args=[1]),
    dict(name="LogGamma", args=[0.5]),
    dict(name="LucasL", args=[0], fail="'lucas' is not defined"),
    dict(name="MeijerG", args=[[[], []], [[1], [-1]],1], fail="TypeError"),
    dict(name="MersennePrimeExponent", args=[10], fail="x is not an integer"),
    dict(name="ModularInverse", args=[3,5], fail="TypeError"),
    dict(name="MoebiusMu", args=[10], fail="'mobius' is not defined"), # [sic] - is typo?
    dict(name="PartitionsP", args=[10], fail="partition() missing 1"), # sympy generates incorrect code it seems
    dict(name="PauliMatrix", args=[0], fail="physics.matrices.msigma"),
    dict(name="Pi", args=None),
    dict(name="Piecewise", args=[], fail="N fails"), # how to test?
    dict(name="Plus", args=[0, 1]),
    dict(name="Pochhammer", args=[3, 2]),
    dict(name="PolyGamma", args=[3]),
    dict(name="PolyGamma", args=[1, 2]),
    dict(name="PolyLog", args=[3,0.5], fail="'polylog' is not defined"),
    dict(name="PossibleZeroQ", args=[1]),
    dict(name="Power", args=[2, 2]),
    dict(name="Prime", args=[17], fail="'SympyPrime' is not defined"),
    dict(name="PrimePi", args=[0], fail="'primepi' is not defined"),
    dict(name="PrimeQ", args=[17], fail="N and sympy differ"), # !
    dict(name="Product", args=[1,2,3], fail="N fails"), # takes function - compilable?
    dict(name="ProductLog", args=[-1.5]),
    dict(name="Re", args=[0]),
    dict(name="Root", args=[0], fail="N fails"), # takes function - compilable?
    dict(name="RootSum", args=[0], fail="N fails"), # takes function - compilable?
    dict(name="Sec", args=[0]),
    dict(name="Sech", args=[0]),
    dict(name="Sign", args=[0]),
    dict(name="Sin", args=[0]),
    dict(name="Sinh", args=[0]),
    dict(name="SixJSymbol", args=[[1,2,3],[2,1,2]], fail="physics.wigner.wigner_6j"),
    dict(name="Slot", args=[0], fail="N fails"), # not numeric?
    dict(name="SphericalBesselJ", args=[1, 1]),
    dict(name="SphericalBesselY", args=[1, 1]),
    dict(name="SphericalHankelH1", args=[1,2], fail="N and sympy differ"),
    dict(name="SphericalHankelH2", args=[1,2], fail="N and sympy differ"),
    dict(name="SphericalHarmonicY", args=[3,1,1,1], fail="assoc_legendre not registered"),
    dict(name="Sqrt", args=[2]),
    dict(name="StieltjesGamma", args=[1], fail="N fails"),
    dict(name="StirlingS1", args=[1,2], fail="not registered"),
    dict(name="StirlingS2", args=[1,2], fail="not registered"),
    dict(name="StruveH", args=[1,2], fail="sympy_name is ''"),
    dict(name="StruveL", args=[1,2], fail="sympy_name is ''"),
    dict(name="Subfactorial", args=[4], fail="N and sympy differ"),
    dict(name="Sum", args=[0], fail="N fails"), # takes function - compilable?
    dict(name="Tan", args=[0]),
    dict(name="Tanh", args=[0]),
    dict(name="ThreeJSymbol", args=[[6,0],[4,0],[2,0]], fail="physics.wigner.wigner_3j"),
    dict(name="Times", args=[1, 2, 3]),
    dict(name="Unequal", args=[0, 1]),
    dict(name="WeberE", args=[0.5,5], fail="sympy_name is ''"),
    dict(name="Zeta", args=[0]),
    #
    # Following have no sympy_name but do have mpamath_name.
    #
    # dict(name="Glaisher", args=None, fail="to_sympy() fails"),
    # dict(name="Khinchin", args=None, fail="to_sympy() fails"),
    #
    # Following have none of the above but do have A_NUMERIC_FUNCTION set
    #
    dict(name="AiryAiZero", args=[1,1], fail="N fail"),
    dict(name="AiryBiZero", args=[0], fail="N fails"),
    dict(name="BernsteinBasis", args=[4, 3, 0.5]),
    dict(name="CubeRoot", args=[3]),
    dict(name="Divide", args=[1, 1]),
    dict(name="FractionalPart", args=rounding, fail="not registered"), # sympy.frac gives different answers :(
    dict(name="IntegerPart", args=rounding, fail="not registered"), # sympy.Integer doesn't quite work
    dict(name="Log10", args=[10]),
    dict(name="Log2", args=[10]),
    dict(name="LogisticSigmoid", args=[0], fail="not registered"),
    dict(name="Max", args=[0,1]),
    dict(name="Min", args=[0,1]),
    dict(name="Minus", args=[5]),
    dict(name="Mod", args=[10,3]),
    dict(name="Mod", args=[-10,3]),
    dict(name="Mod", args=[10,-3]),
    dict(name="Mod", args=[-10,-3]),
    dict(name="Multinomial", args=[1,2,1]),
    dict(name="PolygonalNumber", args=[0], fail="not registered"),
    dict(name="Quotient", args=[5,3], fail="not registered"),
    dict(name="QuotientRemainder", args=[5,3], fail="not registered"),
    dict(name="RealAbs", args=[-1], fail="not registered"),
    dict(name="RealSign", args=[0], fail="not registered"),
    dict(name="Round", args=rounding, fail="not registered"),
    dict(name="Subtract", args=[5, 3]),
    dict(name="UnitStep", args=[0], fail="not registered"),
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
    # dict(name="FromDigits", args=[0]),
    # dict(name="FullSimplify", args=[0]),
    # dict(name="Gudermannian", args=[0]),
    # dict(name="IntegerDigits", args=[0]),
    # dict(name="IntegerExponent", args=[0]),
    # dict(name="IntegerLength", args=[0]),
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
    # dict(name="RealDigits", args=[0]),
    # dict(name="Reals", args=[0]),
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
    # dict(name="Variables", args=[0]),
    # fmt: on
]

debug = 0
check_failing = False


# Testing is showing multiple small numerical deviations
# between platforms, so instead of chasing them down one
# by one, let's just make all the tests "close-enough" tests.
def one(name, args, scipy=False, expected=None, fail=False):
    if fail and not check_failing:
        return

    def failure(name, msg):
        msg = f"{name}: {msg}"
        if fail and str(fail) not in msg:
            raise Exception(f"expected failure {fail}, got failure {msg}")
        raise AssertionError(msg)

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
            failure(name, f"N fails, returning {expected} - check args")
        else:
            expected = expected.to_python()

    # compile function
    try:
        expr = session.parse(def_expr)
        fun = plot_compile(session.evaluation, expr, parms, debug)
    except Exception as oops:
        failure(name, f"compilaton failed: {oops}")

    # run compiled function to get result
    try:
        result = fun(*args)
    except Exception as oops:
        src = inspect.getsource(fun)
        failure(name, f"{oops} while executing:\n{src}")

    # this allows comparison of functions that return List using np.isclose
    wrap = lambda x: np.array(x) if isinstance(x, list) else x
    result = wrap(result)
    expected = wrap(expected)

    # compare
    if not isinstance(result, (int,float,complex,bool,np.ndarray,np.number,np.bool)):
        failure(name, f"bad type {type(result)}")
    elif not np.isclose(result, expected).all():
        failure(name, f"N and sympy differ: expected {expected}, got {result}")
    elif fail:
        raise Exception("unexpected success")
    else:
        # print(f"{name} succeeds: expected {expected.value}, got {result}")
        pass


def test():
    for test in tests:
        try:
            one(**test)
        except AssertionError as oops:
            if not "fail" in test:
                print(oops)
                raise


if __name__ == "__main__":
    check_failing = True
    debug = 1
    test()
