#!/usr/bin/env python3
import json
import sys

# Normalize the reported `ops` to the value obtained for a certain task that
# takes nearly 1s.

NORMALIZATION_TASK_KEY = "test_reference_benchmark"


def normalize_benchmarks(target_file):

    if not NORMALIZATION_TASK_KEY:
        print("Normalization not available")
        return

    with open(target_file) as f:
        data = json.load(f)

    # Buscar el benchmark de referencia
    ref_bench = None
    for bench in data["benchmarks"]:
        if bench["name"] == NORMALIZATION_TASK_KEY:
            ref_bench = bench
            break

    if ref_bench is None:
        print(
            f"⚠️ Benchmark for the reference task '{NORMALIZATION_TASK_KEY} not found'. Exit."
        )
        sys.exit(1)

    # Extract the reference value
    ref_value = ref_bench["stats"]["ops"]
    # Store the reference scale in machine info
    data["machine_info"]["reference_time_scale"] = ref_value

    # Normalize the benchmarks
    for bench in data["benchmarks"]:
        if bench["name"] == NORMALIZATION_TASK_KEY:
            bench["stats"]["ops"] = 1.0
        else:
            bench["stats"]["ops"] = bench["stats"]["ops"] / ref_value

    with open(target_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Normalized benchmarks saved in {target_file}.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Use: normalize_benchmarks.py <benchmarkfile.json>")
        sys.exit(1)
    normalize_benchmarks(sys.argv[1])
