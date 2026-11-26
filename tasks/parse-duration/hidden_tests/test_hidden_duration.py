import pytest
from duration import parse_duration


@pytest.mark.parametrize("text,exp", [
    ("1h30m", 5400), ("90s", 90), ("2h", 7200), ("1d2h", 93600),
    ("1h30m15s", 5415), (" 1h 5m ", 3900), ("1.5h", 5400), ("0.5m", 30),
    ("2H", 7200), ("45m", 2700), ("1d", 86400),
])
def test_valid(text, exp):
    out = parse_duration(text)
    assert out == exp and isinstance(out, int)


@pytest.mark.parametrize("text", ["", "   ", "5x", "10", "5m1h", "1h1h", "-5m", "h"])
def test_invalid(text):
    with pytest.raises(ValueError):
        parse_duration(text)
