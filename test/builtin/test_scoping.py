# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.scoping.
"""
from test.helper import check_evaluation, session

import pytest

from mathics.core.symbols import Symbol


def test_unique():
    """
    test Unique
    """

    # test Unique[]
    symbol = session.evaluate("Unique[]")
    assert isinstance(
        symbol, Symbol
    ), f"Unique[] should return a Symbol; got {type(symbol)}"
    symbol_set = set([symbol])
    for i in range(5):
        symbol = session.evaluate("Unique[]")
        assert (
            symbol not in symbol_set
        ), "Unique[] should return different symbols; {symbol.name} is duplicated"
        symbol_set.add(symbol)

    # test Unique[<prefix>]
    symbol_prefix = symbol.name[0]

    for i in range(5):
        symbol = session.evaluate(f"Unique[{symbol_prefix}]")
        assert (
            symbol not in symbol_set
        ), "Unique[{symbol_prefix}] should return different symbols; {symbol.name} is duplicated"


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("InputForm[$Context]", None, '"Global`"', None),
        ## Test general context behaviour
        ("Plus === Global`Plus", None, "False", None),
        ("`Plus === Global`Plus", None, "True", None),
        ("Unique[{}]", None, "{}", None),
    ],
)
def test_scoping(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Block[{i = 0}, With[{}, Module[{j = i}, Set[i, i+1]; j]]]", None, "0", None),
    ],
)
def test_scoping_constructs(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # Local variables that nothing references are removed when the
        # Module is done, as in WMA.
        (
            'mf[n_] := Module[{e = Range[n], c}, c = e^2; Total[c]]; mf[10]; Names["Global`e$*"]',
            "{}",
        ),
        (
            'TimeConstrained[Module[{big = Range[10^5]}, While[True, big[[1]]]], 0.2]; Names["Global`big$*"]',
            "{}",
        ),
        (
            'CheckAbort[Module[{ab = Range[10]}, Abort[]], 0]; Names["Global`ab$*"]',
            "{}",
        ),
        # ... but the ones still referenced stay. These were checked against WMA 15.
        ("mg := Module[{x}, mh = x; x = 5]; mg; mh", "5"),
        ("Module[{cnt = 0}, minc[] := ++cnt]; minc[]; minc[]", "2"),
        ("mk[] := Module[{r = 7}, Return[Hold[r]]]; ReleaseHold[mk[]]", "7"),
        ("ReleaseHold[Catch[Module[{t = 8}, Throw[Hold[t]]]]]", "8"),
        ("mff = Module[{a = 5}, # + a &]; mff[1]", "6"),
        ("Module[{q = 3}, mgg = Function[x, x + q]]; mgg[1]", "4"),
        ("mmk[] := Module[{p, w = 2}, p[x_] := x w; p]; mpp = mmk[]; mpp[3]", "6"),
        ("Module[{u = 1, v}, v = Hold[u]; mstore = v]; ReleaseHold[mstore]", "1"),
        (
            'Module[{s1 = 4}, massoc = <|"k" -> Hold[s1]|>]; ReleaseHold[massoc["k"]]',
            "4",
        ),
        (
            "Module[{s2 = 6}, mdisp = Dispatch[{z -> Hold[s2]}]]; ReleaseHold[z /. mdisp]",
            "6",
        ),
        (
            "Module[{o1 = 9}, Options[moptf] = {mopt -> Hold[o1]}]; ReleaseHold[OptionValue[moptf, mopt]]",
            "9",
        ),
        ("Module[{d1 = 10}, mdv[1] = Hold[d1]]; ReleaseHold[mdv[1]]", "10"),
        (
            "Module[{u1 = 11}, muptag /: muph[muptag] = Hold[u1]]; ReleaseHold[muph[muptag]]",
            "11",
        ),
        (
            "Module[{n1 = 12, n2}, n2 = Hold[n1]; Module[{}, mkeep = Hold[n2]]]; ReleaseHold[ReleaseHold[mkeep]]",
            "12",
        ),
        (
            "Module[{y1 = 13}, Module[{y2 = Hold[y1]}, mdeep = y2]]; ReleaseHold[mdeep]",
            "13",
        ),
        # A Module inside another one with a large result leaves the
        # decision to the enclosing Module, which removes or keeps the
        # variables the same way.
        (
            'mbig[] := Module[{lb = Range[3000]}, {lb, lb}]; Module[{ob}, ob = mbig[]; Length[ob]]; Names["Global`lb$*"]',
            "{}",
        ),
        (
            "mref[] := Module[{lr = 14}, Join[Hold @@ Range[3000], Hold[lr]]]; Last[List @@ Module[{or}, or = mref[]; or]]",
            "14",
        ),
        (
            'Module[{oc}, Do[Module[{lc = Range[3000]}, {lc, lc}], {3}]]; Names["Global`lc$*"]',
            "{}",
        ),
    ],
)
def test_module_releases_unreferenced_variables(str_expr, str_expected):
    check_evaluation(str_expr, str_expected, hold_expected=True)
