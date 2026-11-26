"""Interval utilities."""


def merge_intervals(intervals):
    """Merge overlapping closed intervals given as (start, end) pairs."""
    result = []
    for start, end in intervals:
        if result and start < result[-1][1]:
            result[-1] = (result[-1][0], end)
        else:
            result.append((start, end))
    return result
