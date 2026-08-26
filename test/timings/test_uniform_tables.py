import os
from test.helper import session

import pytest


def test_check_property():
    session.evaluate("ClearAll[i,uniformTable,nonuniformTable]")
    table_uniform_expr = session.evaluate("uniformTable=Table[1./(1.+i^2),{i,0,1000}]")
    table_non_uniform_expr = session.evaluate(
        "nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}]"
    )
    assert table_uniform_expr.elements_properties.is_uniform
    assert not table_non_uniform_expr.elements_properties.is_uniform


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize(
    ["expr", "expect"],
    [
        (None, None),
        ("F[__Real]:=1;", None),
        ("uniformTable=Table[1./(1.+i^2),{i,0,1000}];", None),
        ("nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,1000}];", None),
        ("Plus@@uniformTable", "2.075674547634748"),
        ("MatchQ[uniformTable,{__Real}]", "System`True"),
        ("Length[F@@uniformTable]", "0"),
        ("Plus@@nonuniformTable", "2.075674547634748"),
        ("MatchQ[nonuniformTable,{__Real}]", "System`False"),
        ("Length[F@@nonuniformTable]", "1001"),
    ],
)
def test_evaluate_benchmark(benchmark, expr, expect):
    # TODO: rewrite this to be used with pytest-benchmark
    if expr is None:
        return
    if expect is None:
        expect = "System`Null"

    def impl():
        assert str(session.evaluate(expr)) == expect

    benchmark.pedantic(impl, rounds=10, iterations=2)
