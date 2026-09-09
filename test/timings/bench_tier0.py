import time

from mathics.core.load_builtin import import_and_load_builtins

import_and_load_builtins()

from mathics.eval.rule_dispatch_index import RuleDispatchIndex
from mathics.session import MathicsSession

_real_candidates = RuleDispatchIndex.candidates


def _no_filter_candidates(self, expr):
    return self._rules


def bench(n_rules, n_lookups, use_index):
    session = MathicsSession(character_encoding="ASCII")
    RuleDispatchIndex.candidates = (
        _real_candidates if use_index else _no_filter_candidates
    )

    # Every rule shares the exact same first 2 positions (_Integer,
    # _Integer) -- with only Tier 1 (capped at MAX_INDEXED_POSITIONS=2)
    # these would all land in ONE shared bucket, indistinguishable.
    # They differ only in position 3 (a distinct literal per rule),
    # which Tier 0 (full arity) can resolve directly.
    rules_src = ", ".join(
        f"f[_Integer, _Integer, {i}, _Symbol] -> {i}" for i in range(n_rules)
    )
    session.evaluate(f"d = Dispatch[{{{rules_src}}}]")

    expr_hit_last = f"f[1, 2, {n_rules - 1}, sym]"
    expr_miss = f"f[1, 2, {n_rules}, sym]"

    t0 = time.perf_counter()
    for _ in range(n_lookups):
        session.evaluate(f"{expr_hit_last} /. d")
    t_hit = time.perf_counter() - t0

    t0 = time.perf_counter()
    for _ in range(n_lookups):
        session.evaluate(f"{expr_miss} /. d")
    t_miss = time.perf_counter() - t0

    RuleDispatchIndex.candidates = _real_candidates
    return t_hit, t_miss


if __name__ == "__main__":
    for n_rules in (50, 200, 1000):
        n_lookups = 300
        t_hit_full, t_miss_full = bench(n_rules, n_lookups, use_index=False)
        t_hit_idx, t_miss_idx = bench(n_rules, n_lookups, use_index=True)
        print(f"n_rules={n_rules} n_lookups={n_lookups}")
        print(
            f"  hit(last rule):  full={t_hit_full:.4f}s  indexed={t_hit_idx:.4f}s  "
            f"speedup={t_hit_full / t_hit_idx:.1f}x"
        )
        print(
            f"  miss:            full={t_miss_full:.4f}s  indexed={t_miss_idx:.4f}s  "
            f"speedup={t_miss_full / t_miss_idx:.1f}x"
        )
