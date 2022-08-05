# cython: language_level=3

"""
Mathematical Constants

Numeric, Arithmetic, or Symbolic constants like Pi, E, or Infinity.
"""

# This tells documentation how to sort this module
sort_order = "mathics.builtin.mathematical-constants"


import math
import mpmath
import numpy
import sympy


from mathics.builtin.base import Builtin, Predefined, SympyObject

from mathics.core.atoms import (
    MachineReal,
    PrecisionReal,
)
from mathics.core.attributes import constant, protected, read_protected
from mathics.core.number import get_precision, PrecisionValueError, machine_precision
from mathics.core.symbols import (
    Atom,
    Symbol,
    strip_context,
)
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
        mpmath.mp.dps = int_d = int(d * 3.321928)
        return getattr(mpmath, fn)(prec=int_d)


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
    attributes = constant | protected | read_protected
    nargs = {0}
    options = {"Method": "Automatic"}

    def apply_N(self, precision, evaluation):
        "N[%(name)s, precision_?NumericQ]"
        return self.get_constant(precision, evaluation)

    def is_constant(self) -> bool:
        return True

    def get_constant(self, precision, evaluation):
        # first, determine the precision
        machine_d = int(0.30103 * machine_precision)
        d = None
        if precision:
            try:
                d = get_precision(precision, evaluation)
            except PrecisionValueError:
                pass

        if d is None:
            d = machine_d

        # If preference not especified, determine it
        # from the precision.
        preference = None
        preflist = evaluation._preferred_n_method.copy()
        while preflist:
            pref_method = preflist.pop()
            if pref_method in ("numpy", "mpmath", "sympy"):
                preference = pref_method
                break

        if preference is None:
            if d <= machine_d:
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
            value = numpy_constant(self.numpy_name)
            if d == machine_d:
                return MachineReal(value)
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
            self.numpy_name = strip_context(self.get_name()).lower()
        self.mathics_to_numpy[self.__class__.__name__] = self.numpy_name

    def to_numpy(self, args):
        if self.numpy_name is None or len(args) != 0:
            return None
        return self.get_constant()


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
    <url>:Catalan's constant: https://en.wikipedia.org/wiki/Catalan%27s_constant</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.Catalan</url>, <url>:WMA: https://reference.wolfram.com/language/ref/Catalan.html</url>)

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
    <url>:Complex Infinity: https://en.wikipedia.org/wiki/Infinity#Complex_analysis</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/core.html?highlight=zoo#complexinfinity</url>, <url>:WMA: https://reference.wolfram.com/language/ref/ComplexInfinity.html</url>)
    <dl>
      <dt>'ComplexInfinity'
      <dd>represents an infinite complex quantity of undetermined direction.
    </dl>

    >> 1 / ComplexInfinity
     = 0
    >> ComplexInfinity * Infinity
     = ComplexInfinity
    >> FullForm[ComplexInfinity]
     = DirectedInfinity[]

    ## Issue689
    #> ComplexInfinity + ComplexInfinity
     : Indeterminate expression ComplexInfinity + ComplexInfinity encountered.
     = Indeterminate
    #> ComplexInfinity + Infinity
     : Indeterminate expression ComplexInfinity + Infinity encountered.
     = Indeterminate
    """

    summary_text = "infinite complex quantity of undetermined direction"
    sympy_name = "zoo"

    rules = {
        "ComplexInfinity": "DirectedInfinity[]",
    }


class Degree(_MPMathConstant, _NumpyConstant, _SympyConstant):
    """
    <url>:Degree (angle): https://en.wikipedia.org/wiki/Degree_(angle)</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Degree.html</url>)

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

    #> Cos[Degree[x]]
     = Cos[Degree[x]]


    #> N[Degree]
     = 0.0174533
    #> N[Degree, 30]
     = 0.0174532925199432957692369076849
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

    def apply_N(self, precision, evaluation):
        "N[Degree, precision_]"
        try:
            if precision:
                d = get_precision(precision, evaluation)
            else:
                d = get_precision(Symbol("System`MachinePrecision"), evaluation)
        except PrecisionValueError:
            return

        # FIXME: There are all sorts of interactions between in the trig functions,
        # that are expected to work out right. Until we have convertion between
        # mpmath and sympy worked out so that values can be made the to the same
        # precision and compared. we have to not use mpmath right now.
        # return self.get_constant(precision, evaluation, preference="mpmath")

        if d is None:
            return MachineReal(math.pi / 180)
        else:
            return PrecisionReal((sympy.pi / 180).n(d))


class E(_MPMathConstant, _NumpyConstant, _SympyConstant):
    """
    <url>:Euler's number: https://en.wikipedia.org/wiki/E_(mathematical_constant)</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/core.html#exp1</url>, <url>:WMA: https://reference.wolfram.com/language/ref/E.html</url>)

    <dl>
      <dt>'E'
      <dd>is the constant \u2107 with numerical value \u2243 2.71828.
    </dl>

    >> N[E]
     = 2.71828
    >> N[E, 50]
     = 2.7182818284590452353602874713526624977572470937000

    #> 5. E
     = 13.5914
    """

    summary_text = "exponential constant E ≃ 2.7182"
    mpmath_name = "e"
    numpy_name = "e"
    sympy_name = "E"

    def apply_N(self, precision, evaluation):
        "N[E, precision_]"
        return self.get_constant(precision, evaluation)


class EulerGamma(_MPMathConstant, _NumpyConstant, _SympyConstant):
    """
    <url>:Euler's constant: https://en.wikipedia.org/wiki/Euler%27s_constant</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.EulerGamma</url>, <url>:WMA: https://reference.wolfram.com/language/ref/EulerGamma.html</url>)

    <dl>
      <dt>'EulerGamma'
      <dd>is Euler's constant \u03b3 with numerial value \u2243 0.577216.
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
    <url>:Glaisher–Kinkelin constant: https://en.wikipedia.org/wiki/Glaisher%E2%80%93Kinkelin_constant</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/constants.html#glaisher-s-constant-glaisher</url>, <url>:WMA: https://reference.wolfram.com/language/ref/Glaisher.html</url>)
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
    <url>:Golden ratio: https://en.wikipedia.org/wiki/Golden_ratio</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/constants.html#golden-ratio-phi</url>, <url>:WMA: https://reference.wolfram.com/language/ref/GoldenRatio.html</url>)

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
    <url>:Indeterminate form: https://en.wikipedia.org/wiki/Indeterminate_form</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.NaN</url>, <url>:WMA: https://reference.wolfram.com/language/ref/Indeterminate.html</url>)
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

    def apply_N(self, precision, evaluation, options={}):
        "N[%(name)s, precision_?NumericQ, OptionsPattern[%(name)s]]"
        return SymbolIndeterminate


class Infinity(_SympyConstant):
    """
    <url>:Infinity: https://en.wikipedia.org/wiki/Infinity</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.Infinity</url>, <url>:WMA: https://reference.wolfram.com/language/ref/Infinity.html</url>)

    <dl>
      <dt>'Infinity'
      <dd>a symbol that represents an infinite real quantity.
    </dl>

    >> 1 / Infinity
     = 0
    >> Infinity + 100
     = Infinity

    Use 'Infinity' in sum and limit calculations:
    >> Sum[1/x^2, {x, 1, Infinity}]
     = Pi ^ 2 / 6

    #> FullForm[Infinity]
     = DirectedInfinity[1]
    #> (2 + 3.5*I) / Infinity
     = 0.
    #> Infinity + Infinity
     = Infinity
    #> Infinity / Infinity
     : Indeterminate expression 0 Infinity encountered.
     = Indeterminate
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
    <url>:Khinchin's constant: https://en.wikipedia.org/wiki/Khinchin%27s_constant</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/constants.html#mpmath.mp.khinchin</url>, <url>:WMA: https://reference.wolfram.com/language/ref/Khinchin.html</url>)
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
    Overflow (<url>:WMA: https://reference.wolfram.com/language/ref/Overflow.html</url>)

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


class Pi(_MPMathConstant, _SympyConstant):
    """
    <url>:Pi, \u03c0: https://en.wikipedia.org/wiki/Pi</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.Pi</url>, <url>:WMA: https://reference.wolfram.com/language/ref/Pi.html</url>)

    <dl>
      <dt>'Pi'
      <dd>is the constant \u03c0.
    </dl>

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


class Underflow(Builtin):
    """
    <url>:Arithmetic underflow: https://en.wikipedia.org/wiki/Arithmetic_underflow</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Underflow.html</url>)

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
