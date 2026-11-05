"""Lesson 10 — Classes. A Nation and a Market.

How to check: double-click check.bat in the course folder and type 10.
Replace each `raise NotImplementedError(...)` with your code. Don't rename the
classes, fields or methods — the tests use them.
"""
from dataclasses import dataclass


@dataclass
class Nation:
    name: str
    treasury: float
    income: float = 0.0
    expenses: float = 0.0
    debt: float = 0.0
    interest_rate: float = 0.0  # monthly rate charged on `debt`, e.g. 0.02 = 2%/month
    max_debt: float = 1000.0

    def __post_init__(self):
        """Exercise 1. Validate the starting values. Raise ValueError if
        income, expenses, debt or max_debt is negative, or interest_rate is negative.
        (treasury MAY be negative — nations can start broke.)
        If everything is fine, do nothing.
        """
        raise NotImplementedError("Exercise 1")

    def balance(self):
        """Exercise 2. Return this month's net change WITHOUT modifying anything:
        income - expenses - debt * interest_rate

        Nation("A", 0, income=100, expenses=60, debt=500, interest_rate=0.02).balance() -> 30.0
        """
        raise NotImplementedError("Exercise 2")

    def tick(self):
        """Exercise 3. Advance one month: add balance() to treasury.
        Return the new treasury.
        """
        raise NotImplementedError("Exercise 3")

    def take_loan(self, amount, rate):
        """Exercise 4. Borrow `amount` at monthly `rate`.

        - Raise ValueError if amount <= 0.
        - Raise ValueError if debt + amount would exceed max_debt (equal is allowed).
          In both error cases, change NOTHING.
        - Otherwise: set interest_rate to the debt-weighted average of the old rate and
          the new one:  (debt * interest_rate + amount * rate) / (debt + amount)
          then add amount to both debt and treasury.
        """
        raise NotImplementedError("Exercise 4")

    def repay(self, amount):
        """Exercise 5. Pay back `amount` of debt from the treasury.

        - Raise ValueError if amount <= 0, if amount > debt, or if amount > treasury.
          Change nothing in those cases.
        - Otherwise subtract amount from both treasury and debt.
        - If debt reaches 0, also reset interest_rate to 0.0.
        """
        raise NotImplementedError("Exercise 5")

    def months_until_broke(self, limit=600):
        """Exercise 6. How many ticks until treasury goes strictly below 0?
        Return that number of months (an int >= 1), or None if it doesn't happen
        within `limit` months. If the treasury is ALREADY negative, return 0.

        Must NOT change this nation. Hint: dataclasses.replace(self) makes a copy
        you can tick freely.
        """
        raise NotImplementedError("Exercise 6")


class Market:
    def __init__(self, prices):
        """Exercise 7a. Store a COPY of the `prices` dict (good -> price) as
        self.prices, so later changes to the caller's dict don't affect the market.
        Raise ValueError if any price is <= 0.
        """
        raise NotImplementedError("Exercise 7a")

    def price_of(self, good):
        """Exercise 7b. Return the price of `good`. Raise KeyError if unknown
        (plain dict indexing already does that)."""
        raise NotImplementedError("Exercise 7b")

    def __repr__(self):
        """Exercise 7c. Return the string  Market(<n> goods)  e.g. 'Market(2 goods)'."""
        raise NotImplementedError("Exercise 7c")

    def sell(self, nation, good, qty):
        """Exercise 8. `nation` sells qty units of good to the market.
        Raise ValueError if qty <= 0. Otherwise add price * qty to nation.treasury
        and return the revenue.
        """
        raise NotImplementedError("Exercise 8")
