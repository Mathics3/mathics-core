# -*- coding: utf-8 -*-

"""
Trigonometric Functions

Numerical values and derivatives can be computed; however, \
most special exact values and simplification rules are not implemented yet.
"""

import math
from collections import namedtuple
from contextlib import contextmanager
from itertools import chain

import mpmath

from mathics.builtin.arithmetic import _MPMathFunction
from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer, Integer0, IntegerM1, Real
from mathics.core.convert.python import from_python
from mathics.core.exceptions import IllegalStepSpecification
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolPower
from mathics.core.systemsymbols import (
    SymbolArcCos,
    SymbolArcSin,
    SymbolArcTan,
    SymbolCos,
    SymbolSin,
)


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
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/AnglePath.html</url>

    <dl>
      <dt>'AnglePath[{$phi1$, $phi2$, ...}]'
      <dd>returns the points formed by a turtle starting at {0, 0} and angled \
          at 0 degrees going through
          the turns given by angles $phi1$, $phi2$, ... and using distance 1 \
          for each step.

      <dt>'AnglePath[{{$r1$, $phi1$}, {$r2$, $phi2$}, ...}]'
      <dd>instead of using 1 as distance, use $r1$, $r2$, ... as distances for \
          the respective steps.

      <dt>'AnglePath[$phi0$, {$phi1$, $phi2$, ...}]'
      <dd>starts with direction $phi0$ instead of 0.

      <dt>'AnglePath[{$x$, $y$}, {$phi1$, $phi2$, ...}]'
      <dd>starts at {$x, $y} instead of {0, 0}.

      <dt>'AnglePath[{{$x$, $y$}, $phi0$}, {$phi1$, $phi2$, ...}]'
      <dd>specifies initial position {$x$, $y$} and initial direction $phi0$.

      <dt>'AnglePath[{{$x$, $y$}, {$dx$, $dy$}}, {$phi1$, $phi2$, ...}]'
      <dd>specifies initial position {$x$, $y$} and a slope {$dx$, $dy$} that is \
          understood to be the initial direction of the turtle.
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
                    raise IllegalStepSpecification
                arguments = step.elements
                if len(arguments) != 2:
                    raise IllegalStepSpecification
                return arguments

        else:

            def parse(step):
                if step.get_head_name() == "System`List":
                    raise IllegalStepSpecification
                return None, step

        try:
            fold = AnglePathFold(parse)
            elements = [
                ListExpression(x, y) for x, y, _ in fold.fold((x0, y0, phi0), steps)
            ]
            return ListExpression(*elements)
        except IllegalStepSpecification:
            evaluation.message("AnglePath", "steps", ListExpression(*steps))

    def eval(self, steps, evaluation):
        "AnglePath[{steps___}]"
        return AnglePath._compute(
            Integer0, Integer0, None, steps.get_sequence(), evaluation
        )

    def eval_phi0(self, phi0, steps, evaluation):
        "AnglePath[phi0_, {steps___}]"
        return AnglePath._compute(
            Integer0, Integer0, phi0, steps.get_sequence(), evaluation
        )

    def eval_xy(self, x, y, steps, evaluation):
        "AnglePath[{x_, y_}, {steps___}]"
        return AnglePath._compute(x, y, None, steps.get_sequence(), evaluation)

    def eval_xy_phi0(self, x, y, phi0, steps, evaluation):
        "AnglePath[{{x_, y_}, phi0_}, {steps___}]"
        return AnglePath._compute(x, y, phi0, steps.get_sequence(), evaluation)

    def eval_xy_dx(self, x, y, dx, dy, steps, evaluation):
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
    Inverse cosine, <url>
    :arccosine:
    https://en.wikipedia.org/wiki/Inverse_trigonometric_functions#Principal_values</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#acot</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#acos</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcCos.html</url>)

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

    mpmath_name = "acos"

    rules = {
        "ArcCos[0]": "Pi / 2",
        "ArcCos[1]": "0",
        "ArcCos[Undefined]": "Undefined",
        "Derivative[1][ArcCos]": "-1/Sqrt[1-#^2]&",
    }
    summary_text = "inverse cosine function"
    sympy_name = "acos"


class ArcCot(_MPMathFunction):
    """
    Inverse cotangent, <url>
    :arccotangent:
    https://en.wikipedia.org/wiki/Inverse_trigonometric_functions#Principal_values</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#acot</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#acot</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcCot.html</url>)

    <dl>
      <dt>'ArcCot[$z$]'
      <dd>returns the inverse cotangent of $z$.
    </dl>

    >> ArcCot[0]
     = Pi / 2
    >> ArcCot[1]
     = Pi / 4
    """

    mpmath_name = "acot"

    rules = {
        "ArcCot[0]": "Pi / 2",
        "ArcCot[1]": "Pi / 4",
        "ArcCot[Undefined]": "Undefined",
        "Derivative[1][ArcCot]": "-1/(1+#^2)&",
    }
    summary_text = "inverse cotangent function"
    sympy_name = "acot"


class ArcCsc(_MPMathFunction):
    """
    Inverse cosecant, <url>
    :arccosecant:
    https://en.wikipedia.org/wiki/Inverse_trigonometric_functions#Principal_values</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#acsc</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#acsc</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcCsc.html</url>)

    <dl>
      <dt>'ArcCsc[$z$]'
      <dd>returns the inverse cosecant of $z$.
    </dl>

    >> ArcCsc[1]
     = Pi / 2
    >> ArcCsc[-1]
     = -Pi / 2
    """

    mpmath_name = "acsc"

    rules = {
        "ArcCsc[Undefined]": "Undefined",
        "ArcCsc[0]": "ComplexInfinity",
        "ArcCsc[1]": "Pi / 2",
        "Derivative[1][ArcCsc]": "-1 / (Sqrt[1 - 1/#^2] * #^2)&",
    }
    summary_text = "inverse cosecant function"
    sympy_name = "acsc"

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            return Expression(
                SymbolArcSin, Expression(SymbolPower, expr.elements[0], Integer(-1))
            ).to_sympy()


class ArcSec(_MPMathFunction):
    """
    Inverse secant, <url>
    :arcsecant:
    https://en.wikipedia.org/wiki/Inverse_trigonometric_functions#Principal_values</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#sympy.functions.elementary.trigonometric.asec</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#asec</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcSec.html</url>)

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
        "ArcSec[0]": "ComplexInfinity",
        "ArcSec[1]": "0",
        "ArcSec[Undefined]": "Undefined",
        "Derivative[1][ArcSec]": "1 / (Sqrt[1 - 1/#^2] * #^2)&",
    }

    summary_text = "inverse secant function"
    sympy_name = "asec"

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            return Expression(
                SymbolArcCos, Expression(SymbolPower, expr.elements[0], IntegerM1)
            ).to_sympy()


class ArcSin(_MPMathFunction):
    """
    Inverse sine, <url>
    :arcsine:
    https://en.wikipedia.org/wiki/Inverse_trigonometric_functions#Principal_values</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#asin</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#asin</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcSin.html</url>)

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
        "ArcSin[0]": "0",
        "ArcSin[1]": "Pi / 2",
        "ArcSin[Undefined]": "Undefined",
        "Derivative[1][ArcSin]": "1/Sqrt[1-#^2]&",
    }

    summary_text = "inverse sine function"
    sympy_name = "asin"


class ArcTan(_MPMathFunction):
    """
    Inverse tangent, <url>
    :arctangent:
    https://en.wikipedia.org/wiki/Inverse_trigonometric_functions#Principal_values</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#atan</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#atan</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcTan.html</url>)

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
        "ArcTan[0]": "0",
        "ArcTan[1]": "Pi/4",
        "ArcTan[Undefined]": "Undefined",
        "ArcTan[Undefined, x_]": "Undefined",
        "ArcTan[y_, Undefined]": "Undefined",
        "ArcTan[x_?RealNumberQ, y_?RealNumberQ]": """If[x == 0, If[y == 0, 0, If[y > 0, Pi/2, -Pi/2]], If[x > 0,
            ArcTan[y/x], If[y >= 0, ArcTan[y/x] + Pi, ArcTan[y/x] - Pi]]]""",
        "Derivative[1][ArcTan]": "1/(1+#^2)&",
    }

    summary_text = "inverse tangent function"
    sympy_name = "atan"


class Cos(_MPMathFunction):
    """
    <url>
    :Cosine:
    https://en.wikipedia.org/wiki/Sine_and_cosine</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#cos</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#cos</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Cos.html</url>)

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
        "Cos[(1/2) * Pi]": "0",
        "Cos[0]": "1",
        "Cos[Pi]": "-1",
        "Cos[Undefined]": "Undefined",
        "Cos[n_Integer * Pi]": "(-1)^n",
        "Derivative[1][Cos]": "-Sin[#]&",
    }

    summary_text = "cosine function"
    sympy_name = "cos"


class Cot(_MPMathFunction):
    """
    <url>
    :Cotangent:
    https://en.wikipedia.org/wiki/Trigonometric_functions</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#cot</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#cot</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Cot.html</url>)

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
        "Cot[0]": "ComplexInfinity",
        "Cot[Undefined]": "Undefined",
        "Derivative[1][Cot]": "-Csc[#]^2&",
    }

    summary_text = "cotangent function"
    sympy_name = "cot"


class Csc(_MPMathFunction):
    """
    <url>
    :Cosecant:
    https://en.wikipedia.org/wiki/Trigonometric_functions</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#csc</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#csc</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Csc.html</url>)

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
        "Csc[0]": "ComplexInfinity",
        "Csc[Undefined]": "Undefined",
        "Derivative[1][Csc]": "-Cot[#] Csc[#]&",
    }

    summary_text = "cosecant function"
    sympy_name = "csc"

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            return Expression(
                SymbolPower, Expression(SymbolSin, expr.elements[0]), Integer(-1)
            ).to_sympy()


class Haversine(_MPMathFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Haversine.html</url>

    <dl>
      <dt>'Haversine[$z$]'
      <dd>returns the haversine function of $z$.
    </dl>

    >> Haversine[1.5]
     = 0.464631

    >> Haversine[0.5 + 2I]
     = -1.15082 + 0.869405 I
    """

    rules = {"Haversine[z_]": "Power[Sin[z/2], 2]"}
    summary_text = "Haversine function"


class InverseHaversine(_MPMathFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/InverseHaversine.html</url>

    <dl>
      <dt>'InverseHaversine[$z$]'
      <dd>returns the inverse haversine function of $z$.
    </dl>

    >> InverseHaversine[0.5]
     = 1.5708

    >> InverseHaversine[1 + 2.5 I]
     = 1.76459 + 2.33097 I
    """

    rules = {"InverseHaversine[z_]": "2 * ArcSin[Sqrt[z]]"}
    summary_text = "inverse Haversine function"


class Sec(_MPMathFunction):
    """
    <url>
    :Secant:
    https://en.wikipedia.org/wiki/Trigonometric_functions</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#sec</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#sec</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Sec.html</url>)

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

    mpmath_name = "sec"

    rules = {
        "Derivative[1][Sec]": "Sec[#] Tan[#]&",
        "Sec[0]": "1",
    }

    summary_text = "secant function"
    sympy_name = "sec"

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            return Expression(
                SymbolPower, Expression(SymbolCos, expr.elements[0]), Integer(-1)
            ).to_sympy()


class Sin(_MPMathFunction):
    """
    <url>
    :Sine:
    https://en.wikipedia.org/wiki/Sine_and_cosine</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#sin</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#sin</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Sin.html</url>)

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

    mpmath_name = "sin"

    rules = {
        "Derivative[1][Sin]": "Cos[#]&",
        "Sin[Pi]": "0",
        "Sin[n_Integer*Pi]": "0",
        "Sin[(1/2) * Pi]": "1",
        "Sin[0]": "0",
        "Sin[Undefined]": "Undefined",
    }
    summary_text = "sine function"
    sympy_name = "sin"


class Tan(_MPMathFunction):
    """
    <url>
    :Tangent:
    https://en.wikipedia.org/wiki/Tangent</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#tan</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/trigonometric.html#tan</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Tan.html</url>)

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

    mpmath_name = "tan"

    rules = {
        "Derivative[1][Tan]": "Sec[#]^2&",
        "Tan[(1/2) * Pi]": "ComplexInfinity",
        "Tan[0]": "0",
        "Tan[Undefined]": "Undefined",
    }

    summary_text = "tangent function"
    sympy_name = "tan"
