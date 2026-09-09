import time

from mathics.core.load_builtin import import_and_load_builtins

import_and_load_builtins()

from mathics.session import MathicsSession


def reconstruct_scan(self, eligible):
    return [rule for i, rule in enumerate(self._rules) if i in eligible]


def reconstruct_sorted(self, eligible):
    return [self._rules[i] for i in sorted(eligible)]


def bench_reconstruction(n_rules, n_calls, reconstruct_fn):
    session = MathicsSession(character_encoding="ASCII")
    rules_src = ", ".join(f"f[_Integer, {i}] -> {i}" for i in range(n_rules))
    d = session.evaluate(f"Dispatch[{{{rules_src}}}]")
    idx = d.dispatch_index

    target = session.evaluate(f"f[3, {n_rules - 1}]")

    # Isolate ONLY the final reordering step -- compute the eligible set
    # the same way candidates() does (regardless of which tier resolved
    # it), then time just the two ways of turning it into an ordered list.
    eligible = idx._compute_eligible(target)

    t0 = time.perf_counter()
    for _ in range(n_calls):
        reconstruct_fn(idx, eligible)
    return time.perf_counter() - t0


if __name__ == "__main__":
    n_calls = 20000
    for n_rules in (100, 1000, 10000, 50000):
        t_scan = bench_reconstruction(n_rules, n_calls, reconstruct_scan)
        t_sorted = bench_reconstruction(n_rules, n_calls, reconstruct_sorted)
        print(
            f"n_rules={n_rules:>6} n_calls={n_calls}  "
            f"scan(O(n))={t_scan:.4f}s  sorted(O(k log k))={t_sorted:.4f}s  "
            f"speedup={t_scan / t_sorted:.1f}x"
        )
