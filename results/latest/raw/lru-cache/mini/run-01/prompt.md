You are working in a small Python repository (the current directory).
Resolve the following issue.

<issue>
`lru.LRUCache` does not behave like a least-recently-used cache.

- `get(key)` should mark the key as most recently used, but it doesn't, so a key that was just read can be evicted next.
- `put` on an existing key should update the value and mark it most recently used without evicting anything.
- `get` on a missing key should return the `default` argument (default `None`).
- `len(cache)` and `key in cache` should work, and `in` must not change recency.
- Creating a cache with capacity < 1 should raise `ValueError`.
</issue>

Change the source code so the behaviour described in the issue is correct.
Hidden tests that check every point in the issue will be run after you finish,
and the existing tests in tests/ must keep passing. Do not edit or delete tests.
You can run the tests with `python -m pytest -q`. When you are done, stop.
