"""
List-Oriented Tests
"""

from mathics.builtin.base import Builtin, Test
from mathics.core.atoms import Integer, Integer1, Integer2
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import InvalidLevelspecError
from mathics.core.expression import Expression
from mathics.core.rules import Pattern
from mathics.core.symbols import Atom, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolSubsetQ
from mathics.eval.parts import python_levelspec


class ArrayQ(Builtin):
    """
    <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArrayQ.html</url>

    <dl>
      <dt>'ArrayQ[$expr$]'
      <dd>tests whether $expr$ is a full array.

      <dt>'ArrayQ[$expr$, $pattern$]'
      <dd>also tests whether the array depth of $expr$ matches $pattern$.

      <dt>'ArrayQ[$expr$, $pattern$, $test$]'
      <dd>furthermore tests whether $test$ yields 'True' for all elements of $expr$.
        'ArrayQ[$expr$]' is equivalent to 'ArrayQ[$expr$, _, True&]'.
    </dl>

    >> ArrayQ[a]
     = False
    >> ArrayQ[{a}]
     = True
    >> ArrayQ[{{{a}},{{b,c}}}]
     = False
    >> ArrayQ[{{a, b}, {c, d}}, 2, SymbolQ]
     = True
    """

    rules = {
        "ArrayQ[expr_]": "ArrayQ[expr, _, True&]",
        "ArrayQ[expr_, pattern_]": "ArrayQ[expr, pattern, True&]",
    }

    summary_text = "test whether an object is a tensor of a given rank"

    def eval(self, expr, pattern, test, evaluation: Evaluation):
        "ArrayQ[expr_, pattern_, test_]"

        pattern = Pattern.create(pattern)

        dims = [len(expr.get_elements())]  # to ensure an atom is not an array

        def check(level, expr):
            if not expr.has_form("List", None):
                test_expr = Expression(test, expr)
                if test_expr.evaluate(evaluation) != SymbolTrue:
                    return False
                level_dim = None
            else:
                level_dim = len(expr.elements)

            if len(dims) > level:
                if dims[level] != level_dim:
                    return False
            else:
                dims.append(level_dim)
            if level_dim is not None:
                for element in expr.elements:
                    if not check(level + 1, element):
                        return False
            return True

        if not check(0, expr):
            return SymbolFalse

        depth = len(dims) - 1  # None doesn't count
        if not pattern.does_match(Integer(depth), evaluation):
            return SymbolFalse
        return SymbolTrue


class DisjointQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/DisjointQ.html</url>

    <dl>
      <dt>'DisjointQ[$a$, $b$]'
      <dd>gives True if $a$ and $b$ are disjoint, or False if $a$ and \
      $b$ have any common elements.
    </dl>
    """

    rules = {"DisjointQ[a_List, b_List]": "Not[IntersectingQ[a, b]]"}
    summary_text = "test whether two lists do not have common elements"


class IntersectingQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/IntersectingQ.html</url>

    <dl>
      <dt>'IntersectingQ[$a$, $b$]'
      <dd>gives True if there are any common elements in $a and $b, or \
          False if $a and $b are disjoint.
    </dl>
    """

    rules = {"IntersectingQ[a_List, b_List]": "Length[Intersect[a, b]] > 0"}
    summary_text = "test whether two lists have common elements"


class LevelQ(Test):
    """
    <dl>
      <dt>'LevelQ[$expr$]'
      <dd>tests whether $expr$ is a valid level specification. This function \
          is primarily used in function patterns for specifying type of a \
          parameter.
    </dl>

    >> LevelQ[2]
     = True
    >> LevelQ[{2, 4}]
     = True
    >> LevelQ[Infinity]
     = True
    >> LevelQ[a + b]
     = False

    We will define MyMap with the "level" parameter as a synonym for the \
    Builtin Map equivalent:

    >> MyMap[f_, expr_, Pattern[levelspec, _?LevelQ]] := Map[f, expr, levelspec]

    >> MyMap[f, {{a, b}, {c, d}}, {2}]
      = {{f[a], f[b]}, {f[c], f[d]}}

    >> Map[f, {{a, b}, {c, d}}, {2}]
      = {{f[a], f[b]}, {f[c], f[d]}}

    But notice that when we pass an invalid level specification, MyMap \
    does not match and therefore does not pass the arguments through to 'Map'. \
    So we do not see the error message that 'Map' would normally produce

    >> Map[f, {{a, b}, {c, d}}, x]
     : Level specification x is not of the form n, {n}, or {m, n}.
     = Map[f, {{a, b}, {c, d}}, x]

    >> MyMap[f, {{a, b}, {c, d}}, {1, 2, 3}]
     = MyMap[f, {{a, b}, {c, d}}, {1, 2, 3}]
    """

    summary_text = "test whether is a valid level specification"

    def test(self, ls):
        try:
            start, stop = python_levelspec(ls)
            return True
        except InvalidLevelspecError:
            return False


class MatrixQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MatrixQ.html</url>

    <dl>
      <dt>'MatrixQ[$m$]'
      <dd>gives 'True' if $m$ is a list of equal-length lists.

      <dt>'MatrixQ[$m$, $f$]'
      <dd>gives 'True' only if '$f$[$x$]' returns 'True' for when applied to \
         element $x$ of the matrix $m$.
    </dl>

    >> MatrixQ[{{1, 3}, {4.0, 3/2}}, NumberQ]
     = True

    These are not matrices:
    >> MatrixQ[{{1}, {1, 2}}] (* first row should have length two *)
     = False

    >> MatrixQ[Array[a, {1, 1, 2}]]
     = False

    Supply a test function parameter to generalize and specialize:
    >> MatrixQ[{{1, 2}, {3, 4 + 5}}, Positive]
     = True

    >> MatrixQ[{{1, 2 I}, {3, 4 + 5}}, Positive]
     = False
    """

    rules = {
        "MatrixQ[expr_]": "ArrayQ[expr, 2]",
        "MatrixQ[expr_, test_]": "ArrayQ[expr, 2, test]",
    }

    summary_text = "gives 'True' if the given argument is a list of equal-length lists"


class MemberQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MemberQ.html</url>

    <dl>
      <dt>'MemberQ[$list$, $pattern$]'
      <dd>returns 'True' if $pattern$ matches any element of $list$, or 'False' otherwise.
    </dl>

    >> MemberQ[{a, b, c}, b]
     = True
    >> MemberQ[{a, b, c}, d]
     = False
    >> MemberQ[{"a", b, f[x]}, _?NumericQ]
     = False
    >> MemberQ[_List][{{}}]
     = True
    """

    rules = {
        "MemberQ[list_, pattern_]": ("Length[Select[list, MatchQ[#, pattern]&]] > 0"),
        "MemberQ[pattern_][expr_]": "MemberQ[expr, pattern]",
    }
    summary_text = "test whether an element is a member of a list"


class NotListQ(Test):
    """
    <dl>
      <dt>'NotListQ[$expr$]'
      <dd>returns 'True' if $expr$ is not a list. This function is primarily \
          used in function patterns for specifying type of a parameter.
    </dl>

    Consider this definition for taking the deriviate 'Sin' of a function:

    >> MyD[Sin[f_],x_?NotListQ] := D[f,x]*Cos[f]
     =

    We use "MyD" above to distinguish it from the Builtin 'D'. Now let's try it:

    >> MyD[Sin[2 x], x]
     = 2 Cos[2 x]

    And compare it with the Builtin deriviative function 'D':

    >> D[Sin[2 x], x]
     = 2 Cos[2 x]

    Note however the pattern only matches if the $x$ parameter is not a list:

    >> MyD[{Sin[2], Sin[4]}, {1, 2}]
     = MyD[{Sin[2], Sin[4]}, {1, 2}]

    """

    summary_text = "test if an expression is not a list"

    def test(self, expr):
        return expr.get_head_name() != "System`List"


class SubsetQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SubsetQ.html</url>

    <dl>
      <dt>'SubsetQ[$list1$, $list2$]'
      <dd>returns True if $list2$ is a subset of $list1$, and False otherwise.
    </dl>

    >> SubsetQ[{1, 2, 3}, {3, 1}]
     = True

    The empty list is a subset of every list:
    >> SubsetQ[{}, {}]
     = True

    >> SubsetQ[{1, 2, 3}, {}]
     = True

    Every list is a subset of itself:
    >> SubsetQ[{1, 2, 3}, {1, 2, 3}]
     = True

    #> SubsetQ[{1, 2, 3}, {0, 1}]
     = False

    #> SubsetQ[{1, 2, 3}, {1, 2, 3, 4}]
     = False

    #> SubsetQ[{1, 2, 3}]
     : SubsetQ called with 1 argument; 2 arguments are expected.
     = SubsetQ[{1, 2, 3}]

    #> SubsetQ[{1, 2, 3}, {1, 2}, {3}]
     : SubsetQ called with 3 arguments; 2 arguments are expected.
     = SubsetQ[{1, 2, 3}, {1, 2}, {3}]

    #> SubsetQ[a + b + c, {1}]
     : Heads Plus and List at positions 1 and 2 are expected to be the same.
     = SubsetQ[a + b + c, {1}]

    #> SubsetQ[{1, 2, 3}, n]
     : Nonatomic expression expected at position 2 in SubsetQ[{1, 2, 3}, n].
     = SubsetQ[{1, 2, 3}, n]

    #> SubsetQ[f[a, b, c], f[a]]
     = True
    """

    messages = {
        # FIXME: This message doesn't exist in more modern WMA, and
        # Subset *can* take more than 2 arguments.
        "argr": "SubsetQ called with 1 argument; 2 arguments are expected.",
        "argrx": "SubsetQ called with `1` arguments; 2 arguments are expected.",
        "heads": "Heads `1` and `2` at positions 1 and 2 are expected to be the same.",
        "normal": "Nonatomic expression expected at position `1` in `2`.",
    }
    summary_text = "test if a list is a subset of another list"

    def eval(self, expr, subset, evaluation: Evaluation):
        "SubsetQ[expr_, subset___]"

        if isinstance(expr, Atom):
            evaluation.message(
                "SubsetQ", "normal", Integer1, Expression(SymbolSubsetQ, expr, subset)
            )
            return

        subset = subset.get_sequence()
        if len(subset) > 1:
            evaluation.message("SubsetQ", "argrx", Integer(len(subset) + 1))
            return
        elif len(subset) == 0:
            evaluation.message("SubsetQ", "argr")
            return

        subset = subset[0]
        if isinstance(subset, Atom):
            evaluation.message(
                "SubsetQ", "normal", Integer2, Expression(SymbolSubsetQ, expr, subset)
            )
            return
        if expr.get_head_name() != subset.get_head_name():
            evaluation.message("SubsetQ", "heads", expr.get_head(), subset.get_head())
            return

        if set(subset.elements).issubset(set(expr.elements)):
            return SymbolTrue
        else:
            return SymbolFalse


class VectorQ(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/VectorQ.html</url>

    <dl>
      <dt>'VectorQ[$v$]'
      <dd>returns 'True' if $v$ is a list of elements which are not themselves lists.

      <dt>'VectorQ[$v$, $f$]'
      <dd>returns 'True' if $v$ is a vector and '$f$[$x$]' returns 'True' for each element $x$ of $v$.
    </dl>

    >> VectorQ[{a, b, c}]
     = True
    """

    rules = {
        "VectorQ[expr_]": "ArrayQ[expr, 1]",
        "VectorQ[expr_, test_]": "ArrayQ[expr, 1, test]",
    }
    summary_text = "test whether an object is a vector"


# TODO DuplicateFreeQ
