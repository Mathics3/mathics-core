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

LIST_VALUES = [f"$u{i}" for i in range(100)]

REGRESSION_BENCHMARKS = {
    # Basic Arithmetic
    "arithmetic": [
        ("1 + 2", 100, 20),
        ("(*Long Sum*)" + "+".join(LIST_VALUES), 10, 2),
        ("5 * 3", 100, 20),
        ("1+2*3", 100, 20),
        ("(1+2)*3", 100, 20),
        ("1/2+3/4", 100, 20),
        ("5^3", 100, 20),
        ("10^100", 100, 20),
    ],
    # Assign. This should come before any other test.
    "assign": [
        ("ClearAll[F,x]; F[x_]:=x^2", 10, 50),
        ("ClearAll[F,x]; F[x_]:=x^2/;x>4", 10, 50),
        ("ClearAll[F,x]; F[x_]^:=x^2/;x>4", 10, 50),
        ("ClearAll[u]; u=4;u^2", 10, 50),
        ("ClearAll[u,z]; u=z;", 10, 50),
        ("ClearAll[u,z]; u=z/;z>1", 10, 50),
        ("ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{j,20}];", 10, 2),
        ("ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{j,20}];A[[1,2]]=4", 10, 2),
        ("ClearAll[A,i,j]; A=Table[1.*i*j,{i,20},{j,20}];A[[All,2]]=4", 10, 2),
        ("SetAttributes[OrderlessF, Orderless];", 10, 20),
        ("SetAttributes[FlatF, Flat];", 10, 20),
    ],
    # Symbolic Algebra
    "symbolic": [
        ("Expand[(a+b)^5]", 10, 2),
        ("Expand[(a+b+c)^5]", 10, 2),
        ("Expand[(a+b+c+d)^5]", 10, 2),
        ("Expand[(a+b)^10]", 10, 2),
        ("Nest[F,x,3]", 10, 2),
        ("Nest[FlatF,x,3]", 10, 2),
    ],
    # Numerical functions ("NumericQ", "Positive", "Negative", "NonNegative")
    "numeric": [
        ("NumericQ[Sqrt[2]]", 10, 20),
        ("NumericQ[Sqrt[-2]]", 10, 20),
        ("NumericQ[Sqrt[2.]]", 10, 20),
        ("NumericQ[Sqrt[-2.]]", 10, 20),
        ("Positive[Sqrt[2]]", 10, 20),
        ("Positive[Sqrt[-2]]", 10, 20),
        ("Positive[Sqrt[2.]]", 10, 20),
        ("Positive[Sqrt[-2.]]", 10, 20),
        ("Negative[Sqrt[2]]", 10, 20),
        ("Negative[Sqrt[-2]]", 10, 20),
        ("Negative[Sqrt[2.]]", 10, 20),
        ("Negative[Sqrt[-2.]]", 10, 20),
        ("NonNegative[Sqrt[2]]", 10, 20),
        ("NonNegative[Sqrt[-2]]", 10, 20),
        ("NonNegative[Sqrt[2.]]", 10, 20),
        ("NonNegative[Sqrt[-2.]]", 10, 20),
    ],
    # List operations
    "list": [
        ("Range[100]", 10, 20),
        ("Range[1000]", 10, 20),
        ("Table[i, {i, 1, 100}]", 10, 2),
        ("Table[i^2, {i, 1, 100}]", 10, 2),
        ("Table[i*j, {i, 1., 10.},{j, 1., 10.}]", 10, 2),
        ("Plus@@Table[i^2, {i, 1, 100}]", 10, 20),
        ("Total[Range[100]]", 10, 20),
        ("Length[Range[1000]]", 10, 20),
        ("nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,100}];", 2, 2),
        ("uniformTable=Table[1./(1.+i^2),{i,0,100}];", 2, 2),
        ("Plus@@uniformTable", 10, 20),
        ("Plus@@nonuniformTable", 10, 20),
        ("MatchQ[uniformTable,{__Real}]", 10, 20),
        ("MatchQ[nonuniformTable,{__Real}]", 10, 20),
        ("Length[nonuniformTable]", 10, 20),
        ("Length[uniformTable]", 10, 20),
    ],
    # Pattern matching (added by hand)
    "pattern": [
        ("Replace[x, x->y]", 50, 20),
        ("Replace[{x,y}, {x->a, y->b}]", 50, 20),
        (
            "Hold["
            + 10 * "FlatF["
            + "x"
            + 10 * "]"
            + "]/. HoldPattern[FlatF[x_]]->FlatF[1]",
            10,
            20,
        ),
        (
            "Hold[OrderlessF["
            + ",".join(LIST_VALUES)
            + "]]/. HoldPattern[OrderlessF[x__]]->F[1]",
            10,
            20,
        ),
        (
            "Hold[OrderlessF["
            + ",".join(LIST_VALUES)
            + "u->1,v:>2]]/. HoldPattern[OrderlessF[x__],opt:OptionValues[]]->F[1, {opt}]",
            10,
            20,
        ),
        ("Cases[{1,2,3,4}, x_Integer /; x>2]", 10, 20),
        ("Select[Range[100], PrimeQ]", 10, 20),
        ("Range[100]/.{a__Integer}->a[[1]]", 10, 20),
        ("F@@Join[Range[100],a->1]/.F[a__Integer,OptionsPattern[]]->a[[1]]", 10, 20),
        (
            "OrderlessF@@Join[Range[100],a->1]/.F[a__Integer,OptionsPattern[]]->a[[1]]",
            10,
            20,
        ),
    ],
    "plot": [
        ("p=Plot[Sin[2 Pi x],{x,0,3}];", 3, 1),
        ("p=Plot[If[x>1,x,-x],{x,0,3}];", 3, 1),
        ("p=DensityPlot[x*y,{x,0,3},{y,0,3}];", 3, 1),
        ("p=Plot3D[x*y,{x,0,3},{y,0,3}];", 3, 1),
    ],
}

# Flatten the structure to parametrize the tests
BENCHMARK_TASKS = [("reset::reset", None, 3, 1000)]
for category, tasks in REGRESSION_BENCHMARKS.items():
    for expr, repeat, number in tasks:
        # Names for the report
        short_expr = expr[:40] + "..." if len(expr) > 40 else expr
        name = f"{category}::{short_expr}"
        print("parse", expr)
        p_expr = session.parse(expr)
        BENCHMARK_TASKS.append((name, p_expr, repeat, number))

# Explicit ids
param_ids = [name for name, _, _, _ in BENCHMARK_TASKS]


import pytest


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
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
    print("name", name)
    evaluation = session.evaluation
    definitions = evaluation.definitions
    if expr is None:
        session.reset()
        evaluation = session.evaluation
        definitions = evaluation.definitions
        # Ensure that all the symbols exists
        session.evaluate(
            "{0,1,2,3,4,5,6,7,10,25,100,1000,F,FlatF, OrderlessF,A,B, i,j,u,v,x,y,z,a,b,c};"
        )
        session.evaluate("SetAttributes[FlatF, Flat];")
        session.evaluate("SetAttributes[OrderlessF, Orderless];")
        session.evaluate("nonuniformTable=Table[If[i==0,1,1./(1.+i^2)],{i, 0,100}];")
        session.evaluate("uniformTable=Table[1./(1.+i^2),{i,0,100}];")
        session.evaluate("listelems={" + ",".join(LIST_VALUES) + "};")

        def impl():
            evaluation.iteration_count = 0
            evaluation.stopped = False
            evaluation.out.clear()
            return

    else:

        def impl():
            # Evaluating the session
            definitions.now += 1
            evaluation.iteration_count = 0
            evaluation.stopped = False
            evaluation.out.clear()
            expr.clear_cache()
            expr.evaluate(evaluation)

    benchmark.pedantic(impl, rounds=repeat, iterations=number)
