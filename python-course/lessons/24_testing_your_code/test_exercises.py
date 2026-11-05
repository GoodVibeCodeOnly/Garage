import statistics

import pytest


# ---- Exercises 1-3 --------------------------------------------------------

@pytest.mark.parametrize("x,lo,hi,exp", [
    (5, 0, 10, 5), (-3, 0, 10, 0), (99, 0, 10, 10), (0, 0, 10, 0), (10, 0, 10, 10), (2.5, 1, 3, 2.5),
])
def test_clamp(ex, x, lo, hi, exp):
    assert ex.clamp(x, lo, hi) == exp


def test_clamp_bad_range(ex):
    with pytest.raises(ValueError):
        ex.clamp(1, 5, 0)


def test_win_rate(ex):
    assert ex.win_rate(7, 10) == pytest.approx(0.7)
    assert isinstance(ex.win_rate(1, 1), float)


@pytest.mark.parametrize("w,g", [(0, 0), (-1, 4), (5, 4), (1, -1)])
def test_win_rate_errors(ex, w, g):
    with pytest.raises(ValueError):
        ex.win_rate(w, g)


@pytest.mark.parametrize("text,exp", [
    ("12.5%", 0.125), (" 40 % ", 0.4), ("-3%", -0.03), ("7", 0.07), ("100%", 1.0),
])
def test_parse_percent(ex, text, exp):
    assert ex.parse_percent(text) == pytest.approx(exp)


@pytest.mark.parametrize("bad", ["", "%", "abc%", "12%%", "  "])
def test_parse_percent_rejects(ex, bad):
    with pytest.raises(ValueError):
        ex.parse_percent(bad)


# ---- Exercises 4-5 --------------------------------------------------------

def test_find_median_bug_cases(ex):
    cases = ex.find_median_bug_cases()
    assert len(cases) >= 2 and len({tuple(c) for c in cases}) >= 2, "need 2+ distinct cases"
    for c in cases:
        assert len(c) > 0
        assert ex.buggy_median(list(c)) != statistics.median(c), f"{c} doesn't expose the bug"


def _true_tax(income):
    return 0.2 * max(0, min(income, 50_000) - 10_000) + 0.4 * max(0, income - 50_000)


def test_find_tax_bug_incomes(ex):
    incomes = ex.find_tax_bug_incomes()
    assert any(i <= 60_000 for i in incomes), "include one income <= 60_000"
    for i in incomes:
        assert i >= 0
        assert ex.buggy_tax(i) != pytest.approx(_true_tax(i)), f"buggy_tax({i}) is actually correct"


# ---- Exercises 6-7: mutation testing --------------------------------------

def good_clamp(x, lo, hi):
    if lo > hi:
        raise ValueError
    return max(lo, min(x, hi))


def mut_clamp_no_lo(x, lo, hi):
    if lo > hi:
        raise ValueError
    return min(x, hi)


def mut_clamp_no_hi(x, lo, hi):
    if lo > hi:
        raise ValueError
    return max(lo, x)


def mut_clamp_no_check(x, lo, hi):
    return max(lo, min(x, hi))


def mut_clamp_boundary(x, lo, hi):
    if lo > hi:
        raise ValueError
    if x <= lo:
        return lo + (x == lo)   # off-by-one exactly at lo
    return min(x, hi)


def test_check_clamp_accepts_correct(ex):
    ex.check_clamp(good_clamp)   # must not raise


@pytest.mark.parametrize("mutant", [mut_clamp_no_lo, mut_clamp_no_hi, mut_clamp_no_check, mut_clamp_boundary])
def test_check_clamp_catches_mutant(ex, mutant):
    ex.check_clamp(good_clamp)   # a suite that rejects everything doesn't count
    with pytest.raises(BaseException):
        ex.check_clamp(mutant)


def good_win_rate(w, g):
    if g <= 0 or not 0 <= w <= g:
        raise ValueError
    return w / g


def mut_wr_no_zero(w, g):
    if not 0 <= w <= g:
        raise ValueError
    return 0.0 if g == 0 else w / g


def mut_wr_int(w, g):
    if g <= 0 or not 0 <= w <= g:
        raise ValueError
    return w // g if w % g == 0 else w / g   # returns int for 0/n and n/n


def mut_wr_allows_over(w, g):
    if g <= 0 or w < 0:
        raise ValueError
    return w / g


def mut_wr_allows_negative(w, g):
    if g <= 0 or w > g:
        raise ValueError
    return w / g


def mut_wr_wrong(w, g):
    if g <= 0 or not 0 <= w <= g:
        raise ValueError
    return w / (g + 1)


def test_check_win_rate_accepts_correct(ex):
    ex.check_win_rate(good_win_rate)


@pytest.mark.parametrize("mutant", [mut_wr_no_zero, mut_wr_int, mut_wr_allows_over,
                                    mut_wr_allows_negative, mut_wr_wrong])
def test_check_win_rate_catches_mutant(ex, mutant):
    ex.check_win_rate(good_win_rate)
    with pytest.raises(BaseException):
        ex.check_win_rate(mutant)
