import pytest


def test_total_after_months(ex):
    assert ex.total_after_months(500, 100, 50, 0) == pytest.approx(500)
    assert ex.total_after_months(500, 100, 50, 1) == pytest.approx(550)
    assert ex.total_after_months(500, 100, 50, 2) == pytest.approx(601.0), \
        "month 2 income is 101 (grew 1% after month 1)"
    assert ex.total_after_months(0, 100, 100, 12) == pytest.approx(68.25)


def test_compound_schedule(ex):
    assert ex.compound_schedule(1000, 0.1, 3) == pytest.approx([1000, 1100.0, 1210.0, 1331.0])
    assert ex.compound_schedule(500, 0.05, 0) == pytest.approx([500])


def test_compound_schedule_length(ex):
    assert len(ex.compound_schedule(100, 0.04, 10)) == 11, "years + 1 entries (year 0 included)"
    assert ex.compound_schedule(100, 0.04, 10)[-1] == pytest.approx(148.02)


def test_months_until_bankrupt(ex):
    assert ex.months_until_bankrupt(100, 50, 80, 0) == 4
    assert ex.months_until_bankrupt(0, 50, 51, 0) == 1
    assert ex.months_until_bankrupt(100, 50, 40, 0) is None


def test_months_until_bankrupt_growth(ex):
    # expenses start below income but grow 2% a month
    assert ex.months_until_bankrupt(1000, 600, 520, 0.02) == 23


def test_months_until_bankrupt_zero_is_ok(ex):
    assert ex.months_until_bankrupt(30, 50, 80, 0) == 2, "a balance of exactly 0 is not bankrupt"
    assert ex.months_until_bankrupt(60, 50, 80, 0) == 3


def test_longest_win_streak(ex):
    assert ex.longest_win_streak("WWLWWWL") == 3
    assert ex.longest_win_streak("") == 0
    assert ex.longest_win_streak("LLL") == 0
    assert ex.longest_win_streak("WWWW") == 4, "a streak that runs to the end still counts"
    assert ex.longest_win_streak("LWLWWLW") == 2


def test_first_month_over(ex):
    assert ex.first_month_over([100, 250, 900, 1200], 500) == 3
    assert ex.first_month_over([600], 500) == 1, "months are counted from 1"
    assert ex.first_month_over([100, 250], 500) is None
    assert ex.first_month_over([500, 501], 500) == 2, "strictly above"


def test_net_by_month(ex):
    assert ex.net_by_month([600, 640], [580, 650]) == [20, -10]
    assert ex.net_by_month([], []) == []


def test_taxable_income(ex):
    assert ex.taxable_income([100, 200, 300], [0, 3, 8]) == pytest.approx(200)
    assert ex.taxable_income([100, 100, 100, 100], [0.5, 1, 5, 5.1]) == pytest.approx(200)
    assert ex.taxable_income([], []) == pytest.approx(0)
