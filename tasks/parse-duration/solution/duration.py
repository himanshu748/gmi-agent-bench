"""Parse human-readable durations."""
import re

_RE = re.compile(
    r"^\s*(?:(\d+(?:\.\d+)?)\s*d)?\s*(?:(\d+(?:\.\d+)?)\s*h)?\s*(?:(\d+(?:\.\d+)?)\s*m)?\s*(?:(\d+(?:\.\d+)?)\s*s)?\s*$",
    re.IGNORECASE,
)
_MULT = (86400, 3600, 60, 1)


def parse_duration(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("empty duration")
    m = _RE.match(text)
    if not m or all(g is None for g in m.groups()):
        raise ValueError(f"invalid duration: {text!r}")
    total = sum(float(g) * k for g, k in zip(m.groups(), _MULT) if g is not None)
    return int(round(total))
