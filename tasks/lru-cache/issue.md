`lru.LRUCache` does not behave like a least-recently-used cache.

- `get(key)` should mark the key as most recently used, but it doesn't, so a key that was just read can be evicted next.
- `put` on an existing key should update the value and mark it most recently used without evicting anything.
- `get` on a missing key should return the `default` argument (default `None`).
- `len(cache)` and `key in cache` should work, and `in` must not change recency.
- Creating a cache with capacity < 1 should raise `ValueError`.
