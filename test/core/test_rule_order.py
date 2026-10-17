# -*- coding: utf-8 -*-
"""
Rule ordering: partial order by inclusion of matched sets.
Expected values come from Mathematica
(incomparable rules keep their definition order).
"""
import pytest

from mathics.core.load_builtin import import_and_load_builtins
from mathics.core.pattern.specificity import rule_le, rule_lt
from mathics.session import MathicsSession

import_and_load_builtins()
session = MathicsSession()


def rules_of(name):
    return session.definitions.get_definition("Global`" + name).downvalues


def lhs_order(name, defs):
    session.evaluate(f"ClearAll[{name}]")
    for d in defs:
        session.evaluate(d)
    return [
        str(r.pattern.expr).replace("System`", "").replace("Global`", "")
        for r in rules_of(name)
    ]


GEN = "A[Pattern[n, Blank[Integer]], Blank[]]"
ESP = "A[Pattern[n, Blank[Integer]], Pattern[m, Blank[Integer]]]"
GEN_LHS = "Condition[" + GEN + ", Less[n, 0]]"
ESP1 = "A[Pattern[n, Blank[Integer]], 1]"

A_CASES = [
    (["A[n_Integer,_]=0", "A[n_Integer,m_Integer]=1"], [ESP, GEN]),
    (["A[n_Integer,_]:=0/;n<0", "A[n_Integer,m_Integer]:=1"], [GEN, ESP]),
    (["A[n_Integer,m_Integer]:=1", "A[n_Integer,_]:=0/;n<0"], [ESP, GEN]),
    (["A[n_Integer,_]/;n<0:=0", "A[n_Integer,m_Integer]:=1"], [GEN_LHS, ESP]),
    (["A[n_Integer,m_Integer]:=1", "A[n_Integer,_]/;n<0:=0"], [ESP, GEN_LHS]),
    (["A[n_Integer,_]:=0", "A[n_Integer,m_Integer]:=1/;n<0"], [ESP, GEN]),
    (["A[n_Integer,_]:=0/;n<0", "A[n_Integer,m_Integer]:=1/;n>5"], [GEN, ESP]),
    (["A[n_Integer,m_Integer]:=1/;n>5", "A[n_Integer,_]:=0/;n<0"], [ESP, GEN]),
    (
        ["A[n_Integer,_]:=0/;n<0", "A[n_Integer,m_Integer]:=1", "A[n_Integer,1]:=2"],
        [GEN, ESP1, ESP],
    ),
]


@pytest.mark.parametrize(("defs", "expected"), A_CASES)
def test_A_cases(defs, expected):
    assert lhs_order("A", defs) == expected


def test_F_G():
    f = lhs_order(
        "F",
        [
            "F[x_Integer,y_Integer]=1",
            "F[x_Integer,_]=2",
            "F[_,x_Integer]=3",
            "F[__Integer]=4",
        ],
    )
    assert [x.count("Blank[]") for x in f] == [0, 1, 1, 0]
    assert f[-1].startswith("F[BlankSequence[Integer]")
    g = lhs_order(
        "G",
        [
            "G[__Integer]=4",
            "G[_,x_Integer]=3",
            "G[x_Integer,_]=2",
            "G[x_Integer,y_Integer]=1",
        ],
    )
    assert g[0].startswith("G[Pattern[x, Blank[Integer]], Pattern[y")
    assert g[1].startswith("G[BlankSequence[Integer]")
    assert g[2].startswith("G[Blank[], Pattern[x")
    assert g[3].startswith("G[Pattern[x, Blank[Integer]], Blank[]")


PARTITIONS = [
    "P[n_Integer]:=P[n,n]",
    "P[n_Integer,_]:={}/;n<0",
    "P[0,_]:={{}}",
    "P[n_Integer,1]:={Table[1,{n}]}",
    "P[_,0]:={}",
    "P[n_Integer,maxpart_Integer]:=Join[Map[(Prepend[#,maxpart])&,P[n-maxpart,maxpart]],P[n,maxpart-1]]",
]


def test_partitions_order_and_termination():
    order = lhs_order("P", PARTITIONS)
    assert order[0] == "P[Pattern[n, Blank[Integer]]]"
    assert order[-1].startswith("P[Pattern[n, Blank[Integer]], Pattern[maxpart")
    assert session.evaluate("Length[P[5]]").value == 7
    assert str(session.evaluate("P[-3, 2]")) == "{}"
    assert str(session.evaluate("P[4, 0]")) == "{}"


# ssm patterns, as in the Mathematica experiment
SSM = {
    "X": "ssm[_a,_a]",
    "B": "ssm[_b]",
    "A": "ssm[_a]",
    "U": "ssm[_]",
    "S": "ssm[__a]",
    "N": "ssm[___a]",
    "T": "ssm[__a,__b]",
    "D": "ssm[__]",
    "Z": "ssm[___]",
    "E": "ssm[]",
}
MATRIX_ORDER = "XBAUSNTDZ"
# Mathematica: 1 if the order of the pair does not depend on definition order
MATRIX = [
    [1, 0, 0, 0, 1, 1, 0, 1, 1],
    [0, 1, 0, 1, 0, 0, 0, 1, 1],
    [0, 0, 1, 1, 1, 1, 0, 1, 1],
    [0, 1, 1, 1, 0, 0, 0, 1, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 1, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Orders produced by Mathematica for random insertion orders
MMA_OUTPUTS = [
    "EBXASNTUDZ",
    "ETXBAUSDNZ",
    "EATBUXSDNZ",
    "EXTABUSDNZ",
    "EBAUXSNTDZ",
    "ETAXSNBUDZ",
    "EABUXSTDNZ",
    "EABXSNUTDZ",
]


def ssm_rule(code):
    session.evaluate("ClearAll[ssm]")
    session.evaluate(SSM[code] + " = 1")
    return rules_of("ssm")[0]


def ssm_rules():
    return {c: ssm_rule(c) for c in SSM}


def test_ssm_comparability_matrix():
    # Rules must survive ClearAll, so keep copies
    rules = {}
    for c in SSM:
        rules[c] = ssm_rule(c)
    for i, ci in enumerate(MATRIX_ORDER):
        for j, cj in enumerate(MATRIX_ORDER):
            comparable = bool(
                rule_le(rules[ci], rules[cj]) or rule_le(rules[cj], rules[ci])
            )
            assert comparable == bool(MATRIX[i][j]), (SSM[ci], SSM[cj])


@pytest.mark.parametrize("out", MMA_OUTPUTS)
def test_ssm_mathematica_outputs_are_consistent(out):
    rules = {c: ssm_rule(c) for c in SSM}
    # no later rule is strictly more specific than an earlier one
    for i in range(len(out)):
        for j in range(i + 1, len(out)):
            assert not rule_lt(rules[out[j]], rules[out[i]]), (out, out[i], out[j])
    # inserting in Mathematica's output order must reproduce it
    session.evaluate("ClearAll[ssm]")
    for c in out:
        session.evaluate(SSM[c] + " = 1")
    got = [str(r.pattern.expr) for r in rules_of("ssm")]
    session.evaluate("ClearAll[ssm]")
    for c in out:
        session.evaluate(SSM[c] + " = 1")
    expected = [str(rules[c].pattern.expr) for c in out]
    assert got == expected


H_CASES = [
    # (definitions, order obtained in Mathematica)
    (
        ["h[_]=1", "h[x_Integer,_]=1", "h[_Integer]=1"],
        ["h[Blank[Integer]]", "h[Blank[]]", "h[Pattern[x, Blank[Integer]], Blank[]]"],
    ),
    (
        ["h[_]=1", "h[x_Integer,_]=1", "h[_Integer]=1", "h[x_Integer,y_Integer]=1"],
        [
            "h[Blank[Integer]]",
            "h[Blank[]]",
            "h[Pattern[x, Blank[Integer]], Pattern[y, Blank[Integer]]]",
            "h[Pattern[x, Blank[Integer]], Blank[]]",
        ],
    ),
]


@pytest.mark.parametrize(("defs", "expected"), H_CASES)
def test_insertion_scheme_matches_mathematica(defs, expected):
    """A new rule goes before the first existing rule that contains it
    (a binary search or a backwards scan give different results)."""
    assert lhs_order("h", defs) == expected
