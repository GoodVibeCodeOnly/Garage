"""Worked example: inventories, market prices, ledgers.

Run:  python example.py
"""

prices = {"grain": 2.0, "iron": 9.5, "cloth": 6.0, "wine": 14.0, "spices": 40.0}

nations = {
    "Venice": {"treasury": 900, "inventory": {"wine": 30, "cloth": 12, "spices": 4}},
    "Genoa": {"treasury": 650, "inventory": {"iron": 20, "grain": 150}},
    "Milan": {"treasury": 400, "inventory": {"iron": 45, "cloth": 30, "silk": 5}},
}


def portfolio_value(inventory, prices):
    total = 0.0
    for good, qty in inventory.items():
        total += qty * prices.get(good, 0)  # silk has no market price -> worth 0
    return total


print("Portfolio values")
for name, info in nations.items():
    inv = info["inventory"]
    value = portfolio_value(inv, prices)
    best = max(inv, key=lambda g: inv[g] * prices.get(g, 0))
    print(f"  {name:<7} treasury={info['treasury']:>4}  goods={value:>7.1f}  "
          f"net worth={info['treasury'] + value:>7.1f}  top holding={best}")

# Counting: which goods change hands most often?
trades = ["grain", "iron", "grain", "wine", "grain", "iron", "spices"]
counts = {}
for good in trades:
    counts[good] = counts.get(good, 0) + 1
print("\nTrade counts:", counts)

# Merging two ledgers: SUM on shared keys
ledger_q1 = {"grain": 50, "iron": -10, "wine": 3}
ledger_q2 = {"iron": 25, "wine": -3, "cloth": 8}
merged = dict(ledger_q1)
for good, qty in ledger_q2.items():
    merged[good] = merged.get(good, 0) + qty
print("Merged ledger (summed):  ", merged)
print("ledger_q1 | ledger_q2 (overwrite, NOT a sum):", ledger_q1 | ledger_q2)

# Dict of lists: group a flat price log by good
price_log = [("grain", 2.0), ("iron", 9.5), ("grain", 2.2), ("iron", 9.9), ("grain", 1.9)]
history = {}
for good, price in price_log:
    history.setdefault(good, []).append(price)
print("\nPrice history:", history)
for good, series in history.items():
    print(f"  {good:<6} avg={sum(series) / len(series):.2f}  over {len(series)} observations")
