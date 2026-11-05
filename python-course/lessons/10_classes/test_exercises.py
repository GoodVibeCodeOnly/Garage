import pytest


def make(ex, **kw):
    base = dict(name="Venice", treasury=500.0, income=60.0, expenses=50.0)
    base.update(kw)
    return ex.Nation(**base)


def test_post_init_accepts_valid(ex):
    n = make(ex, treasury=-100)
    assert n.treasury == -100, "a negative starting treasury is allowed"


@pytest.mark.parametrize("field", ["income", "expenses", "debt", "max_debt", "interest_rate"])
def test_post_init_rejects_negative(ex, field):
    with pytest.raises(ValueError):
        make(ex, **{field: -1})


def test_balance(ex):
    n = ex.Nation("A", 0, income=100, expenses=60, debt=500, interest_rate=0.02)
    assert n.balance() == pytest.approx(30.0)
    assert n.treasury == 0, "balance() must not modify the treasury"


def test_tick(ex):
    n = make(ex)
    assert n.tick() == pytest.approx(510.0)
    n.tick()
    assert n.treasury == pytest.approx(520.0)


def test_tick_with_interest(ex):
    n = make(ex, debt=1000, interest_rate=0.01)
    n.tick()
    assert n.treasury == pytest.approx(500.0)


def test_take_loan(ex):
    n = make(ex)
    n.take_loan(400, 0.02)
    assert (n.treasury, n.debt) == (pytest.approx(900), pytest.approx(400))
    assert n.interest_rate == pytest.approx(0.02)


def test_take_loan_blends_rate(ex):
    n = make(ex)
    n.take_loan(200, 0.01)
    n.take_loan(200, 0.03)
    assert n.interest_rate == pytest.approx(0.02)
    assert n.debt == pytest.approx(400)


def test_take_loan_cap(ex):
    n = make(ex, max_debt=500)
    n.take_loan(500, 0.02)  # exactly at the cap is fine
    with pytest.raises(ValueError):
        n.take_loan(1, 0.02)
    assert n.debt == pytest.approx(500) and n.treasury == pytest.approx(1000), \
        "a rejected loan must change nothing"


def test_take_loan_nonpositive(ex):
    n = make(ex)
    with pytest.raises(ValueError):
        n.take_loan(0, 0.02)
    with pytest.raises(ValueError):
        n.take_loan(-50, 0.02)
    assert n.debt == 0


def test_repay(ex):
    n = make(ex)
    n.take_loan(300, 0.02)
    n.repay(100)
    assert (n.treasury, n.debt) == (pytest.approx(700), pytest.approx(200))
    assert n.interest_rate == pytest.approx(0.02)


def test_repay_full_resets_rate(ex):
    n = make(ex)
    n.take_loan(300, 0.02)
    n.repay(300)
    assert n.debt == 0
    assert n.interest_rate == 0.0, "interest_rate resets when debt is cleared"


def test_repay_invalid(ex):
    n = make(ex, treasury=50, debt=200, interest_rate=0.01)
    for bad in (0, -5, 300, 100):  # 300 > debt, 100 > treasury
        with pytest.raises(ValueError):
            n.repay(bad)
    assert (n.treasury, n.debt) == (50, 200)


def test_months_until_broke(ex):
    n = ex.Nation("Genoa", 100, income=50, expenses=80)  # -30/month
    assert n.months_until_broke() == 4  # 70, 40, 10, -20
    assert n.treasury == 100, "must not modify the original nation"


def test_months_until_broke_never_and_already(ex):
    assert make(ex).months_until_broke() is None
    assert make(ex, treasury=-1, income=100).months_until_broke() == 0


def test_months_until_broke_zero_is_not_broke(ex):
    n = ex.Nation("A", 60, income=0, expenses=30)  # 30, 0, -30
    assert n.months_until_broke() == 3, "0 is not broke; strictly below 0"


def test_market_init_copy(ex):
    prices = {"wine": 14.0, "iron": 9.5}
    m = ex.Market(prices)
    prices["wine"] = 999
    assert m.price_of("wine") == pytest.approx(14.0), "store a copy of prices"
    assert m.price_of("iron") == pytest.approx(9.5)


def test_market_invalid_and_unknown(ex):
    with pytest.raises(ValueError):
        ex.Market({"wine": 0})
    m = ex.Market({"wine": 1.0})
    with pytest.raises(KeyError):
        m.price_of("silk")


def test_market_repr(ex):
    assert repr(ex.Market({"wine": 14.0, "iron": 9.5})) == "Market(2 goods)"


def test_market_sell(ex):
    m = ex.Market({"wine": 14.0})
    n = make(ex)
    assert m.sell(n, "wine", 3) == pytest.approx(42.0)
    assert n.treasury == pytest.approx(542.0), "sell must change the nation passed in"
    with pytest.raises(ValueError):
        m.sell(n, "wine", 0)
    assert n.treasury == pytest.approx(542.0)


def test_nation_repr_from_dataclass(ex):
    assert "Venice" in repr(make(ex))
