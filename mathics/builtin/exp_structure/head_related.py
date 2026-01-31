"""
Head-Related Operations
"""

from mathics.core.builtin import Builtin
from mathics.core.expression import Evaluation, Expression
from mathics.core.symbols import Atom
from mathics.core.systemsymbols import SymbolOperate


class Operate(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Operate.html</url>

    <dl>
      <dt>'Operate'[$p$, $expr$]
      <dd>applies $p$ to the head of $expr$.

      <dt>'Operate'[$p$, $expr$, $n$]
      <dd>applies $p$ to the $n$th head of $expr$.
    </dl>

    >> Operate[p, f[a, b]]
     = p[f][a, b]

    The default value of $n$ is 1:
    >> Operate[p, f[a, b], 1]
     = p[f][a, b]

    With $n$=0, 'Operate' acts like 'Apply':
    >> Operate[p, f[a][b][c], 0]
     = p[f[a][b][c]]
    """

    summary_text = "apply a function to the head of an expression"
    messages = {
        "intnn": "Non-negative integer expected at position `2` in `1`.",
    }

    def eval(self, p, expr, n, evaluation: Evaluation):
        "Operate[p_, expr_, Optional[n_, 1]]"

        head_depth = n.get_int_value()
        if head_depth is None or head_depth < 0:
            evaluation.message(
                "Operate", "intnn", Expression(SymbolOperate, p, expr, n), 3
            )
            return

        if head_depth == 0:
            # Act like Apply
            return Expression(p, expr)

        if isinstance(expr, Atom):
            return expr

        expr = expr.copy()
        e = expr

        for i in range(1, head_depth):
            e = e.head
            if isinstance(e, Atom):
                # n is higher than the depth of heads in expr: return
                # expr unmodified.
                return expr

        # Otherwise, if we get here, e.head points to the head we need
        # to apply p to. Python's reference semantics mean that this
        # assignment modifies expr as well.
        e.set_head(Expression(p, e.head))

        return expr


class Through(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Through.html</url>

    <dl>
      <dt>'Through'[$p$[$f$][$x$]]
      <dd>gives $p$[$f$[$x$]].
    </dl>

    >> Through[f[g][x]]
     = f[g[x]]
    >> Through[p[f, g][x]]
     = p[f[x], g[x]]
    """

    summary_text = "distribute operators that appears inside the head of expressions"

    def eval(self, p, args, x, evaluation: Evaluation):
        "Through[p_[args___][x___]]"

        elements = []
        for element in args.get_sequence():
            elements.append(Expression(element, *x.get_sequence()))
        return Expression(p, *elements)
