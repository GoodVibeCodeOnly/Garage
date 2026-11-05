"""Worked example: a Paradox-style treasury simulation with classes.

Run:  python example.py   (also writes output/treasury.png)
"""
import pathlib
import random
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


@dataclass
class Nation:
    name: str
    treasury: float
    income: float
    expenses: float
    debt: float = 0.0
    interest_rate: float = 0.0   # monthly rate on outstanding debt
    max_debt: float = 1000.0

    def __post_init__(self):
        if self.income < 0 or self.expenses < 0:
            raise ValueError("income and expenses must be non-negative")

    def balance(self):
        """Monthly surplus (positive) or deficit (negative), after interest."""
        return self.income - self.expenses - self.debt * self.interest_rate

    def tick(self):
        """Advance one month."""
        self.treasury += self.balance()

    def take_loan(self, amount, rate):
        if amount <= 0:
            raise ValueError("loan amount must be positive")
        if self.debt + amount > self.max_debt:
            raise ValueError(f"{self.name}: loan would exceed debt cap {self.max_debt}")
        # New debt changes the blended interest rate (weighted average).
        self.interest_rate = (self.debt * self.interest_rate + amount * rate) / (self.debt + amount)
        self.debt += amount
        self.treasury += amount


class Market:
    def __init__(self, prices, seed=0):
        self.prices = dict(prices)          # copy: the market owns its prices
        self._rng = random.Random(seed)

    def __repr__(self):
        return f"Market({self.prices})"

    def drift(self):
        """Random-walk every price by up to +/-5%."""
        for good in self.prices:
            self.prices[good] *= 1 + self._rng.uniform(-0.05, 0.05)

    def sell(self, nation, good, qty):
        revenue = self.prices[good] * qty
        nation.treasury += revenue          # mutates the actual Nation passed in
        return revenue


frugal = Nation("Venice", treasury=500, income=60, expenses=50)
indebted = Nation("Genoa", treasury=200, income=55, expenses=70)
indebted.take_loan(600, rate=0.02)
print(frugal)
print(indebted)

market = Market({"wine": 14.0, "iron": 9.5})
history = {frugal.name: [], indebted.name: []}
for month in range(24):
    market.drift()
    market.sell(frugal, "wine", 2)          # Venice exports a little wine each month
    for n in (frugal, indebted):
        n.tick()
        history[n.name].append(n.treasury)

print("\nAfter 24 months:")
for n in (frugal, indebted):
    print(f"  {n.name:<7} treasury={n.treasury:8.1f}  monthly balance={n.balance():6.1f}")
print(" ", market)

print("\nTrying to borrow past the cap:")
try:
    indebted.take_loan(500, rate=0.03)
except ValueError as err:
    print("  ValueError:", err)

out = pathlib.Path("output")
out.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(8, 4))
for name, series in history.items():
    ax.plot(range(1, 25), series, label=name)
ax.axhline(0, color="grey", linewidth=1)
ax.set_xlabel("month")
ax.set_ylabel("treasury (ducats)")
ax.legend()
fig.tight_layout()
fig.savefig(out / "treasury.png", dpi=100)
print("\nSaved", out / "treasury.png")
