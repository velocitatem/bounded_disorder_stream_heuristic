"""Batch Local-Inversion Repair Sort."""

from collections import deque


def repair_sort(arr: list) -> tuple[list, int]:
    """Sort arr using repeated local-inversion repair passes.

    Returns (sorted_list, number_of_passes).
    """
    arr = deque(arr)
    turns = 0

    while True:
        turns += 1
        arr_new: deque = deque()
        last = None
        sorted_this_pass = True

        while arr:
            item = arr.popleft()

            if last is not None and item < last:
                arr_new.appendleft(item)
                sorted_this_pass = False
            else:
                arr_new.append(item)

            last = item

        arr = arr_new

        if sorted_this_pass:
            break

    return list(arr), turns
