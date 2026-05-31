import random
import pytest
from lirsort import perturbed_stream_sort
from lirsort.metrics import DisorderMetrics, perturbed_stream_sort_with_metrics


PERTURBED = [1, 2, 4, 3, 5, 8, 6, 7, 9, 11, 10, 12]


def test_stream_sorts_within_lag():
    assert list(perturbed_stream_sort(PERTURBED, max_lag=3)) == sorted(PERTURBED)


def test_stream_empty():
    assert list(perturbed_stream_sort([], max_lag=4)) == []


def test_stream_single_item():
    assert list(perturbed_stream_sort([7], max_lag=4)) == [7]


def test_stream_already_sorted():
    data = list(range(20))
    assert list(perturbed_stream_sort(data, max_lag=4)) == data


def test_lag_violation_produces_wrong_output():
    bad = [0, 1, 2, 3, 4, 5, 6, -1]
    result = list(perturbed_stream_sort(bad, max_lag=3))
    assert result != sorted(bad)


def _make_stream(noise, seed=0):
    rng = random.Random(seed)
    base = list(range(50))
    for i in range(len(base)):
        j = min(len(base) - 1, i + rng.randint(0, noise))
        base[i], base[j] = base[j], base[i]
    return base


def test_disorder_score_increases_with_noise():
    scores = []
    for noise in (0, 2, 5):
        m = DisorderMetrics()
        list(perturbed_stream_sort_with_metrics(_make_stream(noise), max_lag=noise + 2, metrics=m))
        scores.append(m.disorder_score)
    assert scores[0] <= scores[1] <= scores[2]


def test_zero_disorder_on_sorted_input():
    m = DisorderMetrics()
    list(perturbed_stream_sort_with_metrics(range(20), max_lag=4, metrics=m))
    assert m.total_inversions == 0
    assert m.disorder_score == 0.0
