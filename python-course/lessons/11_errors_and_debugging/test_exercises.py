import pytest


# Exercise 1
def test_parse_share_basic(ex):
    assert ex.parse_share("45.5%") == pytest.approx(0.455)
    assert ex.parse_share(" 12 % ") == pytest.approx(0.12)
    assert ex.parse_share("60") == pytest.approx(0.6)


def test_parse_share_bounds(ex):
    assert ex.parse_share("0%") == 0
    assert ex.parse_share("100%") == pytest.approx(1.0)
    with pytest.raises(ValueError):
        ex.parse_share("101%")
    with pytest.raises(ValueError):
        ex.parse_share("-3%")


def test_parse_share_junk(ex):
    with pytest.raises(ValueError):
        ex.parse_share("n/a")
    with pytest.raises(ValueError):
        ex.parse_share("")


# Exercise 2
def test_safe_ratio(ex):
    assert ex.safe_ratio(10, 4) == 2.5
    assert ex.safe_ratio(0, 5) == 0
    assert ex.safe_ratio(3, 0) is None, "dividing by zero should give None"


# Exercise 3
def test_get_pollster(ex):
    assert ex.get_pollster({"pollster": "  Ipsos "}) == "Ipsos"
    assert ex.get_pollster({}) == "unknown", "missing key -> default"
    assert ex.get_pollster({"pollster": None}) == "unknown", "None -> default"
    assert ex.get_pollster({}, default="?") == "?"


# Exercise 4
def test_last_n(ex):
    assert ex.last_n([1, 2, 3, 4], 2) == [3, 4], "order should be preserved"
    assert ex.last_n([1, 2, 3], 1) == [3]
    assert ex.last_n([1, 2, 3], 10) == [1, 2, 3]
    assert ex.last_n([1, 2, 3], 0) == []
    assert ex.last_n([], 3) == []


def test_last_n_new_list(ex):
    polls = [1, 2, 3]
    out = ex.last_n(polls, 3)
    out.append(99)
    assert polls == [1, 2, 3], "don't return the original list object"


# Exercise 5
def test_parse_record_good(ex):
    assert ex.parse_record("YouGov, 2024-03-01, 1500, 45.5%") == {
        "pollster": "YouGov", "date": "2024-03-01", "sample": 1500,
        "share": pytest.approx(0.455),
    }
    r = ex.parse_record("  Ipsos ,2024-04-10,800,  38 ")
    assert r["pollster"] == "Ipsos" and r["sample"] == 800
    assert r["share"] == pytest.approx(0.38)


@pytest.mark.parametrize("line", [
    "YouGov, 2024-03-01, 1500",              # too few fields
    "YouGov, 2024-03-01, 1500, 45%, extra",  # too many
    ", 2024-03-01, 1500, 45%",               # empty pollster
    "YouGov, 2024-03-01, lots, 45%",         # sample not int
    "YouGov, 2024-03-01, 1500.5, 45%",       # sample not int
    "YouGov, 2024-03-01, 0, 45%",            # sample not positive
    "YouGov, 2024-03-01, -20, 45%",
    "YouGov, 2024-03-01, 1500, 145%",        # share out of range
    "YouGov, 2024-03-01, 1500, ???",         # share junk
])
def test_parse_record_bad(ex, line):
    with pytest.raises(ValueError):
        ex.parse_record(line)


# Exercise 6
LINES = [
    "YouGov, 2024-03-01, 1500, 45%",
    "",
    "Ipsos, 2024-03-02, abc, 40%",
    "Survation, 2024-03-03, 1000, 50%",
    "   ",
    "broken line",
]


def test_parse_all(ex):
    records, errors = ex.parse_all(LINES)
    assert [r["pollster"] for r in records] == ["YouGov", "Survation"]
    assert [n for n, _ in errors] == [3, 6], "line numbers count from 1, blanks included"
    assert all(isinstance(msg, str) and msg for _, msg in errors)


def test_parse_all_empty(ex):
    assert ex.parse_all([]) == ([], [])


# Exercise 7
def test_weighted_share(ex):
    recs = [{"share": 0.40, "sample": 1000}, {"share": 0.50, "sample": 3000}]
    assert ex.weighted_share(recs) == pytest.approx(0.475)


def test_weighted_share_empty(ex):
    with pytest.raises(ValueError):
        ex.weighted_share([])


# Exercise 8
def test_error_name(ex):
    assert ex.error_name(int, "abc") == "ValueError"
    assert ex.error_name(len, 5) == "TypeError"
    assert ex.error_name(abs, -3) == "ok"
    assert ex.error_name(lambda: {}["x"]) == "KeyError"
    assert ex.error_name(lambda: [][0]) == "IndexError"
    assert ex.error_name(lambda: 1 / 0) == "ZeroDivisionError"
