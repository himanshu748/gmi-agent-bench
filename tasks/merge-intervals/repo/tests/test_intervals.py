from intervals import merge_intervals


def test_overlap():
    assert merge_intervals([(1, 4), (2, 6)]) == [(1, 6)]


def test_disjoint():
    assert merge_intervals([(1, 2), (5, 6)]) == [(1, 2), (5, 6)]
