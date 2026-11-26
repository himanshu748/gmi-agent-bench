"""Tiny semantic-version helpers."""
import functools
import re

_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$")


def parse(version):
    m = _RE.match(version.strip()) if isinstance(version, str) else None
    if not m:
        raise ValueError(f"invalid version: {version!r}")
    core = tuple(int(x) for x in m.group(1, 2, 3))
    pre = tuple(m.group(4).split(".")) if m.group(4) else ()
    return core, pre


def _cmp_ident(x, y):
    xn, yn = x.isdigit(), y.isdigit()
    if xn and yn:
        x, y = int(x), int(y)
    elif xn != yn:
        return -1 if xn else 1
    return (x > y) - (x < y)


def compare(a, b):
    """Return -1 if a < b, 0 if equal, 1 if a > b."""
    (ca, pa), (cb, pb) = parse(a), parse(b)
    if ca != cb:
        return -1 if ca < cb else 1
    if not pa or not pb:
        return (not pa) - (not pb) if (pa or pb) else 0
    for x, y in zip(pa, pb):
        c = _cmp_ident(x, y)
        if c:
            return c
    return (len(pa) > len(pb)) - (len(pa) < len(pb))


def sort_versions(versions):
    return sorted(versions, key=functools.cmp_to_key(compare))
