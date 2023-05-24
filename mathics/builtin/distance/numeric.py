"""
Numerical Data
"""

from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer1, Integer2
from mathics.core.expression import Evaluation, Expression
from mathics.core.symbols import (
    SymbolAbs,
    SymbolDivide,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
)
from mathics.core.systemsymbols import (
    SymbolDot,
    SymbolMax,
    SymbolNorm,
    SymbolSubtract,
    SymbolTotal,
)


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
      <dt>'BrayCurtisDistance[$u$, $v$]'
       <dd>returns the Bray-Curtis distance between $u$ and $v$.
    </dl>

    The Bray-Curtis distance is equivalent to Total[Abs[u-v]]/Total[Abs[u+v]].
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
      <dt>'CanberraDistance[$u$, $v$]'
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
      <dt>'ChessboardDistance[$u$, $v$]'
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
    https://en.wikipedia.org/wiki/Cosine_similarity</url> \
    (<url>:WMA:
    https://reference.wolfram.com/language/ref/CosineDistance.html</url>)

    <dl>
      <dt>'CosineDistance[$u$, $v$]'
      <dd>returns the cosine distance between $u$ and $v$.
    </dl>

    The cosine distance is given by $1 - u\cdot v/(Norm[u] Norm[v])=2\sin(\phi/2)^2$ with $\phi$
    the angle between both vectors.

    >> N[CosineDistance[{7, 9}, {71, 89}]]
     = 0.0000759646

    >> CosineDistance[{a, b}, {c, d}]
     = 1 + (-a c - b d) / (Sqrt[Abs[a] ^ 2 + Abs[b] ^ 2] Sqrt[Abs[c] ^ 2 + Abs[d] ^ 2])
    """

    summary_text = "cosine distance"

    def eval(self, u, v, evaluation: Evaluation):
        "CosineDistance[u_, v_]"
        dot = _norm_calc(SymbolDot, u, v, evaluation)
        if dot is not None:
            return Expression(
                SymbolSubtract,
                Integer1,
                Expression(
                    SymbolDivide,
                    dot,
                    Expression(
                        SymbolTimes,
                        Expression(SymbolNorm, u),
                        Expression(SymbolNorm, v),
                    ),
                ),
            )


class EuclideanDistance(Builtin):
    """
    <url>
    :Euclidean similarity:
    https://en.wikipedia.org/wiki/Euclidean_distance</url> \
    (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/EuclideanDistance.html</url>)

    <dl>
      <dt>'EuclideanDistance[$u$, $v$]'
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
      <dt>'ManhattanDistance[$u$, $v$]'
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
      <dt>'SquaredEuclideanDistance[$u$, $v$]'
      <dd>returns squared the euclidean distance between $u$ and $v$.
    </dl>

    >> SquaredEuclideanDistance[-7, 5]
     = 144

    >> SquaredEuclideanDistance[{-1, -1}, {1, 1}]
     = 8
    """

    summary_text = "square of the euclidean distance"

    def eval(self, u, v, evaluation: Evaluation):
        "SquaredEuclideanDistance[u_, v_]"
        t = _norm_calc(SymbolSubtract, u, v, evaluation)
        if t is not None:
            return Expression(SymbolPower, Expression(SymbolNorm, t), Integer2)
