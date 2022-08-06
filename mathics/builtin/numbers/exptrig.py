# -*- coding: utf-8 -*-

"""
Exponential and Trigonometric Functions

Numerical values and derivatives can be computed; however, most special exact values and simplification rules are not implemented yet.
"""

import math
import mpmath

from collections import namedtuple
from contextlib import contextmanager
from itertools import chain

from mathics.builtin.arithmetic import _MPMathFunction
from mathics.builtin.base import Builtin
from mathics.core.atoms import (
    Integer,
    Integer0,
    IntegerM1,
    Real,
)
from mathics.core.attributes import listable, numeric_function, protected
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolPower
from mathics.core.systemsymbols import SymbolCos, SymbolE, SymbolSin

SymbolArcCos = Symbol("ArcCos")
SymbolArcSin = Symbol("ArcSin")
SymbolArcTan = Symbol("ArcTan")


class Fold:
    # allows inherited classes to specify a single algorithm implementation that
    # can be called with machine precision, arbitrary precision or symbolically.

    ComputationFunctions = namedtuple("ComputationFunctions", ("sin", "cos"))

    FLOAT = 0
    MPMATH = 1
    SYMBOLIC = 2

    math = {
        FLOAT: ComputationFunctions(
            cos=math.cos,
            sin=math.sin,
        ),
        MPMATH: ComputationFunctions(
            cos=mpmath.cos,
            sin=mpmath.sin,
        ),
        SYMBOLIC: ComputationFunctions(
            cos=lambda x: Expression(SymbolCos, x),
            sin=lambda x: Expression(SymbolSin, x),
        ),
    }

    operands = {
        FLOAT: lambda x: None if x is None else x.round_to_float(),
        MPMATH: lambda x: None if x is None else x.to_mpmath(),
        SYMBOLIC: lambda x: x,
    }

    def _operands(self, state, steps):
        raise NotImplementedError

    def _fold(self, state, steps, math):
        raise NotImplementedError

    def _spans(self, operands):
        spans = {}
        k = 0
        j = 0

        for mode in (self.FLOAT, self.MPMATH):
            for i, operand in enumerate(operands[k:]):
                if operand[0] > mode:
                    break
                j = i + k + 1

            if k == 0 and j == 1:  # only init state? then ignore.
                j = 0

            spans[mode] = slice(k, j)
            k = j

        spans[self.SYMBOLIC] = slice(k, len(operands))

        return spans

    def fold(self, x, ll):
        # computes fold(x, ll) with the internal _fold function. will start
        # its evaluation machine precision, and will escalate to arbitrary
        # precision if or symbolical evaluation only if necessary. folded
        # items already computed are carried over to new evaluation modes.

        yield x  # initial state

        init = None
        operands = list(self._operands(x, ll))
        spans = self._spans(operands)

        for mode in (self.FLOAT, self.MPMATH, self.SYMBOLIC):
            s_operands = [y[1:] for y in operands[spans[mode]]]

            if not s_operands:
                continue

            if mode == self.MPMATH:
                from mathics.core.number import min_prec

                precision = min_prec(*[t for t in chain(*s_operands) if t is not None])
                working_precision = mpmath.workprec
            else:

                @contextmanager
                def working_precision(_):
                    yield

                precision = None

            if mode == self.FLOAT:

                def out(z):
                    return Real(z)

            elif mode == self.MPMATH:

                def out(z):
                    return Real(z, precision)

            else:

                def out(z):
                    return z

            as_operand = self.operands.get(mode)

            def converted_operands():
                for y in s_operands:
                    yield tuple(as_operand(t) for t in y)

            with working_precision(precision):
                c_operands = converted_operands()

                if init is not None:
                    c_init = tuple(
                        (None if t is None else as_operand(from_python(t)))
                        for t in init
                    )
                else:
                    c_init = next(c_operands)
                    init = tuple((None if t is None else out(t)) for t in c_init)

                generator = self._fold(c_init, c_operands, self.math.get(mode))

                for y in generator:
                    y = tuple(out(t) for t in y)
                    yield y
                    init = y


class AnglePath(Builtin):
    """
    <dl>
    <dt>'AnglePath[{$phi1$, $phi2$, ...}]'
        <dd>returns the points formed by a turtle starting at {0, 0} and angled at 0 degrees going through
        the turns given by angles $phi1$, $phi2$, ... and using distance 1 for each step.
    <dt>'AnglePath[{{$r1$, $phi1$}, {$r2$, $phi2$}, ...}]'
        <dd>instead of using 1 as distance, use $r1$, $r2$, ... as distances for the respective steps.
    <dt>'AnglePath[$phi0$, {$phi1$, $phi2$, ...}]'
        <dd>starts with direction $phi0$ instead of 0.
    <dt>'AnglePath[{$x$, $y$}, {$phi1$, $phi2$, ...}]'
        <dd>starts at {$x, $y} instead of {0, 0}.
    <dt>'AnglePath[{{$x$, $y$}, $phi0$}, {$phi1$, $phi2$, ...}]'
        <dd>specifies initial position {$x$, $y$} and initial direction $phi0$.
    <dt>'AnglePath[{{$x$, $y$}, {$dx$, $dy$}}, {$phi1$, $phi2$, ...}]'
        <dd>specifies initial position {$x$, $y$} and a slope {$dx$, $dy$} that is understood to be the
        initial direction of the turtle.
    </dl>

    >> AnglePath[{90 Degree, 90 Degree, 90 Degree, 90 Degree}]
     = {{0, 0}, {0, 1}, {-1, 1}, {-1, 0}, {0, 0}}

    >> AnglePath[{{1, 1}, 90 Degree}, {{1, 90 Degree}, {2, 90 Degree}, {1, 90 Degree}, {2, 90 Degree}}]
     = {{1, 1}, {0, 1}, {0, -1}, {1, -1}, {1, 1}}

    >> AnglePath[{a, b}]
     = {{0, 0}, {Cos[a], Sin[a]}, {Cos[a] + Cos[a + b], Sin[a] + Sin[a + b]}}

    >> Precision[Part[AnglePath[{N[1/3, 100], N[2/3, 100]}], 2, 1]]
     = 100.

    >> Graphics[Line[AnglePath[Table[1.7, {50}]]]]
     = -Graphics-

    >> Graphics[Line[AnglePath[RandomReal[{-1, 1}, {100}]]]]
     = -Graphics-
    """

    summary_text = 'form a path from a sequence of "turtle-like" turns and motions'
    messages = {"steps": "`1` is not a valid description of steps."}

    @staticmethod
    def _compute(x0, y0, phi0, steps, evaluation):
        if not steps:
            return ListExpression()

        if steps[0].get_head_name() == "System`List":

            def parse(step):
                if step.get_head_name() != "System`List":
                    raise _IllegalStepSpecification
                arguments = step.elements
                if len(arguments) != 2:
                    raise _IllegalStepSpecification
                return arguments

        else:

            def parse(step):
                if step.get_head_name() == "System`List":
                    raise _IllegalStepSpecification
                return None, step

        try:
            fold = AnglePathFold(parse)
            elements = [
                ListExpression(x, y) for x, y, _ in fold.fold((x0, y0, phi0), steps)
            ]
            return ListExpression(*elements)
        except _IllegalStepSpecification:
            evaluation.message("AnglePath", "steps", ListExpression(*steps))

    def apply(self, steps, evaluation):
        "AnglePath[{steps___}]"
        return AnglePath._compute(
            Integer0, Integer0, None, steps.get_sequence(), evaluation
        )

    def apply_phi0(self, phi0, steps, evaluation):
        "AnglePath[phi0_, {steps___}]"
        return AnglePath._compute(
            Integer0, Integer0, phi0, steps.get_sequence(), evaluation
        )

    def apply_xy(self, x, y, steps, evaluation):
        "AnglePath[{x_, y_}, {steps___}]"
        return AnglePath._compute(x, y, None, steps.get_sequence(), evaluation)

    def apply_xy_phi0(self, x, y, phi0, steps, evaluation):
        "AnglePath[{{x_, y_}, phi0_}, {steps___}]"
        return AnglePath._compute(x, y, phi0, steps.get_sequence(), evaluation)

    def apply_xy_dx(self, x, y, dx, dy, steps, evaluation):
        "AnglePath[{{x_, y_}, {dx_, dy_}}, {steps___}]"
        phi0 = Expression(SymbolArcTan, dx, dy)
        return AnglePath._compute(x, y, phi0, steps.get_sequence(), evaluation)


class AnglePathFold(Fold):
    def __init__(self, parse):
        self._parse = parse

    def _operands(self, state, steps):
        SYMBOLIC = self.SYMBOLIC
        MPMATH = self.MPMATH
        FLOAT = self.FLOAT

        def check_pos_operand(x):
            if x is not None:
                if isinstance(x, Integer) and x.get_int_value() in (0, 1):
                    pass
                elif not isinstance(x, Real):
                    return SYMBOLIC
                elif not x.is_machine_precision():
                    return MPMATH
            return FLOAT

        def check_angle_operand(phi):
            if phi is not None:
                if not isinstance(phi, Real):
                    return SYMBOLIC
                elif not phi.is_machine_precision():
                    return MPMATH
            return FLOAT

        parse = self._parse

        x, y, phi = state
        mode = max(check_pos_operand(x), check_pos_operand(y), check_angle_operand(phi))
        yield mode, x, y, phi

        for step in steps:
            distance, delta_phi = parse(step)
            mode = max(check_angle_operand(delta_phi), check_pos_operand(distance))
            yield mode, distance, delta_phi

    def _fold(self, state, steps, math):
        sin = math.sin
        cos = math.cos

        x, y, phi = state

        for distance, delta_phi in steps:
            if phi is None:
                phi = delta_phi
            else:
                phi += delta_phi

            dx = cos(phi)
            dy = sin(phi)

            if distance is not None:
                dx *= distance
                dy *= distance

            x += dx
            y += dy

            yield x, y, phi


class ArcCos(_MPMathFunction):
    """
    <dl>
    <dt>'ArcCos[$z$]'
        <dd>returns the inverse cosine of $z$.
    </dl>

    >> ArcCos[1]
     = 0
    >> ArcCos[0]
     = Pi / 2
    >> Integrate[ArcCos[x], {x, -1, 1}]
     = Pi
    """

    summary_text = "inverse cosine function"
    sympy_name = "acos"
    mpmath_name = "acos"

    rules = {
        "Derivative[1][ArcCos]": "-1/Sqrt[1-#^2]&",
        "ArcCos[0]": "Pi / 2",
        "ArcCos[1]": "0",
    }


class ArcCot(_MPMathFunction):
    """
    <dl>
      <dt>'ArcCot[$z$]'
      <dd>returns the inverse cotangent of $z$.
    </dl>

    >> ArcCot[0]
     = Pi / 2
    >> ArcCot[1]
     = Pi / 4
    """

    summary_text = "inverse cotangent function"
    sympy_name = "acot"
    mpmath_name = "acot"

    rules = {
        "Derivative[1][ArcCot]": "-1/(1+#^2)&",
        "ArcCot[0]": "Pi / 2",
        "ArcCot[1]": "Pi / 4",
    }


class ArcCsc(_MPMathFunction):
    """
    <dl>
      <dt>'ArcCsc[$z$]'
      <dd>returns the inverse cosecant of $z$.
    </dl>

    >> ArcCsc[1]
     = Pi / 2
    >> ArcCsc[-1]
     = -Pi / 2
    """

    summary_text = "inverse cosecant function"
    sympy_name = ""
    mpmath_name = "acsc"

    rules = {
        "Derivative[1][ArcCsc]": "-1 / (Sqrt[1 - 1/#^2] * #^2)&",
        "ArcCsc[0]": "ComplexInfinity",
        "ArcCsc[1]": "Pi / 2",
    }

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            return Expression(
                SymbolArcSin, Expression(SymbolPower, expr.elements[0], Integer(-1))
            ).to_sympy()


class ArcSec(_MPMathFunction):
    """
    <dl>
      <dt>'ArcSec[$z$]'
      <dd>returns the inverse secant of $z$.
    </dl>

    >> ArcSec[1]
     = 0
    >> ArcSec[-1]
     = Pi
    """

    mpmath_name = "asec"

    rules = {
        "Derivative[1][ArcSec]": "1 / (Sqrt[1 - 1/#^2] * #^2)&",
        "ArcSec[0]": "ComplexInfinity",
        "ArcSec[1]": "0",
    }

    summary_text = "inverse secant function"
    sympy_name = ""

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            return Expression(
                SymbolArcCos, Expression(SymbolPower, expr.elements[0], IntegerM1)
            ).to_sympy()


class ArcSin(_MPMathFunction):
    """
    <dl>
    <dt>'ArcSin[$z$]'
        <dd>returns the inverse sine of $z$.
    </dl>

    >> ArcSin[0]
     = 0
    >> ArcSin[1]
     = Pi / 2
    """

    mpmath_name = "asin"

    rules = {
        "Derivative[1][ArcSin]": "1/Sqrt[1-#^2]&",
        "ArcSin[0]": "0",
        "ArcSin[1]": "Pi / 2",
    }

    summary_text = "inverse sine function"
    sympy_name = "asin"


class ArcTan(_MPMathFunction):
    """
    <dl>
    <dt>'ArcTan[$z$]'
        <dd>returns the inverse tangent of $z$.
    </dl>

    >> ArcTan[1]
     = Pi / 4
    >> ArcTan[1.0]
     = 0.785398
    >> ArcTan[-1.0]
     = -0.785398

    >> ArcTan[1, 1]
     = Pi / 4
    #> ArcTan[-1, 1]
     = 3 Pi / 4
    #> ArcTan[1, -1]
     = -Pi / 4
    #> ArcTan[-1, -1]
     = -3 Pi / 4

    #> ArcTan[1, 0]
     = 0
    #> ArcTan[-1, 0]
     = Pi
    #> ArcTan[0, 1]
     = Pi / 2
    #> ArcTan[0, -1]
     = -Pi / 2
    """

    mpmath_name = "atan"

    rules = {
        "ArcTan[1]": "Pi/4",
        "ArcTan[0]": "0",
        "Derivative[1][ArcTan]": "1/(1+#^2)&",
        "ArcTan[x_?RealNumberQ, y_?RealNumberQ]": """If[x == 0, If[y == 0, 0, If[y > 0, Pi/2, -Pi/2]], If[x > 0,
            ArcTan[y/x], If[y >= 0, ArcTan[y/x] + Pi, ArcTan[y/x] - Pi]]]""",
    }

    summary_text = "inverse tangent function"
    sympy_name = "atan"


class Cos(_MPMathFunction):
    """
    <dl>
    <dt>'Cos[$z$]'
        <dd>returns the cosine of $z$.
    </dl>

    >> Cos[3 Pi]
     = -1

    #> Cos[1.5 Pi]
     = -1.83697×10^-16
    """

    mpmath_name = "cos"

    rules = {
        "Cos[Pi]": "-1",
        "Cos[n_Integer * Pi]": "(-1)^n",
        "Cos[(1/2) * Pi]": "0",
        "Cos[0]": "1",
        "Derivative[1][Cos]": "-Sin[#]&",
    }

    summary_text = "cosine function"


class Cot(_MPMathFunction):
    """
    <dl>
      <dt>'Cot[$z$]'
      <dd>returns the cotangent of $z$.
    </dl>

    >> Cot[0]
     = ComplexInfinity
    >> Cot[1.]
     = 0.642093
    """

    mpmath_name = "cot"

    rules = {
        "Derivative[1][Cot]": "-Csc[#]^2&",
        "Cot[0]": "ComplexInfinity",
    }

    summary_text = "cotangent function"


class Csc(_MPMathFunction):
    """
    <dl>
      <dt>'Csc[$z$]'
      <dd>returns the cosecant of $z$.
    </dl>

    >> Csc[0]
     = ComplexInfinity
    >> Csc[1] (* Csc[1] in Mathematica *)
     = 1 / Sin[1]
    >> Csc[1.]
     = 1.1884
    """

    mpmath_name = "csc"

    rules = {
        "Derivative[1][Csc]": "-Cot[#] Csc[#]&",
        "Csc[0]": "ComplexInfinity",
    }

    summary_text = "cosecant function"

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            return Expression(
                SymbolPower, Expression(SymbolSin, expr.elements[0]), Integer(-1)
            ).to_sympy()


class Exp(_MPMathFunction):
    """
    <dl>
      <dt>'Exp[$z$]'
      <dd>returns the exponential function of $z$.
    </dl>

    >> Exp[1]
     = E
    >> Exp[10.0]
     = 22026.5
    >> Exp[x] //FullForm
     = Power[E, x]

    >> Plot[Exp[x], {x, 0, 3}]
     = -Graphics-
    #> Exp[1.*^20]
     : Overflow occurred in computation.
     = Overflow[]
    """

    rules = {
        "Exp[x_]": "E ^ x",
        "Derivative[1][Exp]": "Exp",
    }
    summary_text = "exponential function"

    def from_sympy(self, sympy_name, elements):
        return Expression(SymbolPower, SymbolE, elements[0])


class Haversine(_MPMathFunction):
    """
    <dl>
      <dt>'Haversine[$z$]'
      <dd>returns the haversine function of $z$.
    </dl>

    >> Haversine[1.5]
     = 0.464631

    >> Haversine[0.5 + 2I]
     = -1.15082 + 0.869405 I
    """

    summary_text = "Haversine function"
    rules = {"Haversine[z_]": "Power[Sin[z/2], 2]"}


class _IllegalStepSpecification(Exception):
    pass


class InverseHaversine(_MPMathFunction):
    """
    <dl>
      <dt>'InverseHaversine[$z$]'
      <dd>returns the inverse haversine function of $z$.
    </dl>

    >> InverseHaversine[0.5]
     = 1.5708

    >> InverseHaversine[1 + 2.5 I]
     = 1.76459 + 2.33097 I
    """

    summary_text = "inverse Haversine function"
    rules = {"InverseHaversine[z_]": "2 * ArcSin[Sqrt[z]]"}


class Log(_MPMathFunction):
    """
    <dl>
    <dt>'Log[$z$]'
        <dd>returns the natural logarithm of $z$.
    </dl>

    >> Log[{0, 1, E, E * E, E ^ 3, E ^ x}]
     = {-Infinity, 0, 1, 2, 3, Log[E ^ x]}
    >> Log[0.]
     = Indeterminate
    >> Plot[Log[x], {x, 0, 5}]
     = -Graphics-

    #> Log[1000] / Log[10] // Simplify
     = 3

    #> Log[1.4]
     = 0.336472

    #> Log[Exp[1.4]]
     = 1.4

    #> Log[-1.4]
     = 0.336472 + 3.14159 I

    #> N[Log[10], 30]
     = 2.30258509299404568401799145468
    """

    summary_text = "logarithm function"
    nargs = {2}
    mpmath_name = "log"
    sympy_name = "log"

    rules = {
        "Log[0.]": "Indeterminate",
        "Log[0]": "DirectedInfinity[-1]",
        "Log[Overflow[]]": "Overflow[]",
        "Log[1]": "0",
        "Log[E]": "1",
        "Log[E^x_Integer]": "x",
        "Derivative[1][Log]": "1/#&",
        "Log[x_?InexactNumberQ]": "Log[E, x]",
    }

    def prepare_sympy(self, elements):
        if len(elements) == 2:
            elements = [elements[1], elements[0]]
        return elements

    def get_mpmath_function(self, args):
        return lambda base, x: mpmath.log(x, base)


class Log2(Builtin):
    """
    <dl>
    <dt>'Log2[$z$]'
        <dd>returns the base-2 logarithm of $z$.
    </dl>

    >> Log2[4 ^ 8]
     = 16
    >> Log2[5.6]
     = 2.48543
    >> Log2[E ^ 2]
     = 2 / Log[2]
    """

    summary_text = "base-2 logarithm function"
    attributes = listable | numeric_function | protected

    rules = {
        "Log2[x_]": "Log[2, x]",
    }


class Log10(Builtin):
    """
    <dl>
    <dt>'Log10[$z$]'
        <dd>returns the base-10 logarithm of $z$.
    </dl>

    >> Log10[1000]
     = 3
    >> Log10[{2., 5.}]
     = {0.30103, 0.69897}
    >> Log10[E ^ 3]
     = 3 / Log[10]
    """

    summary_text = "base-10 logarithm function"
    attributes = listable | numeric_function | protected

    rules = {
        "Log10[x_]": "Log[10, x]",
    }


class LogisticSigmoid(Builtin):
    """
    <dl>
    <dt>'LogisticSigmoid[$z$]'
        <dd>returns the logistic sigmoid of $z$.
    </dl>

    >> LogisticSigmoid[0.5]
     = 0.622459

    >> LogisticSigmoid[0.5 + 2.3 I]
     = 1.06475 + 0.808177 I

    >> LogisticSigmoid[{-0.2, 0.1, 0.3}]
     = {0.450166, 0.524979, 0.574443}

    #> LogisticSigmoid[I Pi]
     = LogisticSigmoid[I Pi]
    """

    summary_text = "logistic function"
    attributes = listable | numeric_function | protected

    rules = {"LogisticSigmoid[z_?NumberQ]": "1 / (1 + Exp[-z])"}


class Sec(_MPMathFunction):
    """
    <dl>
    <dt>'Sec[$z$]'
        <dd>returns the secant of $z$.
    </dl>

    >> Sec[0]
     = 1
    >> Sec[1] (* Sec[1] in Mathematica *)
     = 1 / Cos[1]
    >> Sec[1.]
     = 1.85082
    """

    summary_text = "secant function"
    mpmath_name = "sec"

    rules = {
        "Derivative[1][Sec]": "Sec[#] Tan[#]&",
        "Sec[0]": "1",
    }

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            return Expression(
                SymbolPower, Expression(SymbolCos, expr.elements[0]), Integer(-1)
            ).to_sympy()


class Sin(_MPMathFunction):
    """
    <dl>
      <dt>'Sin[$z$]'
      <dd>returns the sine of $z$.
    </dl>

    >> Sin[0]
     = 0
    >> Sin[0.5]
     = 0.479426
    >> Sin[3 Pi]
     = 0
    >> Sin[1.0 + I]
     = 1.29846 + 0.634964 I

    >> Plot[Sin[x], {x, -Pi, Pi}]
     = -Graphics-

    #> N[Sin[1], 40]
     = 0.8414709848078965066525023216302989996226
    """

    summary_text = "sine function"
    mpmath_name = "sin"

    rules = {
        "Sin[Pi]": "0",
        "Sin[n_Integer*Pi]": "0",
        "Sin[(1/2) * Pi]": "1",
        "Sin[0]": "0",
        "Derivative[1][Sin]": "Cos[#]&",
    }


class Tan(_MPMathFunction):
    """
    <dl>
      <dt>'Tan[$z$]'
      <dd>returns the tangent of $z$.
    </dl>

    >> Tan[0]
     = 0
    >> Tan[Pi / 2]
     = ComplexInfinity

    #> Tan[0.5 Pi]
     = 1.63312×10^16
    """

    summary_text = "tangent function"
    mpmath_name = "tan"

    rules = {
        "Tan[(1/2) * Pi]": "ComplexInfinity",
        "Tan[0]": "0",
        "Derivative[1][Tan]": "Sec[#]^2&",
    }
