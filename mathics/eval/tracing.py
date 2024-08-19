"""
Debug Tracing and Trace-Event handlers.

This is how we support external (Mathics3 module) debuggers and tracers.
"""

import inspect
from enum import Enum
from typing import Any, Callable, Optional

TraceEventNames = ("SymPy", "Numpy", "mpmath", "apply")
TraceEvent = Enum("TraceEvent", TraceEventNames)


hook_entry_fn: Optional[Callable] = None
hook_exit_fn: Optional[Callable] = None


def trace_fn_call_event(func: Callable) -> Callable:
    """
    Wrap a a call event with callbacks
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
    A somehwat generic fuction to show an event-traced call.
    """
    if type(fn) == type or inspect.ismethod(fn) or inspect.isfunction(fn):
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
