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

    # warm/compute the eligible set once the same way candidates() does,
    # so we isolate ONLY the final reordering step.
    from itertools import product

    head = target.head
    elements = target.elements
    table = idx._groups[(head, len(elements))]
    from mathics.core.symbols import Atom
    from mathics.eval.rule_dispatch_index import MAX_INDEXED_POSITIONS

    n_positions = min(len(elements), MAX_INDEXED_POSITIONS)
    options_per_position = []
    for pos in range(n_positions):
        arg = elements[pos]
        opts = [("wild",)]
        if isinstance(arg, Atom):
            opts.append(("lit", arg))
        arg_head = arg.get_head() if hasattr(arg, "get_head") else None
        if arg_head is not None:
            opts.append(("head", arg_head))
        options_per_position.append(opts)
    eligible = set(idx._fallback_ids)
    for combo in product(*options_per_position):
        ids = table.get(combo)
        if ids:
            eligible.update(ids)

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
