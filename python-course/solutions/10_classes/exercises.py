"""Lesson 10 — Classes. Model solutions."""
from dataclasses import dataclass, replace


@dataclass
class Nation:
    name: str
    treasury: float
    income: float = 0.0
    expenses: float = 0.0
    debt: float = 0.0
    interest_rate: float = 0.0
    max_debt: float = 1000.0

    def __post_init__(self):
        # The generated __init__ has already assigned the fields; we just check them.
        for field_name in ("income", "expenses", "debt", "max_debt", "interest_rate"):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} must be non-negative")

    def balance(self):
        return self.income - self.expenses - self.debt * self.interest_rate

    def tick(self):
        # Reuse balance() so the monthly formula lives in exactly one place.
        self.treasury += self.balance()
        return self.treasury

    def take_loan(self, amount, rate):
        # Validate everything BEFORE mutating anything, so a failure leaves no
        # half-applied state behind.
        if amount <= 0:
            raise ValueError("loan amount must be positive")
        if self.debt + amount > self.max_debt:
            raise ValueError(f"loan would push debt above {self.max_debt}")
        self.interest_rate = (self.debt * self.interest_rate + amount * rate) / (self.debt + amount)
        self.debt += amount
        self.treasury += amount

    def repay(self, amount):
        if amount <= 0:
            raise ValueError("repayment must be positive")
        if amount > self.debt:
            raise ValueError("cannot repay more than the outstanding debt")
        if amount > self.treasury:
            raise ValueError("not enough money in the treasury")
        self.treasury -= amount
        self.debt -= amount
        if self.debt == 0:
            self.interest_rate = 0.0

    def months_until_broke(self, limit=600):
        if self.treasury < 0:
            return 0
        sim = replace(self)  # a copy with the same field values; ticking it leaves self alone
        for month in range(1, limit + 1):
            sim.tick()
            if sim.treasury < 0:
                return month
        return None
        # Closed-form alternative when balance is constant:
        #   math.floor(treasury / -balance) + 1 for balance < 0.
        # The simulation generalizes if tick() ever gets more complex.


class Market:
    def __init__(self, prices):
        if any(p <= 0 for p in prices.values()):
            raise ValueError("all prices must be positive")
        self.prices = dict(prices)  # copy, so the caller's dict and ours are independent

    def price_of(self, good):
        return self.prices[good]  # KeyError for unknown goods is the right signal

    def __repr__(self):
        return f"Market({len(self.prices)} goods)"

    def sell(self, nation, good, qty):
        if qty <= 0:
            raise ValueError("quantity must be positive")
        revenue = self.price_of(good) * qty
        nation.treasury += revenue  # `nation` is the caller's object, not a copy
        return revenue
