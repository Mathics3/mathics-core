import os
from test.helper import session

import pytest

from mathics.core import pattern as pattern_module
from mathics.core.pattern import BasePattern
from mathics.core.symbols import strip_context


def _hold_pattern(pattern_text):
    """Build a BasePattern from an unevaluated held expression."""
    held = session.evaluate(f"HoldForm[{pattern_text}]")
    expr = held.elements[0]
    return BasePattern.create(expr, evaluation=session.evaluation)


def _held_expression(expr_text):
    """Build an unevaluated Expression from HoldForm."""
    held = session.evaluate(f"HoldForm[{expr_text}]")
    print("held:", held)
    return held.elements[0]


# ---------------------------------------------------------------------------
# Benchmarks for mathics.core.pattern / mathics.core.rules
#
# Each block below targets one specific hypothesis about a performance
# hotspot in the pattern-matching engine:
#
#   1. Orderless + Flat matching (Plus/Times-like): permutation blow-up
#      in ExpressionPattern.get_wrappings.
#   2. "leading_blanks" fast path in basic_match_expression -- guards
#      against regressing the optimization already documented in a
#      comment in pattern.py.
#   3. BlankSequence/BlankNullSequence backtracking over long lists --
#      isolates the cost of pattern_context.copy() per candidate,
#      without combinatorial (Orderless) blow-up.
#   4. FunctionApplyRule.apply_function hot path (strip_context per
#      variable, called on every builtin application).
#   5. Orderless matching with repeated pattern variable names
#      (get_pre_choices_orderless / expr_groups rebuild).
#   6. pattern_precedence, direct micro-benchmark (no evaluator).
#
# IMPORTANT: `session` (test.helper.session) is a module-level singleton
# shared by every test file that imports it. If two files both call
# session.reset() / define named session variables at *import time*
# (module top level), whichever file is imported last wins, and any
# variables defined by the other file's import-time setup are gone by
# the time its tests actually run -- this bit us the first time around
# (see the failures where `sum3`, `bigList`, `f`'s rules, etc. had been
# wiped out by test_uniform_tables.py's own session.reset()).
#
# To make each benchmark immune to import order / to other files also
# using `session`, every test below (re)establishes exactly the session
# state it needs via pytest-benchmark's `setup=` callback, which runs
# right before each round and is NOT included in the measured time.
# Nothing here relies on module-level session.evaluate() calls surviving
# until the test actually runs.
# ---------------------------------------------------------------------------

ORDERLESS_NS = [3, 5, 7, 9, 11]

# Reduce this if the FunctionApplyRule benchmark is too slow for routine
# CI runs; raise it if you want to see the strip_context cost more
# clearly relative to Table/evaluation overhead.
FUNCTIONAPPLY_N = 500

leading_blanks_expect = str(1 + sum(range(5001)))
functionapply_expect = str(sum(i // 7 + i % 7 for i in range(1, FUNCTIONAPPLY_N + 1)))

if os.environ.get("BENCHMARKS", 0):
    # This reset is just for hygiene when running this file in isolation;
    # correctness of the tests below does NOT depend on it surviving.
    session.reset()

    # --- 6. pattern_precedence (micro, no evaluation involved) ------------
    # Build an unevaluated pattern expression via HoldForm (same trick
    # helper.check_evaluation uses for hold_expected), then wrap it as a
    # BasePattern so we can hit `.pattern_precedence` directly, bypassing
    # the evaluator entirely. This is a plain Python object once built,
    # so unlike the other setups it is NOT affected by later
    # session.reset() calls from other test modules.
    _precedence_expr = session.evaluate(
        "HoldForm[f[x_, y_, z_Integer, {a__}, w_ : 3]]"
    ).elements[0]
    precedence_pattern = BasePattern.create(
        _precedence_expr, evaluation=session.evaluation
    )


# ---------------------------------------------------------------------------
# 1. Orderless + Flat scaling
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", ORDERLESS_NS, ids=lambda n: f"n={n}")
def test_orderless_plus_match_benchmark(benchmark, n):
    """Matching x0_+x1_+...+x_{n-1}_ against an n-term symbolic Plus.

    NOTE: this does NOT exercise the permutation blow-up in
    get_wrappings -- every x{i}_ is an exact-count-1 Blank, so `items`
    passed to get_wrappings always has length 1 and the
    `permutations(items)` branch is never reached. What this *does*
    measure is the cost of the subsets()-based search for which
    expression element goes to which pattern slot. Empirically this
    grows close to linearly with n (see
    test_orderless_blank_sequence_wrapping_benchmark below for a case
    that actually hits the permutation path).
    """
    args = ",".join(f"a{i}" for i in range(n))
    pattern = "+".join(f"x{i}_" for i in range(n))
    expr = f"MatchQ[sum{n}, {pattern}]"

    def setup():
        # Symbolic (non-numeric) arguments so Plus doesn't auto-collapse
        # the sum into a single number. Re-run before every round so this
        # doesn't depend on any other test module's session.reset().
        session.evaluate(f"sum{n} = Plus[{args}];")

    def impl():
        assert str(session.evaluate(expr)) == "System`True"

    benchmark.pedantic(impl, setup=setup, rounds=15, warmup_rounds=3, iterations=1)


# ---------------------------------------------------------------------------
# 1b. Orderless + Flat: actual permutation blow-up in get_wrappings
# ---------------------------------------------------------------------------
ORDERLESS_WRAP_NS = [4, 6, 8, 10]


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", ORDERLESS_WRAP_NS, ids=lambda n: f"n={n}")
def test_orderless_blank_sequence_wrapping_benchmark(benchmark, n):
    """x__ + y__ against an n-term symbolic Plus.

    Unlike the exact-Blank case above, x__/y__ are variable-length
    (BlankSequence), so whichever subset of terms x__ ends up capturing
    (if more than one term), get_wrappings has to build a Sequence out
    of it -- and because the head (Plus) is Orderless, it tries EVERY
    permutation of that subset (`for perm in permutations(items)`).
    This is the code path the n-scaling benchmark above does not reach.
    Expect much worse than linear growth here.
    """
    args = ",".join(f"b{i}" for i in range(n))
    expr = f"MatchQ[wrapsum{n}, x__+y__]"

    def setup():
        session.evaluate(f"wrapsum{n} = Plus[{args}];")

    def impl():
        assert str(session.evaluate(expr)) == "System`True"

    benchmark.pedantic(impl, setup=setup, rounds=5, iterations=1)


# ---------------------------------------------------------------------------
# 1c. Orderless + Flat: forced exhaustive search (the real n! case)
# ---------------------------------------------------------------------------
# Keep this small on purpose: n=6 already means enumerating on the order
# of 6! candidate (subset, permutation) combinations, each one paying the
# pattern_context.copy() cost from hypothesis 1. Raise cautiously.
ORDERLESS_FAIL_NS = [3, 4, 5, 6]


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", ORDERLESS_FAIL_NS, ids=lambda n: f"n={n}")
def test_orderless_exhaustive_failure_benchmark(benchmark, n):
    """x__ + y__ /; False against an n-term symbolic Plus.

    The Condition (/;) always fails, so unlike
    test_orderless_blank_sequence_wrapping_benchmark, does_match can
    never short-circuit on the first candidate -- it must exhaust every
    (subset split, permutation) combination before concluding there's
    no match. This is the actual worst-case combinatorial path in
    get_wrappings / expression_pattern_match_element_orderless. No
    setup= needed: the Plus expression is built inline, no named
    session variable involved.
    """
    args = ",".join(f"c{i}" for i in range(n))
    expr = f"MatchQ[Plus[{args}], x__+y__ /; False]"

    def impl():
        assert str(session.evaluate(expr)) == "System`False"

    benchmark.pedantic(impl, rounds=3, iterations=1)


# ---------------------------------------------------------------------------
# 2. leading_blanks fast path
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
def test_leading_blanks_benchmark(benchmark):
    """Same case documented in the comment in pattern.py:
        f[x_, {a__, b_}] = 0;
        f[x_, y_] := y + Total[x];
        First[Timing[f[Range[5000], 1]]]
    We drop Timing (non-deterministic) and check the actual result.
    """

    def setup():
        session.evaluate("Clear[f];")
        session.evaluate("f[x_, {a__, b_}] := 0;")
        session.evaluate("f[x_, y_] := y + Total[x];")

    def impl():
        assert str(session.evaluate("f[Range[5000], 1]")) == leading_blanks_expect

    # setup= requires iterations=1 (pytest-benchmark re-runs setup once
    # per round, not once per iteration); bump rounds instead to keep a
    # similar total sample count.
    benchmark.pedantic(impl, setup=setup, rounds=20, iterations=1)


# ---------------------------------------------------------------------------
# 3. BlankSequence backtracking over a long list
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize(
    ["expr", "expect"],
    [
        # match found near the end of the list: forces backtracking
        # through most of it before succeeding.
        ("MatchQ[bigList, {a___, 3000, b___}]", "System`True"),
        # match never found: forces backtracking through the *entire*
        # list before giving up -- typically the more expensive case.
        ("MatchQ[bigList, {a___, 3001, b___}]", "System`False"),
    ],
)
def test_blank_sequence_backtracking_benchmark(benchmark, expr, expect):
    def setup():
        session.evaluate("bigList = Range[3000];")

    def impl():
        assert str(session.evaluate(expr)) == expect

    # setup= requires iterations=1; bump rounds instead.
    benchmark.pedantic(impl, setup=setup, rounds=20, iterations=1)


# ---------------------------------------------------------------------------
# 4. FunctionApplyRule / strip_context hot path
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
def test_functionapplyrule_hot_path_benchmark(benchmark):
    """Repeated application of multi-argument builtins (Quotient, Mod) --
    each call binds several pattern variables, exercising
    FunctionApplyRule.apply_function's strip_context step many times.
    No named session variable is used here, so no setup= is needed --
    this test was never affected by the cross-file reset issue.
    """
    expr = f"Total[Table[Quotient[i,7]+Mod[i,7], {{i,1,{FUNCTIONAPPLY_N}}}]]"

    def impl():
        assert str(session.evaluate(expr)) == functionapply_expect

    benchmark.pedantic(impl, rounds=5, iterations=1)


# ---------------------------------------------------------------------------
# 4b. strip_context isolated (no evaluator involved)
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
def test_strip_context_call_cost_benchmark(benchmark):
    """Isolates just the string-processing cost that
    FunctionApplyRule.apply_function pays per parameter, per call
    (vars_noctx = dict((strip_context(s), vars[s]) for s in vars)).
    Compare this mean against test_functionapplyrule_hot_path_benchmark's
    per-call mean to see what fraction of that cost is actually
    strip_context vs. the rest of the evaluation machinery (rule lookup,
    argument binding, Table iteration, etc).
    """
    names = [f"System`Private`x{i}" for i in range(4)]
    vars_dict = {n: i for i, n in enumerate(names)}

    def build_noctx():
        return dict(((strip_context(s), vars_dict[s]) for s in vars_dict))

    benchmark(build_noctx)


# ---------------------------------------------------------------------------
# 5. Orderless matching with repeated pattern variable names
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
def test_orderless_repeated_names_benchmark(benchmark):
    def setup():
        session.evaluate("SetAttributes[g, Orderless];")
        session.evaluate("repData = g[1,1,2,2,3,3,4,4,5,5];")

    def impl():
        assert (
            str(session.evaluate("MatchQ[repData, g[a_, a_, rest___]]"))
            == "System`True"
        )

    # setup= requires iterations=1; bump rounds instead, plus a short
    # warmup to absorb first-call session/cache effects (this benchmark
    # showed a ~2x single-run outlier in comparisons before any code
    # changed at all -- see context.md diagnostic notes).
    benchmark.pedantic(impl, setup=setup, rounds=30, warmup_rounds=5, iterations=1)


# ---------------------------------------------------------------------------
# 6. pattern_precedence (micro, no evaluator involved)
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
def test_pattern_precedence_repeated_access_benchmark(benchmark):
    """pattern_precedence rebuilds its sort-key tuple on every access
    (see build_pattern_sort_key in pattern.py) -- this simulates the
    repeated access that happens when sorting many rules/elements that
    share this pattern, e.g. during Orderless sort() or rule dispatch.
    `precedence_pattern` is a plain Python object built once at import
    time and is unaffected by session.reset() calls from other files,
    so no setup= is needed here.

    """

    def impl():
        for _ in range(2000):
            _ = precedence_pattern.pattern_precedence

    benchmark.pedantic(impl, rounds=30, warmup_rounds=5, iterations=5)


# ---------------------------------------------------------------------------
# 7. get_match_candidates() vs get_match_candidates_count()
# ---------------------------------------------------------------------------
CANDIDATE_NS = [10, 100, 1000, 5000]


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", CANDIDATE_NS, ids=lambda n: f"n={n}")
def test_get_match_candidates_benchmark(benchmark, n):
    """Measure the full candidate collection path.

    ExpressionPattern.get_match_candidates() calls does_match() on every
    element and materializes a tuple of successful candidates.
    """
    pattern = _hold_pattern("f[x_]")
    expr = _held_expression("g[" + ",".join(f"f[a{i}]" for i in range(n)) + "]")
    print("expr:", expr)
    candidates = tuple(expr.elements)
    context = {
        "evaluation": session.evaluation,
        "vars_dict": {},
    }

    def impl():
        result = pattern.get_match_candidates(candidates, context)
        assert len(result) == n

    benchmark(impl)


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", CANDIDATE_NS, ids=lambda n: f"n={n}")
def test_get_match_candidates_count_benchmark(benchmark, n):
    """Measure only the candidate-count path.

    This isolates the cost of asking "how many candidates match?" from the
    caller-visible tuple allocation done by get_match_candidates().
    """
    pattern = _hold_pattern("f[x_]")
    expr = _held_expression("f[" + ",".join(f"f[a{i}]" for i in range(n)) + "]")
    candidates = tuple(expr.elements)
    context = {
        "evaluation": session.evaluation,
        "vars_dict": {},
    }

    def impl():
        count = pattern.get_match_candidates_count(candidates, context)
        assert count == n

    benchmark(impl)


# ---------------------------------------------------------------------------
# 8. does_match() scaling
# ---------------------------------------------------------------------------
DOES_MATCH_NS = [10, 100, 1000, 5000]


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", DOES_MATCH_NS, ids=lambda n: f"n={n}")
@pytest.mark.parametrize(
    "pattern_text",
    [
        "x_",
        "x_Integer",
        "f[x_]",
    ],
    ids=["blank", "integer", "expr"],
)
def test_does_match_scaling_benchmark(benchmark, n, pattern_text):
    """Measure repeated does_match() calls independently of candidate setup."""
    pattern = _hold_pattern(pattern_text)

    elements = [session.evaluate(str(i)) for i in range(n)]

    def impl():
        matches = 0
        for element in elements:
            if pattern.does_match(
                element,
                {
                    "evaluation": session.evaluation,
                    "vars_dict": {},
                },
            ):
                matches += 1
        # Keep the result meaningful for the benchmark.
        assert matches >= 0

    benchmark(impl)


# ---------------------------------------------------------------------------
# 9. Orderless repeated names: match/fail scaling
# ---------------------------------------------------------------------------
REPEATED_NAME_NS = [4, 6, 8, 10, 12]


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", REPEATED_NAME_NS, ids=lambda n: f"n={n}")
@pytest.mark.parametrize(
    "success",
    [True, False],
    ids=["match", "fail"],
)
def test_orderless_repeated_names_scaling_benchmark(benchmark, n, success):
    """Scale the get_pre_choices_orderless()/per_name() path.

    The successful case contains a repeated value so a_, a_ can be bound.
    The failing case uses all distinct arguments and therefore has to reject
    candidate assignments.
    """
    args = (
        ",".join(["1", "1"] + [str(i) for i in range(2, n)])
        if success
        else ",".join(str(i) for i in range(1, n + 1))
    )
    expr = f"MatchQ[rep{n}, g[a_, a_, rest___]]"

    def setup():
        session.evaluate("SetAttributes[g, Orderless];")
        session.evaluate(f"rep{n} = g[{args}];")

    def impl():
        expected = "System`True" if success else "System`False"
        assert str(session.evaluate(expr)) == expected

    benchmark.pedantic(
        impl,
        setup=setup,
        rounds=20,
        warmup_rounds=4,
        iterations=1,
    )


# ---------------------------------------------------------------------------
# 10. BlankSequence backtracking by literal position
# ---------------------------------------------------------------------------
BLANK_POSITION_NS = [100, 300, 1000, 2000]


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", BLANK_POSITION_NS, ids=lambda n: f"n={n}")
@pytest.mark.parametrize(
    "position",
    ["first", "middle", "last", "absent"],
    ids=["literal-first", "literal-middle", "literal-last", "literal-absent"],
)
def test_blank_sequence_position_scaling_benchmark(benchmark, n, position):
    """Measure how BlankSequence backtracking depends on literal position."""
    if position == "first":
        literal = 1
    elif position == "middle":
        literal = n // 2
    elif position == "last":
        literal = n
    else:
        literal = n + 1

    expr = f"MatchQ[positionList{n}, {{a___, {literal}, b___}}]"
    expected = "System`True" if position != "absent" else "System`False"

    def setup():
        session.evaluate(f"positionList{n} = Range[{n}];")

    def impl():
        assert str(session.evaluate(expr)) == expected

    benchmark.pedantic(
        impl,
        setup=setup,
        rounds=10,
        iterations=1,
    )


# ---------------------------------------------------------------------------
# 11. Multiple BlankSequences
# ---------------------------------------------------------------------------
MULTI_BLANK_NS = [30, 60, 100, 150]


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", MULTI_BLANK_NS, ids=lambda n: f"n={n}")
@pytest.mark.parametrize(
    "case",
    ["success", "fail"],
    ids=["match", "fail"],
)
def test_multiple_blank_sequences_benchmark(benchmark, n, case):
    """Exercise backtracking with several variable-length sequence patterns."""
    if case == "success":
        literal1 = n // 3
        literal2 = 2 * n // 3
        expected = "System`True"
    else:
        literal1 = n + 1
        literal2 = n + 2
        expected = "System`False"

    expr = f"MatchQ[multiList{n}, " f"{{a___, {literal1}, b___, {literal2}, c___}}]"

    def setup():
        session.evaluate(f"multiList{n} = Range[{n}];")

    def impl():
        assert str(session.evaluate(expr)) == expected

    benchmark.pedantic(
        impl,
        setup=setup,
        rounds=10,
        iterations=1,
    )


# ---------------------------------------------------------------------------
# 12. OneIdentity / Optional
# ---------------------------------------------------------------------------

ONE_IDENTITY_CASES = [
    ("f[1]", "f[x_, y_:3]", "System`True"),
    ("f[1,2]", "f[x_, y_:3]", "System`True"),
    ("1", "f[x_, y_:3]", "System`True"),
    ("f[1,2,3]", "f[x_:1,y_:2,z_:3,w_]", "System`True"),
    ("f[1,2]", "f[x_:1,y_:2,z_]", "System`True"),
    ("f[1]", "f[x_:1,y_:2,z_:3]", "System`True"),
]


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize(
    ["expr_text", "pattern_text", "expected"],
    ONE_IDENTITY_CASES,
    ids=[
        "optional-present",
        "optional-empty",
        "oneidentity-atom",
        "multiple-optionals-present",
        "multiple-optionals-insufficient2",
        "multiple-optionals-insufficient",
    ],
)
def test_one_identity_optional_benchmark(benchmark, expr_text, pattern_text, expected):
    """Exercise match_expression_with_one_identity() and Optional defaults."""
    expr = f"ClearAll[f,x,y,z,w];SetAttributes[f,OneIdentity];MatchQ[{expr_text}, {pattern_text}]"
    print("evaluating", expr, " == ", expected)

    def impl():
        assert str(session.evaluate(expr)) == expected

    benchmark.pedantic(
        impl,
        rounds=20,
        iterations=1,
    )


# ---------------------------------------------------------------------------
# Diagnostic state-count test for Orderless.
#
# This is intentionally a normal test, not a benchmark: monkeypatching
# subsets()/permutations() changes the measured code path enough to make a
# timing comparison misleading. Its purpose is to report the amount of
# combinatorial work generated by the current matcher.
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0), reason="benchmarks not required"
)
@pytest.mark.parametrize("n", [3, 4, 5, 6], ids=lambda n: f"n={n}")
def test_orderless_state_count_diagnostic(monkeypatch, capsys, n):
    """Report generated subset/permutation states for the worst-case matcher."""
    counters = {
        "subsets": 0,
        "subset_items": 0,
        "permutations": 0,
        "permutation_items": 0,
    }

    original_subsets = pattern_module.subsets
    original_permutations = pattern_module.permutations

    def counted_subsets(*args, **kwargs):
        counters["subsets"] += 1
        for item in original_subsets(*args, **kwargs):
            counters["subset_items"] += 1
            yield item

    def counted_permutations(items):
        items = tuple(items)
        counters["permutations"] += 1
        for perm in original_permutations(items):
            counters["permutation_items"] += 1
            yield perm

    monkeypatch.setattr(pattern_module, "subsets", counted_subsets)
    monkeypatch.setattr(pattern_module, "permutations", counted_permutations)

    args = ",".join(f"diag{i}" for i in range(n))
    expr = f"MatchQ[Plus[{args}], x__+y__/;False]"

    assert str(session.evaluate(expr)) == "System`False"

    print(
        f"Orderless n={n}: "
        f"subsets_calls={counters['subsets']}, "
        f"subset_items={counters['subset_items']}, "
        f"permutations_calls={counters['permutations']}, "
        f"permutation_items={counters['permutation_items']}"
    )


@pytest.mark.skipif(
    not os.environ.get("BENCHMARKS", 0),
    reason="benchmarks not required",
)
@pytest.mark.parametrize(
    "n",
    [100, 300, 1000, 2000],
    ids=lambda n: f"n={n}",
)
@pytest.mark.parametrize(
    "position",
    ["first", "middle", "last", "absent"],
    ids=[
        "literal-first",
        "literal-middle",
        "literal-last",
        "literal-absent",
    ],
)
def test_blank_sequence_partition_count(monkeypatch, n, position):
    """Diagnostic count of partitions generated by subranges()."""

    if position == "first":
        literal = 1
    elif position == "middle":
        literal = n // 2
    elif position == "last":
        literal = n
    else:
        literal = n + 1

    counters = {
        "subranges_calls": 0,
        "partitions": 0,
    }

    original_subranges = pattern_module.subranges

    def counted_subranges(*args, **kwargs):
        counters["subranges_calls"] += 1
        for result in original_subranges(*args, **kwargs):
            counters["partitions"] += 1
            yield result

    monkeypatch.setattr(pattern_module, "subranges", counted_subranges)

    expr = f"MatchQ[partitionList{n}, " f"{{a___, {literal}, b___}}]"

    expected = "System`True" if position != "absent" else "System`False"

    session.evaluate(f"partitionList{n} = Range[{n}];")

    assert str(session.evaluate(expr)) == expected

    print(
        f"n={n:5d} "
        f"position={position:6s} "
        f"subranges_calls={counters['subranges_calls']:4d} "
        f"partitions={counters['partitions']:10d}"
    )
