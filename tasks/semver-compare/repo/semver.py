"""Tiny semantic-version helpers."""


def parse(version):
    core = version.split("-")[0]
    return core.split(".")


def compare(a, b):
    """Return -1 if a < b, 0 if equal, 1 if a > b."""
    pa, pb = parse(a), parse(b)
    if pa < pb:
        return -1
    if pa > pb:
        return 1
    return 0


def sort_versions(versions):
    return sorted(versions, key=parse)
