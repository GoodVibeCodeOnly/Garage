import pytest

PRICES = {"grain": 2.0, "iron": 9.5, "cloth": 6.0, "wine": 14.0}


def test_stock_of(ex):
    assert ex.stock_of({"grain": 10}, "grain") == 10
    assert ex.stock_of({"grain": 10}, "iron") == 0
    assert ex.stock_of({}, "iron") == 0


def test_portfolio_value(ex):
    assert ex.portfolio_value({"grain": 10, "iron": 2}, PRICES) == pytest.approx(39.0)
    assert ex.portfolio_value({}, PRICES) == 0


def test_portfolio_value_unpriced(ex):
    assert ex.portfolio_value({"silk": 5, "wine": 1}, PRICES) == pytest.approx(14.0), \
        "goods missing from prices are worth 0 (use .get)"


def test_most_valuable_good(ex):
    assert ex.most_valuable_good({"grain": 100, "iron": 10}, PRICES) == "grain"
    assert ex.most_valuable_good({"grain": 10, "iron": 10}, PRICES) == "iron"


def test_most_valuable_good_edges(ex):
    assert ex.most_valuable_good({}, PRICES) is None
    assert ex.most_valuable_good({"silk": 99, "grain": 1}, PRICES) == "grain"


def test_count_trades(ex):
    assert ex.count_trades(["grain", "iron", "grain"]) == {"grain": 2, "iron": 1}
    assert ex.count_trades([]) == {}


def test_merge_ledgers(ex):
    a = {"grain": 50, "iron": -10}
    b = {"iron": 25, "wine": 5}
    assert ex.merge_ledgers(a, b) == {"grain": 50, "iron": 15, "wine": 5}
    assert a == {"grain": 50, "iron": -10} and b == {"iron": 25, "wine": 5}, \
        "don't modify the input ledgers"


def test_merge_ledgers_drops_zero(ex):
    assert ex.merge_ledgers({"wine": 3}, {"wine": -3}) == {}
    assert ex.merge_ledgers({}, {}) == {}


def test_richest_nation(ex):
    nations = {
        "Venice": {"treasury": 900, "inventory": {}},
        "Genoa": {"treasury": 650},
        "Milan": {"treasury": 1200},
    }
    assert ex.richest_nation(nations) == "Milan"


def test_group_prices(ex):
    recs = [("grain", 2.0), ("iron", 9.5), ("grain", 2.1)]
    assert ex.group_prices(recs) == {"grain": [2.0, 2.1], "iron": [9.5]}
    assert ex.group_prices([]) == {}


def test_average_prices(ex):
    out = ex.average_prices({"grain": [2.0, 2.2], "iron": [9.0], "silk": []})
    assert set(out) == {"grain", "iron"}, "skip empty lists"
    assert out["grain"] == pytest.approx(2.1)
    assert out["iron"] == pytest.approx(9.0)
