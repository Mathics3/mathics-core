"""
Expression Tests
"""
from mathics.builtin.base import Builtin, PatternError, Test
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import SymbolFalse, SymbolTrue
from mathics.eval.patterns import match


class ListQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ListQ.html</url>

    <dl>
      <dt>'ListQ[$expr$]'
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

    def test(self, expr):
        return expr.get_head_name() == "System`List"


class MatchQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MatchQ.html</url>

    <dl>
      <dt>'MatchQ[$expr$, $form$]'
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
