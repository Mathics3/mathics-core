"""
Numerical Data
"""

# Don't use from ... import for eval functions so that
# tracers/debuggers can tap/switch eval functions
import mathics.eval.distance.numeric as distance_numeric
from mathics.core.atoms import Complex, Integer, Integer1, Integer2, Real
from mathics.core.builtin import Builtin
from mathics.core.expression import Evaluation, Expression
from mathics.core.symbols import (
    SymbolAbs,
    SymbolDivide,
    SymbolPlus,
    SymbolPower,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolMax,
    SymbolNorm,
    SymbolSubtract,
    SymbolTotal,
)
from mathics.eval.testing_expressions import eval_ArrayQ


def _norm_calc(head, u, v, evaluation: Evaluation):
    expr = Expression(head, u, v)
    old_quiet_all = evaluation.quiet_all
    try:
        evaluation.quiet_all = True
        expr_eval = expr.evaluate(evaluation)
    finally:
        evaluation.quiet_all = old_quiet_all
    if expr_eval.sameQ(expr):
        evaluation.message("Norm", "nvm")
        return None
    else:
        return expr_eval


class BrayCurtisDistance(Builtin):
    """
    <url>
    :Bray-Curtis Dissimilarity:
    https://en.wikipedia.org/wiki/Bray%E2%80%93Curtis_dissimilarity</url> \
    (<url>:WMA:
    https://reference.wolfram.com/language/ref/BrayCurtisDistance.html</url>)

    <dl>
      <dt>'BrayCurtisDistance'[$u$, $v$]
       <dd>returns the Bray-Curtis distance between $u$ and $v$.
    </dl>

    The Bray-Curtis distance is equivalent to 'Total[Abs[u-v]]/Total[Abs[u+v]]'.
    >> BrayCurtisDistance[-7, 5]
     = 6

    >> BrayCurtisDistance[{-1, -1}, {10, 10}]
     = 11 / 9
    """

    summary_text = "Bray-Curtis distance"

    def eval(self, u, v, evaluation: Evaluation):
        "BrayCurtisDistance[u_, v_]"
        t = _norm_calc(SymbolSubtract, u, v, evaluation)
        if t is not None:
            return Expression(
                SymbolDivide,
                Expression(SymbolTotal, Expression(SymbolAbs, t)),
                Expression(
                    SymbolTotal, Expression(SymbolAbs, Expression(SymbolPlus, u, v))
                ),
            )


class CanberraDistance(Builtin):
    """
    <url>
    :Canberra distance:
    https://en.wikipedia.org/wiki/Canberra_distance</url> \
    (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/CanberraDistance.html</url>)

    <dl>
      <dt>'CanberraDistance'[$u$, $v$]
       <dd>returns the canberra distance between $u$ and $v$, which is a weighted version of the Manhattan distance.
    </dl>

    >> CanberraDistance[-7, 5]
     = 1

    >> CanberraDistance[{-1, -1}, {1, 1}]
     = 2
    """

    summary_text = "Canberra distance"

    def eval(self, u, v, evaluation: Evaluation):
        "CanberraDistance[u_, v_]"
        t = _norm_calc(SymbolSubtract, u, v, evaluation)
        if t is not None:
            return Expression(
                SymbolTotal,
                Expression(
                    SymbolDivide,
                    Expression(SymbolAbs, t),
                    Expression(
                        SymbolPlus, Expression(SymbolAbs, u), Expression(SymbolAbs, v)
                    ),
                ),
            )


class ChessboardDistance(Builtin):
    """
    <url>:Chebyshev distance:https://en.wikipedia.org/wiki/Chebyshev_distance</url> \
    (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/ChessboardDistance.html</url>)

    <dl>
      <dt>'ChessboardDistance'[$u$, $v$]
      <dd>returns the chessboard distance (also known as Chebyshev distance) between $u$ and $v$, which is the number of moves a king on a chessboard needs to get from square $u$ to square $v$.
    </dl>

    >> ChessboardDistance[-7, 5]
     = 12

    >> ChessboardDistance[{-1, -1}, {1, 1}]
     = 2
    """

    summary_text = "chessboard distance"

    def eval(self, u, v, evaluation: Evaluation):
        "ChessboardDistance[u_, v_]"
        t = _norm_calc(SymbolSubtract, u, v, evaluation)
        if t is not None:
            return Expression(SymbolMax, Expression(SymbolAbs, t))


class CosineDistance(Builtin):
    r"""
    <url>
    :Cosine similarity:
    https://en.wikipedia.org/wiki/Cosine_similarity</url> (<url>:WMA:
    https://reference.wolfram.com/language/ref/CosineDistance.html</url>)

    <dl>
      <dt>'CosineDistance'[$u$, $v$]
      <dd>returns the angular cosine distance between vectors $u$ and $v$.
    </dl>

    The cosine distance is equivalent to $1 - (u.Conjugate[v]) / (Norm[u] Norm[v])$.

    >> N[CosineDistance[{7, 9}, {71, 89}]]
     = 0.0000759646

    When the length of either vector is 0, the result is 0:
    >> CosineDistance[{0.0, 0.0}, {x, y}]
     = 0

    >> CosineDistance[{1, 0}, {x, y}]
     = 1 - Conjugate[x] / Sqrt[Abs[x] ^ 2 + Abs[y] ^ 2]

    The order of the vectors influences the result:
    >> CosineDistance[{x, y}, {1, 0}]
     = 1 - x / Sqrt[Abs[x] ^ 2 + Abs[y] ^ 2]

    Cosine distance includes a dot product scaled by norms:
    >> CosineDistance[{a, b, c}, {x, y, z}]
     = 1 + (-a Conjugate[x] - b Conjugate[y] - c Conjugate[z]) / (Sqrt[Abs[a] ^ 2 + Abs[b] ^ 2 + Abs[c] ^ 2] Sqrt[Abs[x] ^ 2 + Abs[y] ^ 2 + Abs[z] ^ 2])

    A Cosine distance applied to complex numbers, uses 'Abs[]' for 'Norm[]' and complex multiplication for dot product,
    1 - $u$ * Conjugate[$v$] / ('Abs[$u$] Abs[$v$]'):

    >> CosineDistance[1+2I, 5]
     = 1 - (1 / 5 + 2 I / 5) Sqrt[5]
    """

    messages = {
        "bldim": "The arguments `1` and `2` do not have compatible dimensions.",
    }

    summary_text = "cosine distance"

    def eval(self, u, v, evaluation: Evaluation):
        "CosineDistance[u_, v_]"

        u_is_vector = eval_ArrayQ(u, Integer1, None, evaluation) is SymbolTrue
        v_is_vector = eval_ArrayQ(u, Integer1, None, evaluation) is SymbolTrue

        if not u_is_vector:
            if not isinstance(u, (Complex, Integer, Real)) and isinstance(
                v, (Complex, Integer, Real)
            ):
                return

            if v_is_vector:
                # u and v are not both vectors nor are they
                # both numeric scalars. There is nothing we can do here.
                return

            # FIXME: what to do about scalar vs vector?

        if v_is_vector:
            # Check dimensions.
            # FIXME: do we need something more general than len() here?
            if len(u.elements) != len(v.elements):
                evaluation.message("CosineDistance", "bldim", u, v)
                return

        # Note: use distance.eval_... not
        # eval_...  This allows tracers and debuggers
        # to redirect eval_ functions.
        return distance_numeric.eval_CosineDistance(u, v)


class EuclideanDistance(Builtin):
    """
    <url>
    :Euclidean similarity:
    https://en.wikipedia.org/wiki/Euclidean_distance</url> \
    (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/EuclideanDistance.html</url>)

    <dl>
      <dt>'EuclideanDistance'[$u$, $v$]
      <dd>returns the euclidean distance between $u$ and $v$.
    </dl>

    >> EuclideanDistance[-7, 5]
     = 12

    >> EuclideanDistance[{-1, -1}, {1, 1}]
     = 2 Sqrt[2]

    >> EuclideanDistance[{a, b}, {c, d}]
     = Sqrt[Abs[a - c] ^ 2 + Abs[b - d] ^ 2]
    """

    summary_text = "euclidean distance"

    def eval(self, u, v, evaluation: Evaluation):
        "EuclideanDistance[u_, v_]"
        t = _norm_calc(SymbolSubtract, u, v, evaluation)
        if t is not None:
            return Expression(SymbolNorm, t)


class ManhattanDistance(Builtin):
    """
    <url>
    :Manhattan distance:
    https://en.wikipedia.org/wiki/Taxicab_geometry</url> \
    (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/ManhattanDistance.html</url>)

    <dl>
      <dt>'ManhattanDistance'[$u$, $v$]
      <dd>returns the Manhattan distance between $u$ and $v$, which is the number of horizontal or vertical moves in the gridlike Manhattan city layout to get from $u$ to $v$.
    </dl>

    >> ManhattanDistance[-7, 5]
     = 12

    >> ManhattanDistance[{-1, -1}, {1, 1}]
     = 4
    """

    summary_text = "Manhattan distance"

    def eval(self, u, v, evaluation: Evaluation):
        "ManhattanDistance[u_, v_]"
        t = _norm_calc(SymbolSubtract, u, v, evaluation)
        if t is not None:
            return Expression(SymbolTotal, Expression(SymbolAbs, t))


class SquaredEuclideanDistance(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SquaredEuclideanDistance.html</url>

    <dl>
      <dt>'SquaredEuclideanDistance'[$u$, $v$]
      <dd>returns squared the euclidean distance between $u$ and $v$.
    </dl>

    >> SquaredEuclideanDistance[-7, 5]
     = 144

    >> SquaredEuclideanDistance[{-1, -1}, {1, 1}]
     = 8
    """

    summary_text = "compute square of the Euclidean distance"

    def eval(self, u, v, evaluation: Evaluation):
        "SquaredEuclideanDistance[u_, v_]"
        t = _norm_calc(SymbolSubtract, u, v, evaluation)
        if t is not None:
            return Expression(SymbolPower, Expression(SymbolNorm, t), Integer2)
