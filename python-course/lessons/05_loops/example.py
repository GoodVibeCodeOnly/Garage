"""Ten-year treasury simulation: loops, accumulators, break, and a plot."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

balance = 1000.0
income, expenses = 600.0, 520.0
debt, DEBT_CAP, LOAN = 0.0, 3000.0, 500.0
INTEREST = 0.005                     # monthly interest on outstanding debt
history = []                         # accumulator: balance each month
month = 0

while month < 120:                   # cap: never simulate more than 10 years
    month += 1
    balance += income - expenses - debt * INTEREST
    income *= 1.01
    expenses *= 1.02
    while balance < 0 and debt < DEBT_CAP:   # take loans until solvent or capped
        debt += LOAN
        balance += LOAN
    history.append(balance)
    if balance < 0:
        print(f"Bankrupt in month {month} (year {(month - 1) // 12 + 1}), debt {debt:,.0f}")
        break
else:
    # A while/for `else` runs only if the loop ended WITHOUT break.
    print("Survived ten years")

for year_end in range(12, len(history) + 1, 12):
    print(f"  end of year {year_end // 12}: balance {history[year_end - 1]:>9,.0f}")

out = Path("output")
out.mkdir(exist_ok=True)
plt.plot(range(1, len(history) + 1), history)
plt.axhline(0, color="grey", linewidth=0.8)
plt.xlabel("month")
plt.ylabel("balance (ducats)")
plt.title("Treasury until bankruptcy")
plt.savefig(out / "treasury.png", dpi=100)
print("Saved output/treasury.png")

# Win streaks: a running counter that resets on a loss
results = "WWLWWWWLLWWWL"
current = best = 0
for r in results:
    if r == "W":
        current += 1
        best = max(best, current)
    else:
        current = 0
wins = results.count("W")
print(f"\n{results}: {wins}/{len(results)} wins ({wins / len(results):.0%}), longest streak {best}")

# enumerate + zip: label each month's net
incomes = [600, 640, 590, 610]
costs = [580, 650, 560, 640]
for m, (inc, cost) in enumerate(zip(incomes, costs), start=1):
    print(f"month {m}: {inc - cost:+d}")
