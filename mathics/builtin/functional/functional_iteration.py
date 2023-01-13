# -*- coding: utf-8 -*-
"""
Iteratively Applying Functions

Functional iteration is an elegant way to represent repeated operations that is used a lot.
"""

from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer1
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import SymbolDirectedInfinity

# This tells documentation how to sort this module
sort_order = "mathics.builtin.iteratively-applying-functions"


class FixedPoint(Builtin):
    """
    <dl>
      <dt>'FixedPoint[$f$, $expr$]'
      <dd>starting with $expr$, iteratively applies $f$ until the result no longer changes.

      <dt>'FixedPoint[$f$, $expr$, $n$]'
      <dd>performs at most $n$ iterations. The same that using $MaxIterations->n$
    </dl>

    >> FixedPoint[Cos, 1.0]
     = 0.739085

    >> FixedPoint[#+1 &, 1, 20]
     = 21

    #> FixedPoint[f, x, 0]
     = x
    #> FixedPoint[f, x, -1]
     : Non-negative integer expected.
     = FixedPoint[f, x, -1]
    #> FixedPoint[Cos, 1.0, Infinity]
     = 0.739085
    """

    options = {
        "MaxIterations": "Infinity",
        "SameTest": "Automatic",
    }

    summary_text = "nest until a fixed point is reached returning the last expression"

    def eval(self, f, expr, n, evaluation: Evaluation, options: dict):
        "FixedPoint[f_, expr_, n_:DirectedInfinity[1], OptionsPattern[FixedPoint]]"
        if n == Expression(SymbolDirectedInfinity, Integer1):
            count = None
        else:
            count = n.get_int_value()
            if count is None or count < 0:
                evaluation.message("FixedPoint", "intnn")
                return

        if count is None:
            count = self.get_option(options, "MaxIterations", evaluation)
            if count.is_numeric(evaluation):
                count = count.get_int_value()
            else:
                count = None

        result = expr
        index = 0
        sametest = self.get_option(options, "SameTest", evaluation)
        if sametest is Symbol("Automatic"):
            sametest = None

        while count is None or index < count:
            evaluation.check_stopped()
            new_result = Expression(f, result).evaluate(evaluation)
            if sametest:
                same = Expression(sametest, result, new_result).evaluate(evaluation)
                same = same is SymbolTrue
                if same:
                    break
            else:
                if new_result == result:
                    result = new_result
                    break
            result = new_result
            index += 1

        return result


class FixedPointList(Builtin):
    """
    <dl>
      <dt>'FixedPointList[$f$, $expr$]'
      <dd>starting with $expr$, iteratively applies $f$ until the result no longer changes, and returns a list of all intermediate results.

      <dt>'FixedPointList[$f$, $expr$, $n$]'
      <dd>performs at most $n$ iterations.
    </dl>

    >> FixedPointList[Cos, 1.0, 4]
     = {1., 0.540302, 0.857553, 0.65429, 0.79348}

    Observe the convergence of Newton's method for approximating square roots:
    >> newton[n_] := FixedPointList[.5(# + n/#) &, 1.];
    >> newton[9]
     = {1., 5., 3.4, 3.02353, 3.00009, 3., 3., 3.}

    Plot the "hailstone" sequence of a number:
    >> collatz[1] := 1;
    >> collatz[x_ ? EvenQ] := x / 2;
    >> collatz[x_] := 3 x + 1;
    >> list = FixedPointList[collatz, 14]
     = {14, 7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1, 1}
    >> ListLinePlot[list]
     = -Graphics-

    #> FixedPointList[f, x, 0]
     = {x}
    #> FixedPointList[f, x, -1]
     : Non-negative integer expected.
     = FixedPointList[f, x, -1]
    #> Last[FixedPointList[Cos, 1.0, Infinity]]
     = 0.739085
    """

    summary_text = "nest until a fixed point is reached return a list "

    def eval(self, f, expr, n, evaluation: Evaluation):
        "FixedPointList[f_, expr_, n_:DirectedInfinity[1]]"

        if n == Expression(SymbolDirectedInfinity, Integer1):
            count = None
        else:
            count = n.get_int_value()
            if count is None or count < 0:
                evaluation.message("FixedPoint", "intnn")
                return

        interm = expr
        result = [interm]

        index = 0
        while count is None or index < count:
            evaluation.check_stopped()

            new_result = Expression(f, interm).evaluate(evaluation)
            result.append(new_result)
            if new_result == interm:
                break

            interm = new_result
            index += 1

        return from_python(result)


class Fold(Builtin):
    """
    <dl>
      <dt>'Fold[$f$, $x$, $list$]'
      <dd>returns the result of iteratively applying the binary
        operator $f$ to each element of $list$, starting with $x$.
      <dt>'Fold[$f$, $list$]'
      <dd>is equivalent to 'Fold[$f$, First[$list$], Rest[$list$]]'.
    </dl>

    >> Fold[Plus, 5, {1, 1, 1}]
     = 8
    >> Fold[f, 5, {1, 2, 3}]
     = f[f[f[5, 1], 2], 3]
    """

    rules = {
        "Fold[exp_, x_, head_]": "Module[{list = Level[head, 1], res = x, i = 1}, Do[res = exp[res, list[[i]]], {i, 1, Length[list]}]; res]",
        "Fold[exp_, head_] /; Length[head] > 0": "Fold[exp, First[head], Rest[head]]",
    }
    summary_text = "iterative application of a binary operation over elements of a list"


class FoldList(Builtin):
    """
    <dl>
      <dt>'FoldList[$f$, $x$, $list$]'
      <dd>returns a list starting with $x$, where each element is
        the result of applying the binary operator $f$ to the previous
        result and the next element of $list$.
      <dt>'FoldList[$f$, $list$]'
      <dd>is equivalent to 'FoldList[$f$, First[$list$], Rest[$list$]]'.
    </dl>

    >> FoldList[f, x, {1, 2, 3}]
     = {x, f[x, 1], f[f[x, 1], 2], f[f[f[x, 1], 2], 3]}
    >> FoldList[Times, {1, 2, 3}]
     = {1, 2, 6}
    """

    rules = {
        "FoldList[exp_, x_, head_]": "Module[{i = 1}, Head[head] @@ Prepend[Table[Fold[exp, x, Take[head, i]], {i, 1, Length[head]}], x]]",
        "FoldList[exp_, head_]": "If[Length[head] == 0, head, FoldList[exp, First[head], Rest[head]]]",
    }
    summary_text = "list of the results of applying a binary operation interatively over elements of a list"


class Nest(Builtin):
    """
    <dl>
      <dt>'Nest[$f$, $expr$, $n$]'
      <dd>starting with $expr$, iteratively applies $f$ $n$ times and returns the final result.
    </dl>

    >> Nest[f, x, 3]
     = f[f[f[x]]]
    >> Nest[(1+#) ^ 2 &, x, 2]
     = (1 + (1 + x) ^ 2) ^ 2
    """

    summary_text = "give the result of nesting a function"

    def eval(self, f, expr, n, evaluation):
        "Nest[f_, expr_, n_Integer]"

        n = n.get_int_value()
        if n is None or n < 0:
            return
        result = expr
        for k in range(n):
            result = Expression(f, result).evaluate(evaluation)
        return result


class NestList(Builtin):
    """
    <dl>
      <dt>'NestList[$f$, $expr$, $n$]'
      <dd>starting with $expr$, iteratively applies $f$ $n$ times and \
          returns a list of all intermediate results.
    </dl>

    >> NestList[f, x, 3]
     = {x, f[x], f[f[x]], f[f[f[x]]]}
    >> NestList[2 # &, 1, 8]
     = {1, 2, 4, 8, 16, 32, 64, 128, 256}

    ## TODO: improve this example when RandomChoice, PointSize, Axes->False are implemented
    Chaos game rendition of the Sierpinski triangle:
    >> vertices = {{0,0}, {1,0}, {.5, .5 Sqrt[3]}};
    >> points = NestList[.5(vertices[[ RandomInteger[{1,3}] ]] + #) &, {0.,0.}, 500];
    >> Graphics[Point[points], ImageSize->Small]
     = -Graphics-
    """

    summary_text = "successively nest a function"

    def eval(self, f, expr, n, evaluation):
        "NestList[f_, expr_, n_Integer]"

        n = n.get_int_value()
        if n is None or n < 0:
            return

        interm = expr
        result = [interm]

        for k in range(n):
            interm = Expression(f, interm).evaluate(evaluation)
            result.append(interm)

        return from_python(result)


class NestWhile(Builtin):
    """
    <dl>
      <dt>'NestWhile[$f$, $expr$, $test$]'
      <dd>applies a function $f$ repeatedly on an expression $expr$, until \
          applying $test$ on the result no longer yields 'True'.

      <dt>'NestWhile[$f$, $expr$, $test$, $m$]'
      <dd>supplies the last $m$ results to $test$ (default value: 1).

      <dt>'NestWhile[$f$, $expr$, $test$, All]'
      <dd>supplies all results gained so far to $test$.
    </dl>

    Divide by 2 until the result is no longer an integer:
    >> NestWhile[#/2&, 10000, IntegerQ]
     = 625 / 2

    Calculate the sum of third powers of the digits of a number until the
    same result appears twice:
    >> NestWhile[Total[IntegerDigits[#]^3] &, 5, UnsameQ, All]
     = 371

    Print the intermediate results:
    >> NestWhile[Total[IntegerDigits[#]^3] &, 5, (Print[{##}]; UnsameQ[##]) &, All]
     | {5}
     | {5, 125}
     | {5, 125, 134}
     | {5, 125, 134, 92}
     | {5, 125, 134, 92, 737}
     | {5, 125, 134, 92, 737, 713}
     | {5, 125, 134, 92, 737, 713, 371}
     | {5, 125, 134, 92, 737, 713, 371, 371}
     = 371
    """

    summary_text = "nest while a condition is satisfied returning the last expression"

    rules = {
        "NestWhile[f_, expr_, test_]": "NestWhile[f, expr, test, 1]",
    }

    def eval(self, f, expr, test, m, evaluation: Evaluation):
        "NestWhile[f_, expr_, test_, Pattern[m,_Integer|All]]"

        results = [expr]
        while True:
            if m.get_name() == "System`All":
                test_elements = results
            else:
                test_elements = results[-m.value :]
            test_expr = Expression(test, *test_elements)
            test_result = test_expr.evaluate(evaluation)
            if test_result is SymbolTrue:
                next = Expression(f, results[-1])
                results.append(next.evaluate(evaluation))
            else:
                break
        return results[-1]


# TODO FoldPair, FoldPairList, LengthWhile, NestGraph, SequneceFold, SequenceFoldList, TakeWhile
