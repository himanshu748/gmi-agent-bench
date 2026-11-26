`intervals.merge_intervals` returns wrong results.

- Touching intervals should merge: `[(1, 3), (3, 5)]` should become `[(1, 5)]`, but it stays as two.
- Unsorted input is not handled: `[(5, 7), (1, 2), (2, 4)]` should give `[(1, 4), (5, 7)]`.
- An interval fully inside another, like `[(1, 10), (2, 3)]`, should give `[(1, 10)]`, but the end shrinks to 3.
- The function must not mutate the caller's list, and must return a list of tuples.
- Empty input returns `[]`. An interval whose start is greater than its end should raise `ValueError`.
