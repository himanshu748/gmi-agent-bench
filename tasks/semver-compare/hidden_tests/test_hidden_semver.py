import pytest
from semver import compare, sort_versions


@pytest.mark.parametrize("a,b,exp", [
    ("1.10.0", "1.9.0", 1),
    ("1.9.0", "1.10.0", -1),
    ("2.0.0", "10.0.0", -1),
    ("1.0.0", "1.0.0", 0),
    ("1.0.0-alpha", "1.0.0", -1),
    ("1.0.0", "1.0.0-rc.1", 1),
    ("1.0.0-alpha", "1.0.0-alpha.1", -1),
    ("1.0.0-alpha.1", "1.0.0-alpha.beta", -1),
    ("1.0.0-beta.2", "1.0.0-beta.11", -1),
    ("1.0.0-rc.1", "1.0.0-beta.11", 1),
    ("1.0.0+build.1", "1.0.0+build.9", 0),
    ("1.0.0-rc.1+b", "1.0.0-rc.1", 0),
])
def test_compare(a, b, exp):
    assert compare(a, b) == exp


def test_sort():
    vs = ["1.0.0", "1.0.0-rc.1", "1.0.0-alpha", "1.10.0", "1.9.0", "1.0.0-beta.11", "1.0.0-beta.2"]
    assert sort_versions(vs) == ["1.0.0-alpha", "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0", "1.9.0", "1.10.0"]


@pytest.mark.parametrize("bad", ["1.2", "a.b.c", "1.2.3.4", ""])
def test_invalid(bad):
    with pytest.raises(ValueError):
        compare(bad, "1.0.0")
