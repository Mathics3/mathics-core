# cython: language_level=3

"""
Mathematical Constants

Numeric, Arithmetic, or Symbolic constants like Pi, E, or Infinity.
"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.mathematical-constants"

import math
from typing import Optional

import mpmath
import numpy
import sympy

from mathics.core.atoms import NUMERICAL_CONSTANTS, MachineReal, PrecisionReal
from mathics.core.attributes import A_CONSTANT, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin, Predefined, SympyObject
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.number import MACHINE_DIGITS, PrecisionValueError, get_precision, prec
from mathics.core.symbols import Atom, Symbol, strip_context
from mathics.core.systemsymbols import SymbolIndeterminate


def mp_constant(fn: str, d=None) -> mpmath.mpf:
    """
    Return the mpmath constant _fn_ with integer precision _d_.
    """
    if d is None:
        return getattr(mpmath, fn)()
    else:
        # TODO: In some functions like Pi, you can
        # ask for a certain number of digits, but the
        # accuracy will be less than that. Figure out
        # what's up and compensate somehow.

        int_d = prec(d)
        with mpmath.workprec(int_d):
            result = str(getattr(mpmath, fn)(prec=int_d))
            return result


def mp_convert_constant(obj, **kwargs):
    if isinstance(obj, mpmath.ctx_mp_python._constant):
        prec = kwargs.get("prec", None)
        if prec is not None:
            return sympy.Float(obj(prec=prec))
        return sympy.Float(obj)
    return obj


def numpy_constant(name: str, d=None) -> float:
    if d:
        # by mmatera: Here I have a question:
        # 0.0123`2 should be rounded to
        # 0.01 or to 0.0123?
        # (absolute versus relative accuracy)
        val = getattr(numpy, name)
        val = numpy.round(val, d)
        return val
    else:
        return getattr(numpy, name)


def sympy_constant(fn, d=None):
    return getattr(sympy, fn).evalf(n=d)


class _Constant_Common(Predefined):
    is_numeric = True
    attributes = A_CONSTANT | A_PROTECTED | A_READ_PROTECTED
    nargs = {0}
    options = {"Method": "Automatic"}

    def eval_N(self, precision, evaluation):
        "N[%(name)s, precision_?NumericQ]"
        return self.get_constant(precision, evaluation)

    def is_constant(self) -> bool:
        return True

    def get_constant(
        self,
        precision: Optional[BaseElement] = None,
        evaluation: Optional[Evaluation] = None,
    ):
        # first, determine the precision
        d = None
        preference = None
        if evaluation:
            if precision:
                try:
                    d = get_precision(precision, evaluation)
                except PrecisionValueError:
                    pass

            preflist = evaluation._preferred_n_method.copy()
            while preflist:
                pref_method = preflist.pop()
                if pref_method in ("numpy", "mpmath", "sympy"):
                    preference = pref_method
                    break

        if d is None:
            d = MACHINE_DIGITS

        # If preference not especified, determine it
        # from the precision.
        if preference is None:
            if d <= MACHINE_DIGITS:
                preference = "numpy"
            else:
                preference = "mpmath"

        # Try to determine the numeric value
        value = None
        if preference == "mpmath" and not hasattr(self, "mpmath_name"):
            preference = "numpy"
        elif preference == "sympy" and not hasattr(self, "sympy_name"):
            preference = "numpy"

        if preference == "numpy" and not hasattr(self, "numpy_name"):
            if hasattr(self, "sympy_name"):
                preference = "sympy"
            elif hasattr(self, "mpmath_name"):
                preference = "mpmath"
            else:
                preference = ""

        if preference == "numpy":
            if d == MACHINE_DIGITS:
                try:
                    return NUMERICAL_CONSTANTS[self.symbol]
                except KeyError:
                    value = MachineReal(numpy_constant(self.numpy_name))
                    NUMERICAL_CONSTANTS[self.symbol] = value
                    return value
            value = numpy_constant(self.numpy_name)
        if preference == "sympy":
            value = sympy_constant(self.sympy_name, d + 2)
        if preference == "mpmath":
            value = mp_constant(self.mpmath_name, d * 2)
        if value:
            return PrecisionReal(sympy.Float(str(value), d))
        # If the value is not available, return none
        # and keep it unevaluated.
        return


class _MPMathConstant(_Constant_Common):
    """Representation of a constant in mpmath, e.g. Pi, E, I, etc."""

    # Subclasses should define this.
    mpmath_name = None

    mathics_to_mpmath = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.mpmath_name is None:
            self.mpmath_name = strip_context(self.get_name()).lower()
        self.mathics_to_mpmath[self.__class__.__name__] = self.mpmath_name

    def to_mpmath(self, args):
        if self.mpmath_name is None or len(args) != 0:
            return None
        return getattr(mpmath, self.mpmath_name)


class _NumpyConstant(_Constant_Common):
    """Representation of a constant in numpy, e.g. Pi, E, etc."""

    # Subclasses should define this.
    numpy_name = None

    mathics_to_numpy = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.numpy_name is None:
            self.numpy_name = strip_context(self.symbol.name).lower()
        self.mathics_to_numpy[self.__class__.__name__] = self.numpy_name
        try:
            value_float = numpy_constant(self.numpy_name)
        except AttributeError:
            value_float = self.to_numpy(self.symbol)
        NUMERICAL_CONSTANTS[self.symbol] = MachineReal(value_float)

    def to_numpy(self, args):
        return NUMERICAL_CONSTANTS[self.symbol]


class _SympyConstant(_Constant_Common, SympyObject):
    """Representation of a constant in Sympy, e.g. Pi, E, I, Catalan, etc."""

    # Subclasses should define this.
    sympy_name = None

    def to_sympy(self, expr=None, **kwargs):
        if expr is None or isinstance(expr, Atom):
            result = getattr(sympy, self.sympy_name)
            if kwargs.get("evaluate", False):
                result = mp_convert_constant(result, **kwargs)
            return result
        else:
            # there is no "native" SymPy expression for e.g. E[x]
            return None


class Catalan(_MPMathConstant, _SympyConstant):
    """
    <url>
    :Catalan's constant:
    https://en.wikipedia.org/wiki/Catalan%27s_constant</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.Catalan</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/Catalan.html</url>)

    <dl>
      <dt>'Catalan'
      <dd>is Catalan's constant with numerical value \u2243 0.915966.
    </dl>

    >> Catalan // N
     = 0.915966

    >> N[Catalan, 20]
     = 0.91596559417721901505
    """

    mpmath_name = "catalan"
    # numpy_name = "catalan"  ## This is not defined in numpy
    sympy_name = "Catalan"
    summary_text = "Catalan's constant C ≃ 0.916"


class ComplexInfinity(_SympyConstant):
    """
    <url>
    :Complex Infinity:
    https://en.wikipedia.org/wiki/Infinity#Complex_analysis</url> \
    is an infinite number in the complex plane whose complex argument \
    is unknown or undefined. (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.ComplexInfinity</url>, <url>
    :MathWorld:
    https://mathworld.wolfram.com/ComplexInfinity.html</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ComplexInfinity.html</url>)

    <dl>
      <dt>'ComplexInfinity'
      <dd>represents an infinite complex quantity of undetermined direction.
    </dl>

    ComplexInfinity can appear as the result of a computation such as dividing by zero:
    >> 1 / 0
     : Infinite expression 1 / 0 encountered.
     = ComplexInfinity

    But it can be used as an explicit value in an expression:
    >> 1 / ComplexInfinity
     = 0

    >> ComplexInfinity * Infinity
     = ComplexInfinity

    ComplexInfinity though is a special case of DirectedInfinity:
    >> FullForm[ComplexInfinity]
     = DirectedInfinity[]

    See also <url>
    :'DirectedInfinity':
    /doc/reference-of-built-in-symbols/mathematical-functions/directedinfinity/</url>.
    """

    summary_text = "infinite complex quantity of undetermined direction"
    sympy_name = "zoo"

    rules = {
        "ComplexInfinity": "DirectedInfinity[]",
    }


class Degree(_MPMathConstant, _NumpyConstant, _SympyConstant):
    """
    <url>
    :Degree (angle):
    https://en.wikipedia.org/wiki/Degree_(angle)</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/Degree.html</url>)

    <dl>
      <dt>'Degree'
      <dd>is the number of radians in one degree. It has a numerical value of \u03c0 / 180.
    </dl>

    >> Cos[60 Degree]
     = 1 / 2

    Degree has the value of Pi / 180
    >> Degree == Pi / 180
     = True

    >> N[\\[Degree]] == N[Degree]
     = True
    """

    summary_text = "conversion factor from radians to degrees"
    mpmath_name = "degree"

    def to_sympy(self, expr=None, **kwargs):
        if expr is Symbol("System`Degree"):
            # return mpmath.degree
            return sympy.pi / 180

    def to_numpy(self, expr=None, **kwargs):
        if expr is Symbol("System`Degree"):
            # return mpmath.degree
            return numpy.pi / 180

    def eval_N(self, precision, evaluation):
        "N[Degree, precision_]"
        try:
            if precision:
                d = get_precision(precision, evaluation)
            else:
                d = get_precision(Symbol("System`MachinePrecision"), evaluation)
        except PrecisionValueError:
            return

        # FIXME: There are all sorts of interactions between in the trig functions,
        # that are expected to work out right. Until we have conversion between
        # mpmath and sympy worked out so that values can be made the to the same
        # precision and compared. we have to not use mpmath right now.
        # return self.get_constant(precision, evaluation, preference="mpmath")

        if d is None:
            return MachineReal(math.pi / 180)
        else:
            return PrecisionReal((sympy.pi / 180).n(d))


class E(_MPMathConstant, _NumpyConstant, _SympyConstant):
    """
    <url>
    :Euler's number:
    https://en.wikipedia.org/wiki/E_(mathematical_constant)</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#exp1</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/E.html</url>)

    <dl>
      <dt>'E'
      <dd>is the constant \u2107 with numerical value \u2243 2.71828.
    </dl>

    >> N[E]
     = 2.71828
    >> N[E, 50]
     = 2.7182818284590452353602874713526624977572470937000
    """

    summary_text = "exponential constant E ≃ 2.7182"
    mpmath_name = "e"
    numpy_name = "e"
    sympy_name = "E"

    def eval_N(self, precision, evaluation):
        "N[E, precision_]"
        return self.get_constant(precision, evaluation)


class EulerGamma(_MPMathConstant, _NumpyConstant, _SympyConstant):
    """
    <url>
    :Euler's constant:
    https://en.wikipedia.org/wiki/Euler%27s_constant</url> (<url>
    :SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.EulerGamma</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/EulerGamma.html</url>)

    <dl>
      <dt>'EulerGamma'
      <dd>is Euler's constant \u03b3 with numerical value \u2243 0.577216.
    </dl>

    >> EulerGamma // N
     = 0.577216

    >> N[EulerGamma, 40]
     = 0.5772156649015328606065120900824024310422
    """

    summary_text = "Euler's constant γ ≃ 0.5772"
    mpmath_name = "euler"
    numpy_name = "euler_gamma"
    sympy_name = "EulerGamma"


class Glaisher(_MPMathConstant):
    """
    <url>
    :Glaisher–Kinkelin constant:
    https://en.wikipedia.org/wiki/Glaisher%E2%80%93Kinkelin_constant</url> (<url>
    :mpmath:
    https://mpmath.org/doc/current/functions/constants.html#glaisher-s-constant-glaisher</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Glaisher.html</url>)
    <dl>
      <dt>'Glaisher'
      <dd>is Glaisher's constant, with numerical value \u2243 1.28243.
    </dl>

    >> N[Glaisher]
     = 1.28243
    >> N[Glaisher, 50]
     = 1.2824271291006226368753425688697917277676889273250
     # 1.2824271291006219541941391071304678916931152343750
    """

    summary_text = "Glaisher's constant A ≃ 1.282"
    mpmath_name = "glaisher"


class GoldenRatio(_MPMathConstant, _SympyConstant):
    """
    <url>
    :Golden ratio:
    https://en.wikipedia.org/wiki/Golden_ratio</url> (<url>
    :mpmath:
    https://mpmath.org/doc/current/functions/constants.html#golden-ratio-phi</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/GoldenRatio.html</url>)

    <dl>
      <dt>'GoldenRatio'
      <dd>is the golden ratio, \u03D5 = (1+Sqrt[5])/2.
    </dl>

    >> GoldenRatio // N
     = 1.61803
    >> N[GoldenRatio, 40]
     = 1.618033988749894848204586834365638117720
    """

    summary_text = "golden ratio φ ≃ 1.6180"
    sympy_name = "GoldenRatio"
    mpmath_name = "phi"


class Indeterminate(_SympyConstant):
    """
    <url>
    :Indeterminate form:
    https://en.wikipedia.org/wiki/Indeterminate_form</url> (<url>
    :SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.NaN</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Indeterminate.html</url>)

    <dl>
      <dt>'Indeterminate'
      <dd>represents an indeterminate result.
    </dl>

    >> 0^0
     : Indeterminate expression 0 ^ 0 encountered.
     = Indeterminate

    >> Tan[Indeterminate]
     = Indeterminate
    """

    summary_text = "indeterminate value"
    sympy_name = "nan"

    def eval_N(self, precision, evaluation, options={}):
        "N[%(name)s, precision_?NumericQ, OptionsPattern[%(name)s]]"
        return SymbolIndeterminate


class Infinity(_SympyConstant):
    """
    <url>:
    Infinity:
    https://en.wikipedia.org/wiki/Infinity</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.Infinity</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Infinity.html</url>)

    <dl>
      <dt>'Infinity'
      <dd>a symbol that represents an infinite real quantity.
    </dl>

    'Infinity' sometimes appears as the result of a calculation:
    >> Precision[1]
     = Infinity

    But 'Infinity' it often used as a value in expressions:
    >> 1 / Infinity
     = 0

    >> Infinity + 100
     = Infinity

    'Infinity' often appears in sum and limit calculations:
    >> Sum[1/x^2, {x, 1, Infinity}]
     = Pi ^ 2 / 6

    >> Limit[1/x, x->0]
     = -Infinity

    However, 'Infinity' a shorthand for 'DirectedInfinity[1]':
    >> FullForm[Infinity]
     = DirectedInfinity[1]

    See also <url>
    :'DirectedInfinity':
    /doc/reference-of-built-in-symbols/mathematical-functions/directedinfinity/</url>.
    """

    sympy_name = "oo"
    numpy_name = "Inf"
    mpmath_name = "inf"
    python_equivalent = math.inf
    summary_text = "infinite real quantity"
    rules = {
        "Infinity": "DirectedInfinity[1]",
        "MakeBoxes[Infinity, f:StandardForm|TraditionalForm]": ('"\\[Infinity]"'),
    }


class Khinchin(_MPMathConstant):
    """
    <url>
    :Khinchin's constant:
    https://en.wikipedia.org/wiki/Khinchin%27s_constant</url> (<url>
    :mpmath:
    https://mpmath.org/doc/current/functions/constants.html#mpmath.mp.khinchin</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Khinchin.html</url>)

    <dl>
      <dt>'Khinchin'
      <dd>is Khinchin's constant, with numerical value \u2243 2.68545.
    </dl>

    >> N[Khinchin]
     = 2.68545
    >> N[Khinchin, 50]
     = 2.6854520010653064453097148354817956938203822939945
     # = 2.6854520010653075701156922150403261184692382812500
    """

    summary_text = "Khinchin's constant K ≃ 2.6854"
    mpmath_name = "khinchin"


class Overflow(Builtin):
    """
    Numeric Overflow (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/Overflow.html
    </url>)

    See also <url>
    :Integer Overflow:
    <https://en.wikipedia.org/wiki/Integer_overflow></url>.

    <dl>
      <dt>'Overflow[]'
      <dd>represents a number too large to be represented by Mathics.
    </dl>

    >> Exp[10.*^20]
     : Overflow occurred in computation.
     = Overflow[]
    >> Table[Exp[10.^k],{k, 3}]
     : Overflow occurred in computation.
     = {22026.5, 2.68812×10^43, Overflow[]}
    >> 1 / Underflow[]
     = Overflow[]
    """

    rules = {
        "Power[Overflow[], -1]": "Underflow[]",
    }
    summary_text = "overflow in numeric evaluation"


class MaxMachineNumber(Predefined):
    """
    Largest normalizable machine number (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/$MaxMachineNumber.html
    </url>)

    <dl>
      <dt>'$MaxMachineNumber'
      <dd>Represents the largest positive number that can be represented \
          as a normalized machine number in the system.
    </dl>

    The product of '$MaxMachineNumber' and  '$MinMachineNumber' is a constant:
    >> $MaxMachineNumber * $MinMachineNumber
     = 4.

    """

    name = "$MaxMachineNumber"
    summary_text = "largest normalized positive machine number"

    def evaluate(self, evaluation: Evaluation) -> MachineReal:
        return NUMERICAL_CONSTANTS[self.symbol]


class MinMachineNumber(Predefined):
    """
    Smallest normalizable machine number (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/$MinMachineNumber.html
    </url>)

    <dl>
      <dt>'$MinMachineNumber'
      <dd>Represents the smallest positive number that can be represented \
          as a normalized machine number in the system.
    </dl>

    'MachinePrecision' minus the 'Log' base 10 of this number is the\
    'Accuracy' of 0`:
    >> MachinePrecision -Log[10., $MinMachineNumber]==Accuracy[0`]
     = True

    """

    name = "$MinMachineNumber"
    summary_text = "smallest normalized positive machine number"

    def evaluate(self, evaluation: Evaluation) -> MachineReal:
        return NUMERICAL_CONSTANTS[self.symbol]


class Pi(_MPMathConstant, _NumpyConstant, _SympyConstant):
    """
    <url>
    :Pi, \u03c0: https://en.wikipedia.org/wiki/Pi</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.Pi</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Pi.html</url>)

    <dl>
      <dt>'Pi'
      <dd>is the constant \u03c0.
    </dl>

    >> Pi
     = Pi

    >> N[Pi]
     = 3.14159

    Pi to a numeric precision of 20 digits:
    >> N[Pi, 20]
     = 3.1415926535897932385

    Note that the above is not the same thing as the number of digits <i>after</i> the decimal point. This may differ from similar concepts from other mathematical libraries, including those which Mathics uses!

    Use numpy to compute Pi to 20 digits:
    >> N[Pi, 20, Method->"numpy"]
     = 3.1415...

    "sympy" is the default method.

    >> Attributes[Pi]
     = {Constant, Protected, ReadProtected}
    """

    mpmath_name = "pi"
    numpy_name = "pi"
    rules = {"MakeBoxes[Pi,(StandardForm|TraditionalForm)]": '"\\[Pi]"'}
    summary_text = "Pi, \u03c0 ≃ 3.1416"
    sympy_name = "pi"


class Undefined(Builtin):
    """
    Undefined symbol/value (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/Undefined.html</url>)

    <dl>
      <dt>'Undefined'
      <dd>a symbol that represents a quantity with no defined value.
    </dl>

    >> ConditionalExpression[a, False]
     = Undefined
    >> Attributes[Undefined]
     = {Protected}
    """

    attributes = A_PROTECTED
    summary_text = "undefined value"


class Underflow(Builtin):
    """
    <url>:Arithmetic underflow:
    https://en.wikipedia.org/wiki/Arithmetic_underflow</url> (<url>
    :WMA: https://reference.wolfram.com/language/ref/Underflow.html</url>)

    <dl>
      <dt>'Overflow[]'
      <dd>represents a number too small to be represented by Mathics.
    </dl>

    >> 1 / Overflow[]
     = Underflow[]
    >> 5 * Underflow[]
     = 5 Underflow[]
    >> % // N
     = 0.
    Underflow[] is kept symbolic in operations against integer numbers,
    but taken as 0. in numeric evaluations:
    >> 1 - Underflow[]
     = 1 - Underflow[]
    >> % // N
     = 1.
    """

    #
    # TODO: handle this kind of expressions where precision may be
    # lost:
    # >> Exp[-1000.]
    #  : Exp[-1000.] is too small to represent as a normalized machine number; precision may be lost.
    #  = Underflow[]

    rules = {
        "Power[Underflow[], -1]": "Overflow[]",
        "x_Real + Underflow[]": "x",
        "Underflow[] * x_Real": "0.",
    }
    summary_text = "underflow in numeric evaluation"


# Constants that are not numpy constants,
for cls in (Catalan, Degree, Glaisher, GoldenRatio, Khinchin):
    instance = cls(expression=False)
    val = instance.get_constant()
    NUMERICAL_CONSTANTS[instance.symbol] = MachineReal(val.value)
