# -*- coding: utf-8 -*-
import time
from mathics.session import MathicsSession
from typing import Optional

session = MathicsSession()


def reset_session(add_builtin=True, catch_interrupt=False):
    global session
    session.reset()


def evaluate_value(str_expr: str):
    return session.evaluate(str_expr).value


def evaluate(str_expr: str):
    return session.evaluate(str_expr)


def check_evaluation(
    str_expr: str,
    str_expected: str,
    failure_message: str = "",
    hold_expected: bool = False,
    to_string_expr: bool = True,
    to_string_expected: bool = True,
    to_python_expected: bool = False,
    expected_messages: Optional[tuple] = None,
):
    """
    Helper function to test Mathics expression against
    its results

    Compares the expressions represented by ``str_expr`` and  ``str_expected`` by evaluating
    the first, and optionally, the second.

    to_string_expr: If ``True`` (default value) the result of the evaluation is converted
                    into a Python string. Otherwise, the expression is kept as an Expression
                    object. If this argument is set to ``None``, the session is reset.

    failure_message (str): message shown in case of failure
    hold_expected (bool): If ``False`` (default value) the ``str_expected`` is evaluated. Otherwise,
                          the expression is considered literally.

    to_string_expected: If ``True`` (default value) the expected expression is
                    evaluated and then converted to a Python string. result of the evaluation is converted
                    into a Python string. If ``False``, the expected expression is kept as an Expression object.

    to_python_expected: If ``True``, and ``to_string_expected`` is ``False``, the result of evaluating ``str_expr``
                    is compared against the result of the evaluation of ``str_expected``, converted into a
                    Python object.

    expected_messages ``Optional[tuple[str]]``: If a tuple of strings are passed into this parameter, messages and prints raised during
                    the evaluation of ``str_expr`` are compared with the elements of the list. If ``None``, this comparison
                    is ommited.
    """
    if str_expr is None:
        reset_session()
        return

    if to_string_expr:
        str_expr = f"ToString[{str_expr}]"
        result = evaluate_value(str_expr)
    else:
        result = evaluate(str_expr)

    outs = [out.text for out in session.evaluation.out]

    if to_string_expected:
        if hold_expected:
            expected = str_expected
        else:
            str_expected = f"ToString[{str_expected}]"
            expected = evaluate_value(str_expected)
    else:
        if hold_expected:
            if to_python_expected:
                expected = str_expected
            else:
                expected = evaluate(f"HoldForm[{str_expected}]").elements[0]
        else:
            expected = evaluate(str_expected)
            if to_python_expected:
                expected = expected.to_python(string_quotes=False)

    print(time.asctime())
    if failure_message:
        print((result, expected))
        assert result == expected, failure_message
    else:
        print((result, expected))
        assert result == expected

    if expected_messages is not None:
        msgs = list(expected_messages)
        expected_len = len(msgs)
        got_len = len(outs)
        assert expected_len == got_len, f"expected {expected_len}; got {got_len}"
        for (out, msg) in zip(outs, msgs):
            if out != msg:
                print(f"out:<<{out}>>")
                print(" and ")
                print(f"expected=<<{msg}>>")
                assert False, " do not match."
