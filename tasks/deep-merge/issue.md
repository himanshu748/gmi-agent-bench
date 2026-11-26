`merge.deep_merge(base, override)` is supposed to recursively merge two config dicts, but:

- nested dicts are replaced instead of merged: `deep_merge({"db": {"host": "a", "port": 1}}, {"db": {"port": 2}})` should give `{"db": {"host": "a", "port": 2}}`
- it mutates `base` (and nested dicts inside it). Neither argument may be modified, and the result must not share nested dict or list objects with the inputs
- lists are replaced, not concatenated
- if one side has a dict and the other a non-dict for the same key, the override value wins
- a value of `None` in `override` deletes that key from the result
- merging works at any depth
