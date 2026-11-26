import pytest
from csvline import split_csv_line


@pytest.mark.parametrize("line,exp", [
    ('a,"b,c",d', ["a", "b,c", "d"]),
    ('"say ""hi""",x', ['say "hi"', "x"]),
    ("a,,b,", ["a", "", "b", ""]),
    ("", [""]),
    (" a , b ", [" a ", " b "]),
    ('"",x', ["", "x"]),
    ('"a""b"', ['a"b']),
    ("a,b,c", ["a", "b", "c"]),
])
def test_split(line, exp):
    assert split_csv_line(line) == exp


def test_sep():
    assert split_csv_line('a;"b;c";d', sep=";") == ["a", "b;c", "d"]


def test_unterminated():
    with pytest.raises(ValueError):
        split_csv_line('a,"b')
