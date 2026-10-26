# -*- coding: utf-8 -*-

"""
Exponential Functions

Numerical values and derivatives can be computed; however, most special exact values \
and simplification rules are not implemented yet.
"""

import math
from collections import namedtuple
from contextlib import contextmanager
from itertools import chain
from typing import Iterable

import mpmath

from mathics.core.atoms import Integer0, Integer1, Real
from mathics.core.attributes import A_LISTABLE, A_NUMERIC_FUNCTION, A_PROTECTED
from mathics.core.builtin import Builtin, MPMathFunction
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.number import min_prec
from mathics.core.symbols import SymbolPower
from mathics.core.systemsymbols import (
    SymbolComplexInfinity,
    SymbolCos,
    SymbolE,
    SymbolIndeterminate,
    SymbolSin,
)
from mathics.eval.numeric import covers_point


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


class Exp(MPMathFunction):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Exp.html</url>

    <dl>
      <dt>'Exp'[$z$]
      <dd>returns the exponential function of $z$.
    </dl>

    >> Exp[1]
     = E
    >> Exp[10.0]
     = 22026.5
    >> Exp[x] // FullForm
     = Power[E, x]

    >> Plot[Exp[x], {x, 0, 3}]
     = -Graphics-
    """

    rules = {
        "Exp[x_]": "E ^ x",
        "Derivative[1][Exp]": "Exp",
    }
    summary_text = "exponential function"

    def from_sympy(self, elements: Iterable) -> Expression:
        return Expression(SymbolPower, SymbolE, elements[0])


class Log(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Log.html</url>

    <dl>
      <dt>'Log'[$z$]
      <dd>returns the natural logarithm of $z$.
    </dl>

    >> Log[{0, 1, E, E * E, E ^ 3, E ^ x}]
     = {-Infinity, 0, 1, 2, 3, Log[E ^ x]}
    >> Log[0.]
     = Indeterminate
    >> Plot[Log[x], {x, 0, 5}]
     = -Graphics-
    """

    summary_text = "logarithm function"
    nargs = {1, 2}
    mpmath_name = "log"
    sympy_name = "log"

    rules = {
        "Derivative[1][Log]": "1/#&",
        "Log[0.]": "Indeterminate",
        "Log[0]": "DirectedInfinity[-1]",
        "Log[1]": "0",
        "Log[E]": "1",
        "Log[E^x_Integer]": "x",
        "Log[Overflow[]]": "Overflow[]",
        "Log[Undefined]": "Undefined",
    }

    def prepare_sympy(self, elements):
        if len(elements) == 2:
            elements = [elements[1], elements[0]]
        return elements

    def get_mpmath_function(self, args):
        if len(args) == 1:
            return mpmath.log
        return lambda base, x: mpmath.log(x, base)

    def special_point_value(self, args):
        # As in WMA, an inexact 0 gives Indeterminate, as Log[2.`20, 0``20],
        # and so does a base that is 1, or whose error covers 1, when x is
        # or covers 1 too: Log[1.`20, 1.`20]. With any other x, Log[x] / 0 is
        # ComplexInfinity, as Log[1.`20, 2]. Any other base gives Log[b, 1]
        # an exact 0.
        if any(isinstance(arg, Real) and arg.is_zero for arg in args):
            return SymbolIndeterminate
        if len(args) == 1:
            return None
        base, x = args
        if _is_or_covers_one(base):
            return (
                SymbolIndeterminate if _is_or_covers_one(x) else SymbolComplexInfinity
            )
        if x.sameQ(Integer1):
            return Integer0
        return None

    @staticmethod
    def condition_numbers(*args: mpmath.mpf) -> tuple[mpmath.mpf, ...]:
        # The arguments, then the value. Log[b, x] is Log[x] / Log[b]. As in
        # WMA, Log[x] has no base E that would add an error of its own.
        *arguments, value = args
        if len(arguments) == 1:
            return (1 / abs(value),)
        base, x = arguments
        return (1 / abs(mpmath.log(base)), 1 / abs(mpmath.log(x)))


def _is_or_covers_one(number) -> bool:
    return number.sameQ(Integer1) or covers_point(number, (1,))


class Log2(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Log2.html</url>

    <dl>
      <dt>'Log2'[$z$]
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
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    rules = {
        "Log2[x_]": "Log[2, x]",
    }


class Log10(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Log10.html</url>

    <dl>
      <dt>'Log10'[$z$]
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
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    rules = {
        "Log10[x_]": "Log[10, x]",
    }


class LogisticSigmoid(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/LogisticSigmoid.html</url>

    <dl>
      <dt>'LogisticSigmoid'[$z$]
      <dd>returns the logistic sigmoid of $z$.
    </dl>

    >> LogisticSigmoid[0.5]
     = 0.622459

    >> LogisticSigmoid[0.5 + 2.3 I]
     = 1.06475 + 0.808177 I

    >> LogisticSigmoid[{-0.2, 0.1, 0.3}]
     = {0.450166, 0.524979, 0.574443}
    """

    summary_text = "logistic function"
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    rules = {"LogisticSigmoid[z_?NumberQ]": "1 / (1 + Exp[-z])"}
