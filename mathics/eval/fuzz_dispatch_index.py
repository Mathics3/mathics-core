import random
import sys

from mathics.core.load_builtin import import_and_load_builtins

import_and_load_builtins()

from mathics.eval.rule_dispatch_index import RuleDispatchIndex
from mathics.session import MathicsSession

_real_candidates = RuleDispatchIndex.candidates


def _no_filter_candidates(self, expr):
    return self._rules


ATOM_POOL = [
    "1",
    "2",
    "3",
    "-1",
    '"a"',
    '"b"',
    "x",
    "y",
    "z",
    "1.5",
    "True",
    "1.0",
    "1``2",
    "0",
    "-0.0",
    "2/3",
    "x_",
    "_Integer",
    "g[x_]",
]

PATTERN_ARG_POOL = [
    "1",
    "2",
    "3",
    "x_",
    "_",
    "_Integer",
    "_String",
    "_Symbol",
    "_Real",
    "x_Integer",
    "y_String",
    "z_",
    "_?(#>0&)",
    "a_/;a>0",
    "_.",
    "x_:9",
    "x__",
    "x___",
    "1|2",
    "Except[1]",
    "1|2|3",
    "_Integer|_String",
    "1|x_",
    "_Integer|_Symbol|4",
]

HEADS = ["f", "g", "h"]


def random_pattern_arg(rng):
    return rng.choice(PATTERN_ARG_POOL)


FULLY_DISCRIMINATED_ARG_POOL = [
    "1",
    "2",
    "3",
    "_Integer",
    "_String",
    "_Symbol",
    "_Real",
    "x_Integer",
    "Verbatim[g[x_]]",
    "1|2|3",
    "_Integer|_String",
]


def random_lhs(rng):
    head = rng.choice(HEADS)
    arity = rng.randint(0, 6)
    if rng.random() < 0.3:
        # Bias toward fully-discriminated rules (no wildcard anywhere)
        # at higher arities, specifically to stress Tier 0.
        args = [rng.choice(FULLY_DISCRIMINATED_ARG_POOL) for _ in range(arity)]
        return f"{head}[{', '.join(args)}]"
    args = [random_pattern_arg(rng) for _ in range(arity)]
    lhs = f"{head}[{', '.join(args)}]"
    r = rng.random()
    if r < 0.2:
        lhs = f"HoldPattern[{lhs}]"
    elif r < 0.3:
        lhs = f"{lhs} /; True"
    elif r < 0.4:
        lhs = f"{lhs} ? (True&)"
    elif r < 0.5 and arity >= 1:
        # Verbatim wrapping one of the arguments, forcing it to be
        # treated as a literal instead of a real pattern.
        args2 = list(args)
        idx = rng.randrange(len(args2))
        args2[idx] = f"Verbatim[{args2[idx]}]"
        lhs = f"{head}[{', '.join(args2)}]"
    return lhs


def random_rule(rng, rhs_id):
    return f"{random_lhs(rng)} -> {rhs_id}"


def random_expr(rng):
    head = rng.choice(HEADS)
    arity = rng.randint(0, 5)
    args = [rng.choice(ATOM_POOL) for _ in range(arity)]
    return f"{head}[{', '.join(args)}]"


def make_orderless_maybe(session, rng):
    if rng.random() < 0.3:
        head = rng.choice(HEADS)
        session.evaluate(f"SetAttributes[{head}, Orderless]")


def run_batch(seed, n_rulesets, n_exprs_per_ruleset, n_rules_per_ruleset):
    rng = random.Random(seed)
    session = MathicsSession(character_encoding="ASCII")
    mismatches = []
    total = 0

    for rs in range(n_rulesets):
        session.evaluate("ClearAll[f, g, h]")
        make_orderless_maybe(session, rng)
        rules_src = ", ".join(random_rule(rng, i) for i in range(n_rules_per_ruleset))
        try:
            dispatch = session.evaluate(f"Dispatch[{{{rules_src}}}]")
        except Exception as e:
            continue
        if not hasattr(dispatch, "rules"):
            continue

        exprs = [random_expr(rng) for _ in range(n_exprs_per_ruleset)]
        for e in exprs:
            total += 1
            full_expr = f"({e}) /. Dispatch[{{{rules_src}}}]"

            RuleDispatchIndex.candidates = _real_candidates
            try:
                r_indexed = session.evaluate(full_expr)
            except Exception as ex:
                r_indexed = ("EXC", str(ex))

            RuleDispatchIndex.candidates = _no_filter_candidates
            try:
                r_full = session.evaluate(full_expr)
            except Exception as ex:
                r_full = ("EXC", str(ex))
            RuleDispatchIndex.candidates = _real_candidates

            if str(r_indexed) != str(r_full):
                mismatches.append((rules_src, e, str(r_indexed), str(r_full)))

    return total, mismatches


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    total, mismatches = run_batch(
        seed, n_rulesets=150, n_exprs_per_ruleset=25, n_rules_per_ruleset=10
    )
    print(f"seed={seed} total_checks={total} mismatches={len(mismatches)}")
    for rules_src, e, r_indexed, r_full in mismatches[:20]:
        print("---MISMATCH---")
        print("rules:", rules_src)
        print("expr:", e)
        print("indexed:", r_indexed)
        print("full   :", r_full)
