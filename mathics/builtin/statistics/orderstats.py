"""
Order Statistics

In statistics, an <url>:order statistic: https://en.wikipedia.org/wiki/Order_statistic</url> gives the $k$-th smmallest value.

Together with <url>:rank statistics: https://en.wikipedia.org/wiki/Ranking</url> these are fundamental tools in non-parametric statistics and inference.

Important special cases of order statistics are finding minimum and maximum value of a sample and sample quantiles.
"""

from mpmath import floor as mpfloor, ceil as mpceil

from mathics.algorithm.introselect import introselect
from mathics.builtin.base import Builtin
from mathics.builtin.lists import _RankedTakeLargest, _RankedTakeSmallest
from mathics.core.atoms import Atom, Integer, Symbol, SymbolTrue
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    SymbolFloor,
    SymbolPlus,
    SymbolTimes,
)
from mathics.core.systemsymbols import SymbolSubtract

SymbolRankedMax = Symbol("RankedMax")
SymbolRankedMin = Symbol("RankedMin")


class Quantile(Builtin):
    """
    <url>:Quantile: https://en.wikipedia.org/wiki/Quantile</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Quantile.html</url>)
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

            x = (Integer(n) + b) * q + a

            numeric_x = x.evaluate(evaluation).numerify(evaluation)

            if isinstance(numeric_x, Integer):
                results.append(ranked(numeric_x.value))
            else:
                py_x = numeric_x.to_mpmath()

                if py_x is None:
                    return

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


class RankedMax(Builtin):
    """
    <dl>
      <dt>'RankedMax[$list$, $n$]'
      <dd>returns the $n$th largest element of $list$ (with $n$ = 1 yielding the largest element,
      $n$ = 2 yielding the second largest element, and so on).
    </dl>

    >> RankedMax[{482, 17, 181, -12}, 2]
     = 181
    """

    messages = {
        "intpm": "Expected positive integer at position 2 in ``.",
        "rank": "The specified rank `1` is not between 1 and `2`.",
    }
    summary_text = "the n-th largest item"

    def apply(self, element, n: Integer, evaluation):
        "RankedMax[element_List, n_Integer]"
        py_n = n.value
        if py_n < 1:
            evaluation.message(
                "RankedMax", "intpm", Expression(SymbolRankedMax, element, n)
            )
        elif py_n > len(element.elements):
            evaluation.message("RankedMax", "rank", py_n, len(element.elements))
        else:
            return introselect(
                element.get_mutable_elements(), len(element.elements) - py_n
            )


class RankedMin(Builtin):
    """
    <dl>
      <dt>'RankedMin[$list$, $n$]'
      <dd>returns the $n$th smallest element of $list$ (with $n$ = 1 yielding the smallest element, $n$ = 2 yielding the second smallest element, and so on).
    </dl>

    >> RankedMin[{482, 17, 181, -12}, 2]
     = 17
    """

    messages = {
        "intpm": "Expected positive integer at position 2 in ``.",
        "rank": "The specified rank `1` is not between 1 and `2`.",
    }
    summary_text = "the n-th smallest item"

    def apply(self, element, n: Integer, evaluation):
        "RankedMin[element_List, n_Integer]"
        py_n = n.value
        if py_n < 1:
            evaluation.message(
                "RankedMin", "intpm", Expression(SymbolRankedMin, element, n)
            )
        elif py_n > len(element.elements):
            evaluation.message("RankedMin", "rank", py_n, len(element.elements))
        else:
            return introselect(element.get_mutable_elements(), py_n - 1)


class Sort(Builtin):
    """
    <dl>
      <dt>'Sort[$list$]'
      <dd>sorts $list$ (or the elements of any other expression) according to canonical ordering.

      <dt>'Sort[$list$, $p$]'
      <dd>sorts using $p$ to determine the order of two elements.
    </dl>

    >> Sort[{4, 1.0, a, 3+I}]
     = {1., 3 + I, 4, a}

    Sort uses 'OrderedQ' to determine ordering by default.
    You can sort patterns according to their precedence using 'PatternsOrderedQ':
    >> Sort[{items___, item_, OptionsPattern[], item_symbol, item_?test}, PatternsOrderedQ]
     = {item_symbol, item_ ? test, item_, items___, OptionsPattern[]}

    When sorting patterns, values of atoms do not matter:
    >> Sort[{a, b/;t}, PatternsOrderedQ]
     = {b /; t, a}
    >> Sort[{2+c_, 1+b__}, PatternsOrderedQ]
     = {2 + c_, 1 + b__}
    >> Sort[{x_ + n_*y_, x_ + y_}, PatternsOrderedQ]
     = {x_ + n_ y_, x_ + y_}

    #> Sort[{x_, y_}, PatternsOrderedQ]
     = {x_, y_}
    """

    summary_text = "sort lexicographically or with any comparison function"

    def apply(self, list, evaluation):
        "Sort[list_]"

        if isinstance(list, Atom):
            evaluation.message("Sort", "normal")
        else:
            new_elements = sorted(list.elements)
            return list.restructure(list.head, new_elements, evaluation)

    def apply_predicate(self, list, p, evaluation):
        "Sort[list_, p_]"

        if isinstance(list, Atom):
            evaluation.message("Sort", "normal")
        else:

            class Key:
                def __init__(self, element):
                    self.element = element

                def __gt__(self, other):
                    return (
                        not Expression(p, self.element, other.element).evaluate(
                            evaluation
                        )
                        is SymbolTrue
                    )

            new_elements = sorted(list.elements, key=Key)
            return list.restructure(list.head, new_elements, evaluation)


class TakeLargest(_RankedTakeLargest):
    """
    <dl>
      <dt>'TakeLargest[$list$, $f$, $n$]'
      <dd>returns the a sorted list of the $n$ largest items in $list$.
    </dl>

    >> TakeLargest[{100, -1, 50, 10}, 2]
     = {100, 50}

    None, Null, Indeterminate and expressions with head Missing are ignored
    by default:
    >> TakeLargest[{-8, 150, Missing[abc]}, 2]
     = {150, -8}

    You may specify which items are ignored using the option ExcludedForms:
    >> TakeLargest[{-8, 150, Missing[abc]}, 2, ExcludedForms -> {}]
     = {Missing[abc], 150}
    """

    summary_text = "sublist of n largest elements"

    def apply(self, element, n, evaluation, options):
        "TakeLargest[element_List, n_, OptionsPattern[TakeLargest]]"
        return self._compute(element, n, evaluation, options)


class TakeSmallest(_RankedTakeSmallest):
    """
    <dl>
      <dt>'TakeSmallest[$list$, $f$, $n$]'
      <dd>returns the a sorted list of the $n$ smallest items in $list$.
    </dl>

    For details on how to use the ExcludedForms option, see TakeLargest[].

    >> TakeSmallest[{100, -1, 50, 10}, 2]
     = {-1, 10}
    """

    summary_text = "sublist of n smallest elements"

    def apply(self, element, n, evaluation, options):
        "TakeSmallest[element_List, n_, OptionsPattern[TakeSmallest]]"
        return self._compute(element, n, evaluation, options)


# TODO: MinMax
