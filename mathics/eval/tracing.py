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


def print_evaluate(expr, evaluation, status: str, fn: Callable, orig_expr=None):
    """
    Called from a decorated Python @trace_evaluate .evaluate()
    method when TraceActivate["evaluate" -> True]
    """

    if evaluation.definitions.timing_trace_evaluation:
        evaluation.print_out(time.time() - evaluation.start_time)

    # Test and dispose of various situations where showing information
    # is pretty useless: evaluating a Symbol is the Symbol.
    # Showing the return value of a ListExpression literal is
    # also useless.
    from mathics.core.symbols import Symbol, SymbolConstant

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

    indents = "  " * evaluation.recursion_depth

    if orig_expr is not None:
        if fn.__name__ == "rewrite_apply_eval_step":
            assert isinstance(expr, tuple)
            if orig_expr != expr[0]:
                if status == "Returning":
                    if expr[1]:
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
            evaluation.print_out(f"{indents}{status}: {orig_expr} = " + str(expr))

    elif fn.__name__ != "rewrite_apply_eval_step":
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

        skip_call = False
        result = None
        was_boxing = evaluation.is_boxing
        if (
            trace_evaluate_on_call is not None
            and not evaluation.is_boxing
            and not isinstance(expr, SymbolConstant)
        ):
            # We may use boxing in print_evaluate_fn(). So turn off
            # boxing temporarily.
            evaluation.is_boxing = True
            skip_call = trace_evaluate_on_call(expr, evaluation, "Evaluating", func)
            evaluation.is_boxing = was_boxing
        if not skip_call:
            result = func(expr, evaluation)
            if trace_evaluate_on_return is not None and not was_boxing:
                trace_evaluate_on_return(result, evaluation, "Returning", func, expr)
            evaluation.is_boxing = was_boxing
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
