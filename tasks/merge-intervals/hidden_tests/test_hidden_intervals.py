import pytest
from intervals import merge_intervals


def test_touching():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]


def test_unsorted():
    assert merge_intervals([(5, 7), (1, 2), (2, 4)]) == [(1, 4), (5, 7)]


def test_contained():
    assert merge_intervals([(1, 10), (2, 3)]) == [(1, 10)]


def test_contained_then_more():
    assert merge_intervals([(1, 10), (2, 3), (9, 12), (20, 21)]) == [(1, 12), (20, 21)]


def test_empty():
    assert merge_intervals([]) == []


def test_no_mutation():
    data = [(3, 4), (1, 2)]
    merge_intervals(data)
    assert data == [(3, 4), (1, 2)]


def test_returns_tuples():
    out = merge_intervals([[1, 2], [2, 3]])
    assert out == [(1, 3)] and all(isinstance(x, tuple) for x in out)


def test_invalid():
    with pytest.raises(ValueError):
        merge_intervals([(5, 1)])


def test_regression_overlap():
    assert merge_intervals([(1, 4), (2, 6)]) == [(1, 6)]
