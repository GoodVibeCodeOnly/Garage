"""Lesson 08 — Dictionaries. Inventories, prices, ledgers.

How to check: double-click check.bat in the course folder and type 08.
Replace each `raise NotImplementedError(...)` with your code.
"""


def stock_of(inventory, good):
    """Exercise 1. Return how many of `good` are in `inventory` (dict good -> qty),
    or 0 if the good isn't there.

    stock_of({"grain": 10}, "grain") -> 10
    stock_of({"grain": 10}, "iron")  -> 0
    """
    raise NotImplementedError("Exercise 1")


def portfolio_value(inventory, prices):
    """Exercise 2. Return the total market value: sum of qty * price for each good.
    Goods with no entry in `prices` are worth 0.

    portfolio_value({"grain": 10, "iron": 2}, {"grain": 2.0, "iron": 9.5}) -> 39.0
    portfolio_value({"silk": 5}, {"grain": 2.0}) -> 0
    """
    raise NotImplementedError("Exercise 2")


def most_valuable_good(inventory, prices):
    """Exercise 3. Return the good whose qty * price is largest (unpriced = 0).
    Return None for an empty inventory. On ties, return the first in the inventory.

    most_valuable_good({"grain": 100, "iron": 10}, {"grain": 2.0, "iron": 9.5}) -> "grain"
    """
    raise NotImplementedError("Exercise 3")


def count_trades(goods):
    """Exercise 4. `goods` is a list of good names, one per trade.
    Return a dict good -> number of times it appears.

    count_trades(["grain", "iron", "grain"]) -> {"grain": 2, "iron": 1}
    """
    raise NotImplementedError("Exercise 4")


def merge_ledgers(a, b):
    """Exercise 5. Each ledger maps good -> net quantity (may be negative).
    Return a NEW dict with quantities SUMMED across both. Don't modify a or b.
    Drop goods whose summed quantity is exactly 0.

    merge_ledgers({"grain": 50, "iron": -10}, {"iron": 25, "wine": 5})
        -> {"grain": 50, "iron": 15, "wine": 5}
    merge_ledgers({"wine": 3}, {"wine": -3}) -> {}
    """
    raise NotImplementedError("Exercise 5")


def richest_nation(nations):
    """Exercise 6. `nations` maps name -> {"treasury": number, ...other keys}.
    Return the name with the largest treasury.

    richest_nation({"Venice": {"treasury": 900}, "Genoa": {"treasury": 650}}) -> "Venice"
    """
    raise NotImplementedError("Exercise 6")


def group_prices(records):
    """Exercise 7. `records` is a list of (good, price) tuples in time order.
    Return a dict good -> list of prices in the order they appeared.

    group_prices([("grain", 2.0), ("iron", 9.5), ("grain", 2.1)])
        -> {"grain": [2.0, 2.1], "iron": [9.5]}
    """
    raise NotImplementedError("Exercise 7")


def average_prices(price_history):
    """Exercise 8. `price_history` maps good -> list of prices.
    Return a dict good -> mean price. Skip goods whose list is empty.

    average_prices({"grain": [2.0, 2.2], "iron": [9.0], "silk": []})
        -> {"grain": 2.1, "iron": 9.0}
    """
    raise NotImplementedError("Exercise 8")
