# -*- coding: utf-8 -*-

"""
Basic statistics
"""


from mathics.algorithm.introselect import introselect

from mathics.builtin.base import Builtin

from mathics.builtin.lists import _Rectangular, _NotRectangularException

from mathics.core.atoms import Integer2
from mathics.core.expression import (
    Expression,
    Integer,
    Symbol,
)

from mathics.core.list import ListExpression
from mathics.core.symbols import (
    SymbolDivide,
    SymbolFloor,
    SymbolPlus,
    SymbolTimes,
)
from mathics.core.systemsymbols import SymbolSubtract

SymbolMedian = Symbol("Median")


class CentralMoment(Builtin):  # see https://en.wikipedia.org/wiki/Central_moment
    """
    <dl>
      <dt>'CentralMoment[$list$, $r$]'
      <dd>gives the the $r$th central moment (i.e. the $r$th moment about the mean) of $list$.
    </dl>

    >> CentralMoment[{1.1, 1.2, 1.4, 2.1, 2.4}, 4]
     = 0.100845
    """

    rules = {
        "CentralMoment[list_List, r_]": "Total[(list - Mean[list]) ^ r] / Length[list]",
    }
    summary_text = "central moments of distributions and data"


class Median(_Rectangular):
    """
    <dl>
      <dt>'Median[$list$]'
      <dd>returns the median of $list$.
    </dl>

    >> Median[{26, 64, 36}]
     = 36

    For lists with an even number of elements, Median returns the mean of the two middle values:
    >> Median[{-11, 38, 501, 1183}]
     = 539 / 2

    Passing a matrix returns the medians of the respective columns:
    >> Median[{{100, 1, 10, 50}, {-1, 1, -2, 2}}]
     = {99 / 2, 1, 4, 26}
    """

    messages = {"rectn": "Expected a rectangular array of numbers at position 1 in ``."}
    summary_text = "central value of a dataset"

    def apply(self, data, evaluation):
        "Median[data_List]"
        if not data.elements:
            return
        if all(element.get_head_name() == "System`List" for element in data.elements):
            try:
                return self.rect(data)
            except _NotRectangularException:
                evaluation.message("Median", "rectn", Expression(SymbolMedian, data))
        elif all(element.is_numeric(evaluation) for element in data.elements):
            v = data.get_mutable_elements()  # copy needed for introselect
            n = len(v)
            if n % 2 == 0:  # even number of elements?
                i = n // 2
                a = introselect(v, i)
                b = introselect(v, i - 1)
                return Expression(SymbolDivide, Expression(SymbolPlus, a, b), Integer2)
            else:
                i = n // 2
                return introselect(v, i)
        else:
            evaluation.message("Median", "rectn", Expression(SymbolMedian, data))


class Quantile(Builtin):
    """
        In statistics and probability, quantiles are cut points dividing the range of a probability distribution into continuous intervals with equal probabilities, or dividing the observations in a sample in the same way.

        Quantile is also known as value at risk (VaR) or fractile.
        <dl>
          <dt>'Quantile[$list$, $q$]'
          <dd>returns the $q$th quantile of $list$.

          <dt>'Quantile[$list$, $q$, {{$a$,$b$}, {$c$,$d$}}]'
          <dd>uses the quantile definition specified by parameters $a$, $b$, $c$, $d$.
          <dt>For a list of length $n$, 'Quantile[list, $q$, {{$a$,$b$}, {$c$,$d$}}]' depends on $x$=$a$+($n$+$b$)$q$.

          If $x$ is an integer, the result is '$s$[[$x$]]', where $s$='Sort[list,Less]'.

          Otherwise, the result is 's[[Floor[x]]]+(s[[Ceiling[x]]]-s[[Floor[x]]])(c+dFractionalPart[x])', with the indices taken to be 1 or n if they are out of range.

    The default choice of parameters is '{{0,0},{1,0}}'.
        </dl>

        Common choices of parameters include:
        <ul>
        <li>'{{0, 0}, {1, 0}}' inverse empirical CDF (default)
        <li>'{{0, 0}, {0, 1}}' linear interpolation (California method)
        </ul>

        'Quantile[list,q]' always gives a result equal to an element of list.

        >> Quantile[Range[11], 1/3]
         = 4

        >> Quantile[Range[16], 1/4]
         = 4

        >> Quantile[{1, 2, 3, 4, 5, 6, 7}, {1/4, 3/4}]
         = {2, 6}
    """

    messages = {
        "nquan": "The quantile `1` has to be between 0 and 1.",
    }

    rules = {
        "Quantile[list_List, q_, abcd_]": "Quantile[list, {q}, abcd]",
        "Quantile[list_List, q_]": "Quantile[list, q, {{0, 0}, {1, 0}}]",
    }
    summary_text = "cut points dividing the range of a probability distribution into continuous intervals"

    def apply(self, data, qs, a, b, c, d, evaluation):
        """Quantile[data_List, qs_List, {{a_, b_}, {c_, d_}}]"""

        n = len(data.elements)
        partially_sorted = data.get_mutable_elements()

        def ranked(i):
            return introselect(partially_sorted, min(max(0, i - 1), n - 1))

        numeric_qs = qs.evaluate(evaluation).numerify(evaluation)
        results = []

        for q in numeric_qs.elements:
            py_q = q.to_mpmath()

            if py_q is None or not 0.0 <= py_q <= 1.0:
                evaluation.message("Quantile", "nquan", q)
                return

            x = Expression(
                SymbolPlus,
                a,
                Expression(SymbolTimes, Expression(SymbolPlus, Integer(n), b), q),
            )

            numeric_x = x.evaluate(evaluation).numerify(evaluation)

            if isinstance(numeric_x, Integer):
                results.append(ranked(numeric_x.get_int_value()))
            else:
                py_x = numeric_x.to_mpmath()

                if py_x is None:
                    return

                from mpmath import floor as mpfloor, ceil as mpceil

                if c.get_int_value() == 1 and d.get_int_value() == 0:  # k == 1?
                    results.append(ranked(int(mpceil(py_x))))
                else:
                    py_floor_x = mpfloor(py_x)
                    s0 = ranked(int(py_floor_x))
                    s1 = ranked(int(mpceil(py_x)))

                    k = Expression(
                        SymbolPlus,
                        c,
                        Expression(
                            SymbolTimes,
                            d,
                            Expression(SymbolSubtract, x, Expression(SymbolFloor, x)),
                        ),
                    )

                    results.append(
                        Expression(
                            SymbolPlus,
                            s0,
                            Expression(
                                SymbolTimes, k, Expression(SymbolSubtract, s1, s0)
                            ),
                        )
                    )

        if len(results) == 1:
            return results[0]
        else:
            return ListExpression(*results)


class Quartiles(Builtin):
    """
    <dl>
    <dt>'Quartiles[$list$]'
      <dd>returns the 1/4, 1/2, and 3/4 quantiles of $list$.
    </dl>

    >> Quartiles[Range[25]]
     = {27 / 4, 13, 77 / 4}
    """

    rules = {
        "Quartiles[list_List]": "Quantile[list, {1/4, 1/2, 3/4}, {{1/2, 0}, {0, 1}}]",
    }
    summary_text = "list of quartiles"
