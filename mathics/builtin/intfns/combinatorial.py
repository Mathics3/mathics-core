# -*- coding: utf-8 -*-
"""
Combinatorial Functions

<url>:Combinatorics: https://en.wikipedia.org/wiki/Combinatorics</url> is an \
area of mathematics primarily concerned with counting, both as a means and an \
end in obtaining results, and certain properties of finite structures.

It is closely related to many other areas of Mathematics and has many \
applications ranging from logic to statistical physics, from evolutionary \
biology to computer science, etc.
"""


from itertools import combinations

from mathics.core.atoms import Integer, Integer1
from mathics.core.attributes import (
    A_LISTABLE,
    A_N_HOLD_FIRST,
    A_NUMERIC_FUNCTION,
    A_ORDERLESS,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, MPMathFunction, SympyFunction
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolDivide,
    SymbolFalse,
    SymbolPlus,
    SymbolTimes,
    SymbolTrue,
)

SymbolBinomial = Symbol("Binomial")
SymbolSubsets = Symbol("Subsets")


class BellB(SympyFunction):
    """
    <url>
    :Bell number: https://en.wikipedia.org/wiki/Bell_number</url> (<url>
    :SymPy: https://docs.sympy.org/latest/modules/functions/combinatorial.html#sympy.functions.combinatorial.numbers.bell</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/BellB.html</url>)
    <dl>
      <dt>'BellB[$n$]'
      <dd>Bell number $B$_$n$.

      <dt>'BellB[$n$, $x$]'
      <dd>Bell polynomial $B$_$n$($x$).
    </dl>

    >> BellB[10]
     = 115975

    >> BellB[5, x]
     = x + 15 x ^ 2 + 25 x ^ 3 + 10 x ^ 4 + x ^ 5
    """

    attributes = A_LISTABLE | A_N_HOLD_FIRST | A_PROTECTED | A_READ_PROTECTED
    summary_text = "Bell numbers"
    sympy_name = "bell"

    def eval(self, z, evaluation: Evaluation):
        "%(name)s[z__]"
        return super().eval(z, evaluation)


class _BooleanDissimilarity(Builtin):
    @staticmethod
    def _to_bool_vector(u):
        def generate():
            for element in u.elements:
                if isinstance(element, Integer):
                    val = element.value
                    if val in (0, 1):
                        yield val
                    else:
                        raise _NoBoolVector
                elif isinstance(element, Symbol):
                    if element is SymbolTrue:
                        yield 1
                    elif element is SymbolFalse:
                        yield 0
                    else:
                        raise _NoBoolVector
                else:
                    raise _NoBoolVector

        try:
            return [x for x in generate()]
        except _NoBoolVector:
            return None

    def eval(self, u, v, evaluation):
        "%(name)s[u_List, v_List]"
        if len(u.elements) != len(v.elements):
            return
        py_u = _BooleanDissimilarity._to_bool_vector(u)
        if py_u is None:
            return
        py_v = _BooleanDissimilarity._to_bool_vector(v)
        if py_v is None:
            return
        counts = [0, 0, 0, 0]
        for a, b in zip(py_u, py_v):
            counts[(a << 1) + b] += 1
        return self._compute(len(py_u), *counts)


class _NoBoolVector(Exception):
    pass


class Binomial(MPMathFunction):
    """

    <url>
    :Binomial Coefficient:
    https://en.wikipedia.org/wiki/Binomial_coefficient</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/combinatorial.html#binomial</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Binomial.html</url>)

    <dl>
      <dt>'Binomial[$n$, $k$]'
      <dd>gives the binomial coefficient $n$ choose $k$.
    </dl>

    >> Binomial[5, 3]
     = 10

    'Binomial' supports inexact numbers:
    >> Binomial[10.5,3.2]
     = 165.286

    Some special cases:
    >> Binomial[10, -2]
     = 0
    >> Binomial[-10.5, -3.5]
     = 0.
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    nargs = {2}
    sympy_name = "binomial"
    mpmath_name = "binomial"
    summary_text = "binomial coefficients"


class CatalanNumber(SympyFunction):
    """
    <url>
    :Catalan Number:
    https://en.wikipedia.org/wiki/Catalan_number</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/combinatorial.html#sympy.functions.combinatorial.numbers.catalan</url>, \
    <url>
    :WMA:
    https://reference.wolfram.com/language/ref/CatalanNumber.html</url>)

    <dl>
      <dt>'CatalanNumber[$n$]'
      <dd>gives the $n$th Catalan number.
    </dl>

    A list of the first five Catalan numbers:
    >> Table[CatalanNumber[n], {n, 1, 5}]
     = {1, 2, 5, 14, 42}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED

    summary_text = "catalan number"
    sympy_name = "catalan"

    # We (and sympy) do not handle fractions or other non-integers
    # right now.
    def eval_integer(self, n: Integer, evaluation):
        "CatalanNumber[n_Integer]"
        return self.eval(n, evaluation)


class DiceDissimilarity(_BooleanDissimilarity):
    r"""
    <url>
    :Sørensen–Dice coefficient:
    https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient</url> (<url>
    :Sympy:
    https://docs.scipy.org/doc/scipy/search.html</url>, <url>
    :DiceDissimilarity:
    https://reference.wolfram.com/language/ref/DiceDissimilarity.html</url>)
    <dl>
      <dt>'DiceDissimilarity[$u$, $v$]'
      <dd>returns the Dice dissimilarity between the two boolean 1-D lists $u$ and $v$.
      This is defined as ($c_tf$ + $c_ft$) / (2 * $c_tt$ + $c_ft$ + c_tf).
      $n$ is len($u$) and $c_ij$ is the number of occurrences of $u$[$k$]=$i$ and $v$[$k$]=$j$ for $k$ < $n$.
    </dl>

    >> DiceDissimilarity[{1, 0, 1, 1, 0, 1, 1}, {0, 1, 1, 0, 0, 0, 1}]
     = 1 / 2
    """

    summary_text = "Dice dissimilarity"

    def _compute(self, n, c_ff, c_ft, c_tf, c_tt):
        return Expression(
            SymbolDivide, Integer(c_tf + c_ft), Integer(2 * c_tt + c_ft + c_tf)
        )


class EulerE(SympyFunction):
    """
    <url>
    :Euler numbers: https://en.wikipedia.org/wiki/Euler_numbers</url> (<url>
    :SymPy: https://docs.sympy.org/latest/modules/functions/combinatorial.html#sympy.functions.combinatorial.numbers.euler</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/EulerE.html</url>)
    <dl>
      <dt>'EulerE[$n$]'
      <dd>Euler number $E$_$n$.

      <dt>'EulerE[$n$, $x$]'
      <dd>Euler polynomial $E$_$n$($x$).
    </dl>

    Odd-index Euler numbers are zero:
    >> Table[EulerE[k], {k, 1, 9, 2}]
     = {0, 0, 0, 0, 0}

    Even-index Euler numbers alternate in sign:
    >> Table[EulerE[k], {k, 0, 8, 2}]
     = {1, -1, 5, -61, 1385}

    >> EulerE[5, z]
     = -1 / 2 + 5 z ^ 2 / 2 - 5 z ^ 4 / 2 + z ^ 5
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "Euler numbers"
    sympy_name = "euler"

    def eval(self, z, evaluation: Evaluation):
        "%(name)s[z__]"
        return super().eval(z, evaluation)


class JaccardDissimilarity(_BooleanDissimilarity):
    """
    <url>
    :Jaccard index:
    https://en.wikipedia.org/wiki/Jaccard_index</url> (<url>
    :SciPy:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jaccard.html</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/JaccardDissimilarity.html</url>)
    <dl>
      <dt>'JaccardDissimilarity[$u$, $v$]'
      <dd>returns the Jaccard-Needham dissimilarity between the two boolean \
          1-D lists $u$ and $v$, which is defined as \
          ($c_tf$ + $c_ft$) / ($c_tt$ + $c_ft$ + $c_tf$), where $n$ is \
          len($u$) and $c_ij$ is the number of occurrences of \
          $u$[$k$]=$i$ and $v$[$k$]=$j$ for $k$ < $n$.
    </dl>

    >> JaccardDissimilarity[{1, 0, 1, 1, 0, 1, 1}, {0, 1, 1, 0, 0, 0, 1}]
     = 2 / 3
    """

    summary_text = "Jaccard dissimilarity"

    def _compute(self, n, c_ff, c_ft, c_tf, c_tt):
        return Expression(
            SymbolDivide, Integer(c_tf + c_ft), Integer(c_tt + c_ft + c_tf)
        )


class LucasL(SympyFunction):
    """
    <url>
    :Lucas Number:
    https://en.wikipedia.org/wiki/Lucas_number</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/combinatorial.html#sympy.functions.combinatorial.numbers.lucas</url>, \
    <url>
    :WMA:
    https://reference.wolfram.com/language/ref/LucasL.html</url>)

    <dl>
      <dt>'LucasL[$n$]'
      <dd>gives the $n$th Lucas number.

      <dt>'LucasL[$n$, $x$]'
      <dd>gives the $n$th Lucas polynomial $L$_($x$).
    </dl>

    A list of the first five Lucas numbers:
    >> Table[LucasL[n], {n, 1, 5}]
     = {1, 3, 4, 7, 11}

    >> Series[LucasL[1/2, x], {x, 0, 5}]
     = 1 + 1 / 4 x + 1 / 32 x ^ 2 + (-1 / 128) x ^ 3 + (-5 / 2048) x ^ 4 + 7 / 8192 x ^ 5 + O[x] ^ 6

    >> Plot[LucasL[1/2, x], {x, -5, 5}]
     = -Graphics-
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED

    sympy_name = "lucas"
    summary_text = "get a Lucas number or polynomial"

    rules = {
        "LucasL[n_, 1]": "LucasL[n]",
        "LucasL[n_, x_]": "(x/2 + Sqrt[1 + x^2 / 4])^n + Cos[n Pi] / (x/2 + Sqrt[1 + x^2 / 4])^n // Simplify",
    }

    def eval_integer(self, n: Integer, evaluation):
        "LucasL[n_Integer]"
        return self.eval(n, evaluation)


class MatchingDissimilarity(_BooleanDissimilarity):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/MatchingDissimilarity.html</url>

    <dl>
      <dt>'MatchingDissimilarity[$u$, $v$]'
      <dd>returns the Matching dissimilarity between the two boolean \
      1-D lists $u$ and $v$, which is defined as ($c_tf$ + $c_ft$) / $n$, \
      where $n$ is len($u$) and $c_ij$ is the number of occurrences of \
      $u$[$k$]=$i$ and $v$[$k$]=$j$ for $k$ < $n$.
    </dl>

    >> MatchingDissimilarity[{1, 0, 1, 1, 0, 1, 1}, {0, 1, 1, 0, 0, 0, 1}]
     = 4 / 7
    """

    summary_text = "simple matching dissimilarity"

    def _compute(self, n, c_ff, c_ft, c_tf, c_tt):
        return Expression(SymbolDivide, Integer(c_tf + c_ft), Integer(n))


class Multinomial(Builtin):
    """
    <url>
    :Multinomial distribution:
    https://en.wikipedia.org/wiki/Multinomial_distribution</url> (<url>\
    :WMA: https://reference.wolfram.com/language/ref/Multinomial.html</url>)
    <dl>
      <dt>'Multinomial[$n1$, $n2$, ...]'
      <dd>gives the multinomial coefficient '($n1$+$n2$+...)!/($n1$!$n2$!...)'.
    </dl>

    >> Multinomial[2, 3, 4, 5]
     = 2522520
    >> Multinomial[]
     = 1
    Multinomial is expressed in terms of 'Binomial':
    >> Multinomial[a, b, c]
     = Binomial[a, a] Binomial[a + b, b] Binomial[a + b + c, c]
    'Multinomial[$n$-$k$, $k$]' is equivalent to 'Binomial[$n$, $k$]'.
    >> Multinomial[2, 3]
     = 10
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_ORDERLESS | A_PROTECTED
    summary_text = "multinomial coefficients"

    def eval(self, values, evaluation):
        "Multinomial[values___]"

        values = values.get_sequence()
        elements = []
        total = []
        for value in values:
            total.append(value)
            elements.append(
                Expression(SymbolBinomial, Expression(SymbolPlus, *total), value)
            )
        return Expression(SymbolTimes, *elements)


class PolygonalNumber(Builtin):
    """
    <url>
    :Polygonal number: https://en.wikipedia.org/wiki/Polygonal_number</url> (<url>
    :WMA: https://reference.wolfram.com/language/ref/PolygonalNumber.html</url>)
    <dl>
      <dt>'PolygonalNumber[$n$]'
      <dd>gives the $n$th triangular number.

      <dt>'PolygonalNumber[$r$, $n$]'
      <dd>gives the $n$th $r$-gonal number.
    </dl>

    >> Table[PolygonalNumber[n], {n, 10}]
     = {1, 3, 6, 10, 15, 21, 28, 36, 45, 55}

    The sum of two consecutive Polygonal numbers is the square of the larger number:
    >> Table[PolygonalNumber[n-1] + PolygonalNumber[n], {n, 10}]
     = {1, 4, 9, 16, 25, 36, 49, 64, 81, 100}

    'PolygonalNumber'[$r$, $n$] can be interpreted as the number of points arranged in the form of $n$-1 polygons of $r$ sides.

    List the tenth $r$-gonal number of regular polygons from 3 to 8:
    >> Table[PolygonalNumber[r, 10], {r, 3, 8}]
     = {55, 100, 145, 190, 235, 280}

    See also <url>
    :Binomial:
    doc/reference-of-built-in-symbols/integer-functions/combinatorial-functions/binomial/</url>, and <url>
    :RegularPolygon:
    doc/reference-of-built-in-symbols/drawing-graphics/regularpolygon/</url>.
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    rules = {
        "PolygonalNumber[n_Integer]": "PolygonalNumber[3, n]",
        "PolygonalNumber[r_Integer, n_Integer]": "(1/2) n (n (r - 2) - r + 4)",
    }
    summary_text = "get polygonal number"


class RogersTanimotoDissimilarity(_BooleanDissimilarity):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RogersTanimotoDissimilarity.html</url>

    <dl>
      <dt>'RogersTanimotoDissimilarity[$u$, $v$]'
      <dd>returns the Rogers-Tanimoto dissimilarity between the two boolean \
      1-D lists $u$ and $v$, which is defined as \
      $R$ / (c_tt + c_ff + $R$) where $n$ is len($u$), c_ij is \
      the number of occurrences of $u$[$k$]=$i$ and $v$[$k]$=$j$ for $k$<n, \
      and $R$ = 2 * ($c_tf$ + $c_ft$).
    </dl>

    >> RogersTanimotoDissimilarity[{1, 0, 1, 1, 0, 1, 1}, {0, 1, 1, 0, 0, 0, 1}]
     = 8 / 11
    """

    summary_text = "Rogers-Tanimoto dissimilarity"

    def _compute(self, n, c_ff, c_ft, c_tf, c_tt):
        r = 2 * (c_tf + c_ft)
        return Expression(SymbolDivide, Integer(r), Integer(c_tt + c_ff + r))


class RussellRaoDissimilarity(_BooleanDissimilarity):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RusselRaoDissimilarity.html</url>

    <dl>
      <dt>'RussellRaoDissimilarity[$u$, $v$]'
      <dd>returns the Russell-Rao dissimilarity between the two boolean \
      1-D lists $u$ and $v$, which is defined as ($n$ - $c_tt$) / $c_tt$ \
      where $n$ is len($u$) and $c_ij$ is \
      the number of occurrences of $u$[k]=i and $v$[$k$]=$j$ for $k$ < $n$.
    </dl>

    >> RussellRaoDissimilarity[{1, 0, 1, 1, 0, 1, 1}, {0, 1, 1, 0, 0, 0, 1}]
     = 5 / 7
    """

    summary_text = "Russell-Rao dissimilarity"

    def _compute(self, n, c_ff, c_ft, c_tf, c_tt):
        return Expression(SymbolDivide, Integer(n - c_tt), Integer(n))


class SokalSneathDissimilarity(_BooleanDissimilarity):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SokalSneathDissimilarity.html</url>

    <dl>
      <dt>'SokalSneathDissimilarity[$u$, $v$]'
      <dd>returns the Sokal-Sneath dissimilarity between the two boolean \
      1-D lists $u$ and $v$, which is defined as $R$ / (c_tt + $R$) where \
      $n$ is len($u$), $c_ij$ is the number of occurrences of \
      $u$[$k$]=$i$ and $v$[k]=$j$ for $k$ < $n$, \
      and $R$ = 2 * ($c_tf$ + $c_ft$).
    </dl>

    >> SokalSneathDissimilarity[{1, 0, 1, 1, 0, 1, 1}, {0, 1, 1, 0, 0, 0, 1}]
     = 4 / 5
    """

    summary_text = "Sokal-Sneath dissimilarity"

    def _compute(self, n, c_ff, c_ft, c_tf, c_tt):
        r = 2 * (c_tf + c_ft)
        return Expression(SymbolDivide, Integer(r), Integer(c_tt + r))


class Subsets(Builtin):
    """
    <url>
    :Subset:
    https://en.wikipedia.org/wiki/Subset</url> (<url>:WMA link:
    https://reference.wolfram.com/language/ref/Subsets.html</url>)

    <dl>
      <dt>'Subsets[$list$]'
      <dd>finds a list of all possible subsets of $list$.

      <dt>'Subsets[$list$, $n$]'
      <dd>finds a list of all possible subsets containing at most $n$ elements.

      <dt>'Subsets[$list$, {$n$}]'
      <dd>finds a list of all possible subsets containing exactly $n$ elements.

      <dt>'Subsets[$list$, {$min$, $max$}]'
      <dd>finds a list of all possible subsets containing between $min$ and \
          $max$ elements.

      <dt>'Subsets[$list$, $spec$, $n$]'
      <dd>finds a list of the first $n$ possible subsets.

      <dt>'Subsets[$list$, $spec$, {$n$}]'
      <dd>finds the $n$th possible subset.
    </dl>

    All possible subsets (power set):
    >> Subsets[{a, b, c}]
     = {{}, {a}, {b}, {c}, {a, b}, {a, c}, {b, c}, {a, b, c}}

    All possible subsets containing up to 2 elements:
    >> Subsets[{a, b, c, d}, 2]
     = {{}, {a}, {b}, {c}, {d}, {a, b}, {a, c}, {a, d}, {b, c}, {b, d}, {c, d}}

    Subsets containing exactly 2 elements:
    >> Subsets[{a, b, c, d}, {2}]
     = {{a, b}, {a, c}, {a, d}, {b, c}, {b, d}, {c, d}}

    The first 5 subsets containing 3 elements:
    >> Subsets[{a, b, c, d, e}, {3}, 5]
     = {{a, b, c}, {a, b, d}, {a, b, e}, {a, c, d}, {a, c, e}}

    All subsets with even length:
    >> Subsets[{a, b, c, d}, {0, 4, 2}]
     = {{}, {a, b}, {a, c}, {a, d}, {b, c}, {b, d}, {c, d}, {a, b, c, d}}

    The 25th subset:
    >> Subsets[Range[5], All, {25}]
     = {{2, 4, 5}}

    The odd-numbered subsets of {a,b,c,d} in reverse order:
    >> Subsets[{a, b, c, d}, All, {15, 1, -2}]
     = {{b, c, d}, {a, b, d}, {c, d}, {b, c}, {a, c}, {d}, {b}, {}}
    """

    messages = {
        "nninfseq": "Position 2 of `1` must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
    }

    rules = {
        "Subsets[list_ , Pattern[n,_List|All|DirectedInfinity[1]], spec_]": "Take[Subsets[list, n], spec]",
    }

    summary_text = "list all the subsets"

    def eval_list(self, list, evaluation):
        "Subsets[list_]"

        if isinstance(list, Atom):
            evaluation.message(
                "Subsets", "normal", Integer1, Expression(SymbolSubsets, list)
            )
        else:
            return self.eval_list_n(list, Integer(len(list.elements)), evaluation)

    def eval_list_n(self, list, n, evaluation):
        "Subsets[list_, n_]"

        expr = Expression(SymbolSubsets, list, n)
        if isinstance(list, Atom):
            evaluation.message("Subsets", "normal", Integer1, expr)
            return
        else:
            head_t = list.head
            # Note: "n" does not have to be an Integer.
            n_value = n.get_int_value()
            if n_value == 0:
                return ListExpression(ListExpression())
            if n_value is None or n_value < 0:
                evaluation.message("Subsets", "nninfseq", expr)
                return

            nested_list = [
                Expression(head_t, *c)
                for i in range(n_value + 1)
                for c in combinations(list.elements, i)
            ]

            return ListExpression(*nested_list)

    def eval_list_pattern(self, list, n, evaluation):
        "Subsets[list_, Pattern[n,_List|All|DirectedInfinity[1]]]"

        expr = Expression(SymbolSubsets, list, n)

        if isinstance(list, Atom):
            evaluation.message("Subsets", "normal", Integer1, expr)
            return
        else:
            head_t = list.head
            if n.get_name() == "System`All" or n.has_form("DirectedInfinity", 1):
                return self.eval_list(list, evaluation)

            n_len = len(n.elements)

            if n_len == 0:
                evaluation.message("Subsets", "nninfseq", expr)
                return

            elif n_len == 1:
                elem1 = n.elements[0].get_int_value()
                if elem1 is None or elem1 < 0:
                    evaluation.message("Subsets", "nninfseq", expr)
                    return
                min_n = elem1
                max_n = min_n + 1
                step_n = 1

            elif n_len == 2:
                elem1 = n.elements[0].get_int_value()
                elem2 = (
                    n.elements[1].get_int_value()
                    if not n.elements[1].has_form("DirectedInfinity", 1)
                    else len(list.elements) + 1
                )
                if elem1 is None or elem2 is None or elem1 < 0 or elem2 < 0:
                    evaluation.message("Subsets", "nninfseq", expr)
                    return
                min_n = elem1
                max_n = elem2 + 1
                step_n = 1

            elif n_len == 3:
                elem1 = n.elements[0].get_int_value()
                elem2 = (
                    n.elements[1].get_int_value()
                    if not n.elements[1].has_form("DirectedInfinity", 1)
                    else len(list.elements) + 1
                )
                elem3 = n.elements[2].get_int_value()
                if (
                    elem1 is None
                    or elem2 is None
                    or elem3 is None
                    or elem1 < 0
                    or elem2 < 0
                ):
                    evaluation.message("Subsets", "nninfseq", expr)
                    return
                step_n = elem3
                if step_n > 0:
                    min_n = elem1
                    max_n = elem2 + 1
                elif step_n < 0:
                    min_n = elem1
                    max_n = elem2 - 1
                else:
                    evaluation.message("Subsets", "nninfseq", expr)
                    return
            else:
                evaluation.message("Subsets", "nninfseq", expr)
                return

            nested_list = [
                Expression(head_t, *c)
                for i in range(min_n, max_n, step_n)
                for c in combinations(list.elements, i)
            ]

            return ListExpression(*nested_list)

    def eval_atom_pattern(self, list, n, spec, evaluation):
        "Subsets[list_?AtomQ, Pattern[n,_List|All|DirectedInfinity[1]], spec_]"

        evaluation.message(
            "Subsets", "normal", Integer1, Expression(SymbolSubsets, list, n, spec)
        )


class YuleDissimilarity(_BooleanDissimilarity):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/YuleDissimilarity.html</url>

    <dl>
      <dt>'YuleDissimilarity[$u$, $v$]'
      <dd>returns the Yule dissimilarity between the two boolean 1-D lists $u$ \
          and $v$, which is defined as $R$ / ($c_tt$ * $c_ff$ + $R$ / 2) \
          where $n$ is len($u$), $c_ij$ is the number of occurrences of \
          $u$[$k$]=$i$ and $v$[$k$]=$j$ for $k$<$n$, \
          and $R$ = 2 * $c_tf$ * $c_ft$.
    </dl>

    >> YuleDissimilarity[{1, 0, 1, 1, 0, 1, 1}, {0, 1, 1, 0, 0, 0, 1}]
     = 6 / 5
    """

    summary_text = "Yule dissimilarity"

    def _compute(self, n, c_ff, c_ft, c_tf, c_tt):
        r_half = c_tf * c_ft
        return Expression(
            SymbolDivide, Integer(2 * r_half), Integer(c_tt * c_ff + r_half)
        )
