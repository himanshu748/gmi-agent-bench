"""Interval utilities."""


def merge_intervals(intervals):
    """Merge overlapping closed intervals given as (start, end) pairs."""
    items = []
    for start, end in intervals:
        if start > end:
            raise ValueError(f"start > end: {(start, end)}")
        items.append((start, end))
    items.sort()
    result = []
    for start, end in items:
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], end))
        else:
            result.append((start, end))
    return result
