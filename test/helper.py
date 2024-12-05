# -*- coding: utf-8 -*-
import os.path as osp
import re
import time
from typing import Optional

from mathics.core.load_builtin import import_and_load_builtins
from mathics.session import MathicsSession

import_and_load_builtins()

# Set up a Mathics session with definitions.
# For consistency set the character encoding ASCII which is
# the lowest common denominator available on all systems.
session = MathicsSession(character_encoding="ASCII")

# Set up a data path that can be used in testing
data_dir = osp.normpath(osp.join(osp.dirname(__file__), "data"))


def reset_session(add_builtin=True, catch_interrupt=False):
    """
    reset the session cleaning all the definitions.
    """
    global session
    session.reset()
    session.evaluate("SetDirectory[$TemporaryDirectory];")


def evaluate_value(str_expr: str):
    return session.evaluate(str_expr).value


def evaluate(str_expr: str):
    return session.evaluate(str_expr)


def check_evaluation(
    str_expr: Optional[str],
    str_expected: Optional[str] = None,
    failure_message: str = "",
    hold_expected: bool = False,
    to_string_expr: Optional[bool] = True,
    to_string_expected: bool = True,
    to_python_expected: bool = False,
    expected_messages: Optional[tuple] = None,
):
    """
    Helper function to test Mathics expression against
    its results.

    Compares the expressions represented by ``str_expr`` and  ``str_expected`` by
    evaluating the first, and optionally, the second. If omitted, `str_expected`
    is assumed to be `"Null"`.

    str_expr: The expression to be tested. If its value is ``None``, the session is
              reset.
              At the beginning of each set of pytests, it is important to call
              ``check_evaluation(None)`` to avoid that definitions introduced by
              other tests affect the results.

    str_expected: The expected result. The value ``None`` is equivalent to ``"Null"``.

    failure_message: message shown in case of failure. Use "" for no failure message.

    hold_expected:   If ``False`` (default value) the ``str_expected`` is evaluated.
                     Otherwise, the expression is considered literally.

    to_string_expr: If ``True`` (default value) the result of the evaluation is
                    converted into a Python string. Otherwise, the expression is kept
                    as an Expression object.
                    If this argument is set to ``None``, the session is reset.

    to_string_expected: If ``True`` (default value) the expected expression is
                        evaluated and then converted to a Python string. result of the
                        evaluation is converted into a Python string.
                        If ``False``, the expected expression is kept as an Expression
                        object.
                        If ``None`` the result string is matched as is.

    to_python_expected: If ``True``, and ``to_string_expected`` is ``False``, the result
                        of evaluating ``str_expr``is compared against the result of the
                        evaluation of ``str_expected``, converted into a
                        Python object.

    expected_messages: If a tuple of strings are passed into
                       this parameter, messages and prints raised during
                       the evaluation of ``str_expr`` are compared with the elements of
                       the list. If ``None``, this comparison
                       is omitted.
    """
    if str_expr is None:
        reset_session()
        return
    if str_expected is None:
        str_expected = "Null"

    if to_string_expr:
        str_expr = f"ToString[{str_expr}]"
        result = evaluate_value(str_expr)
    elif to_string_expr is None:
        result = str_expr
    else:
        result = evaluate(str_expr)

    outs = [out.text for out in session.evaluation.out]

    if to_string_expected:
        if hold_expected:
            expected = str_expected
        else:
            str_expected = f"ToString[{str_expected}]"
            expected = evaluate_value(str_expected)
    elif to_string_expected is None:
        expected = str_expected
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
        if isinstance(expected, re.Pattern):
            assert expected.match(result)
        else:
            assert result == expected

    if expected_messages is not None:
        msgs = list(expected_messages)
        expected_len = len(msgs)
        got_len = len(outs)
        assert (
            expected_len == got_len
        ), f"expected {expected_len}; got {got_len}. Messages: {outs}"
        for out, msg in zip(outs, msgs):
            compare_ok = msg.match(out) if isinstance(msg, re.Pattern) else out == msg
            if not compare_ok:
                print(f"out:<<{out}>>")
                print(" and ")
                print(f"expected=<<{msg}>>")
                assert False, " do not match."


def check_evaluation_as_in_cli(
    str_expr: Optional[str] = None,
    str_expected: Optional[str] = None,
    failure_message: str = "",
    expected_messages: Optional[tuple] = None,
):
    """
    Use this method when special Symbols like Return, %, %%,
    $IterationLimit, $RecursionLimit, etc. are used in the tests.
    """
    if str_expr is None:
        reset_session()
        return

    res = session.evaluate_as_in_cli(str_expr)
    if expected_messages is None:
        assert len(res.out) == 0
    else:
        assert len(res.out) == len(expected_messages)
        for li1, li2 in zip(res.out, expected_messages):
            assert li1.text == li2

    if failure_message:
        assert res.result == str_expected, failure_message
    assert res.result == str_expected
