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

from mathics.core.atoms import Integer
from mathics.core.attributes import A_FLAT, A_ONE_IDENTITY, A_PROTECTED
from mathics.core.builtin import Builtin, InfixOperator
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.eval.tensors import (
    eval_Inner,
    eval_LeviCivitaTensor,
    eval_Outer,
    eval_Transpose,
    get_dimensions,
)


class ArrayDepth(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ArrayDepth.html</url>

    <dl>
      <dt>'ArrayDepth'[$a$]
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
    <dt>'Dimensions'[$expr$]
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
    """

    summary_text = "the dimensions of a tensor"

    def eval(self, expr, evaluation: Evaluation):
        "Dimensions[expr_]"

        return ListExpression(*[Integer(dim) for dim in get_dimensions(expr)])


class Dot(InfixOperator):
    """
    <url>:Dot product:https://en.wikipedia.org/wiki/Dot_product</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/Dot.html</url>)

    <dl>
      <dt>'Dot'[$x$, $y$]
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

    attributes = A_FLAT | A_ONE_IDENTITY | A_PROTECTED

    rules = {
        "Dot[a_List, b_List]": "Inner[Times, a, b, Plus]",
    }

    summary_text = "dot product"


class Inner(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/Inner.html</url>

    <dl>
    <dt>'Inner'[$f$, $x$, $y$, $g$]
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
    """

    messages = {
        "incom": (
            "Length `1` of dimension `2` in `3` is incommensurate with "
            "length `4` of dimension 1 in `5`."
        ),
    }

    rules = {
        "Inner[f_, list1_, list2_]": "Inner[f, list1, list2, Plus]",
    }

    summary_text = "generalized inner product"

    def eval(self, f, list1, list2, g, evaluation: Evaluation):
        "Inner[f_, list1_, list2_, g_]"

        return eval_Inner(f, list1, list2, g, evaluation)


class Outer(Builtin):
    """
    <url>:Outer product:https://en.wikipedia.org/wiki/Outer_product</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/Outer.html</url>)

    <dl>
      <dt>'Outer'[$f$, $x$, $y$]
      <dd>computes a generalised outer product of $x$ and $y$, using the function $f$ in place of multiplication.
    </dl>

    >> Outer[f, {a, b}, {1, 2, 3}]
     = {{f[a, 1], f[a, 2], f[a, 3]}, {f[b, 1], f[b, 2], f[b, 3]}}

    Outer product of two matrices:
    >> Outer[Times, {{a, b}, {c, d}}, {{1, 2}, {3, 4}}]
     = {{{{a, 2 a}, {3 a, 4 a}}, {{b, 2 b}, {3 b, 4 b}}}, {{{c, 2 c}, {3 c, 4 c}}, {{d, 2 d}, {3 d, 4 d}}}}

    Outer product of two sparse arrays:
    >> Outer[Times, SparseArray[{{1, 2} -> a, {2, 1} -> b}], SparseArray[{{1, 2} -> c, {2, 1} -> d}]]
     = SparseArray[Automatic, {2, 2, 2, 2}, 0, {{1, 2, 1, 2} -> a c, {1, 2, 2, 1} -> a d, {2, 1, 1, 2} -> b c, {2, 1, 2, 1} -> b d}]

    'Outer' of multiple lists:
    >> Outer[f, {a, b}, {x, y, z}, {1, 2}]
     = {{{f[a, x, 1], f[a, x, 2]}, {f[a, y, 1], f[a, y, 2]}, {f[a, z, 1], f[a, z, 2]}}, {{f[b, x, 1], f[b, x, 2]}, {f[b, y, 1], f[b, y, 2]}, {f[b, z, 1], f[b, z, 2]}}}

    'Outer' converts input sparse arrays to lists if f=!=Times, or if the input is a mixture of sparse arrays and lists:
    >> Outer[f, SparseArray[{{1, 2} -> a, {2, 1} -> b}], SparseArray[{{1, 2} -> c, {2, 1} -> d}]]
     = {{{{f[0, 0], f[0, c]}, {f[0, d], f[0, 0]}}, {{f[a, 0], f[a, c]}, {f[a, d], f[a, 0]}}}, {{{f[b, 0], f[b, c]}, {f[b, d], f[b, 0]}}, {{f[0, 0], f[0, c]}, {f[0, d], f[0, 0]}}}}

    >> Outer[Times, SparseArray[{{1, 2} -> a, {2, 1} -> b}], {c, d}]
     = {{{0, 0}, {a c, a d}}, {{b c, b d}, {0, 0}}}

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

        return eval_Outer(f, lists, evaluation)


class RotationTransform(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/RotationTransform.html</url>

    <dl>
      <dt>'RotationTransform'[$phi$]
      <dd>gives a rotation by $phi$.

      <dt>'RotationTransform'[$phi$, $p$]
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
      <dt>'ScalingTransform'[$v$]
      <dd>gives a scaling transform of $v$. $v$ may be a scalar or a vector.

      <dt>'ScalingTransform'[$phi$, $p$]
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
    <dt>'ShearingTransform'[$phi$, {1, 0}, {0, 1}]
        <dd>gives a horizontal shear by the angle $phi$.
    <dt>'ShearingTransform'[$phi$, {0, 1}, {1, 0}]
        <dd>gives a vertical shear by the angle $phi$.
    <dt>'ShearingTransform'[$phi$, $u$, $u$, $p$]
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
      <dt>'TransformationFunction'[$m$]
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
      <dt>'TranslationTransform'[$v$]
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
      <dt>'Transpose'[$list$]
      <dd>transposes the first two levels in $list$. The rank of $list$ should be less than 4.
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

    >> matrix3D = {{{1, 2}, {3, 4}}, {{5, 6}, {7, 8}}}; Transpose[matrix3D]
     = {{{1, 2}, {5, 6}}, {{3, 4}, {7, 8}}}

    Transpose is its own inverse. Transposing a matrix twice will give you back the same \
    thing you started out with:

    >> Transpose[Transpose[matrix]] == matrix
     = True

    >> Transpose[Transpose[matrix3D]] == matrix3D
     = True

    If the rank of the list is 0 or 1, you get the list back

    >> Transpose[{}]
     = {}

    >> Transpose[{a, b, c}]
     = {a, b, c}

    #> Clear[matrix, matrix3D, square]
    """

    summary_text = "transpose to rearrange indices in any way"

    def eval(self, m, evaluation: Evaluation):
        """Transpose[m_List]"""
        dimensions = get_dimensions(m)
        if dimensions is None:
            return
        n = len(dimensions)
        if not (0 <= n <= 3):
            return
        if n < 2:
            # Transpose of a 0 or 1-dimensional tensor is itself.
            return m
        if n == 3:
            n_0 = dimensions[0]
            if not all(sublist == n_0 for sublist in dimensions[1:]):
                return
        # FIXME: check 3D dimensions
        return eval_Transpose(m, n)


class ConjugateTranspose(Builtin):
    """
    <url>
    :Conjugate transpose: https://en.wikipedia.org/wiki/Conjugate_transpose</url> (<url>
    :WMA: https://reference.wolfram.com/language/ref/ConjugateTranspose.html</url>)

    <dl>
      <dt>'ConjugateTranspose'[$m$]
      <dd>gives the conjugate transpose of $m$.
    </dl>

    >> ConjugateTranspose[{{0, I}, {0, 0}}]
     = {{0, 0}, {-I, 0}}

    >> ConjugateTranspose[{{1, 2 I, 3}, {3 + 4 I, 5, I}}]
     = {{1, 3 - 4 I}, {-2 I, 5}, {3, -I}}
    """

    rules = {
        "ConjugateTranspose[m_]": "Conjugate[Transpose[m]]",
    }
    summary_text = "give the conjugate transpose"


class LeviCivitaTensor(Builtin):
    """
    <url>:Levi-Civita tensor:https://en.wikipedia.org/wiki/Levi-Civita_symbol</url> \
    (<url>:WMA link:https://reference.wolfram.com/language/ref/LeviCivitaTensor.html</url>)

    <dl>
      <dt>'LeviCivitaTensor'[$d$]
      <dd>gives the $d$-dimensional Levi-Civita totally antisymmetric tensor.
    </dl>

    >> LeviCivitaTensor[3]
     = SparseArray[Automatic, {3, 3, 3}, 0, {{1, 2, 3} -> 1, {1, 3, 2} -> -1, {2, 1, 3} -> -1, {2, 3, 1} -> 1, {3, 1, 2} -> 1, {3, 2, 1} -> -1}]

    >> LeviCivitaTensor[3, List]
     = {{{0, 0, 0}, {0, 0, 1}, {0, -1, 0}}, {{0, 0, -1}, {0, 0, 0}, {1, 0, 0}}, {{0, 1, 0}, {-1, 0, 0}, {0, 0, 0}}}
    """

    rules = {
        "LeviCivitaTensor[d_Integer]/; Greater[d, 0]": "LeviCivitaTensor[d, SparseArray]",
        "LeviCivitaTensor[d_Integer, List] /; Greater[d, 0]": "LeviCivitaTensor[d, SparseArray] // Normal",
    }

    summary_text = "give the Levi-Civita tensor with a given dimension"

    def eval(self, d, type, evaluation: Evaluation):
        "LeviCivitaTensor[d_Integer, type_]"

        return eval_LeviCivitaTensor(d, type)
