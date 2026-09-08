import time

from mathics.core.load_builtin import import_and_load_builtins

import_and_load_builtins()

from mathics.eval.rule_dispatch_index import RuleDispatchIndex
from mathics.session import MathicsSession

_real_candidates = RuleDispatchIndex.candidates


def _no_filter_candidates(self, expr):
    return self._rules


def bench(n_rules, n_lookups, use_index, wide_position0=False):
    session = MathicsSession(character_encoding="ASCII")
    RuleDispatchIndex.candidates = (
        _real_candidates if use_index else _no_filter_candidates
    )

    if wide_position0:
        # Stress case: EVERY rule shares the same type at position 0
        # (large bucket there), and discrimination really happens at
        # position 1. This is where per-position set-intersection has
        # to build/copy a big set for position 0, while the combined-key
        # design still narrows straight to a small bucket via position 1.
        rules_src = ", ".join(f"f[_Integer, {i}] -> {i}" for i in range(n_rules))
        expr_hit_last = f"f[3, {n_rules - 1}]"
        expr_miss = f"f[3, {n_rules}]"
    else:
        # A realistic "type dispatch table" shape: many rules on the same
        # head, differentiated mostly by argument type -- the case the
        # user flagged as common (`head[_h1, _h2, ...]`).
        rules_src = ", ".join(
            f"f[{i}, _Integer, _Symbol] -> {i}" for i in range(n_rules)
        )
        expr_hit_last = f"f[{n_rules - 1}, 3, sym]"
        expr_miss = f"f[{n_rules}, 3, sym]"

    session.evaluate(f"d = Dispatch[{{{rules_src}}}]")

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
    print("=== narrow bucket at position 0 (original shape) ===")
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

    print("\n=== wide bucket at position 0, real discrimination at position 1 ===")
    for n_rules in (50, 200, 1000):
        n_lookups = 300
        t_hit_full, t_miss_full = bench(
            n_rules, n_lookups, use_index=False, wide_position0=True
        )
        t_hit_idx, t_miss_idx = bench(
            n_rules, n_lookups, use_index=True, wide_position0=True
        )
        print(f"n_rules={n_rules} n_lookups={n_lookups}")
        print(
            f"  hit(last rule):  full={t_hit_full:.4f}s  indexed={t_hit_idx:.4f}s  "
            f"speedup={t_hit_full / t_hit_idx:.1f}x"
        )
        print(
            f"  miss:            full={t_miss_full:.4f}s  indexed={t_miss_idx:.4f}s  "
            f"speedup={t_miss_full / t_miss_idx:.1f}x"
        )
