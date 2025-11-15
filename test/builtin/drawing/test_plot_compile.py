from mathics.session import MathicsSession
from mathics.eval.drawing.plot_compile import compile
from mathics.core.expression import Expression
import inspect
import math

tests = [
    ("1 sympy_name", "Abs", [-1]),
    ("1 sympy_name", "AiryAi", [1], 1e-15),
    ("1 sympy_name", "AiryAiPrime", [1], 1e-15),
    ("1 sympy_name", "AiryBi", [1], 1e-15),
    ("1 sympy_name", "AiryBiPrime", [1], 1e-15),
    #("1 sympy_name", "AngerJ", [0,0]),		# may need https://github.com/bdlucas1/mathics-core/pull/8
    ("1 sympy_name", "ArcCos", [0]),		# NEXT: wrong
    ("1 sympy_name", "ArcCosh", [2], 1e-15),
    ("1 sympy_name", "ArcCot", [1]),
    #("1 sympy_name", "ArcCoth", [0.1]),	# sympy returns nan
    #("1 sympy_name", "ArcCsc", [0.1]),		# sympy returns nan
    ("1 sympy_name", "ArcCsch", [0.1]),
    #("1 sympy_name", "ArcSec", [0.1]),		# sympy returns nan
    ("1 sympy_name", "ArcSech", [0.1]),
    ("1 sympy_name", "ArcSin", [0.1]),
    ("1 sympy_name", "ArcSinh", [0]),
    ("1 sympy_name", "ArcTan", [0]),
    ("1 sympy_name", "ArcTanh", [0]),
    ("1 sympy_name", "Arg", [0]),
    #("1 sympy_name", "BellB", [0]),		# not defined
    ("1 sympy_name", "BernoulliB", [0]),	# scipy
    ("1 sympy_name", "BesselI", [0,0]),		# scipy
    #("1 sympy_name", "BesselJ", [0,0]),	# not defined
    #("1 sympy_name", "BesselJZero", [1,1]),	# may need https://github.com/bdlucas1/mathics-core/pull/8
    #("1 sympy_name", "BesselK", [0,0]),	# not defined
    #("1 sympy_name", "BesselY", [0,0]),	# not defined
    #("1 sympy_name", "BesselYZero", [2,2]),	# # may need https://github.com/bdlucas1/mathics-core/pull/8
    ("1 sympy_name", "Beta", [0.5, 1], 1e-15),
    ("1 sympy_name", "Binomial", [3, 0.5], 1e-15),
    ("1 sympy_name", "Catalan", None),
    ("1 sympy_name", "CatalanNumber", [0]),
    ("1 sympy_name", "Ceiling", [0]),
    #("1 sympy_name", "ChebyshevT", [0,1]),	# not defined
    #("1 sympy_name", "ChebyshevU", [0,1]),	# not defined
    #("1 sympy_name", "ClebschGordan", [0,1]),	# args are complicated
    #("1 sympy_name", "ComplexExpand", [0]),
    #("1 sympy_name", "ComplexInfinity", None),	# constant infinity = figure out how to handle
    #("1 sympy_name", "ConditionalExpression", [1,True]),	# error compling - may need PR?
    ("1 sympy_name", "Conjugate", [0]),
    #("1 sympy_name", "ContinuedFraction", [0]),	# needs more investigation
    ("1 sympy_name", "Cos", [0]),
    ("1 sympy_name", "Cosh", [0]),
    ("1 sympy_name", "Cot", [1]),
    ("1 sympy_name", "Coth", [1]),
    ("1 sympy_name", "Csc", [1]),
    #("1 sympy_name", "Curl", [0]),		# is this really numeric?
    #("1 sympy_name", "D", [0]),		# is this really numeric
    ("1 sympy_name", "Degree", None),
    #("1 sympy_name", "Derivative", [0]),	# is this really numeric
    #("1 sympy_name", "DirectedInfinity", [0]),	# infinity - how to handle
    #("1 sympy_name", "DivisorSigma", [1,20]),	# not defined
    ("1 sympy_name", "E", None),
    #("1 sympy_name", "Eigenvalues", [0]),	# complicated

    # STOPPED HERE
    ("1 sympy_name", "EllipticE", [0]),
    ("1 sympy_name", "EllipticF", [0]),
    ("1 sympy_name", "EllipticK", [0]),
    ("1 sympy_name", "EllipticPi", [0]),
    ("1 sympy_name", "Equal", [0]),
    ("1 sympy_name", "Erf", [0]),
    ("1 sympy_name", "Erfc", [0]),
    ("1 sympy_name", "EulerE", [0]),
    ("1 sympy_name", "EulerGamma", [0]),
    ("1 sympy_name", "EulerPhi", [0]),
    ("1 sympy_name", "Exp", [0]),
    ("1 sympy_name", "ExpIntegralE", [0]),
    ("1 sympy_name", "ExpIntegralEi", [0]),
    ("1 sympy_name", "Factorial", [0]),
    ("1 sympy_name", "Factorial2", [0]),
    ("1 sympy_name", "Fibonacci", [0]),
    ("1 sympy_name", "Floor", [0]),
    ("1 sympy_name", "FresnelC", [0]),
    ("1 sympy_name", "FresnelS", [0]),
    ("1 sympy_name", "FromContinuedFraction", [0]),
    ("1 sympy_name", "Function", [0]),
    ("1 sympy_name", "Gamma", [0]),
    ("1 sympy_name", "GegenbauerC", [0]),
    ("1 sympy_name", "GoldenRatio", [0]),
    ("1 sympy_name", "Greater", [0]),
    ("1 sympy_name", "GreaterEqual", [0]),
    ("1 sympy_name", "HankelH1", [0]),
    ("1 sympy_name", "HankelH2", [0]),
    ("1 sympy_name", "HarmonicNumber", [0]),
    ("1 sympy_name", "Haversine", [0]),
    ("1 sympy_name", "HermiteH", [0]),
    ("1 sympy_name", "Hypergeometric1F1", [0]),
    ("1 sympy_name", "Hypergeometric2F1", [0]),
    ("1 sympy_name", "HypergeometricPFQ", [0]),
    ("1 sympy_name", "HypergeometricU", [0]),
    ("1 sympy_name", "I", [0]),
    ("1 sympy_name", "Im", [0]),
    ("1 sympy_name", "Indeterminate", [0]),
    ("1 sympy_name", "Infinity", [0]),
    ("1 sympy_name", "Integrate", [0]),
    ("1 sympy_name", "InverseErf", [0]),
    ("1 sympy_name", "InverseErfc", [0]),
    ("1 sympy_name", "InverseHaversine", [0]),
    ("1 sympy_name", "JacobiP", [0]),
    ("1 sympy_name", "KelvinBei", [0]),
    ("1 sympy_name", "KelvinBer", [0]),
    ("1 sympy_name", "KelvinKei", [0]),
    ("1 sympy_name", "KelvinKer", [0]),
    ("1 sympy_name", "KroneckerProduct", [0]),
    ("1 sympy_name", "LaguerreL", [0]),
    ("1 sympy_name", "LambertW", [0]),
    ("1 sympy_name", "LegendreP", [0]),
    ("1 sympy_name", "LegendreQ", [0]),
    ("1 sympy_name", "LerchPhi", [0]),
    ("1 sympy_name", "Less", [0]),
    ("1 sympy_name", "LessEqual", [0]),
    ("1 sympy_name", "Log", [0]),
    ("1 sympy_name", "LogGamma", [0]),
    ("1 sympy_name", "LucasL", [0]),
    ("1 sympy_name", "MeijerG", [0]),
    ("1 sympy_name", "MersennePrimeExponent", [0]),
    ("1 sympy_name", "ModularInverse", [0]),
    ("1 sympy_name", "MoebiusMu", [0]),
    ("1 sympy_name", "PartitionsP", [0]),
    ("1 sympy_name", "PauliMatrix", [0]),
    ("1 sympy_name", "Pi", [0]),
    ("1 sympy_name", "Piecewise", [0]),
    ("1 sympy_name", "Plus", [0]),
    ("1 sympy_name", "Pochhammer", [0]),
    ("1 sympy_name", "PolyGamma", [0]),
    ("1 sympy_name", "PolyLog", [0]),
    ("1 sympy_name", "PossibleZeroQ", [0]),
    ("1 sympy_name", "Power", [0]),
    ("1 sympy_name", "Prime", [0]),
    ("1 sympy_name", "PrimePi", [0]),
    ("1 sympy_name", "PrimeQ", [0]),
    ("1 sympy_name", "Product", [0]),
    ("1 sympy_name", "ProductLog", [0]),
    ("1 sympy_name", "Re", [0]),
    ("1 sympy_name", "Root", [0]),
    ("1 sympy_name", "RootSum", [0]),
    ("1 sympy_name", "Sec", [0]),
    ("1 sympy_name", "Sech", [0]),
    ("1 sympy_name", "Sign", [0]),
    ("1 sympy_name", "Sin", [0]),
    ("1 sympy_name", "Sinh", [0]),
    ("1 sympy_name", "SixJSymbol", [0]),
    ("1 sympy_name", "Slot", [0]),
    ("1 sympy_name", "SphericalBesselJ", [0]),
    ("1 sympy_name", "SphericalBesselY", [0]),
    ("1 sympy_name", "SphericalHankelH1", [0]),
    ("1 sympy_name", "SphericalHankelH2", [0]),
    ("1 sympy_name", "SphericalHarmonicY", [0]),
    ("1 sympy_name", "Sqrt", [0]),
    ("1 sympy_name", "StieltjesGamma", [0]),
    ("1 sympy_name", "StirlingS1", [0]),
    ("1 sympy_name", "StirlingS2", [0]),
    ("1 sympy_name", "StruveH", [0]),
    ("1 sympy_name", "StruveL", [0]),
    ("1 sympy_name", "Subfactorial", [0]),
    ("1 sympy_name", "Sum", [0]),
    ("1 sympy_name", "Tan", [0]),
    ("1 sympy_name", "Tanh", [0]),
    ("1 sympy_name", "ThreeJSymbol", [0]),
    ("1 sympy_name", "Times", [0]),
    ("1 sympy_name", "Unequal", [0]),
    ("1 sympy_name", "WeberE", [0]),
    ("1 sympy_name", "Zeta", [0]),
    ("3 mpmath_name", "Glaisher", [0]),
    ("3 mpmath_name", "Khinchin", [0]),
    ("7 num", "$MachineEpsilon", [0]),
    ("7 num", "$MachinePrecision", [0]),
    ("7 num", "$MaxMachineNumber", [0]),
    ("7 num", "$MaxPrecision", [0]),
    ("7 num", "$MinMachineNumber", [0]),
    ("7 num", "$MinPrecision", [0]),
    ("7 num", "$RandomState", [0]),
    ("7 num", "Accuracy", [0]),
    ("7 num", "AnglePath", [0]),
    ("7 num", "Apart", [0]),
    ("7 num", "BitLength", [0]),
    ("7 num", "BrayCurtisDistance", [0]),
    ("7 num", "C", [0]),
    ("7 num", "CanberraDistance", [0]),
    ("7 num", "Cancel", [0]),
    ("7 num", "ChessboardDistance", [0]),
    ("7 num", "Chop", [0]),
    ("7 num", "Coefficient", [0]),
    ("7 num", "CoefficientArrays", [0]),
    ("7 num", "CoefficientList", [0]),
    ("7 num", "Collect", [0]),
    ("7 num", "Complexes", [0]),
    ("7 num", "CosineDistance", [0]),
    ("7 num", "DSolve", [0]),
    ("7 num", "Denominator", [0]),
    ("7 num", "DesignMatrix", [0]),
    ("7 num", "Det", [0]),
    ("7 num", "DigitCount", [0]),
    ("7 num", "DiscreteLimit", [0]),
    ("7 num", "DivisorSum", [0]),
    ("7 num", "Divisors", [0]),
    ("7 num", "Eigensystem", [0]),
    ("7 num", "Eigenvectors", [0]),
    ("7 num", "EuclideanDistance", [0]),
    ("7 num", "Expand", [0]),
    ("7 num", "ExpandAll", [0]),
    ("7 num", "ExpandDenominator", [0]),
    ("7 num", "Exponent", [0]),
    ("7 num", "Factor", [0]),
    ("7 num", "FactorInteger", [0]),
    ("7 num", "FactorTermsList", [0]),
    ("7 num", "FindMaximum", [0]),
    ("7 num", "FindMinimum", [0]),
    ("7 num", "FindRoot", [0]),
    ("7 num", "FittedModel", [0]),
    ("7 num", "FractionalPart", [0]),
    ("7 num", "FromDigits", [0]),
    ("7 num", "FullSimplify", [0]),
    ("7 num", "Gudermannian", [0]),
    ("7 num", "IntegerDigits", [0]),
    ("7 num", "IntegerExponent", [0]),
    ("7 num", "IntegerLength", [0]),
    ("7 num", "IntegerPart", [0]),
    ("7 num", "IntegerPartitions", [0]),
    ("7 num", "IntegerReverse", [0]),
    ("7 num", "IntegerString", [0]),
    ("7 num", "Integers", [0]),
    ("7 num", "Inverse", [0]),
    ("7 num", "InverseGudermannian", [0]),
    ("7 num", "JacobiSymbol", [0]),
    ("7 num", "KroneckerSymbol", [0]),
    ("7 num", "LeastSquares", [0]),
    ("7 num", "Limit", [0]),
    ("7 num", "LinearModelFit", [0]),
    ("7 num", "LinearSolve", [0]),
    ("7 num", "Log10", [0]),
    ("7 num", "Log2", [0]),
    ("7 num", "LogisticSigmoid", [0]),
    ("7 num", "MachinePrecision", [0]),
    ("7 num", "ManhattanDistance", [0]),
    ("7 num", "MantissaExponent", [0]),
    ("7 num", "MatrixExp", [0]),
    ("7 num", "MatrixPower", [0]),
    ("7 num", "MatrixRank", [0]),
    ("7 num", "MinimalPolynomial", [0]),
    ("7 num", "N", [0]),
    ("7 num", "NIntegrate", [0]),
    ("7 num", "Negative", [0]),
    ("7 num", "NextPrime", [0]),
    ("7 num", "NonNegative", [0]),
    ("7 num", "NonPositive", [0]),
    ("7 num", "NullSpace", [0]),
    ("7 num", "NumberDigit", [0]),
    ("7 num", "Numerator", [0]),
    ("7 num", "O", [0]),
    ("7 num", "Overflow", [0]),
    ("7 num", "Positive", [0]),
    ("7 num", "PowerExpand", [0]),
    ("7 num", "PowersRepresentations", [0]),
    ("7 num", "Precision", [0]),
    ("7 num", "PseudoInverse", [0]),
    ("7 num", "QRDecomposition", [0]),
    ("7 num", "Random", [0]),
    ("7 num", "RandomChoice", [0]),
    ("7 num", "RandomComplex", [0]),
    ("7 num", "RandomInteger", [0]),
    ("7 num", "RandomPrime", [0]),
    ("7 num", "RandomReal", [0]),
    ("7 num", "RandomSample", [0]),
    ("7 num", "Rationalize", [0]),
    ("7 num", "RealAbs", [0]),
    ("7 num", "RealDigits", [0]),
    ("7 num", "RealSign", [0]),
    ("7 num", "Reals", [0]),
    ("7 num", "Round", [0]),
    ("7 num", "RowReduce", [0]),
    ("7 num", "SeedRandom", [0]),
    ("7 num", "Series", [0]),
    ("7 num", "SeriesCoefficient", [0]),
    ("7 num", "SeriesData", [0]),
    ("7 num", "Simplify", [0]),
    ("7 num", "SingularValueDecomposition", [0]),
    ("7 num", "Solve", [0]),
    ("7 num", "SquaredEuclideanDistance", [0]),
    ("7 num", "SquaresR", [0]),
    ("7 num", "Together", [0]),
    ("7 num", "Tr", [0]),
    ("7 num", "Undefined", [0]),
    ("7 num", "Underflow", [0]),
    ("7 num", "UnitStep", [0]),
    ("7 num", "Variables", [0]),
]

session = MathicsSession()

def fail(name, msg):
    print(f"{name}: {msg}")
    exit(-1)

for _, name, args, *rest in tests:

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


    eps = rest[0] if len(rest) > 0 else 0

    # run N to get expected
    expected = session.evaluate(n_expr)
    if not hasattr(expected, "to_python") or isinstance(expected.to_python(), (Expression,str)):
        fail(name, f"N fails, returning {expected} - check args") # TODO: messages might be helpful
    else:
        expected = expected.to_python()
        
    # compile 
    try:
        #print("xxx compiling", def_expr)
        expr = session.parse(def_expr)
        fun = compile(session.evaluation, expr, parms)
    except Exception as oops:
        fail(name, oops)

    # try running
    try:
        result = fun(*args)
    except Exception as oops:
        src = inspect.getsource(fun)
        fail(name, f"{oops} while executing:\n{src}")
        
    print("xxx", result, expected, type(expected))
    if not math.isfinite(result) or not math.isfinite(expected) or abs(result - expected) > eps:
        fail(name, f"expected {expected}, got {result}, diff {expected-result}")
    else:
        pass
        #print(f"{name} succeeds: expected {expected.value}, got {result}")

