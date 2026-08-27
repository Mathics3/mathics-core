"""
Assumptions and functions that Use Assumptions.
"""

from mathics.builtin.scoping import dynamic_scoping
from mathics.core.attributes import A_HOLD_REST, A_NO_ATTRIBUTES, A_PROTECTED
from mathics.core.builtin import Builtin, Predefined
from mathics.core.convert.sympy_predicates import to_sympy_predicates
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.eval.assumptions.assumptions import eval_Refine
from mathics.eval.inference import get_assumptions_list


class Assuming(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Assuming.html</url>

    <dl>
      <dt>'Assuming'[$cond$, $expr$]
      <dd>Evaluates $expr$ assuming the conditions $cond$.
    </dl>

    >> $Assumptions = { x > 0 }
     = {x > 0}
    >> Assuming[y>0, ConditionalExpression[y x^2, y>0]//Simplify]
     = x ^ 2 y
    >> Assuming[Not[y>0], ConditionalExpression[y x^2, y>0]//Simplify]
     = Undefined
    >> ConditionalExpression[y x ^ 2, y > 0]//Simplify
     = ConditionalExpression[x ^ 2 y, y > 0]
    """

    summary_text = "set assumptions during the evaluation"
    attributes = A_HOLD_REST | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = 2

    def eval_assuming(self, assumptions, expr, evaluation: Evaluation):
        "Assuming[assumptions_, expr_]"
        assumptions = assumptions.evaluate(evaluation)
        if assumptions is SymbolTrue:
            cond = []
        elif isinstance(assumptions, Symbol) or not assumptions.has_form("List", None):
            cond = [assumptions]
        else:
            cond = assumptions.elements
        cond = tuple(cond) + get_assumptions_list(evaluation)
        list_cond = ListExpression(*cond)
        # TODO: reduce the list of predicates
        return dynamic_scoping(
            lambda ev: expr.evaluate(ev), {"System`$Assumptions": list_cond}, evaluation
        )


class Assumptions(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$Assumptions.html</url>
    <dl>
      <dt>'\$Assumptions'
      <dd>is the default setting for the 'Assumptions' option used in such functions as 'Simplify', 'Refine', and 'Integrate'.
    </dl>
    """

    summary_text = "assumptions used to simplify expressions"
    name = "$Assumptions"
    attributes = A_NO_ATTRIBUTES
    rules = {
        "$Assumptions": "True",
    }

    messages = {
        "faas": "Assumptions should not be False.",
        "baas": "Bad formed assumption.",
    }


class Refine(Builtin):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/Refine.html</url>

    <dl>
      <dt>'Refine'[$expr$, $assum$]
      <dd>Simplifies $expr$ that would be obtained if symbols in it were replaced \
      by explicit numerical expressions satisfying the assumptions $assum$.
    </dl>

    'Sqrt' would normally give two roots, but there is only one when we assume we started \
    out with a positive number in $x$:
    >> Refine[Sqrt[x^6], x > 0]
     = x ^ 3

    And now the negative root:
    >> Refine[Sqrt[x^6], x < 0]
     = -x ^ 3

    'Refine' works over domains, such as the real domain:
    >> Refine[Re[x], Element[x, Reals]]
     = x

    And also the rational domains:
    >> Refine[Im[x], Element[x, Rationals]]
     = 0

    ## Bugs in SymPy's refine:
    ## >> Assuming[x >= 0 && y < 0, If[TrueQ[Refine[x - y > 0]], Refine[Sqrt[x^2 y^2]], 0]]
    ##  = x ^ 2 y
    ## Come back to:
    ## >> Assuming[Not[y>0], ConditionalExpression[y x^2, y>0]//Simplify]
    ##  = -xy
    """

    attributes = A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = (1, 2)

    options = {
        "Assumptions": "$Assumptions",
    }

    rules = {
        "Refine[expr_]": "Refine[expr, $Assumptions]",
    }

    summary_text = "simplify an expression according to some criteria"
    sympy_name = "refine"

    def eval(self, expr, assumptions, evaluation: Evaluation):
        "Refine[expr_, assumptions_]"

        # Evaluate the assumptions argument, if provided.
        if assumptions is not None:
            assumptions_eval = assumptions.evaluate(evaluation)
        else:
            assumptions_eval = Symbol("$Assumptions").evaluate(evaluation)

        if assumptions_eval is SymbolFalse:
            evaluation.message("Refine", "fas")

        # If assumptions are trivial, just evaluate expr normally.
        if assumptions_eval is SymbolTrue or assumptions_eval is None:
            return expr.evaluate(evaluation)

        sympy_assumptions = to_sympy_predicates(assumptions_eval)
        return eval_Refine(expr, sympy_assumptions, evaluation)
