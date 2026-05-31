# Local-Inversion Repair Sort (LIR Sort)

>
> **bounded-buffer repair heuristic and disorder metric for perturbed streams** - situations where data arrives almost in order but occasionally late. Use it when you need to sort a stream *and* measure how disordered it was. If you only need to sort, use a min-heap.



## What it is useful for

### 1. Sorting slightly-out-of-order streams while measuring their disorder

LIR Sort is designed for streams where each item arrives within `k` positions of its true sorted position (the *k-sorted* or *bounded-lag* model). A min-heap solves the same sorting problem more efficiently (`O(log k)` per item), but it tells you nothing about the stream's health. LIR Sort exposes every local inversion it encounters, giving you live diagnostics alongside the sorted output:

```python
from lirsort.metrics import DisorderMetrics, perturbed_stream_sort_with_metrics

m = DisorderMetrics()
sorted_events = list(perturbed_stream_sort_with_metrics(event_stream, max_lag=8, metrics=m))

print(m.disorder_score)          # 0.0 = perfectly ordered, 1.0 = heavily perturbed
print(m.avg_passes_per_window)   # average repair effort per buffer window
print(m.total_inversions)        # raw count of detected local drops
```

If `disorder_score` starts climbing unexpectedly, the stream is experiencing more perturbation than usual - a signal worth alerting on before downstream consumers notice.

### 2. Stream health monitoring without a separate analysis pass

Because the repair loop counts inversions as a byproduct of sorting, there is no second pass over the data. You get sorted output *and* a disorder score from a single traversal of the buffer.

Possible uses:
- **Distributed log aggregation** - detect when a node is producing delayed or reordered events.
- **Sensor / IoT telemetry** - flag increased network jitter by watching `avg_passes_per_window` rise.
- **Financial tick feeds** - quantify how out-of-order a feed is becoming without a separate monitoring pipeline.
- **Streaming ETL quality gates** - reject or flag windows whose `disorder_score` exceeds a threshold before they reach a database.

### 3. Educational visualisation of local disorder repair

The repair rule is intentionally simple and visually legible:

```
scan left → right
if current item < previous item:   prepend it to the next buffer   (it arrived late)
else:                              append it normally
repeat until one full pass has no local drops
```

That makes it a good teaching vehicle for:
- what a local inversion is
- why bounded-disorder assumptions matter in streaming
- the tradeoff between buffer depth and output latency
- how adaptive sorting differs from comparison-based worst-case sorting



## Literature context

The broad ideas here are not new. Adaptive sorting, inversion-based disorder measures, k-sorted stream sorting with heaps, and out-of-order event-time processing (watermarks, Flink-style windowing) all cover this ground more rigorously.

The specific prepend-on-local-drop transformation - scan, detect `item < last`, prepend to next buffer, repeat - appears uncommon enough to be an independent heuristic, but it has not been benchmarked against stronger baselines and should not be positioned as a competitive sorting algorithm.

The honest niche is the one described above: a single-pass repair loop that also reports how hard it had to work.



## Quick start

```python
from lirsort import perturbed_stream_sort

stream = [1, 2, 4, 3, 5, 8, 6, 7, 9, 11, 10, 12]
result = list(perturbed_stream_sort(stream, max_lag=3))
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
```

Run the full demo:

```bash
python demo.py
```

Run tests:

```bash
python -m pytest tests/
```


## Known limitation

The bounded-lag assumption is required for correctness. If an item arrives more than `max_lag` positions late, it may be emitted out of order. This is not a bug - it is a fundamental constraint of online sorting without full lookahead.

```python
bad_stream = [0, 1, 2, 3, 4, 5, 6, -1]   # -1 arrives 7 positions late
list(perturbed_stream_sort(bad_stream, max_lag=3))
# output is NOT [−1, 0, 1, 2, 3, 4, 5, 6]
```
