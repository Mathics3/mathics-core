from mathics.session import MathicsSession
from mathics.eval.drawing.plot_compile import compile
from mathics.core.expression import Expression
import inspect
import math

tests = [
    # have sympy_name
    dict(name="Abs", args=[-1]),
    dict(name="AiryAi", args=[1], tol=1e-15),
    dict(name="AiryAiPrime", args=[1], tol=1e-15),
    dict(name="AiryBi", args=[1], tol=1e-15),
    dict(name="AiryBiPrime", args=[1], tol=1e-15),
    #dict(name="AngerJ", args=[0,0]),		# may need https://github.com/bdlucas1/mathics-core/pull/8
    dict(name="ArcCos", args=[0]),		# NEXT: wrong
    dict(name="ArcCosh", args=[2], tol=1e-15),
    dict(name="ArcCot", args=[1]),
    #dict(name="ArcCoth", args=[0.1]),	# sympy returns nan
    #dict(name="ArcCsc", args=[0.1]),		# sympy returns nan
    dict(name="ArcCsch", args=[0.1]),
    #dict(name="ArcSec", args=[0.1]),		# sympy returns nan
    dict(name="ArcSech", args=[0.1]),
    dict(name="ArcSin", args=[0.1]),
    dict(name="ArcSinh", args=[0]),
    dict(name="ArcTan", args=[0]),
    dict(name="ArcTanh", args=[0]),
    dict(name="Arg", args=[0]),
    #dict(name="BellB", args=[0]),		# not defined
    dict(name="BernoulliB", args=[0]),	# scipy
    dict(name="BesselI", args=[0,0]),		# scipy
    #dict(name="BesselJ", args=[0,0]),	# not defined
    #dict(name="BesselJZero", args=[1,1]),	# may need https://github.com/bdlucas1/mathics-core/pull/8
    #dict(name="BesselK", args=[0,0]),	# not defined
    #dict(name="BesselY", args=[0,0]),	# not defined
    #dict(name="BesselYZero", args=[2,2]),	# # may need https://github.com/bdlucas1/mathics-core/pull/8
    dict(name="Beta", args=[0.5, 1], tol=1e-15),
    dict(name="Binomial", args=[3, 0.5], tol=1e-15),
    dict(name="Catalan", args=None),
    dict(name="CatalanNumber", args=[0]),
    dict(name="Ceiling", args=[0]),
    #dict(name="ChebyshevT", args=[0,1]),	# not defined
    #dict(name="ChebyshevU", args=[0,1]),	# not defined
    #dict(name="ClebschGordan", args=[0,1]),	# args are complicated
    #dict(name="ComplexExpand", args=[0]),
    #dict(name="ComplexInfinity", args=None),	# constant infinity = figure out how to handle
    #dict(name="ConditionalExpression", args=[1,True]),	# error compling - may need PR?
    dict(name="Conjugate", args=[0]),
    #dict(name="ContinuedFraction", args=[0]),	# needs more investigation
    dict(name="Cos", args=[0]),
    dict(name="Cosh", args=[0]),
    dict(name="Cot", args=[1]),
    dict(name="Coth", args=[1]),
    dict(name="Csc", args=[1]),
    #dict(name="Curl", args=[0]),		# is this really numeric?
    #dict(name="D", args=[0]),		# is this really numeric
    dict(name="Degree", args=None),
    #dict(name="Derivative", args=[0]),	# is this really numeric
    #dict(name="DirectedInfinity", args=[0]),	# infinity - how to handle
    #dict(name="DivisorSigma", args=[1,20]),	# not defined
    dict(name="E", args=None),
    #dict(name="Eigenvalues", args=[0]),	# complicated

    # STOPPED HERE
    dict(name="EllipticE", args=[0]),
    dict(name="EllipticF", args=[0]),
    dict(name="EllipticK", args=[0]),
    dict(name="EllipticPi", args=[0]),
    dict(name="Equal", args=[0]),
    dict(name="Erf", args=[0]),
    dict(name="Erfc", args=[0]),
    dict(name="EulerE", args=[0]),
    dict(name="EulerGamma", args=[0]),
    dict(name="EulerPhi", args=[0]),
    dict(name="Exp", args=[0]),
    dict(name="ExpIntegralE", args=[0]),
    dict(name="ExpIntegralEi", args=[0]),
    dict(name="Factorial", args=[0]),
    dict(name="Factorial2", args=[0]),
    dict(name="Fibonacci", args=[0]),
    dict(name="Floor", args=[0]),
    dict(name="FresnelC", args=[0]),
    dict(name="FresnelS", args=[0]),
    dict(name="FromContinuedFraction", args=[0]),
    dict(name="Function", args=[0]),
    dict(name="Gamma", args=[0]),
    dict(name="GegenbauerC", args=[0]),
    dict(name="GoldenRatio", args=[0]),
    dict(name="Greater", args=[0]),
    dict(name="GreaterEqual", args=[0]),
    dict(name="HankelH1", args=[0]),
    dict(name="HankelH2", args=[0]),
    dict(name="HarmonicNumber", args=[0]),
    dict(name="Haversine", args=[0]),
    dict(name="HermiteH", args=[0]),
    dict(name="Hypergeometric1F1", args=[0]),
    dict(name="Hypergeometric2F1", args=[0]),
    dict(name="HypergeometricPFQ", args=[0]),
    dict(name="HypergeometricU", args=[0]),
    dict(name="I", args=[0]),
    dict(name="Im", args=[0]),
    dict(name="Indeterminate", args=[0]),
    dict(name="Infinity", args=[0]),
    dict(name="Integrate", args=[0]),
    dict(name="InverseErf", args=[0]),
    dict(name="InverseErfc", args=[0]),
    dict(name="InverseHaversine", args=[0]),
    dict(name="JacobiP", args=[0]),
    dict(name="KelvinBei", args=[0]),
    dict(name="KelvinBer", args=[0]),
    dict(name="KelvinKei", args=[0]),
    dict(name="KelvinKer", args=[0]),
    dict(name="KroneckerProduct", args=[0]),
    dict(name="LaguerreL", args=[0]),
    dict(name="LambertW", args=[0]),
    dict(name="LegendreP", args=[0]),
    dict(name="LegendreQ", args=[0]),
    dict(name="LerchPhi", args=[0]),
    dict(name="Less", args=[0]),
    dict(name="LessEqual", args=[0]),
    dict(name="Log", args=[0]),
    dict(name="LogGamma", args=[0]),
    dict(name="LucasL", args=[0]),
    dict(name="MeijerG", args=[0]),
    dict(name="MersennePrimeExponent", args=[0]),
    dict(name="ModularInverse", args=[0]),
    dict(name="MoebiusMu", args=[0]),
    dict(name="PartitionsP", args=[0]),
    dict(name="PauliMatrix", args=[0]),
    dict(name="Pi", args=[0]),
    dict(name="Piecewise", args=[0]),
    dict(name="Plus", args=[0]),
    dict(name="Pochhammer", args=[0]),
    dict(name="PolyGamma", args=[0]),
    dict(name="PolyLog", args=[0]),
    dict(name="PossibleZeroQ", args=[0]),
    dict(name="Power", args=[0]),
    dict(name="Prime", args=[0]),
    dict(name="PrimePi", args=[0]),
    dict(name="PrimeQ", args=[0]),
    dict(name="Product", args=[0]),
    dict(name="ProductLog", args=[0]),
    dict(name="Re", args=[0]),
    dict(name="Root", args=[0]),
    dict(name="RootSum", args=[0]),
    dict(name="Sec", args=[0]),
    dict(name="Sech", args=[0]),
    dict(name="Sign", args=[0]),
    dict(name="Sin", args=[0]),
    dict(name="Sinh", args=[0]),
    dict(name="SixJSymbol", args=[0]),
    dict(name="Slot", args=[0]),
    dict(name="SphericalBesselJ", args=[0]),
    dict(name="SphericalBesselY", args=[0]),
    dict(name="SphericalHankelH1", args=[0]),
    dict(name="SphericalHankelH2", args=[0]),
    dict(name="SphericalHarmonicY", args=[0]),
    dict(name="Sqrt", args=[0]),
    dict(name="StieltjesGamma", args=[0]),
    dict(name="StirlingS1", args=[0]),
    dict(name="StirlingS2", args=[0]),
    dict(name="StruveH", args=[0]),
    dict(name="StruveL", args=[0]),
    dict(name="Subfactorial", args=[0]),
    dict(name="Sum", args=[0]),
    dict(name="Tan", args=[0]),
    dict(name="Tanh", args=[0]),
    dict(name="ThreeJSymbol", args=[0]),
    dict(name="Times", args=[0]),
    dict(name="Unequal", args=[0]),
    dict(name="WeberE", args=[0]),
    dict(name="Zeta", args=[0]),

    # no sympy_name but have mpmath_name
    dict(name="Glaisher", args=[0]),
    dict(name="Khinchin", args=[0]),

    # number or numeric in path
    dict(name="$MachineEpsilon", args=[0]),
    dict(name="$MachinePrecision", args=[0]),
    dict(name="$MaxMachineNumber", args=[0]),
    dict(name="$MaxPrecision", args=[0]),
    dict(name="$MinMachineNumber", args=[0]),
    dict(name="$MinPrecision", args=[0]),
    dict(name="$RandomState", args=[0]),
    dict(name="Accuracy", args=[0]),
    dict(name="AnglePath", args=[0]),
    dict(name="Apart", args=[0]),
    dict(name="BitLength", args=[0]),
    dict(name="BrayCurtisDistance", args=[0]),
    dict(name="C", args=[0]),
    dict(name="CanberraDistance", args=[0]),
    dict(name="Cancel", args=[0]),
    dict(name="ChessboardDistance", args=[0]),
    dict(name="Chop", args=[0]),
    dict(name="Coefficient", args=[0]),
    dict(name="CoefficientArrays", args=[0]),
    dict(name="CoefficientList", args=[0]),
    dict(name="Collect", args=[0]),
    dict(name="Complexes", args=[0]),
    dict(name="CosineDistance", args=[0]),
    dict(name="DSolve", args=[0]),
    dict(name="Denominator", args=[0]),
    dict(name="DesignMatrix", args=[0]),
    dict(name="Det", args=[0]),
    dict(name="DigitCount", args=[0]),
    dict(name="DiscreteLimit", args=[0]),
    dict(name="DivisorSum", args=[0]),
    dict(name="Divisors", args=[0]),
    dict(name="Eigensystem", args=[0]),
    dict(name="Eigenvectors", args=[0]),
    dict(name="EuclideanDistance", args=[0]),
    dict(name="Expand", args=[0]),
    dict(name="ExpandAll", args=[0]),
    dict(name="ExpandDenominator", args=[0]),
    dict(name="Exponent", args=[0]),
    dict(name="Factor", args=[0]),
    dict(name="FactorInteger", args=[0]),
    dict(name="FactorTermsList", args=[0]),
    dict(name="FindMaximum", args=[0]),
    dict(name="FindMinimum", args=[0]),
    dict(name="FindRoot", args=[0]),
    dict(name="FittedModel", args=[0]),
    dict(name="FractionalPart", args=[0]),
    dict(name="FromDigits", args=[0]),
    dict(name="FullSimplify", args=[0]),
    dict(name="Gudermannian", args=[0]),
    dict(name="IntegerDigits", args=[0]),
    dict(name="IntegerExponent", args=[0]),
    dict(name="IntegerLength", args=[0]),
    dict(name="IntegerPart", args=[0]),
    dict(name="IntegerPartitions", args=[0]),
    dict(name="IntegerReverse", args=[0]),
    dict(name="IntegerString", args=[0]),
    dict(name="Integers", args=[0]),
    dict(name="Inverse", args=[0]),
    dict(name="InverseGudermannian", args=[0]),
    dict(name="JacobiSymbol", args=[0]),
    dict(name="KroneckerSymbol", args=[0]),
    dict(name="LeastSquares", args=[0]),
    dict(name="Limit", args=[0]),
    dict(name="LinearModelFit", args=[0]),
    dict(name="LinearSolve", args=[0]),
    dict(name="Log10", args=[0]),
    dict(name="Log2", args=[0]),
    dict(name="LogisticSigmoid", args=[0]),
    dict(name="MachinePrecision", args=[0]),
    dict(name="ManhattanDistance", args=[0]),
    dict(name="MantissaExponent", args=[0]),
    dict(name="MatrixExp", args=[0]),
    dict(name="MatrixPower", args=[0]),
    dict(name="MatrixRank", args=[0]),
    dict(name="MinimalPolynomial", args=[0]),
    dict(name="N", args=[0]),
    dict(name="NIntegrate", args=[0]),
    dict(name="Negative", args=[0]),
    dict(name="NextPrime", args=[0]),
    dict(name="NonNegative", args=[0]),
    dict(name="NonPositive", args=[0]),
    dict(name="NullSpace", args=[0]),
    dict(name="NumberDigit", args=[0]),
    dict(name="Numerator", args=[0]),
    dict(name="O", args=[0]),
    dict(name="Overflow", args=[0]),
    dict(name="Positive", args=[0]),
    dict(name="PowerExpand", args=[0]),
    dict(name="PowersRepresentations", args=[0]),
    dict(name="Precision", args=[0]),
    dict(name="PseudoInverse", args=[0]),
    dict(name="QRDecomposition", args=[0]),
    dict(name="Random", args=[0]),
    dict(name="RandomChoice", args=[0]),
    dict(name="RandomComplex", args=[0]),
    dict(name="RandomInteger", args=[0]),
    dict(name="RandomPrime", args=[0]),
    dict(name="RandomReal", args=[0]),
    dict(name="RandomSample", args=[0]),
    dict(name="Rationalize", args=[0]),
    dict(name="RealAbs", args=[0]),
    dict(name="RealDigits", args=[0]),
    dict(name="RealSign", args=[0]),
    dict(name="Reals", args=[0]),
    dict(name="Round", args=[0]),
    dict(name="RowReduce", args=[0]),
    dict(name="SeedRandom", args=[0]),
    dict(name="Series", args=[0]),
    dict(name="SeriesCoefficient", args=[0]),
    dict(name="SeriesData", args=[0]),
    dict(name="Simplify", args=[0]),
    dict(name="SingularValueDecomposition", args=[0]),
    dict(name="Solve", args=[0]),
    dict(name="SquaredEuclideanDistance", args=[0]),
    dict(name="SquaresR", args=[0]),
    dict(name="Together", args=[0]),
    dict(name="Tr", args=[0]),
    dict(name="Undefined", args=[0]),
    dict(name="Underflow", args=[0]),
    dict(name="UnitStep", args=[0]),
    dict(name="Variables", args=[0]),
]

session = MathicsSession()

def fail(name, msg):
    print(f"{name}: {msg}")
    exit(-1)

def one(name, args, tol=0):

    print("===", name)

    if args is None:

        # constant
        args = []
        parms = []
        n_expr = f"N[{name}]"
        def_expr = f"{name}"

    else:

        # function
        parms = [c for c in "xyzuvw"[0:len(args)]]
        n_expr = f"N[{name}[{','.join(str(arg) for arg in args)}]]"
        def_expr = f"{name}[{','.join(parms)}]"

    # run N[] to get expected
    expected = session.evaluate(n_expr)
    if not hasattr(expected, "to_python") or isinstance(expected.to_python(), (Expression,str)):
        fail(name, f"N fails, returning {expected} - check args") # TODO: messages might be helpful
    else:
        expected = expected.to_python()
        
    # compile function
    try:
        expr = session.parse(def_expr)
        fun = compile(session.evaluation, expr, parms)
    except Exception as oops:
        fail(name, oops)

    # run compiled function to get result
    try:
        result = fun(*args)
    except Exception as oops:
        src = inspect.getsource(fun)
        fail(name, f"{oops} while executing:\n{src}")
        
    # compare
    if result != expected:
        if math.isfinite(result) and math.isfinite(expected):
            if abs(result - expected) > tol:
                fail(name, f"expected {expected}, got {result}, diff {expected-result}")
        else:
            fail(name, f"expected {expected}, got {result}")
    else:
        pass
        #print(f"{name} succeeds: expected {expected.value}, got {result}")

if __name__ == "__main__":
    for test in tests:
        one(**test)
