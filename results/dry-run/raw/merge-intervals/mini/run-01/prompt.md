You are working in a small Python repository (the current directory).
Resolve the following issue.

<issue>
`intervals.merge_intervals` returns wrong results.

- Touching intervals should merge: `[(1, 3), (3, 5)]` should become `[(1, 5)]`, but it stays as two.
- Unsorted input is not handled: `[(5, 7), (1, 2), (2, 4)]` should give `[(1, 4), (5, 7)]`.
- An interval fully inside another, like `[(1, 10), (2, 3)]`, should give `[(1, 10)]`, but the end shrinks to 3.
- The function must not mutate the caller's list, and must return a list of tuples.
- Empty input returns `[]`. An interval whose start is greater than its end should raise `ValueError`.
</issue>

Change the source code so the behaviour described in the issue is correct.
Hidden tests that check every point in the issue will be run after you finish,
and the existing tests in tests/ must keep passing. Do not edit or delete tests.
You can run the tests with `python -m pytest -q`. When you are done, stop.
