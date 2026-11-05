import pytest


def test_win_rate(ex):
    assert ex.win_rate(["W", "L", "W", "W"]) == pytest.approx(0.75)
    assert ex.win_rate(["L", "L"]) == pytest.approx(0.0)


def test_win_rate_empty(ex):
    assert ex.win_rate([]) == 0.0, "empty history should give 0.0, not ZeroDivisionError"


def test_last_n(ex):
    assert ex.last_n(["W", "L", "W"], 2) == ["L", "W"]
    assert ex.last_n(["W", "L", "W"], 10) == ["W", "L", "W"]


def test_last_n_zero(ex):
    assert ex.last_n(["W", "L"], 0) == [], "results[-0:] is the whole list — handle n == 0"


def test_last_n_is_copy(ex):
    src = ["W", "L"]
    out = ex.last_n(src, 5)
    out.append("X")
    assert src == ["W", "L"], "return a new list, not the original"


def test_rating_series(ex):
    assert ex.rating_series(["W", "W", "L"]) == [1516, 1532, 1516]
    assert ex.rating_series([], start=1000) == []


def test_rating_series_params(ex):
    assert ex.rating_series(["L", "W"], start=1000, k=10) == [990, 1000]


def test_peak(ex):
    assert ex.peak([1500, 1530, 1510, 1530]) == (1, 1530), "use the FIRST index of the max"
    assert ex.peak([5]) == (0, 5)


def test_rolling_mean(ex):
    assert ex.rolling_mean([1, 2, 3, 4, 5], 3) == pytest.approx([2.0, 3.0, 4.0])
    assert ex.rolling_mean([10, 20], 1) == pytest.approx([10, 20])


def test_rolling_mean_edges(ex):
    assert ex.rolling_mean([1, 2, 3], 3) == pytest.approx([2.0])
    assert ex.rolling_mean([1, 2], 3) == []


def test_longest_streak(ex):
    assert ex.longest_streak(["W", "W", "L", "W", "W", "W", "L"]) == 3
    assert ex.longest_streak(["W", "L", "L", "W"], kind="L") == 2
    assert ex.longest_streak([]) == 0
    assert ex.longest_streak(["L", "L"]) == 0


def test_longest_streak_at_end(ex):
    assert ex.longest_streak(["L", "W", "W", "W", "W"]) == 4, "don't forget a streak that runs to the end"


def test_top_players(ex):
    table = [["Ana", 1612], ["Ben", 1490], ["Cy", 1530]]
    assert ex.top_players(table, 2) == [["Ana", 1612], ["Cy", 1530]]
    assert table == [["Ana", 1612], ["Ben", 1490], ["Cy", 1530]], "don't reorder the input"


def test_top_players_ties_and_overflow(ex):
    table = [["A", 1500], ["B", 1600], ["C", 1500]]
    assert ex.top_players(table, 10) == [["B", 1600], ["A", 1500], ["C", 1500]]


def test_record_matches(ex):
    h = ["W"]
    assert ex.record_matches(h, ["L", "W"]) == (3, 2)
    assert h == ["W", "L", "W"], "history must be modified in place (use extend)"


def test_record_matches_flat(ex):
    h = []
    ex.record_matches(h, ["W", "W"])
    assert h == ["W", "W"], "items should be added individually, not as a nested list"
