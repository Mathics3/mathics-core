# -*- coding: utf-8 -*-
from test.helper import check_evaluation, evaluate
from mathics.core.symbols import Symbol

import pytest
import sys

import time


@pytest.mark.skipif(
    sys.platform in ("win32",),
    reason="pyston and win32 does not do well killing threads",
)
def test_timeconstrained_assignment_1():
    # This test
    str_expr1 = "a=1.; TimeConstrained[Do[Pause[.1];a=a+1,{1000}],1]"
    result = evaluate(str_expr1)
    str_expected = "$Aborted"
    expected = evaluate(str_expected)
    assert result == expected
    time.sleep(1)
    # if all the operations where instantaneous, then the
    # value of ``a`` should be 10. However, in macOS, ``a``
    # just reach 3...
    assert evaluate("a").to_python() <= 10


@pytest.mark.skipif(
    sys.platform in ("win32",),
    reason="pyston and win32 does not do well killing threads",
)
def test_timeconstrained_assignment_2():
    # This test checks if the assignment is really aborted
    # if the RHS exceeds the wall time.
    str_expr1 = "a=1.; TimeConstrained[a=(Pause[.2];2.),.1]"
    result = evaluate(str_expr1)
    str_expected = "$Aborted"
    expected = evaluate(str_expected)
    assert result == expected
    time.sleep(0.2)
    assert evaluate("a").to_python() == 1.0


@pytest.mark.skipif(
    sys.platform in ("win32",),
    reason="pyston and win32 does not do well killing threads",
)
def test_timeconstrained_sympy():
    # This test tries to run a large and onerous calculus that runs
    # in sympy (outside the control of Mathics).
    # If the behaviour is the right one, the evaluation
    # is interrupted before it saturates memory and raise a SIGEV
    # exception.
    str_expr = "TimeConstrained[Integrate[Sin[x]^1000000, x], 0.9]"
    result = evaluate(str_expr)

    assert result is None or result == Symbol("$Aborted")


@pytest.mark.skipif(
    sys.platform in ("win32",),
    reason="pyston and win32 does not do well killing threads",
)
def test_timeremaining():
    str_expr = "TimeConstrained[1+2; TimeRemaining[], 0.9]"
    result = evaluate(str_expr)
    assert result is None or 0 < result.to_python() < 0.9


def test_datelist():
    for str_expr, str_expected in (
        ('DateList["2016-09-09"]', "{2016, 9, 9, 0, 0, 0.}"),
        # strptime should ignore leading 0s
        (
            'DateList[{"6/6/91", {"Day", "Month", "YearShort"}}]',
            "{1991, 6, 6, 0, 0, 0.}",
        ),
        (
            'DateList[{"6/06/91", {"Day", "Month", "YearShort"}}]',
            "{1991, 6, 6, 0, 0, 0.}",
        ),
        (
            'DateList[{"06/06/91", {"Day", "Month", "YearShort"}}]',
            "{1991, 6, 6, 0, 0, 0.}",
        ),
        (
            'DateList[{"06/6/91", {"Day", "Month", "YearShort"}}]',
            "{1991, 6, 6, 0, 0, 0.}",
        ),
        ('DateList[{"5/18", {"Month", "Day"}}][[1]] == DateList[][[1]]', "True"),
        ("Quiet[DateList[abc]]", "DateList[abc]"),
    ):
        check_evaluation(str_expr, str_expected)


def test_datestring2():
    for str_expr, str_expected in (
        ## Check Leading 0s
        # (
        #  'DateString[{1979, 3, 14}, {"DayName", "  ", "MonthShort", "-", "YearShort"}',
        # "Wednesday  3-79"
        # ),
        (
            "DateString[{1979, 3, 4}]",
            "Sun 4 Mar 1979 00:00:00",
        ),
        ('DateString[{"5/19"}]', "5/19"),
        ('DateString["2000-12-1", "Year"]', "2000"),
    ):
        check_evaluation(str_expr, str_expected, hold_expected=True)
