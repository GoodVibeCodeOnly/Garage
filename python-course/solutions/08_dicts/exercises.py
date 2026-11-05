"""Lesson 08 — Dictionaries. Model solutions."""


def stock_of(inventory, good):
    return inventory.get(good, 0)


def portfolio_value(inventory, prices):
    # Alternative one-liner: sum(q * prices.get(g, 0) for g, q in inventory.items())
    total = 0
    for good, qty in inventory.items():
        total += qty * prices.get(good, 0)
    return total


def most_valuable_good(inventory, prices):
    if not inventory:
        return None
    # max() over a dict iterates keys; key= ranks each by its total value.
    return max(inventory, key=lambda g: inventory[g] * prices.get(g, 0))


def count_trades(goods):
    counts = {}
    for good in goods:
        counts[good] = counts.get(good, 0) + 1
    return counts
    # Or: dict(collections.Counter(goods))


def merge_ledgers(a, b):
    merged = dict(a)  # shallow copy so `a` is untouched
    for good, qty in b.items():
        merged[good] = merged.get(good, 0) + qty
    # Build a new dict rather than deleting while iterating (which raises an error).
    return {good: qty for good, qty in merged.items() if qty != 0}


def richest_nation(nations):
    return max(nations, key=lambda name: nations[name]["treasury"])


def group_prices(records):
    history = {}
    for good, price in records:
        # setdefault returns the existing list, or inserts [] and returns that.
        history.setdefault(good, []).append(price)
    return history


def average_prices(price_history):
    averages = {}
    for good, series in price_history.items():
        if series:  # empty list is falsy -> skip, avoids ZeroDivisionError
            averages[good] = sum(series) / len(series)
    return averages
