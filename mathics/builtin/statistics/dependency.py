# -*- coding: utf-8 -*-

# TODO: separate these when we have more
"""
Dependency and Dispursion Statistics
"""

# This tells documentation how to sort this module
# Here we are also hiding "moements" since this can erroneously appear at the top level.
sort_order = "mathics.builtin.special-moments"

from mathics.builtin.base import Builtin

from mathics.builtin.lists import _Rectangular, _NotRectangularException

from mathics.core.atoms import Integer
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolDivide
from mathics.core.systemsymbols import SymbolDot, SymbolMean, SymbolSubtract

SymbolConjugate = Symbol("Conjugate")
SymbolCovariance = Symbol("Covariance")
SymbolSqrt = Symbol("Sqrt")
SymbolStandardDeviation = Symbol("StandardDeviation")
SymbolVariance = Symbol("Variance")


class Correlation(Builtin):
    """
    <url>:Pearson correlation coefficient:https://en.wikipedia.org/wiki/Pearson_correlation_coefficient</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Correlation.html</url>)
    <url>
    <dl>
      <dt>'Correlation[$a$, $b$]'
      <dd>computes Pearson's correlation of two equal-sized vectors $a$ and $b$.
    </dl>

    An example from Wikipedia:

    >> Correlation[{10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5}, {8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68}]
     = 0.816421
    """

    messages = {
        "shlen": "`` must contain at least two elements.",
        "vctmat": "`1` and `2` need to be of equal length.",
    }
    summary_text = "Pearson's correlation of a pair of datasets"

    def apply(self, a, b, evaluation):
        "Correlation[a_List, b_List]"

        if len(a.elements) != len(b.elements):
            evaluation.message("Correlation", "vctmat", a, b)
        elif len(a.elements) < 2:
            evaluation.message("Correlation", "shlen", a)
        elif len(b.elements) < 2:
            evaluation.message("Correlation", "shlen", b)
        else:
            da = Expression(SymbolStandardDeviation, a)
            db = Expression(SymbolStandardDeviation, b)
            return Expression(SymbolCovariance, a, b) / (da * db)


class Covariance(Builtin):
    """
    <url>:Covariance: https://en.wikipedia.org/wiki/Covariance</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Covariance.html</url>)
    <dl>
      <dt>'Covariance[$a$, $b$]'
      <dd>computes the covariance between the equal-sized vectors $a$ and $b$.
    </dl>

    >> Covariance[{0.2, 0.3, 0.1}, {0.3, 0.3, -0.2}]
     = 0.025
    """

    messages = {
        "shlen": "`` must contain at least two elements.",
        "vctmat": "`1` and `2` need to be of equal length.",
    }
    summary_text = "covariance matrix for a pair of datasets"

    def apply(self, a, b, evaluation):
        "Covariance[a_List, b_List]"

        if len(a.elements) != len(b.elements):
            evaluation.message("Covariance", "vctmat", a, b)
        elif len(a.elements) < 2:
            evaluation.message("Covariance", "shlen", a)
        elif len(b.elements) < 2:
            evaluation.message("Covariance", "shlen", b)
        else:
            ma = Expression(SymbolSubtract, a, Expression(SymbolMean, a))
            mb = Expression(SymbolSubtract, b, Expression(SymbolMean, b))
            return Expression(
                SymbolDivide,
                Expression(SymbolDot, ma, Expression(SymbolConjugate, mb)),
                Integer(len(a.elements) - 1),
            )


class StandardDeviation(_Rectangular):
    """
    <url>:Standard deviation: https://en.wikipedia.org/wiki/Standard_deviation</url> (<url>:WMA: https://reference.wolfram.com/language/ref/StandardDeviation.html</url>)
    <dl>
      <dt>'StandardDeviation[$list$]'
      <dd>computes the standard deviation of $list. $list$ may consist of numerical values or symbols. Numerical values may be real or complex.

      StandardDeviation[{{$a1$, $a2$, ...}, {$b1$, $b2$, ...}, ...}] will yield
      {StandardDeviation[{$a1$, $b1$, ...}, StandardDeviation[{$a2$, $b2$, ...}], ...}.
    </dl>

    >> StandardDeviation[{1, 2, 3}]
     = 1

    >> StandardDeviation[{7, -5, 101, 100}]
     = Sqrt[13297] / 2

    >> StandardDeviation[{a, a}]
     = 0

    >> StandardDeviation[{{1, 10}, {-1, 20}}]
     = {Sqrt[2], 5 Sqrt[2]}
    """

    messages = {
        "shlen": "`` must contain at least two elements.",
        "rectt": "Expected a rectangular array at position 1 in ``.",
    }
    summary_text = "standard deviation of a dataset"

    def apply(self, l, evaluation):
        "StandardDeviation[l_List]"
        if len(l.elements) <= 1:
            evaluation.message("StandardDeviation", "shlen", l)
        elif all(element.get_head_name() == "System`List" for element in l.elements):
            try:
                return self.rect(l)
            except _NotRectangularException:
                evaluation.message(
                    "StandardDeviation", "rectt", Expression(SymbolStandardDeviation, l)
                )
        else:
            return Expression(SymbolSqrt, Expression(SymbolVariance, l))


class Variance(_Rectangular):
    """
    <url>:Variance: https://en.wikipedia.org/wiki/Variance</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Variance.html</url>)
    <dl>
      <dt>'Variance[$list$]'
      <dd>computes the variance of $list. $list$ may consist of numerical values or symbols. Numerical values may be real or complex.

      Variance[{{$a1$, $a2$, ...}, {$b1$, $b2$, ...}, ...}] will yield {Variance[{$a1$, $b1$, ...}, Variance[{$a2$, $b2$, ...}], ...}.
    </dl>

    >> Variance[{1, 2, 3}]
     = 1

    >> Variance[{7, -5, 101, 3}]
     = 7475 / 3

    >> Variance[{1 + 2I, 3 - 10I}]
     = 74

    >> Variance[{a, a}]
     = 0

    >> Variance[{{1, 3, 5}, {4, 10, 100}}]
     = {9 / 2, 49 / 2, 9025 / 2}
    """

    messages = {
        "shlen": "`` must contain at least two elements.",
        "rectt": "Expected a rectangular array at position 1 in ``.",
    }
    summary_text = "variance of a dataset"

    # for the general formulation of real and complex variance below, see for example
    # https://en.wikipedia.org/wiki/Variance#Generalizations

    def apply(self, l, evaluation):
        "Variance[l_List]"
        if len(l.elements) <= 1:
            evaluation.message("Variance", "shlen", l)
        elif all(element.get_head_name() == "System`List" for element in l.elements):
            try:
                return self.rect(l)
            except _NotRectangularException:
                evaluation.message("Variance", "rectt", Expression(SymbolVariance, l))
        else:
            d = Expression(SymbolSubtract, l, Expression(SymbolMean, l))
            return Expression(
                SymbolDivide,
                Expression(SymbolDot, d, Expression(SymbolConjugate, d)),
                Integer(len(l.elements) - 1),
            )


# TODO for Dispersion:
#  TrimmedVariance, WinsorizedVariance, StandardDeviation, MeanDeviation, MedianDeviation, QuartileDeviation, InterquartileRange, QnDispersion, SnDispersion, BiweightMidvariance
# TODO for Dependency:
#  Correlation, AbsoluteCorrelation, SpearmanRho,  KendallTau, HoeffdingD, GoodmanKruskalGamma, BlomqvistBeta, WilksW, PillaiTrace
