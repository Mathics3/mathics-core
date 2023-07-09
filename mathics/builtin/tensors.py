# -*- coding: utf-8 -*-

"""
Tensors

A <url>:tensor: https://en.wikipedia.org/wiki/Tensor</url> is an algebraic \
object that describes a (multilinear) relationship between sets of algebraic \
objects related to a vector space. Objects that tensors may map between \
include vectors and scalars, and even other tensors.

There are many types of tensors, including scalars and vectors (which are \
the simplest tensors), dual vectors, multilinear maps between vector spaces, \
and even some operations such as the dot product. Tensors are defined \
independent of any basis, although they are often referred to by their \
components in a basis related to a particular coordinate system.

Mathics3 represents tensors of vectors and matrices as lists; tensors \
of any rank can be handled.
"""


from mathics.builtin.base import BinaryOperator, Builtin
from mathics.core.atoms import Integer, String
from mathics.core.attributes import A_FLAT, A_ONE_IDENTITY, A_PROTECTED
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolFalse, SymbolTrue
from mathics.eval.parts import get_part


def get_default_distance(p):
    if all(q.is_numeric() for q in p):
        return Symbol("SquaredEuclideanDistance")
    elif all(q.get_head_name() == "System`List" for q in p):
        dimensions = [get_dimensions(q) for q in p]
        if len(dimensions) < 1:
            return None
        d0 = dimensions[0]
        if not all(d == d0 for d in dimensions[1:]):
            return None
        if len(dimensions[0]) == 1:  # vectors?

            def is_boolean(x):
                return x.get_head_name() == "System`Symbol" and x in (
                    SymbolTrue,
                    SymbolFalse,
                )

            if all(all(is_boolean(e) for e in q.elements) for q in p):
                return Symbol("JaccardDissimilarity")
        return Symbol("SquaredEuclideanDistance")
    elif all(isinstance(q, String) for q in p):
        return Symbol("EditDistance")
    else:
        from mathics.builtin.colors.color_directives import expression_to_color

        if all(expression_to_color(q) is not None for q in p):
            return Symbol("ColorDistance")

        return None


def get_dimensions(expr, head=None):
    if isinstance(expr, Atom):
        return []
    else:
        if head is not None and not expr.head.sameQ(head):
            return []
        sub_dim = None
        sub = []
        for element in expr.elements:
            sub = get_dimensions(element, expr.head)
            if sub_dim is None:
                sub_dim = sub
            else:
                if sub_dim != sub:
                    sub = []
                    break
        return [len(expr.elements)] + sub


class ArrayDepth(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ArrayDepth.html</url>

    <dl>
      <dt>'ArrayDepth[$a$]'
      <dd>returns the depth of the non-ragged array $a$, defined as \
      'Length[Dimensions[$a$]]'.
    </dl>

    >> ArrayDepth[{{a,b},{c,d}}]
     = 2
    >> ArrayDepth[x]
     = 0
    """

    rules = {
        "ArrayDepth[list_]": "Length[Dimensions[list]]",
    }

    summary_text = "the rank of a tensor"


class Dimensions(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/Dimensions.html</url>

    <dl>
    <dt>'Dimensions[$expr$]'
        <dd>returns a list of the dimensions of the expression $expr$.
    </dl>

    A vector of length 3:
    >> Dimensions[{a, b, c}]
     = {3}

    A 3x2 matrix:
    >> Dimensions[{{a, b}, {c, d}, {e, f}}]
     = {3, 2}

    Ragged arrays are not taken into account:
    >> Dimensions[{{a, b}, {b, c}, {c, d, e}}]
     = {3}

    The expression can have any head:
    >> Dimensions[f[f[a, b, c]]]
     = {1, 3}

    #> Dimensions[{}]
     = {0}
    #> Dimensions[{{}}]
     = {1, 0}
    """

    summary_text = "the dimensions of a tensor"

    def eval(self, expr, evaluation: Evaluation):
        "Dimensions[expr_]"

        return ListExpression(*[Integer(dim) for dim in get_dimensions(expr)])


class Dot(BinaryOperator):
    """
    <url>:Dot product:https://en.wikipedia.org/wiki/Dot_product</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/Dot.html</url>)

    <dl>
      <dt>'Dot[$x$, $y$]'
      <dt>'$x$ . $y$'
      <dd>computes the vector dot product or matrix product $x$ . $y$.
    </dl>

    Scalar product of vectors:
    >> {a, b, c} . {x, y, z}
     = a x + b y + c z
    Product of matrices and vectors:
    >> {{a, b}, {c, d}} . {x, y}
     = {a x + b y, c x + d y}
    Matrix product:
    >> {{a, b}, {c, d}} . {{r, s}, {t, u}}
     = {{a r + b t, a s + b u}, {c r + d t, c s + d u}}
    >> a . b
     = a . b
    """

    operator = "."
    precedence = 490
    attributes = A_FLAT | A_ONE_IDENTITY | A_PROTECTED

    rules = {
        "Dot[a_List, b_List]": "Inner[Times, a, b, Plus]",
    }

    summary_text = "dot product"


class Inner(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/Inner.html</url>

    <dl>
    <dt>'Inner[$f$, $x$, $y$, $g$]'
        <dd>computes a generalised inner product of $x$ and $y$, using
        a multiplication function $f$ and an addition function $g$.
    </dl>

    >> Inner[f, {a, b}, {x, y}, g]
     = g[f[a, x], f[b, y]]

    'Inner' can be used to compute a dot product:
    >> Inner[Times, {a, b}, {c, d}, Plus] == {a, b} . {c, d}
     = True

    The inner product of two boolean matrices:
    >> Inner[And, {{False, False}, {False, True}}, {{True, False}, {True, True}}, Or]
     = {{False, False}, {True, True}}

    Inner works with tensors of any depth:
    >> Inner[f, {{{a, b}}, {{c, d}}}, {{1}, {2}}, g]
     = {{{g[f[a, 1], f[b, 2]]}}, {{g[f[c, 1], f[d, 2]]}}}


    ## Issue #670
    #> A = {{ b ^ ( -1 / 2), 0}, {a * b ^ ( -1 / 2 ), b ^ ( 1 / 2 )}}
     = {{1 / Sqrt[b], 0}, {a / Sqrt[b], Sqrt[b]}}
    #> A . Inverse[A]
     = {{1, 0}, {0, 1}}
    #> A
     = {{1 / Sqrt[b], 0}, {a / Sqrt[b], Sqrt[b]}}
    """

    messages = {
        "incom": (
            "Length `1` of dimension `2` in `3` is incommensurate with "
            "length `4` of dimension 1 in `5."
        ),
    }

    rules = {
        "Inner[f_, list1_, list2_]": "Inner[f, list1, list2, Plus]",
    }

    summary_text = "generalized inner product"

    def eval(self, f, list1, list2, g, evaluation: Evaluation):
        "Inner[f_, list1_, list2_, g_]"

        m = get_dimensions(list1)
        n = get_dimensions(list2)

        if not m or not n:
            evaluation.message("Inner", "normal")
            return
        if list1.get_head() != list2.get_head():
            evaluation.message("Inner", "heads", list1.get_head(), list2.get_head())
            return
        if m[-1] != n[0]:
            evaluation.message("Inner", "incom", m[-1], len(m), list1, n[0], list2)
            return

        head = list1.get_head()
        inner_dim = n[0]

        def rec(i_cur, j_cur, i_rest, j_rest):
            evaluation.check_stopped()
            if i_rest:
                elements = []
                for i in range(1, i_rest[0] + 1):
                    elements.append(rec(i_cur + [i], j_cur, i_rest[1:], j_rest))
                return Expression(head, *elements)
            elif j_rest:
                elements = []
                for j in range(1, j_rest[0] + 1):
                    elements.append(rec(i_cur, j_cur + [j], i_rest, j_rest[1:]))
                return Expression(head, *elements)
            else:

                def summand(i):
                    part1 = get_part(list1, i_cur + [i])
                    part2 = get_part(list2, [i] + j_cur)
                    return Expression(f, part1, part2)

                part = Expression(g, *[summand(i) for i in range(1, inner_dim + 1)])
                # cur_expr.elements.append(part)
                return part

        return rec([], [], m[:-1], n[1:])


class Outer(Builtin):
    """
    <url>:Outer product:https://en.wikipedia.org/wiki/Outer_product</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/Outer.html</url>)

    <dl>
      <dt>'Outer[$f$, $x$, $y$]'
      <dd>computes a generalised outer product of $x$ and $y$, using the function $f$ in place of multiplication.
    </dl>

    >> Outer[f, {a, b}, {1, 2, 3}]
     = {{f[a, 1], f[a, 2], f[a, 3]}, {f[b, 1], f[b, 2], f[b, 3]}}

    Outer product of two matrices:
    >> Outer[Times, {{a, b}, {c, d}}, {{1, 2}, {3, 4}}]
     = {{{{a, 2 a}, {3 a, 4 a}}, {{b, 2 b}, {3 b, 4 b}}}, {{{c, 2 c}, {3 c, 4 c}}, {{d, 2 d}, {3 d, 4 d}}}}

    'Outer' of multiple lists:
    >> Outer[f, {a, b}, {x, y, z}, {1, 2}]
     = {{{f[a, x, 1], f[a, x, 2]}, {f[a, y, 1], f[a, y, 2]}, {f[a, z, 1], f[a, z, 2]}}, {{f[b, x, 1], f[b, x, 2]}, {f[b, y, 1], f[b, y, 2]}, {f[b, z, 1], f[b, z, 2]}}}

    Arrays can be ragged:
    >> Outer[Times, {{1, 2}}, {{a, b}, {c, d, e}}]
     = {{{{a, b}, {c, d, e}}, {{2 a, 2 b}, {2 c, 2 d, 2 e}}}}

    Word combinations:
    >> Outer[StringJoin, {"", "re", "un"}, {"cover", "draw", "wind"}, {"", "ing", "s"}] // InputForm
     = {{{"cover", "covering", "covers"}, {"draw", "drawing", "draws"}, {"wind", "winding", "winds"}}, {{"recover", "recovering", "recovers"}, {"redraw", "redrawing", "redraws"}, {"rewind", "rewinding", "rewinds"}}, {{"uncover", "uncovering", "uncovers"}, {"undraw", "undrawing", "undraws"}, {"unwind", "unwinding", "unwinds"}}}

    Compositions of trigonometric functions:
    >> trigs = Outer[Composition, {Sin, Cos, Tan}, {ArcSin, ArcCos, ArcTan}]
     = {{Composition[Sin, ArcSin], Composition[Sin, ArcCos], Composition[Sin, ArcTan]}, {Composition[Cos, ArcSin], Composition[Cos, ArcCos], Composition[Cos, ArcTan]}, {Composition[Tan, ArcSin], Composition[Tan, ArcCos], Composition[Tan, ArcTan]}}
    Evaluate at 0:
    >> Map[#[0] &, trigs, {2}]
     = {{0, 1, 0}, {1, 0, 1}, {0, ComplexInfinity, 0}}
    """

    summary_text = "generalized outer product"

    def eval(self, f, lists, evaluation: Evaluation):
        "Outer[f_, lists__]"

        lists = lists.get_sequence()
        head = None
        for list in lists:
            if isinstance(list, Atom):
                evaluation.message("Outer", "normal")
                return
            if head is None:
                head = list.head
            elif not list.head.sameQ(head):
                evaluation.message("Outer", "heads", head, list.head)
                return

        def rec(item, rest_lists, current):
            evaluation.check_stopped()
            if isinstance(item, Atom) or not item.head.sameQ(head):
                if rest_lists:
                    return rec(rest_lists[0], rest_lists[1:], current + [item])
                else:
                    return Expression(f, *(current + [item]))
            else:
                elements = []
                for element in item.elements:
                    elements.append(rec(element, rest_lists, current))
                return Expression(head, *elements)

        return rec(lists[0], lists[1:], [])


class RotationTransform(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/RotationTransform.html</url>

    <dl>
      <dt>'RotationTransform[$phi$]'
      <dd>gives a rotation by $phi$.

      <dt>'RotationTransform[$phi$, $p$]'
      <dd>gives a rotation by $phi$ around the point $p$.
    </dl>
    """

    rules = {
        "RotationTransform[phi_]": "TransformationFunction[{{Cos[phi], -Sin[phi], 0}, {Sin[phi], Cos[phi], 0}, {0, 0, 1}}]",
        "RotationTransform[phi_, p_]": "TranslationTransform[p] . RotationTransform[phi] . TranslationTransform[-p]",
    }
    summary_text = "symbolic representation of a rotation in 3D"


class ScalingTransform(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ScalingTransform.html</url>

    <dl>
      <dt>'ScalingTransform[$v$]'
      <dd>gives a scaling transform of $v$. $v$ may be a scalar or a vector.

      <dt>'ScalingTransform[$phi$, $p$]'
      <dd>gives a scaling transform of $v$ that is centered at the point $p$.
    </dl>
    """

    rules = {
        "ScalingTransform[v_]": "TransformationFunction[DiagonalMatrix[Join[v, {1}]]]",
        "ScalingTransform[v_, p_]": "TranslationTransform[p] . ScalingTransform[v] . TranslationTransform[-p]",
    }
    summary_text = "symbolic representation of a scale transformation"


class ShearingTransform(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ShearingTransform.html</url>

    <dl>
    <dt>'ShearingTransform[$phi$, {1, 0}, {0, 1}]'
        <dd>gives a horizontal shear by the angle $phi$.
    <dt>'ShearingTransform[$phi$, {0, 1}, {1, 0}]'
        <dd>gives a vertical shear by the angle $phi$.
    <dt>'ShearingTransform[$phi$, $u$, $u$, $p$]'
        <dd>gives a shear centered at the point $p$.
    </dl>
    """

    rules = {
        "ShearingTransform[phi_, {1, 0}, {0, 1}]": "TransformationFunction[{{1, Tan[phi], 0}, {0, 1, 0}, {0, 0, 1}}]",
        "ShearingTransform[phi_, {0, 1}, {1, 0}]": "TransformationFunction[{{1, 0, 0}, {Tan[phi], 1, 0}, {0, 0, 1}}]",
        "ShearingTransform[phi_, u_, v_, p_]": "TranslationTransform[p] . ShearingTransform[phi, u, v] . TranslationTransform[-p]",
    }
    summary_text = "symbolic representation of a shearing transformation"


class TransformationFunction(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/TransformationFunction.html</url>

    <dl>
      <dt>'TransformationFunction[$m$]'
      <dd>represents a transformation.
    </dl>

    >> RotationTransform[Pi].TranslationTransform[{1, -1}]
     = TransformationFunction[{{-1, 0, -1}, {0, -1, 1}, {0, 0, 1}}]

    >> TranslationTransform[{1, -1}].RotationTransform[Pi]
     = TransformationFunction[{{-1, 0, 1}, {0, -1, -1}, {0, 0, 1}}]
    """

    rules = {
        "Dot[TransformationFunction[a_], TransformationFunction[b_]]": "TransformationFunction[a . b]",
        "TransformationFunction[m_][v_]": "Take[m . Join[v, {1}], Length[v]]",
    }
    summary_text = "general symbolic representation of transformation"


class TranslationTransform(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/TranslationTransform.html</url>

    <dl>
      <dt>'TranslationTransform[$v$]'
      <dd>gives a 'TransformationFunction' that translates points by vector $v$.
    </dl>

    >> t = TranslationTransform[{x0, y0}]
     = TransformationFunction[{{1, 0, x0}, {0, 1, y0}, {0, 0, 1}}]

    >> t[{x, y}]
     = {x + x0, y + y0}

    From <url>
    :Creating a Sierpinsky gasket with the missing triangles filled in:
    "https://mathematica.stackexchange.com/questions/7360/creating-a-sierpinski-gasket-with-the-missing-triangles-filled-in/7361#7361</url>:
    >> Show[Graphics[Table[Polygon[TranslationTransform[{Sqrt[3] (i - j/2), 3 j/2}] /@ {{Sqrt[3]/2, -1/2}, {0, 1}, {-Sqrt[3]/2, -1/2}}], {i, 7}, {j, i}]]]
     = -Graphics-
    """

    rules = {
        "TranslationTransform[v_]": "TransformationFunction[IdentityMatrix[Length[v] + 1] + "
        "(Join[ConstantArray[0, Length[v]], {#}]& /@ Join[v, {0}])]",
    }
    summary_text = "create a vector translation function"


class Transpose(Builtin):
    """
    <url>
    :Transpose: https://en.wikipedia.org/wiki/Transpose</url> (<url>
    :WMA: https://reference.wolfram.com/language/ref/Transpose.html</url>)

    <dl>
      <dt>'Tranpose[$m$]'
      <dd>transposes rows and columns in the matrix $m$.
    </dl>

    >> square = {{1, 2, 3}, {4, 5, 6}}; Transpose[square]
     = {{1, 4}, {2, 5}, {3, 6}}

    >> MatrixForm[%]
     = 1   4
     .
     . 2   5
     .
     . 3   6

    >> matrix = {{1, 2}, {3, 4}, {5, 6}}; MatrixForm[Transpose[matrix]]
     = 1   3   5
     .
     . 2   4   6

    Transpose is its own inverse. Transposing a matrix twice will give you back the same thing you started out with:

    >> Transpose[Transpose[matrix]] == matrix
     = True

    #> Clear[matrix, square]
    #> Transpose[x]
     = Transpose[x]
    """

    summary_text = "transpose to rearrange indices in any way"

    def eval(self, m, evaluation: Evaluation):
        "Transpose[m_?MatrixQ]"

        result = []
        for row_index, row in enumerate(m.elements):
            for col_index, item in enumerate(row.elements):
                if row_index == 0:
                    result.append([item])
                else:
                    result[col_index].append(item)
        return ListExpression(*[ListExpression(*row) for row in result])
