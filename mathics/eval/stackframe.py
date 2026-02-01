"""
Mathics3 Introspection routines to get Mathics3-oriented Python frames.
"""

import inspect
from types import FrameType
from typing import Optional

from mathics.core.builtin import Builtin
from mathics.core.expression import Expression


def find_Mathics3_evaluation_method(frame: Optional[FrameType]) -> Optional[FrameType]:
    """
    Returns the most recent Mathics3 evaluation frame given "frame".
    """
    if not inspect.isframe(frame):
        return None

    while frame is not None:
        if is_Mathics3_eval_method(frame):
            return frame
        frame = frame.f_back
    return None


def get_self(frame: FrameType) -> Optional[FrameType]:
    """Returns the `self` object in a Python frame if it exists, or None if
    it does not exist.
    """
    return frame.f_locals.get("self", None)


def get_eval_Expression() -> Optional[Expression]:
    """Returns the Expression used in a Mathics3 evaluation() or
    eval() Builtin method. This is often needed in an error message to
    report what Expression was getting evaluated. None is returned if
    not found.

    The function is fragile in that it relies on the Mathics3 implementation
    having a Expression.rewrite_apply_eval_step() method.  It walks to
    call stack to find that Expression.

    None is returned if we can't find this.
    """
    frame = inspect.currentframe()
    if frame is None:
        return None

    frame = frame.f_back
    while True:
        if frame is None:
            return None
        method_code = frame.f_code
        if method_code.co_name == "rewrite_apply_eval_step":
            if (self_obj := get_self(frame)) is not None and isinstance(
                self_obj, Expression
            ):
                return self_obj

        frame = frame.f_back


def get_eval_doc_signature() -> Optional[str]:
    """Returns Builtin __doc__ string, essentially the Function or
    Variable signature, for the most recent Mathics3 eval method

    The function is fragile in that it relies on the Mathics3 implementation
    protocol of having evaluation methods that start with "eval" and belong
    to some Mathics3 Builtin class.

    None is returned if we can't find such a docstring.
    """

    eval_frame = find_Mathics3_evaluation_method(inspect.currentframe().f_back)
    if eval_frame is None:
        return None
    eval_method_name = eval_frame.f_code.co_name
    eval_method = getattr(eval_frame.f_locals.get("self"), eval_method_name)
    if eval_method:
        return eval_method.__doc__
    return None


def is_Mathics3_eval_method(frame) -> bool:
    """
    Returns True if frame is Python frame object for a Mathics3 Builtin, and
    returns False otherwise.
    """
    if not inspect.isframe(frame):
        return False

    method_code = frame.f_code
    if not method_code.co_name.startswith("eval"):
        return False
    if frame.f_locals.get("evaluation", None) is None:
        return False

    if (self_obj := get_self(frame)) is None or frame.f_locals.get(
        "evaluation", None
    ) is None:
        return False
    return isinstance(self_obj, Builtin)
