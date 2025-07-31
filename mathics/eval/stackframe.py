"""
Mathics3 Introspection routines to get Mathics3-oriented Python frames.
"""

import inspect
from types import FrameType
from typing import Optional

from mathics.core.builtin import Builtin


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
