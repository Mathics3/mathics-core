"""
Expression Tests
"""
from mathics.core.atoms import Integer0, Integer1, IntegerM1
from mathics.core.builtin import Builtin, PatternError, Test
from mathics.core.evaluation import Evaluation
from mathics.core.pattern import BasePattern
from mathics.core.symbols import SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolRule, SymbolRuleDelayed
from mathics.eval.patterns import match


class ListQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ListQ.html</url>

    <dl>
      <dt>'ListQ'[$expr$]
      <dd>tests whether $expr$ is a 'List'.
    </dl>

    >> ListQ[{1, 2, 3}]
     = True
    >> ListQ[{{1, 2}, {3, 4}}]
     = True
    >> ListQ[x]
     = False
    """

    summary_text = "test if an expression is a list"

    def test(self, expr) -> bool:
        return expr.get_head_name() == "System`List"


class MatchQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MatchQ.html</url>

    <dl>
      <dt>'MatchQ'[$expr$, $form$]
      <dd>tests whether $expr$ matches $form$.
    </dl>

    >> MatchQ[123, _Integer]
     = True
    >> MatchQ[123, _Real]
     = False
    >> MatchQ[_Integer][123]
     = True
    >> MatchQ[3, Pattern[3]]
     : First element in pattern Pattern[3] is not a valid pattern name.
     = False

    See also <url>
    :'Cases':
    /doc/reference-of-built-in-symbols/list-functions/elements-of-lists/cases/</url>.
    """

    rules = {"MatchQ[form_][expr_]": "MatchQ[expr, form]"}
    summary_text = "test whether an expression matches a pattern"

    def eval(self, expr, form, evaluation: Evaluation):
        "MatchQ[expr_, form_]"

        try:
            if match(expr, form, evaluation):
                return SymbolTrue
            return SymbolFalse
        except PatternError as e:
            evaluation.message(e.name, e.tag, *(e.args))
            return SymbolFalse


class Order(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Order.html</url>

    <dl>
      <dt>'Order'[$x$, $y$]
      <dd>returns a number indicating the canonical ordering of $x$ and $y$. \
         1 indicates that $x$ is before $y$, and -1 that $y$ is before $x$. \
         0 indicates that there is no specific ordering. Uses the same order \
         as 'Sort'.
    </dl>

    >> Order[7, 11]
     = 1

    >> Order[100, 10]
     = -1

    >> Order[x, z]
     = 1

    >> Order[x, x]
     = 0
    """

    summary_text = "order expressions"

    def eval(self, x, y, evaluation: Evaluation):
        "Order[x_, y_]"
        if x < y:
            return Integer1
        elif x > y:
            return IntegerM1
        else:
            return Integer0


class OrderedQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OrderedQ.html</url>

    <dl>
      <dt>'OrderedQ'[{$a$, $b$}]
      <dd>is 'True' if $a$ sorts before $b$ according to canonical
        ordering.
    </dl>

    >> OrderedQ[{a, b}]
     = True
    >> OrderedQ[{b, a}]
     = False
    """

    summary_text = "test whether elements are canonically sorted"

    def eval(self, expr, evaluation: Evaluation):
        "OrderedQ[expr_]"

        for index, value in enumerate(expr.elements[:-1]):
            if expr.elements[index] <= expr.elements[index + 1]:
                continue
            else:
                return SymbolFalse
        return SymbolTrue


# Note not in WMA anymore
class PatternsOrderedQ(Builtin):
    """
    <dl>
      <dt>'PatternsOrderedQ'[$patt1$, $patt2$]
      <dd>returns 'True' if pattern $patt1$ would be applied before
        $patt2$ according to canonical pattern ordering.
    </dl>

    >> PatternsOrderedQ[x__, x_]
     = False
    >> PatternsOrderedQ[x_, x__]
     = True
    >> PatternsOrderedQ[b, a]
     = True
    """

    summary_text = "test whether patterns are canonically sorted"

    def eval(self, p1, p2, evaluation: Evaluation):
        "PatternsOrderedQ[p1_, p2_]"
        # Convert the expressions into patterns first
        p1 = BasePattern.create(p1)
        p2 = BasePattern.create(p2)
        print("\np1:\n", p1.get_sort_key(True))
        print("\np2:\n", p2.get_sort_key(True))

        if p1.get_sort_key(True) <= p2.get_sort_key(True):
            return SymbolTrue
        else:
            return SymbolFalse
