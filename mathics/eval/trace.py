"""
Eval routines from mathics.trace
"""

import inspect
from math import log10
from typing import Any, Tuple


def eval_Stacktrace():
    """
    Display the Python call stack but filtered so that we Builtin calls.
    """
    from mathics.core.expression import Expression

    frame = inspect.currentframe()
    assert frame is not None
    frame = frame.f_back
    frame_number = -2
    last_was_eval = False

    frames = []
    while frame is not None:
        is_builtin, self_obj = is_showable_frame(frame)
        if is_builtin:
            # The two frames are always Stacktrace[]
            # and Evaluate of that. So skip these.
            if frame_number > 0 and not last_was_eval:
                if isinstance(self_obj, Expression):
                    last_was_eval = False
                    frame_str = self_obj
                else:
                    last_was_eval = True
                    builtin_class = self_obj.__class__
                    mathics_builtin_name = builtin_class.__name__
                    if len(frame.f_code.co_consts) > 0:
                        # Use code's __doc__ string
                        frame_str = frame.f_code.co_consts[0]
                        if frame_str.startswith("%(name)s"):
                            frame_str = frame_str.replace(
                                "%(name)s", mathics_builtin_name
                            )
                    else:
                        frame_str = mathics_builtin_name
                frames.append(frame_str)
            frame_number += 1
        frame = frame.f_back

    # FIXME this should done in a separate function and the
    # we should return the above.
    n = len(frames)
    max_width = int(log10(n + 1)) + 1
    number_template = "%%%dd" % max_width
    for frame_number, frame_str in enumerate(frames):
        formatted_frame_number = number_template % (n - frame_number)
        print(f"{formatted_frame_number}: {frame_str}")
    pass


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
