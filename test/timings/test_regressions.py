# test/timings/test_regressions.py
"""
Performance regression Benchmarks for Mathics3.
Contains a minimal subset of expressions to measure the time
for the most critical operations in the interpreter.

Executed only when the environment variable BENCHMARKS=1.
"""

import os
from test.helper import session

import pytest

# ------------------------------------------------------------
# Explicit definition of the benchmarks.
# Each entry is a tuple (expression, rounds, iterations)
# ------------------------------------------------------------

REGRESSION_BENCHMARKS = {
    # Basic Arithmetic
    "arithmetic": [
        ("1 + 2", 10, 2),
        ("5 * 3", 10, 2),
        ("1+2*3", 10, 2),
        ("(1+2)*3", 10, 2),
        ("1/2+3/4", 10, 2),
        ("5^3", 10, 2),
        ("10^100", 10, 2),
    ],
    # Assign. This should come before any other test.
    "assign": [
        ("ClearAll[F,x]; F[x_]:=x^2", 10, 2),
        ("ClearAll[F,x]; F[x_]:=x^2/;x>4", 10, 2),
        ("ClearAll[F,x]; F[x_]^:=x^2/;x>4", 10, 2),
        ("ClearAll[u]; u=4;u^2", 10, 2),
        ("ClearAll[u,z]; u=z;", 10, 2),
        ("ClearAll[u,z]; u=z/;z>1", 10, 2),
        ("ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{j,20}];", 10, 2),
        ("ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{j,20}];A[[1,2]]=4", 10, 2),
        ("ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{j,20}];A[[All,2]]=4", 10, 2),
        ("SetAttributes[OrderlessF, Orderless];", 10, 2),
        ("SetAttributes[FlatF, Flat];", 10, 2),
    ],
    # Symbolic Algebra
    "symbolic": [
        ("Expand[(a+b)^5]", 10, 2),
        ("Expand[(a+b+c)^5]", 10, 2),
        ("Expand[(a+b+c+d)^5]", 10, 2),
        ("Expand[(a+b)^10]", 10, 2),
        ("Nest[F,x,3]", 10, 2),
        ("Nest[FlatF,x]", 10, 2),
    ],
    # Numerical functions ("NumericQ", "Positive", "Negative", "NonNegative")
    "numeric": [
        ("NumericQ[Sqrt[2]]", 10, 2),
        ("NumericQ[Sqrt[-2]]", 10, 2),
        ("NumericQ[Sqrt[2.]]", 10, 2),
        ("NumericQ[Sqrt[-2.]]", 10, 2),
        ("Positive[Sqrt[2]]", 10, 2),
        ("Positive[Sqrt[-2]]", 10, 2),
        ("Positive[Sqrt[2.]]", 10, 2),
        ("Positive[Sqrt[-2.]]", 10, 2),
        ("Negative[Sqrt[2]]", 10, 2),
        ("Negative[Sqrt[-2]]", 10, 2),
        ("Negative[Sqrt[2.]]", 10, 2),
        ("Negative[Sqrt[-2.]]", 10, 2),
        ("NonNegative[Sqrt[2]]", 10, 2),
        ("NonNegative[Sqrt[-2]]", 10, 2),
        ("NonNegative[Sqrt[2.]]", 10, 2),
        ("NonNegative[Sqrt[-2.]]", 10, 2),
    ],
    # List operations
    "list": [
        ("Range[100]", 10, 2),
        ("Range[1000]", 10, 2),
        ("Table[i, {i, 1, 100}]", 10, 2),
        ("Table[i^2, {i, 1, 100}]", 10, 2),
        ("Plus@@Table[i^2, {i, 1, 100}]", 10, 2),
        ("Total[Range[100]]", 10, 2),
        ("Length[Range[1000]]", 10, 2),
        ("nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,100}];", 2, 2),
        ("uniformTable=Table[1./(1.+i^2),{i,0,100}];", 2, 2),
        ("Plus@@uniformTable", 10, 2),
        ("Plus@@nonuniformTable", 10, 2),
        ("MatchQ[uniformTable,{__Real}]", 10, 2),
        ("MatchQ[nonuniformTable,{__Real}]", 10, 2),
        ("Length[nonuniformTable]", 10, 2),
        ("Length[uniformTable]", 10, 2),
    ],
    # Pattern matching (añadidas manualmente)
    "pattern": [
        ("Replace[x, x->y]", 10, 2),
        ("Replace[{x,y}, {x->a, y->b}]", 10, 2),
        ("Cases[{1,2,3,4}, x_Integer /; x>2]", 10, 2),
        ("Select[Range[100], PrimeQ]", 10, 2),
        ("Range[100]/.{a__Integer}->a[[1]]", 10, 2),
        ("F@@Join[Range[100],a->1]/.F[a__Integer,OptionsPattern[]]->a[[1]]", 10, 2),
        (
            "OrderlessF@@Join[Range[100],a->1]/.F[a__Integer,OptionsPattern[]]->a[[1]]",
            10,
            2,
        ),
    ],
    "plot": [
        ("p=Plot[Sin[2 Pi x],{x,0,3}];", 3, 2),
        ("p=Plot[If[x>1,x,-x],{x,0,3}];", 3, 2),
        ("p=DensityPlot[x*y,{x,0,3},{y,0,3}];", 3, 2),
        ("p=Plot3D[x*y,{x,0,3},{y,0,3}];", 3, 2),
    ],
}

# Flatten the structure to parametrize the tests
BENCHMARK_TASKS = [("reset::reset", None, 0, 0)]
for category, tasks in REGRESSION_BENCHMARKS.items():
    for expr, repeat, number in tasks:
        # Names for the report
        short_expr = expr[:40] + "..." if len(expr) > 40 else expr
        name = f"{category}::{short_expr}"
        BENCHMARK_TASKS.append((name, expr, repeat, number))

# Explicit ids
param_ids = [name for name, _, _, _ in BENCHMARK_TASKS]


import pytest


@pytest.mark.benchmark(
    group="reference",
    min_rounds=10,
    max_time=0.5,
)
def test_reference_benchmark(benchmark):
    # Uses as a baseline the time that takes to sum
    # the square of the first 30000 integers in Python.
    # The task takes nearly 1s on average in my Thinkpad T15
    # with 16GB RAM running Ubuntu.
    def reference_task():
        return sum([i**2 for i in range(30000)])

    result = benchmark(reference_task)
    assert result == sum(i**2 for i in range(30000))


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("name,expr,repeat,number", BENCHMARK_TASKS, ids=param_ids)
def test_regression_benchmark(benchmark, name, expr, repeat, number):
    """
    Run a regression benchmark using session.evaluate.
    """
    if expr is None:
        session.reset()
        return

    def impl():
        # Evaluating the session
        session.evaluate(expr)

    benchmark.pedantic(impl, rounds=repeat, iterations=number)
