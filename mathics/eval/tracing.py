"""
Debug Tracing and Trace-Event handlers.

This is how we support external (Mathics3 module) debuggers and tracers.
"""

import inspect
import time
from enum import Enum
from typing import Any, Callable, Optional

TraceEventNames = ("SymPy", "Numpy", "mpmath", "apply", "evaluate", "debugger")
TraceEvent = Enum("TraceEvent", TraceEventNames)


hook_entry_fn: Optional[Callable] = None
hook_exit_fn: Optional[Callable] = None


def is_performing_rewrite(func) -> bool:
    """ "
    Returns true if we are in the rewrite expression phase
    as opposed to the apply-function/evaluation phase of
    evaluation. The way we determine this is highly specific
    to the Mathics3 code as it stands right now. So this
    code is highly fragile and can change when the
    evaluation code changes. However encapsulating this
    in a function helps narrows the fragility to one place.
    """
    return hasattr(func, "__name__") and func.__name__ == "rewrite_apply_eval_step"


def skip_trivial_evaluation(expr, status: str, orig_expr=None) -> bool:
    """
    Look for uninteresting evaluations that we should avoid showing
    printing tracing status or stopping in a debugger.

    This includes things like:
    * the evaluation is a literal that evaluates to the same thing,
    * evaluating a Symbol which the Symbol.
    * Showing the return value of a ListExpression literal
    * Evaluating Pattern[] which define a pattern.
    """
    from mathics.core.expression import Expression
    from mathics.core.symbols import Symbol, SymbolConstant
    from mathics.core.systemsymbols import SymbolBlank, SymbolPattern

    if isinstance(expr, tuple):
        expr = expr[0]

    if isinstance(expr, Expression):
        if expr.head in (SymbolPattern, SymbolBlank):
            return True

    if status == "Returning":
        if (
            hasattr(expr, "is_literal")
            and expr.is_literal
            and hasattr(orig_expr, "is_literal")
            and orig_expr.is_literal
        ):
            return True
        pass
        if isinstance(expr, Symbol) and not isinstance(expr, SymbolConstant):
            # Evaluation of a symbol, like Plus isn't that interesting.
            # Right now, SymbolConstant are not literals. If this
            # changes, we don't need this clause.
            return True

    else:
        # Status != "Returning", i.e. executing

        if isinstance(expr, Symbol):
            # Evaluation of a symbol, like Plus isn't that interesting
            return True

        if orig_expr == expr:
            # If the two expressions are the same, there is no point in
            # repeating the output.
            return True

    return False


def print_evaluate(expr, evaluation, status: str, fn: Callable, orig_expr=None):
    """
    Called from a decorated Python @trace_evaluate .evaluate()
    method when TraceActivate["evaluate" -> True] or
    running TraceEvaluation.
    """

    if evaluation.definitions.timing_trace_evaluation:
        evaluation.print_out(time.time() - evaluation.start_time)

    if skip_trivial_evaluation(expr, status, orig_expr):
        return

    indents = "  " * evaluation.recursion_depth

    if orig_expr is not None:
        if is_performing_rewrite(fn):
            assert isinstance(expr, tuple)
            if orig_expr != expr[0]:
                if status == "Returning":
                    if expr[1] and evaluation.definitions.trace_show_rewrites:
                        status = "Rewriting"
                        arrow = " -> "
                    else:
                        return
                else:
                    arrow = " = "
                    return

                evaluation.print_out(
                    f"{indents}{status}: {expr[0]}" + arrow + str(expr)
                )
        else:
            if status == "Returning" and isinstance(expr, tuple):
                if not evaluation.definitions.trace_show_rewrite:
                    return
                status = "Replacing"
                expr = expr[0]
            elif not evaluation.definitions.trace_evaluation:
                return
            expr_str = str(expr)
            if status == "Replacing" and orig_expr == expr_str:
                return
            evaluation.print_out(f"{indents}{status}: {orig_expr} = {expr_str}")

    elif not is_performing_rewrite(fn):
        if not evaluation.definitions.trace_evaluation:
            return
        evaluation.print_out(f"{indents}{status}: {expr}")
    return


# When not None, evaluate() methods call this
# to show the status of evaluation on entry and return.
trace_evaluate_on_call: Optional[Callable] = None
trace_evaluate_on_return: Optional[Callable] = None


def trace_evaluate(func: Callable) -> Callable:
    """
    Wrap a method evaluate() call event with trace_evaluate_on_call()
    and trace_evaluate_on_return() callback so we can trace the
    progress in evaluation.
    """

    def wrapper(expr, evaluation) -> Any:
        from mathics.core.symbols import SymbolConstant

        # trace_evaluate_action allows for trace_evaluate_on_call()
        # and trace_evaluate_return() to set the value of the
        # expression instead of calling the function or replacing
        # of return value of a Mathics3 function call.
        trace_evaluate_action: Optional[Any] = None
        result = None
        was_boxing = evaluation.is_boxing
        if (
            trace_evaluate_on_call is not None
            and not evaluation.is_boxing
            and not isinstance(expr, SymbolConstant)
        ):
            # We may use boxing in print_evaluate_fn(). So turn off
            # boxing temporarily.
            phase_name = "Rewriting" if is_performing_rewrite(func) else "Evaluating"
            evaluation.is_boxing = True
            trace_evaluate_action = trace_evaluate_on_call(
                expr, evaluation, phase_name, func
            )
            evaluation.is_boxing = was_boxing
        if trace_evaluate_action is None:
            result = func(expr, evaluation)
            if trace_evaluate_on_return is not None and not was_boxing:
                trace_evaluate_action = trace_evaluate_on_return(
                    expr=result,
                    evaluation=evaluation,
                    status="Returning",
                    fn=expr,
                    orig_expr=expr,
                )
            if trace_evaluate_action is not None:
                result = (
                    (trace_evaluate_action, False)
                    if is_performing_rewrite(func)
                    else trace_evaluate_action
                )
            evaluation.is_boxing = was_boxing
        else:
            result = (
                (trace_evaluate_action, False)
                if is_performing_rewrite(func)
                else trace_evaluate_action
            )
        return result

    return wrapper


def trace_fn_call_event(func: Callable) -> Callable:
    """
    Wrap a call event with callbacks,
    so we can track what happened before the call and
    the result returned by the call.

    A traced function could be a sympy or mpmath call or
    maybe a bulltin-function call.
    """

    def wrapper(*args) -> Any:
        skip_call = False
        result = None
        event_type = args[0]
        if hook_entry_fn is not None:
            skip_call = hook_entry_fn(*args)
        if not skip_call:
            result = func(*args[1:])
        if hook_exit_fn is not None:
            result = hook_exit_fn(event_type, result)
        return result

    return wrapper


@trace_fn_call_event
def trace_call(fn: Callable, *args) -> Any:
    """
    Runs a function inside a decorator that
    traps call and return information that can be used in
    a tracer or debugger
    """
    return fn(*args)


def call_event_print(event: TraceEvent, fn: Callable, *args) -> bool:
    """
    A somewhat generic function to show an event-traced call.
    """
    if isinstance(type(fn), type) or inspect.ismethod(fn) or inspect.isfunction(fn):
        name = f"{fn.__module__}.{fn.__qualname__}"
    else:
        name = str(fn)
    print(f"{event.name} call  : {name}{args[:3]}")
    return False


def return_event_print(event: TraceEvent, result: Any) -> Any:
    """
    A somewhat generic function to print a traced call's
    return value.
    """
    print(f"{event.name} result: {result}")
    return result


def run_fast(fn: Callable, *args) -> Any:
    """
    Fast-path call to run a event-tracable function, but no tracing is
    in effect. This add another level of indirection to
    some function calls, but Jit'ing will probably remove this
    when it is a bottleneck.
    """
    return fn(*args)


def run_mpmath_traced(fn: Callable, *args) -> Any:
    return trace_call(TraceEvent.mpmath, fn, *args)


def run_sympy_traced(fn: Callable, *args) -> Any:
    return trace_call(TraceEvent.SymPy, fn, *args)


# The below functions are changed by a tracer or debugger
# to get information from traced functions.
# These have to be defined.
run_sympy: Callable = run_fast
run_mpmath: Callable = run_fast

# If you want to test without using Mathics3 debugger module:

# import os
# if os.environ.get("MATHICS3_SYMPY_TRACE", None) is not None:
#     hook_entry_fn = call_event_print
#     hook_exit_fn = return_event_print
#     run_sympy: Callable = run_sympy_traced

# if os.environ.get("MATHICS3_MPMATH_TRACE", None) is not None:
#     hook_entry_fn = call_event_print
#     hook_exit_fn = return_event_print
#     run_mpmath: Callable = run_mpmath_traced
