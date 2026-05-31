"""Streaming Local-Inversion Repair Sort with bounded lag."""

from typing import Iterable, Iterator
from ._window import repair_window


def perturbed_stream_sort(stream: Iterable, max_lag: int = 8) -> Iterator:
    """Yield sorted items from a bounded-disorder stream.

    Items may be displaced by at most max_lag positions. Larger max_lag
    tolerates more disorder but increases per-item cost.
    """
    buffer: list = []

    for item in stream:
        buffer.append(item)

        if len(buffer) > max_lag:
            buffer, _, _ = repair_window(buffer)
            yield buffer.pop(0)

    buffer, _, _ = repair_window(buffer)
    yield from buffer
