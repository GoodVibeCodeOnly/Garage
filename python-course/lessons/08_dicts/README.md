# 08 — Dictionaries

A dict maps **keys** to **values**: good → quantity, good → price, nation → treasury.
Lists answer "what's at position 3?"; dicts answer "what's the value for *grain*?"
That's how most real data is shaped, and it's exactly what a JSON file or a pandas
row looks like.

## Basics

```python
inventory = {"grain": 120, "iron": 40, "cloth": 15}
inventory["iron"]          # 40
inventory["wine"] = 8      # add a new key
inventory["grain"] -= 20   # update in place
"iron" in inventory        # True — checks KEYS, fast
len(inventory)             # 4
del inventory["cloth"]
```

Keys must be immutable (str, int, tuple). Values can be anything, including lists
and other dicts. Since Python 3.7 dicts keep insertion order.

## Missing keys: `[]` vs `.get`

```python
inventory["spices"]            # KeyError
inventory.get("spices")        # None
inventory.get("spices", 0)     # 0  — a default you choose
```

Use `[]` when a missing key is a bug you want to hear about. Use `.get(key, default)`
when missing just means "zero" or "not applicable".

## Iterating

```python
for good in inventory:                 # keys
for qty in inventory.values():         # values
for good, qty in inventory.items():    # both — the one you'll use most
    print(good, qty)
```

`.items()` yields `(key, value)` pairs, and `good, qty` unpacks each pair.

## Portfolio value: two dicts, one key space

```python
prices = {"grain": 2.0, "iron": 9.5, "wine": 14.0}
value = 0
for good, qty in inventory.items():
    value += qty * prices[good]
```

If a good might not have a price, `prices.get(good, 0)` decides what that means —
an explicit modelling choice, not an accident.

## Counting

The single most common dict pattern:

```python
counts = {}
for good in ["grain", "iron", "grain", "wine", "grain"]:
    counts[good] = counts.get(good, 0) + 1
# {"grain": 3, "iron": 1, "wine": 1}
```

`collections.Counter` does this for you (`Counter(goods)`), but write the loop by
hand at least once — the `get(k, 0) + 1` pattern generalizes to summing, not just
counting: `totals[good] = totals.get(good, 0) + qty`.

## Merging trade ledgers

Two ledgers of net flows (positive = bought, negative = sold) need *summing* on
shared keys:

```python
a = {"grain": 50, "iron": -10}
b = {"iron": 25, "wine": 5}
merged = dict(a)                      # copy, don't mutate a
for good, qty in b.items():
    merged[good] = merged.get(good, 0) + qty
# {"grain": 50, "iron": 15, "wine": 5}
```

Compare `a | b` (Python 3.9+), which *overwrites* rather than sums: right side
wins. Know which one you mean.

## Nested dicts and dict of lists

```python
nations = {
    "Venice": {"treasury": 900, "inventory": {"wine": 30, "cloth": 12}},
    "Genoa":  {"treasury": 650, "inventory": {"iron": 20}},
}
nations["Venice"]["inventory"]["wine"]   # 30

price_history = {"grain": [2.0, 2.1, 1.9], "iron": [9.5, 9.8]}
price_history["grain"].append(2.2)       # dict of lists: a time series per key
```

To build a dict of lists from flat records, use `setdefault`:

```python
by_good = {}
for good, price in [("grain", 2.0), ("iron", 9.5), ("grain", 2.1)]:
    by_good.setdefault(good, []).append(price)
```

`setdefault(k, [])` returns the existing list, or inserts and returns a new empty
one. (`collections.defaultdict(list)` is the alternative.)

## Worked example

`example.py` holds three nations' inventories and a market price table. It values
each portfolio, finds each nation's most valuable holding, counts which goods
appear in trade records, merges two ledgers, and groups a price log into a dict of
lists to compute average prices.

## Exercises

In `exercises.py`:

1. `stock_of(inventory, good)` — quantity, or 0 if absent.
2. `portfolio_value(inventory, prices)` — sum of qty × price (unpriced goods worth 0).
3. `most_valuable_good(inventory, prices)` — good with the highest total value.
4. `count_trades(goods)` — counting pattern.
5. `merge_ledgers(a, b)` — sum flows by key without mutating inputs.
6. `richest_nation(nations)` — nested dict lookup.
7. `group_prices(records)` — list of `(good, price)` → dict of lists.
8. `average_prices(price_history)` — dict of lists → dict of means.

## How to check

Double-click `check.bat` in the course folder and type `08`.
