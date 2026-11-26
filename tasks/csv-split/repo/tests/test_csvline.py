from csvline import split_csv_line


def test_plain():
    assert split_csv_line("a,b,c") == ["a", "b", "c"]
