import pytest


def test_is_bankrupt(ex):
    assert ex.is_bankrupt(-100, -20) is True
    assert ex.is_bankrupt(-100, 50) is False, "recovering, not bankrupt"
    assert ex.is_bankrupt(100, -20) is False
    assert ex.is_bankrupt(0, -20) is False, "0 is not negative"


@pytest.mark.parametrize("margin, label", [
    (6.2, "safe Blue"), (-6.2, "safe Red"), (5, "safe Blue"), (-5, "safe Red"),
    (2.5, "lean Blue"), (-2.5, "lean Red"), (2, "lean Blue"), (4.99, "lean Blue"),
    (1.9, "tossup"), (-1.9, "tossup"), (0, "tossup"),
])
def test_classify_margin(ex, margin, label):
    assert ex.classify_margin(margin) == label


@pytest.mark.parametrize("income, tax", [
    (0, 0), (8_000, 0), (10_000, 0), (25_000, 3_000), (40_000, 6_000),
    (50_000, 10_000), (100_000, 30_000),
])
def test_progressive_tax(ex, income, tax):
    assert ex.progressive_tax(income) == pytest.approx(tax)


def test_progressive_tax_no_cliff(ex):
    assert ex.progressive_tax(40_001) - ex.progressive_tax(40_000) == pytest.approx(0.4), \
        "only the slice above 40k is taxed at 40%"


def test_stability_change(ex):
    assert ex.stability_change(True, 25, -50) == -3
    assert ex.stability_change(True, 15, 100) == -1
    assert ex.stability_change(False, 0, 1500) == 1
    assert ex.stability_change(False, 0, 999) == 0
    assert ex.stability_change(True, 5, 2000) == 0, "the +1 is for peace only"
    assert ex.stability_change(False, 30, -1) == -1, "exhaustion only matters at war"


def test_clamp_stability(ex):
    assert ex.clamp_stability(5) == 3
    assert ex.clamp_stability(-4) == -3
    assert ex.clamp_stability(1) == 1
    assert ex.clamp_stability(3) == 3
    assert ex.clamp_stability(-3) == -3


def test_beats_baseline(ex):
    assert ex.beats_baseline(11, 20) is True
    assert ex.beats_baseline(10, 20) is False, "exactly 50% doesn't beat the baseline"
    assert ex.beats_baseline(0, 0) is False


@pytest.mark.parametrize("balance, label", [
    (-1, "in debt"), (0, "empty"), (1, "tight"), (499.99, "tight"),
    (500, "healthy"), (4999, "healthy"), (5000, "overflowing"), (1e6, "overflowing"),
])
def test_describe_treasury(ex, balance, label):
    assert ex.describe_treasury(balance) == label
