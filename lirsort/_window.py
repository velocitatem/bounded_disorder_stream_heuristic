"""Shared window repair primitive used by stream and metrics modules."""

from collections import deque


def repair_window(arr: list) -> tuple[list, int, int]:
    """Apply local-inversion repair passes to a small buffer.

    Returns (repaired_list, passes, inversions_detected).
    """
    buf = deque(arr)
    continuity = 0
    turns = 0
    inversions = 0

    while len(buf) > 1 and continuity <= len(buf) - 2:
        turns += 1
        buf_new: deque = deque()
        last = None
        continuity = 0

        while buf:
            item = buf.popleft()

            if last is not None and item < last:
                buf_new.appendleft(item)
                inversions += 1
            else:
                buf_new.append(item)

            if last is not None and item >= last:
                continuity += 1
            else:
                continuity = 0

            last = item

        buf = buf_new

    return list(buf), turns, inversions
