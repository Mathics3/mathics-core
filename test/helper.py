# -*- coding: utf-8 -*-
import time
from mathics.session import MathicsSession

session = MathicsSession()


def reset_session(add_builtin=True, catch_interrupt=False):
    """
    Reset the session cleaning all the definitions.
    """
    global session
    session.reset()


def evaluate_value(str_expr: str):
    return session.evaluate(str_expr).value


def evaluate(str_expr: str):
    return session.evaluate(str_expr)


def check_evaluation(
    str_expr: str,
    str_expected: str,
    message="",
    to_string_expr=True,
    to_string_expected=True,
    to_python_expected=False,
    msgs=None,
):
    """Helper function to test Mathics expression against
    its results"""
    if to_string_expr:
        str_expr = f"ToString[{str_expr}]"
        result = evaluate_value(str_expr)
    else:
        result = evaluate(str_expr)
    outs = [out.text for out in session.evaluation.out]

    if to_string_expected:
        str_expected = f"ToString[{str_expected}]"
        expected = evaluate_value(str_expected)
    else:
        expected = evaluate(str_expr)
        if to_python_expected:
            expected = expected.to_python(string_quotes=False)

    if msgs:
        if isinstance(msgs, str):
            msgs = [msgs]

    print(time.asctime())
    if message:
        print((result, expected))
        assert result == expected, message
    else:
        print((result, expected))
        assert result == expected

    if msgs:
        msgs = list(msgs)
        assert len(outs) == len(msgs), "outs are not the same."
        for (out, msg) in zip(outs, msgs):
            assert out == msg
