import pytest
from lirsort import repair_sort


def test_basic():
    assert repair_sort([3, 1, 2])[0] == [1, 2, 3]


def test_already_sorted_single_pass():
    _, passes = repair_sort(list(range(10)))
    assert passes == 1


def test_reverse_sorted():
    assert repair_sort([5, 4, 3, 2, 1])[0] == [1, 2, 3, 4, 5]


def test_duplicates():
    data = [3, 1, 3, 2, 1]
    assert repair_sort(data)[0] == sorted(data)


def test_single_element():
    result, passes = repair_sort([42])
    assert result == [42] and passes == 1


def test_empty():
    result, passes = repair_sort([])
    assert result == [] and passes == 1


def test_does_not_mutate_input():
    original = [5, 3, 1, 4, 2]
    repair_sort(original)
    assert original == [5, 3, 1, 4, 2]
