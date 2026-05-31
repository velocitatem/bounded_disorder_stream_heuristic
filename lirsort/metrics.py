"""Stream sort with disorder metrics — the diagnostic face of LIR Sort."""

from dataclasses import dataclass, field
from typing import Iterable, Iterator
from ._window import repair_window


@dataclass
class DisorderMetrics:
    total_passes: int = 0
    total_inversions: int = 0
    repair_calls: int = 0
    max_passes_single_window: int = 0
    items_emitted: int = 0

    @property
    def avg_passes_per_window(self) -> float:
        return self.total_passes / self.repair_calls if self.repair_calls else 0.0

    @property
    def avg_inversions_per_window(self) -> float:
        return self.total_inversions / self.repair_calls if self.repair_calls else 0.0

    @property
    def disorder_score(self) -> float:
        """Normalised [0, 1] indicator of stream perturbation.

        A score near 0 means the stream was nearly sorted.
        A score near 1 means heavy disorder within each window.
        """
        if self.repair_calls == 0:
            return 0.0
        return min(self.avg_inversions_per_window / max(self.items_emitted, 1), 1.0)

    def __str__(self) -> str:
        return (
            f"DisorderMetrics("
            f"repair_calls={self.repair_calls}, "
            f"total_passes={self.total_passes}, "
            f"total_inversions={self.total_inversions}, "
            f"avg_passes={self.avg_passes_per_window:.2f}, "
            f"avg_inversions={self.avg_inversions_per_window:.2f}, "
            f"disorder_score={self.disorder_score:.4f})"
        )


def perturbed_stream_sort_with_metrics(
    stream: Iterable,
    max_lag: int = 8,
    metrics: DisorderMetrics | None = None,
) -> Iterator:
    """Like perturbed_stream_sort but accumulates disorder metrics in-place.

    Pass an existing DisorderMetrics instance to aggregate across multiple
    stream segments. A new one is created if none is provided (and discarded
    after the call — retrieve it via the generator's .metrics attribute).

    Usage::

        m = DisorderMetrics()
        result = list(perturbed_stream_sort_with_metrics(stream, metrics=m))
        print(m)
    """
    if metrics is None:
        metrics = DisorderMetrics()

    buffer: list = []

    for item in stream:
        buffer.append(item)

        if len(buffer) > max_lag:
            buffer, passes, inversions = repair_window(buffer)
            metrics.total_passes += passes
            metrics.total_inversions += inversions
            metrics.repair_calls += 1
            metrics.max_passes_single_window = max(
                metrics.max_passes_single_window, passes
            )
            emitted = buffer.pop(0)
            metrics.items_emitted += 1
            yield emitted

    buffer, passes, inversions = repair_window(buffer)
    metrics.total_passes += passes
    metrics.total_inversions += inversions
    metrics.repair_calls += 1
    metrics.max_passes_single_window = max(metrics.max_passes_single_window, passes)

    for item in buffer:
        metrics.items_emitted += 1
        yield item
