#!/usr/bin/env python3
"""Interactive demonstration of Local-Inversion Repair Sort.

Run with:  python demo.py
"""

import random
from lirsort import repair_sort, perturbed_stream_sort
from lirsort.metrics import DisorderMetrics, perturbed_stream_sort_with_metrics


# ── helpers ──────────────────────────────────────────────────────────────────

def make_perturbed_stream(n: int, max_lag: int, seed: int = 42) -> list[int]:
    """Generate a sorted sequence with random local perturbations."""
    rng = random.Random(seed)
    base = list(range(n))
    out = base.copy()
    for i in range(n):
        j = min(n - 1, i + rng.randint(0, max_lag))
        out[i], out[j] = out[j], out[i]
    return out


def header(text: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {text}")
    print('─' * 60)


# ── demo 1: batch sort ────────────────────────────────────────────────────────

header("1 · Batch repair sort")

data = [5, 3, 8, 1, 9, 2, 7, 4, 6]
print(f"  input : {data}")
sorted_data, passes = repair_sort(data)
print(f"  output: {sorted_data}")
print(f"  passes: {passes}")


# ── demo 2: already-sorted data exits in one pass ────────────────────────────

header("2 · Already-sorted input — one pass")

already = list(range(10))
_, passes = repair_sort(already)
print(f"  passes needed: {passes}  (expected 1)")


# ── demo 3: streaming sort on a perturbed stream ─────────────────────────────

header("3 · Streaming sort — perturbed stream (max_lag=3)")

stream = [1, 2, 4, 3, 5, 8, 6, 7, 9, 11, 10, 12]
print(f"  input : {stream}")
result = list(perturbed_stream_sort(stream, max_lag=3))
print(f"  output: {result}")
print(f"  sorted: {result == sorted(stream)}")


# ── demo 4: disorder metrics ──────────────────────────────────────────────────

header("4 · Disorder metrics on a synthetic perturbed stream")

for noise in (1, 3, 6):
    stream = make_perturbed_stream(100, max_lag=noise)
    m = DisorderMetrics()
    _ = list(perturbed_stream_sort_with_metrics(stream, max_lag=noise + 2, metrics=m))
    print(f"  noise={noise:2d}  {m}")


# ── demo 5: failure case (lag violated) ──────────────────────────────────────

header("5 · Failure case — item arrives later than max_lag allows")

bad_stream = [0, 1, 2, 3, 4, 5, 6, -1]
result = list(perturbed_stream_sort(bad_stream, max_lag=3))
print(f"  input : {bad_stream}")
print(f"  output: {result}")
print(f"  sorted: {result == sorted(bad_stream)}  ← expected False: lag violated")


# ── demo 6: disorder detection as a stream health signal ─────────────────────

header("6 · Disorder score as a stream health signal")

print("  Simulating streams with increasing disorder levels:\n")
print(f"  {'lag':>4}  {'disorder_score':>14}  {'avg_passes':>10}")
print(f"  {'─'*4}  {'─'*14}  {'─'*10}")

for lag in range(0, 9):
    stream = make_perturbed_stream(200, max_lag=lag)
    m = DisorderMetrics()
    _ = list(perturbed_stream_sort_with_metrics(stream, max_lag=lag + 2, metrics=m))
    print(f"  {lag:>4}  {m.disorder_score:>14.4f}  {m.avg_passes_per_window:>10.2f}")

print()
