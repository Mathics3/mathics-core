import inspect
from types import FrameType
from typing import Optional

from mathics.core.builtin import Builtin


def is_mathics3_eval_method(frame) -> bool:
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

    if (self_obj := frame.f_locals.get("self", None)) is None or frame.f_locals.get(
        "evaluation", None
    ) is None:
        return False
    return isinstance(self_obj, Builtin)


def find_mathics3_evaluation_method(frame: Optional[FrameType]) -> Optional[FrameType]:
    """
    Returns the most recent evaluation frame for frome
    """
    if not inspect.isframe(frame):
        return None

    while frame is not None:
        if is_mathics3_eval_method(frame):
            return frame
        frame = frame.f_back
    return None
