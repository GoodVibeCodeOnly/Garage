# 10 — Classes

Up to now, a nation has been a dict: `{"treasury": 900, "income": 50, ...}` plus a
pile of loose functions that take that dict and change it. That works, until five
functions each need to remember that the treasury can't go below a debt limit, or
someone writes `nation["tresury"] = 0` and nothing complains.

A class bundles **data** (attributes) with the **operations** that are allowed on it
(methods) and lets you enforce rules in one place. That's the whole pitch. No
inheritance hierarchies needed here.

## A minimal class

```python
class Nation:
    def __init__(self, name, treasury):
        self.name = name
        self.treasury = treasury

    def collect(self, amount):
        self.treasury += amount

venice = Nation("Venice", 900)     # calls __init__
venice.collect(50)                 # same as Nation.collect(venice, 50)
venice.treasury                    # 950
```

- `__init__` runs when you create an instance; it sets up the attributes.
- `self` is the particular instance — `venice` here. Python passes it automatically.
- Each instance has its own attributes: `Nation("Genoa", 650)` is separate.

## `__repr__`: make it printable

Without it, `print(venice)` shows `<__main__.Nation object at 0x7f...>`. Useless
when debugging.

```python
    def __repr__(self):
        return f"Nation(name={self.name!r}, treasury={self.treasury})"
```

`!r` uses the repr of the value, so strings get quotes. Convention: make `__repr__`
look like the code that would recreate the object.

## Invariants: raise `ValueError`

An invariant is a rule that must always hold. Enforce it at the door:

```python
    def spend(self, amount):
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self.treasury -= amount
```

`raise` stops the method immediately; nothing is changed. The caller can catch it
with `try/except ValueError`. Validating in methods is the main reason to prefer a
class over a dict: there's exactly one way in, and it checks.

## Dataclasses: skip the boilerplate

For classes that are mostly data, `@dataclass` writes `__init__`, `__repr__` and
`__eq__` for you from type-annotated fields:

```python
from dataclasses import dataclass, field

@dataclass
class Nation:
    name: str
    treasury: float
    income: float = 0.0
    expenses: float = 0.0
    loans: list = field(default_factory=list)   # mutable default: use a factory

    def __post_init__(self):                    # runs after the generated __init__
        if self.income < 0:
            raise ValueError("income must be >= 0")

    def balance(self):
        return self.income - self.expenses
```

`Nation("Venice", 900, income=60)` now just works, and `print` shows every field.
`field(default_factory=list)` is the dataclass version of Lesson 06's
"never use a mutable default" — each nation gets its own list.
The type hints (`str`, `float`) are documentation; Python doesn't enforce them.

## Methods that change state vs methods that report

Keep them distinct. `balance()` computes and returns; `tick()` advances a month and
changes `treasury`. A good habit: state-changing methods return `None` (or something
small and useful), reporting methods never change anything.

## Objects that hold objects

A `Market` can hold a dict of prices and operate on `Nation` instances:

```python
class Market:
    def __init__(self, prices):
        self.prices = dict(prices)

    def sell(self, nation, good, qty):
        nation.treasury += self.prices[good] * qty
```

Objects passed into methods are the *same* objects (not copies), so `sell` really
changes that nation's treasury.

## Worked example

`example.py` defines a `Nation` dataclass with `tick()` (monthly income minus
expenses minus loan interest) and `take_loan()`, plus a `Market` that drifts prices
and buys goods. It simulates two years for a frugal and an indebted nation, shows
the invariant firing when a loan would break the debt cap, and saves a treasury
chart to `output/treasury.png`.

## Exercises

In `exercises.py` you'll fill in the methods of two classes:

1. `Nation.__post_init__` — validate starting values.
2. `Nation.balance()` — monthly surplus/deficit.
3. `Nation.tick()` — advance one month (income, expenses, interest).
4. `Nation.take_loan(amount, rate)` — with a debt cap invariant.
5. `Nation.repay(amount)` — reduce debt, can't overpay or overspend.
6. `Nation.months_until_broke()` — simulate on a copy until treasury < 0.
7. `Market.__init__`, `Market.price_of`, `Market.__repr__`.
8. `Market.sell(nation, good, qty)` — move money into a nation's treasury.

## How to check

Double-click `check.bat` in the course folder and type `10`.
