import pytest
from lru import LRUCache


def test_get_refreshes():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3


def test_update_existing_no_evict():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2); c.put("a", 10)
    assert c.get("b") == 2 and c.get("a") == 10 and len(c) == 2


def test_update_refreshes():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2); c.put("a", 3); c.put("c", 4)
    assert "b" not in c and "a" in c


def test_default():
    c = LRUCache(1)
    assert c.get("x") is None and c.get("x", 5) == 5


def test_contains_no_refresh():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    assert "a" in c
    c.put("c", 3)
    assert "a" not in c


def test_len():
    c = LRUCache(3)
    for i in range(10):
        c.put(i, i)
    assert len(c) == 3


@pytest.mark.parametrize("cap", [0, -1])
def test_bad_capacity(cap):
    with pytest.raises(ValueError):
        LRUCache(cap)
