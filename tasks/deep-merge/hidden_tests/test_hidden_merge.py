from merge import deep_merge


def test_nested():
    assert deep_merge({"db": {"host": "a", "port": 1}}, {"db": {"port": 2}}) == {"db": {"host": "a", "port": 2}}


def test_deep():
    a = {"x": {"y": {"z": 1, "w": 2}}}
    b = {"x": {"y": {"z": 3}, "v": 4}}
    assert deep_merge(a, b) == {"x": {"y": {"z": 3, "w": 2}, "v": 4}}


def test_no_mutation():
    a = {"db": {"host": "a"}, "l": [1]}
    b = {"db": {"port": 2}, "m": {"k": 1}}
    out = deep_merge(a, b)
    assert a == {"db": {"host": "a"}, "l": [1]}
    assert b == {"db": {"port": 2}, "m": {"k": 1}}
    out["db"]["host"] = "zzz"; out["l"].append(2); out["m"]["k"] = 9
    assert a["db"]["host"] == "a" and a["l"] == [1] and b["m"]["k"] == 1


def test_lists_replaced():
    assert deep_merge({"l": [1, 2]}, {"l": [3]}) == {"l": [3]}


def test_type_conflict():
    assert deep_merge({"a": {"b": 1}}, {"a": 5}) == {"a": 5}
    assert deep_merge({"a": 5}, {"a": {"b": 1}}) == {"a": {"b": 1}}


def test_none_deletes():
    assert deep_merge({"a": 1, "b": {"c": 1, "d": 2}}, {"a": None, "b": {"c": None}}) == {"b": {"d": 2}}


def test_flat():
    assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}
