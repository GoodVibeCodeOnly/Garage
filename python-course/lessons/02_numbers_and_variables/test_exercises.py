import math

import pytest


def test_monthly_net(ex):
    assert ex.monthly_net(600, 150, 360, 40) == 350
    assert ex.monthly_net(100, 0, 200, 50) == -150, "a deficit should be negative"


def test_regiments_affordable(ex):
    assert ex.regiments_affordable(1000, 85) == (11, 65)
    assert ex.regiments_affordable(85, 85) == (1, 0)
    assert ex.regiments_affordable(50, 85) == (0, 50)


def test_regiments_are_ints(ex):
    r, left = ex.regiments_affordable(1000, 85)
    assert isinstance(r, int) and isinstance(left, int), "use // and %, not /"


def test_loan_balance(ex):
    assert ex.loan_balance(1000, 0.04, 10) == pytest.approx(1480.24)
    assert ex.loan_balance(750, 0.05, 4) == pytest.approx(911.63)
    assert ex.loan_balance(500, 0.1, 0) == pytest.approx(500)


def test_real_value(ex):
    assert ex.real_value(1000, 0.03, 4) == pytest.approx(888.487, abs=1e-3)
    assert ex.real_value(1000, 0.0, 10) == pytest.approx(1000)


def test_monthly_rate(ex):
    assert ex.monthly_rate(0.12) == pytest.approx(0.0094888, rel=1e-4)
    assert ex.monthly_rate(0.12) != pytest.approx(0.01), "don't just divide by 12"


def test_monthly_rate_roundtrip(ex):
    m = ex.monthly_rate(0.07)
    assert (1 + m) ** 12 - 1 == pytest.approx(0.07)


def test_years_to_double(ex):
    assert ex.years_to_double(0.05) == 15
    assert ex.years_to_double(0.10) == 8
    assert ex.years_to_double(1.0) == 1
    assert isinstance(ex.years_to_double(0.05), int)


def test_loans_needed(ex):
    assert ex.loans_needed(700, 250) == 3
    assert ex.loans_needed(750, 250) == 3, "an exact multiple needs no extra loan"
    assert ex.loans_needed(751, 250) == 4
    assert ex.loans_needed(0, 250) == 0


def test_nearly_equal(ex):
    assert ex.nearly_equal(0.1 + 0.2, 0.3) is True
    assert ex.nearly_equal(0.3, 0.31) is False
    assert ex.nearly_equal(sum([0.1] * 10), 1.0) is True
