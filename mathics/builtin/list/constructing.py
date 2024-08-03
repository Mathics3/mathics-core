# -*- coding: utf-8 -*-

"""
Constructing Lists

Functions for constructing lists of various sizes and structure.

See also Constructing Vectors.
"""

from itertools import permutations

from mathics.builtin.box.layout import RowBox
from mathics.core.atoms import Integer, is_integer_rational_or_real
from mathics.core.attributes import A_HOLD_FIRST, A_LISTABLE, A_LOCKED, A_PROTECTED
from mathics.core.builtin import Builtin, IterationFunction, Pattern
from mathics.core.convert.expression import to_expression
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import ElementsProperties
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, structure
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom
from mathics.core.systemsymbols import SymbolNormal
from mathics.eval.lists import get_tuples, list_boxes


class Array(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Array.html</url>

    <dl>
      <dt>'Array[$f$, $n$]'
      <dd>returns the $n$-element list '{$f$[1], ..., $f$[$n$]}'.

      <dt>'Array[$f$, $n$, $a$]'
      <dd>returns the $n$-element list '{$f$[$a$], ..., $f$[$a$ + $n$]}'.

      <dt>'Array[$f$, {$n$, $m$}, {$a$, $b$}]'
      <dd>returns an $n$-by-$m$ matrix created by applying $f$ to indices \
          ranging from '($a$, $b$)' to '($a$ + $n$, $b$ + $m$)'.

      <dt>'Array[$f$, $dims$, $origins$, $h$]'
      <dd>returns an expression with the specified dimensions and index origins, \
          with head $h$ (instead of 'List').
    </dl>

    >> Array[f, 4]
     = {f[1], f[2], f[3], f[4]}
    >> Array[f, {2, 3}]
     = {{f[1, 1], f[1, 2], f[1, 3]}, {f[2, 1], f[2, 2], f[2, 3]}}
    >> Array[f, {2, 3}, 3]
     = {{f[3, 3], f[3, 4], f[3, 5]}, {f[4, 3], f[4, 4], f[4, 5]}}
    >> Array[f, {2, 3}, {4, 6}]
     = {{f[4, 6], f[4, 7], f[4, 8]}, {f[5, 6], f[5, 7], f[5, 8]}}
    >> Array[f, {2, 3}, 1, Plus]
     = f[1, 1] + f[1, 2] + f[1, 3] + f[2, 1] + f[2, 2] + f[2, 3]
    """

    messages = {
        "plen": "`1` and `2` should have the same length.",
    }

    summary_text = "form an array by applying a function to successive indices"

    def eval(self, f, dimsexpr, origins, head, evaluation: Evaluation):
        "Array[f_, dimsexpr_, origins_:1, head_:List]"

        if dimsexpr.has_form("List", None):
            dims = dimsexpr.get_mutable_elements()
        else:
            dims = [dimsexpr]
        for index, dim in enumerate(dims):
            value = dim.get_int_value()
            if value is None:
                evaluation.message("Array", "ilsnn", 2)
                return
            dims[index] = value
        if origins.has_form("List", None):
            if len(origins.elements) != len(dims):
                evaluation.message("Array", "plen", dimsexpr, origins)
                return
            origins = origins.get_mutable_elements()
        else:
            origins = [origins] * len(dims)
        for index, origin in enumerate(origins):
            value = origin.get_int_value()
            if value is None:
                evaluation.message("Array", "ilsnn", 3)
                return
            origins[index] = value

        dims = list(zip(dims, origins))

        def rec(rest_dims, current):
            evaluation.check_stopped()
            if rest_dims:
                level = []
                count, origin = rest_dims[0]
                for index in range(origin, origin + count):
                    level.append(rec(rest_dims[1:], current + [index]))
                return Expression(head, *level)
            else:
                return to_expression(f, *current, elements_conversion_fn=Integer)

        return rec(dims, [])


class ConstantArray(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ConstantArray.html</url>

    <dl>
      <dt>'ConstantArray[$expr$, $n$]'
      <dd>returns a list of $n$ copies of $expr$.
    </dl>

    >> ConstantArray[a, 3]
     = {a, a, a}
    >> ConstantArray[a, {2, 3}]
     = {{a, a, a}, {a, a, a}}
    """

    summary_text = "form a constant array"
    rules = {
        "ConstantArray[c_, dims_]": "Apply[Table[c, ##]&, List /@ dims]",
        "ConstantArray[c_, n_Integer]": "ConstantArray[c, {n}]",
    }


class List(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/List.html</url>

    <dl>
      <dt>'List[$e1$, $e2$, ..., $ei$]'
      <dt>'{$e1$, $e2$, ..., $ei$}'
      <dd>represents a list containing the elements $e1$...$ei$.
    </dl>

    'List' is the head of lists:
    >> Head[{1, 2, 3}]
     = List

    Lists can be nested:
    >> {{a, b, {c, d}}}
     = {{a, b, {c, d}}}
    """

    attributes = A_LOCKED | A_PROTECTED
    summary_text = "form a list"

    def eval(self, elements, evaluation):
        """List[elements___]"""
        # Pick out the elements part of the parameter elements;
        # we we will call that `elements_part_of_elements__`.
        # Note that the parameter elements may be wrapped in a Sequence[]
        # so remove that if when it is present.
        elements_part_of_elements__ = elements.get_sequence()
        return ListExpression(*elements_part_of_elements__)

    def eval_makeboxes(self, items, f, evaluation):
        """MakeBoxes[{items___},
        f:StandardForm|TraditionalForm|OutputForm|InputForm|FullForm]"""

        items = items.get_sequence()
        return RowBox(*list_boxes(items, f, evaluation, "{", "}"))


class Normal(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Normal.html</url>

    <dl>
      <dt>'Normal[expr_]'
      <dd> Brings special expressions to a normal expression from different special \
           forms.
    </dl>
    """

    summary_text = "convert objects to normal expressions"

    def eval_general(self, expr, evaluation: Evaluation):
        "Normal[expr_]"
        if isinstance(expr, Atom):
            return
        return Expression(
            expr.get_head(),
            *[Expression(SymbolNormal, element) for element in expr.elements],
        )


range_list_elements_properties = ElementsProperties(
    elements_fully_evaluated=True, is_flat=True, is_ordered=True
)


class Range(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Range.html</url>

    <dl>
      <dt>'Range[$n$]'
      <dd>returns a list of integers from 1 to $n$.

      <dt>'Range[$a$, $b$]'
      <dd>returns a list of (Integer, Rational, Real) numbers from $a$ to $b$.

      <dt>'Range[$a$, $b$, $di$]'
      <dd>returns a list of numbers from $a$ to $b$ using step $di$.
        More specifically, 'Range' starts from $a$ and successively adds \
        increments of $di$ until the result is greater (if $di$ > 0) or \
        less (if $di$ < 0) than $b$.
    </dl>

    >> Range[5]
     = {1, 2, 3, 4, 5}

    >> Range[-3, 2]
     = {-3, -2, -1, 0, 1, 2}

    >> Range[5, 1, -2]
     = {5, 3, 1}

    >> Range[1.0, 2.3]
     = {1., 2.}

    >> Range[0, 2, 1/3]
     = {0, 1 / 3, 2 / 3, 1, 4 / 3, 5 / 3, 2}

    >> Range[1.0, 2.3, .5]
     = {1., 1.5, 2.}

    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "range": "Range specification does not have appropriate bounds.",
    }

    rules = {
        "Range[imax_]": "Range[1, imax, 1]",
        "Range[imin_, imax_]": "Range[imin, imax, 1]",
    }

    summary_text = "form a list from a range of numbers or other objects"

    def eval(self, imin, imax, di, evaluation: Evaluation):
        "Range[imin_, imax_, di_]"

        for arg in imin, imax, di:
            if not is_integer_rational_or_real(arg):
                evaluation.message(self.get_name(), "range")
                return

        if (
            isinstance(imin, Integer)
            and isinstance(imax, Integer)
            and isinstance(di, Integer)
        ):
            pm = 1 if di.value >= 0 else -1
            result = [Integer(i) for i in range(imin.value, imax.value + pm, di.value)]
            return ListExpression(
                *result, elements_properties=range_list_elements_properties
            )

        imin = imin.to_sympy()
        imax = imax.to_sympy()
        di = di.to_sympy()

        def compare_type(a, b):
            return a <= b if di >= 0 else a >= b

        index = imin
        result = []
        while compare_type(index, imax):
            evaluation.check_stopped()
            result.append(from_sympy(index))
            index += di
        return ListExpression(
            *result, elements_properties=range_list_elements_properties
        )


class Permutations(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Permutations.html</url>

    <dl>
      <dt>'Permutations[$list$]'
      <dd>gives all possible orderings of the items in $list$.

      <dt>'Permutations[$list$, $n$]'
      <dd>gives permutations up to length $n$.

      <dt>'Permutations[$list$, {$n$}]'
      <dd>gives permutations of length $n$.
    </dl>

    >> Permutations[{y, 1, x}]
     = {{y, 1, x}, {y, x, 1}, {1, y, x}, {1, x, y}, {x, y, 1}, {x, 1, y}}

    Elements are differentiated by their position in $list$, not their value.

    >> Permutations[{a, b, b}]
     = {{a, b, b}, {a, b, b}, {b, a, b}, {b, b, a}, {b, a, b}, {b, b, a}}

    >> Permutations[{1, 2, 3}, 2]
     = {{}, {1}, {2}, {3}, {1, 2}, {1, 3}, {2, 1}, {2, 3}, {3, 1}, {3, 2}}

    >> Permutations[{1, 2, 3}, {2}]
     = {{1, 2}, {1, 3}, {2, 1}, {2, 3}, {3, 1}, {3, 2}}
    """

    messages = {
        "argt": "Permutation expects at least one argument.",
        "nninfseq": "The number specified at position 2 of `` must be a non-negative "
        "integer, All, or Infinity.",
    }

    summary_text = "form permutations of a list"

    def eval_argt(self, evaluation: Evaluation):
        "Permutations[]"
        evaluation.message(self.get_name(), "argt")

    def eval(self, li, evaluation: Evaluation):
        "Permutations[li_List]"
        return ListExpression(
            *[ListExpression(*p) for p in permutations(li.elements, len(li.elements))],
        )

    def eval_n(self, li, n, evaluation: Evaluation):
        "Permutations[li_List, n_]"

        rs = None
        if isinstance(n, Integer):
            py_n = min(n.get_int_value(), len(li.elements))
        elif n.has_form("List", 1) and isinstance(n.elements[0], Integer):
            py_n = n.elements[0].get_int_value()
            rs = (py_n,)
        elif (
            n.has_form("DirectedInfinity", 1) and n.elements[0].get_int_value() == 1
        ) or n.get_name() == "System`All":
            py_n = len(li.elements)
        else:
            py_n = None

        if py_n is None or py_n < 0:
            evaluation.message(
                self.get_name(), "nninfseq", Expression(self.get_name(), li, n)
            )
            return

        if rs is None:
            rs = range(py_n + 1)

        inner = structure("List", li, evaluation)
        outer = structure("List", inner, evaluation)

        return outer([inner(p) for r in rs for p in permutations(li.elements, r)])


class Reap(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Reap.html</url>

    <dl>
      <dt>'Reap[$expr$]'
      <dd>gives the result of evaluating $expr$, together with all values \
          sown during this evaluation. Values sown with different tags \
          are given in different lists.

      <dt>'Reap[$expr$, $pattern$]'
      <dd>only yields values sown with a tag matching $pattern$.
        'Reap[$expr$]' is equivalent to 'Reap[$expr$, _]'.

      <dt>'Reap[$expr$, {$pattern1$, $pattern2$, ...}]'
      <dd>uses multiple patterns.

      <dt>'Reap[$expr$, $pattern$, $f$]'
      <dd>applies $f$ on each tag and the corresponding values sown \
          in the form '$f$[tag, {e1, e2, ...}]'.
    </dl>

    >> Reap[Sow[3]; Sow[1]]
     = {1, {{3, 1}}}

    >> Reap[Sow[2, {x, x, x}]; Sow[3, x]; Sow[4, y]; Sow[4, 1], {_Symbol, _Integer, x}, f]
     = {4, {{f[x, {2, 2, 2, 3}], f[y, {4}]}, {f[1, {4}]}, {f[x, {2, 2, 2, 3}]}}}

    Find the unique elements of a list, keeping their order:
    >> Reap[Sow[Null, {a, a, b, d, c, a}], _, # &][[2]]
     = {a, b, d, c}

    Sown values are reaped by the innermost matching 'Reap':
    >> Reap[Reap[Sow[a, x]; Sow[b, 1], _Symbol, Print["Inner: ", #1]&];, _, f]
     | Inner: x
     = {Null, {f[1, {b}]}}

    When no value is sown, an empty list is returned:
    >> Reap[x]
     = {x, {}}
    """

    summary_text = 'create lists of elements "sown" inside programs'
    attributes = A_HOLD_FIRST | A_PROTECTED

    rules = {
        "Reap[expr_, pattern_, f_]": (
            "{#[[1]], #[[2, 1]]}& [Reap[expr, {pattern}, f]]"
        ),
        "Reap[expr_, pattern_]": "Reap[expr, pattern, #2&]",
        "Reap[expr_]": "Reap[expr, _]",
    }

    def eval(self, expr, patterns, f, evaluation: Evaluation):
        "Reap[expr_, {patterns___}, f_]"

        patterns = patterns.get_sequence()
        sown = [(Pattern.create(pattern), []) for pattern in patterns]

        def listener(e, tag):
            result = False
            for pattern, items in sown:
                if pattern.does_match(tag, evaluation):
                    for item in items:
                        if item[0].sameQ(tag):
                            item[1].append(e)
                            break
                    else:
                        items.append((tag, [e]))
                    result = True
            return result

        evaluation.add_listener("sow", listener)
        try:
            result = expr.evaluate(evaluation)
            items = []
            for pattern, tags in sown:
                list_of_elements = []
                for tag, elements in tags:
                    list_of_elements.append(
                        Expression(f, tag, ListExpression(*elements))
                    )
                items.append(ListExpression(*list_of_elements))
            return ListExpression(result, ListExpression(*items))
        finally:
            evaluation.remove_listener("sow", listener)


class Sow(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Sow.html</url>

    <dl>
      <dt>'Sow[$e$]'
      <dd>sends the value $e$ to the innermost 'Reap'.

      <dt>'Sow[$e$, $tag$]'
      <dd>sows $e$ using $tag$. 'Sow[$e$]' is equivalent to 'Sow[$e$, Null]'.

      <dt>'Sow[$e$, {$tag1$, $tag2$, ...}]'
      <dd>uses multiple tags.
    </dl>
    """

    summary_text = "send an expression to the nearest enclosing Reap"
    rules = {
        "Sow[e_]": "Sow[e, {Null}]",
        "Sow[e_, tag_]": "Sow[e, {tag}]",
    }

    def eval(self, e, tags, evaluation: Evaluation):
        "Sow[e_, {tags___}]"

        tags = tags.get_sequence()
        for tag in tags:
            evaluation.publish("sow", e, tag)
        return e


class Table(IterationFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Table.html</url>

    <dl>
      <dt>'Table[$expr$, $n$]'
      <dd>generates a list of $n$ copies of $expr$.

      <dt>'Table[$expr$, {$i$, $n$}]'
      <dd>generates a list of the values of expr when $i$ runs from 1 to $n$.

      <dt>'Table[$expr$, {$i$, $start$, $stop$, $step$}]'
      <dd>evaluates $expr$ with $i$ ranging from $start$ to $stop$,
        incrementing by $step$.

      <dt>'Table[$expr$, {$i$, {$e1$, $e2$, ..., $ei$}}]'
      <dd>evaluates $expr$ with $i$ taking on the values $e1$, $e2$,
        ..., $ei$.
    </dl>

    >> Table[x, 3]
     = {x, x, x}
    >> n = 0; Table[n = n + 1, {5}]
     = {1, 2, 3, 4, 5}
    >> Table[i, {i, 4}]
     = {1, 2, 3, 4}
    >> Table[i, {i, 2, 5}]
     = {2, 3, 4, 5}
    >> Table[i, {i, 2, 6, 2}]
     = {2, 4, 6}
    >> Table[i, {i, Pi, 2 Pi, Pi / 2}]
     = {Pi, 3 Pi / 2, 2 Pi}
    >> Table[x^2, {x, {a, b, c}}]
     = {a ^ 2, b ^ 2, c ^ 2}

    'Table' supports multi-dimensional tables:
    >> Table[{i, j}, {i, {a, b}}, {j, 1, 2}]
     = {{{a, 1}, {a, 2}}, {{b, 1}, {b, 2}}}
    """

    rules = {
        "Table[expr_, n_Integer]": "Table[expr, {n}]",
    }

    summary_text = "make a table of values of an expression"

    def get_result(self, elements) -> ListExpression:
        return ListExpression(
            *elements,
            elements_properties=ElementsProperties(elements_fully_evaluated=True),
        )


class Tuples(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Tuples.html</url>

    <dl>
      <dt>'Tuples[$list$, $n$]'
      <dd>returns a list of all $n$-tuples of elements in $list$.

      <dt>'Tuples[{$list1$, $list2$, ...}]'
      <dd>returns a list of tuples with elements from the given lists.
    </dl>

    >> Tuples[{a, b, c}, 2]
     = {{a, a}, {a, b}, {a, c}, {b, a}, {b, b}, {b, c}, {c, a}, {c, b}, {c, c}}
    >> Tuples[{}, 2]
     = {}
    >> Tuples[{a, b, c}, 0]
     = {{}}

    >> Tuples[{{a, b}, {1, 2, 3}}]
     = {{a, 1}, {a, 2}, {a, 3}, {b, 1}, {b, 2}, {b, 3}}

    The head of $list$ need not be 'List':
    >> Tuples[f[a, b, c], 2]
     = {f[a, a], f[a, b], f[a, c], f[b, a], f[b, b], f[b, c], f[c, a], f[c, b], f[c, c]}
    However, when specifying multiple expressions, 'List' is always used:
    >> Tuples[{f[a, b], g[c, d]}]
     = {{a, c}, {a, d}, {b, c}, {b, d}}
    """

    summary_text = "form n-tuples from a list"

    def eval_n(self, expr, n: Integer, evaluation: Evaluation):
        "Tuples[expr_, n_Integer]"

        if isinstance(expr, Atom):
            evaluation.message("Tuples", "normal")
            return
        py_n = n.value
        if py_n is None or py_n < 0:
            evaluation.message("Tuples", "intnn")
            return
        items = expr.elements

        def iterate(n_rest):
            evaluation.check_stopped()
            if n_rest <= 0:
                yield []
            else:
                for item in items:
                    for rest in iterate(n_rest - 1):
                        yield [item] + rest

        return ListExpression(
            *(Expression(expr.head, *elements) for elements in iterate(py_n))
        )

    def eval_lists(self, exprs, evaluation: Evaluation):
        "Tuples[{exprs___}]"

        exprs = exprs.get_sequence()
        items = []
        for expr in exprs:
            evaluation.check_stopped()
            if isinstance(expr, Atom):
                evaluation.message("Tuples", "normal")
                return
            items.append(expr.elements)

        return ListExpression(
            *(ListExpression(*elements) for elements in get_tuples(items)),
        )
