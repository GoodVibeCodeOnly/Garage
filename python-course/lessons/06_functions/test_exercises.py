import pytest


def test_production_basic(ex):
    assert ex.production(100, 2) == pytest.approx(200)


def test_production_efficiency(ex):
    assert ex.production(100, 2, efficiency=0.5) == pytest.approx(100)
    assert ex.production(0, 5) == pytest.approx(0)


def test_upkeep_default(ex):
    assert ex.upkeep(10) == pytest.approx(20.0)


def test_upkeep_keywords(ex):
    assert ex.upkeep(10, discount=0.25) == pytest.approx(15.0)
    assert ex.upkeep(10, cost_per_unit=3, discount=0.5) == pytest.approx(15.0)


def test_tariff_default(ex):
    assert ex.tariff_revenue(500) == pytest.approx(50.0)


def test_tariff_exemption_boundary(ex):
    assert ex.tariff_revenue(200, rate=0.2, exempt_below=300) == 0
    assert ex.tariff_revenue(300, rate=0.2, exempt_below=300) == pytest.approx(60.0), \
        "exempt only when STRICTLY below the threshold"


def test_net_income(ex):
    assert ex.net_income(100, 2, 10, 500) == pytest.approx(230.0)
    assert ex.net_income(0, 0, 5, 0) == pytest.approx(-10.0)


def test_net_income_returns_not_prints(ex):
    assert ex.net_income(10, 1, 0, 0) is not None, "use return, not print"


def test_apply_policy(ex):
    assert ex.apply_policy([100, 200], lambda v: v * 2) == [200, 400]
    assert ex.apply_policy([], abs) == []
    assert ex.apply_policy([-3, 4], abs) == [3, 4]


def test_apply_policy_no_mutation(ex):
    vals = [1, 2, 3]
    ex.apply_policy(vals, lambda v: v * 10)
    assert vals == [1, 2, 3], "must not modify the input list"


def test_best_policy(ex):
    pol = {"low": lambda v: v * 0.05, "high": lambda v: v * 0.2}
    assert ex.best_policy(1000, pol) == "high"


def test_best_policy_depends_on_value(ex):
    pol = {
        "flat": lambda v: v * 0.1,
        "protect": lambda v: 0.0 if v < 300 else v * 0.25,
    }
    assert ex.best_policy(200, pol) == "flat"
    assert ex.best_policy(1000, pol) == "protect"


def test_best_policy_tie_first(ex):
    pol = {"a": lambda v: 1, "b": lambda v: 1}
    assert ex.best_policy(0, pol) == "a"


def test_make_flat_tax(ex):
    tax10 = ex.make_flat_tax(0.1)
    assert callable(tax10), "make_flat_tax must return a function"
    assert tax10(500) == pytest.approx(50.0)
    assert ex.make_flat_tax(0.25)(400) == pytest.approx(100.0)


def test_make_flat_tax_independent(ex):
    a, b = ex.make_flat_tax(0.1), ex.make_flat_tax(0.5)
    assert (a(100), b(100)) == (pytest.approx(10), pytest.approx(50))


def test_predict_scope(ex):
    assert ex.predict_scope() == (70, 100), \
        "the assignment inside spend() creates a LOCAL treasury; the global is unchanged"
