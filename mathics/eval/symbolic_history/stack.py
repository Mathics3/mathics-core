"""
Evaluation routines from mathics.builtin.symbolic_history.stack
"""

import inspect
from typing import Any, Callable, Tuple

import mathics.eval.tracing
from mathics.core.atoms import Symbol
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolConstant, SymbolHoldForm


def eval_Stack() -> ListExpression:
    """
    Display the Python call stack but filtered so that we Builtin calls.
    """

    frame = inspect.currentframe()
    assert frame is not None
    frame = frame.f_back
    frame_number = -2

    frames = []
    last_self_obj = None
    while frame is not None:
        is_builtin, self_obj = is_showable_frame(frame)
        if is_builtin:
            # The two frames are always Stacktrace[]
            # and Evaluate of that. So skip these.
            if frame_number > 0:
                if self_obj != last_self_obj:
                    if isinstance(self_obj, Expression):
                        frames.insert(0, Expression(SymbolHoldForm, self_obj))
                    else:
                        builtin_class = self_obj.__class__
                        mathics_builtin_name = builtin_class.__name__
                        frames.insert(0, Symbol(mathics_builtin_name))
                    last_self_obj = self_obj
            frame_number += 1
        frame = frame.f_back

    return ListExpression(*frames)


def save_evaluate(expr, evaluation, status: str, fn: Callable, orig_expr=None):
    """
    Called from a decorated Python @trace_evaluate .evaluate()
    method when Trace["evaluate" -> True]
    """

    # Test and dispose of various situations where showing information
    # is pretty useless: evaluating a Symbol is the Symbol.
    # Showing the return value of a ListExpression literal is
    # also useless.

    if isinstance(expr, Symbol) and not isinstance(expr, SymbolConstant):
        return

    if (
        status == "Returning"
        and hasattr(expr, "is_literal")
        and expr.is_literal
        and hasattr(orig_expr, "is_literal")
        and orig_expr.is_literal
    ):
        return

    if orig_expr == expr:
        # If the two expressions are the same, there is no point in
        # repeating the output.
        return

    # Below, We have to save not only the expression result but also
    # for returns where the return came from in order to prevent
    # seeing a return value twice, once form rewite_apply_eval_step,
    # and once from Expression.evaluate.

    fn_name = fn.__name__
    if orig_expr is not None:
        if fn_name == "rewrite_apply_eval_step":
            assert isinstance(expr, tuple)
            if orig_expr != expr[0]:
                evaluation.trace_info.append(
                    (fn_name, Expression(SymbolHoldForm, expr[0]))
                )
        else:
            evaluation.trace_info.append((fn_name, Expression(SymbolHoldForm, expr)))

    elif fn_name != "rewrite_apply_eval_step":
        evaluation.trace_info.append((fn_name, Expression(SymbolHoldForm, expr)))
    return


def eval_Trace(expr, evaluation: Evaluation) -> ListExpression:
    """
    Display the evaluation calls.
    """

    evaluation.trace_info = []
    old_evaluation_call_hook = mathics.eval.tracing.trace_evaluate_on_call
    old_evaluation_return_hook = mathics.eval.tracing.trace_evaluate_on_return

    mathics.eval.tracing.trace_evaluate_on_call = save_evaluate
    mathics.eval.tracing.trace_evaluate_on_return = save_evaluate

    try:
        expr.evaluate(evaluation)
    except Exception:
        raise
    finally:
        mathics.eval.tracing.trace_evaluate_on_call = old_evaluation_call_hook
        mathics.eval.tracing.trace_evaluate_on_return = old_evaluation_return_hook

    result = []
    # We can get duplicate results in returns as a result of
    # rewrite_eval_step returning and then evaluation returning.
    # So we filter this case out.

    last_expr = None
    last_fn_name = ""

    for fn_name, expr in evaluation.trace_info:
        if (
            not (last_fn_name == "rewrite_apply_eval_step" and fn_name == "evaluate")
            or last_expr != expr
        ):
            result.append(expr)
        last_fn_name = fn_name
        last_expr = expr

    return ListExpression(*result)


def is_showable_frame(frame) -> Tuple[bool, Any]:
    """
    Return True if frame is the frame for an eval() function of a
    Mathics3 Builtin function, {List,}Expression.evaluate(),
    or a rewrite step.

    We make the check based on whether the function name starts with "eval",
    has a "self" parameter and the class that self is an instance of the Builtin
    class.
    """
    from mathics.core.builtin import Builtin
    from mathics.core.expression import Expression

    if not inspect.isframe(frame):
        return False, None
    if not frame.f_code.co_name.startswith("eval"):
        return False, None
    self_obj = frame.f_locals.get("self")

    return isinstance(self_obj, (Builtin, Expression)), self_obj
