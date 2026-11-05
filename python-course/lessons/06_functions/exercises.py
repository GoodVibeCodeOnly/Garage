"""Lesson 06 — Functions. Game-economy formulas.

How to check: double-click check.bat in the course folder and type 06.
Replace each `raise NotImplementedError(...)` with your code. Return values; don't print.
"""


def production(workers, output_per_worker, efficiency=1.0):
    """Exercise 1. Return workers * output_per_worker * efficiency.

    production(100, 2)                 -> 200.0 (or 200)
    production(100, 2, efficiency=0.5) -> 100.0
    """
    raise NotImplementedError("Exercise 1")


def upkeep(units, cost_per_unit=2.0, discount=0.0):
    """Exercise 2. Monthly upkeep = units * cost_per_unit, reduced by `discount`
    (a fraction, e.g. 0.25 means 25% off).

    upkeep(10)                 -> 20.0
    upkeep(10, discount=0.25)  -> 15.0
    upkeep(10, cost_per_unit=3, discount=0.5) -> 15.0
    """
    raise NotImplementedError("Exercise 2")


def tariff_revenue(import_value, rate=0.1, exempt_below=0.0):
    """Exercise 3. Return import_value * rate, EXCEPT return 0.0 when
    import_value is strictly below `exempt_below`.

    tariff_revenue(500)                      -> 50.0
    tariff_revenue(200, rate=0.2, exempt_below=300) -> 0.0
    tariff_revenue(300, rate=0.2, exempt_below=300) -> 60.0
    """
    raise NotImplementedError("Exercise 3")


def net_income(workers, output_per_worker, units, import_value):
    """Exercise 4. Compose your functions above (call them, don't re-type formulas):

    net = production(workers, output_per_worker)        # default efficiency
        + tariff_revenue(import_value)                  # default rate, no exemption
        - upkeep(units)                                 # default cost, no discount

    net_income(100, 2, 10, 500) -> 200 + 50 - 20 = 230.0
    """
    raise NotImplementedError("Exercise 4")


def apply_policy(values, policy):
    """Exercise 5. `policy` is a function taking one number. Return a NEW list
    with policy applied to each value, in order. Don't modify `values`.

    apply_policy([100, 200], lambda v: v * 2) -> [200, 400]
    apply_policy([], abs)                     -> []
    """
    raise NotImplementedError("Exercise 5")


def best_policy(import_value, policies):
    """Exercise 6. `policies` maps a name (str) to a function f(import_value) -> revenue.
    Return the NAME whose function yields the highest revenue for import_value.
    If tied, return whichever comes first in the dict.

    best_policy(1000, {"low": lambda v: v * 0.05, "high": lambda v: v * 0.2}) -> "high"
    """
    raise NotImplementedError("Exercise 6")


def make_flat_tax(rate):
    """Exercise 7. Return a FUNCTION that takes an amount and returns amount * rate.

    tax10 = make_flat_tax(0.1)
    tax10(500) -> 50.0
    make_flat_tax(0.25)(400) -> 100.0
    Hint: define a function inside this one and return it (without calling it).
    """
    raise NotImplementedError("Exercise 7")


def predict_scope():
    """Exercise 8. Predict, don't run. What is the value of `result`?

        treasury = 100
        def spend(amount):
            treasury = 100 - amount
            return treasury
        spent = spend(30)
        result = (spent, treasury)

    Return your answer as a tuple of two ints, e.g. return (0, 0).
    """
    raise NotImplementedError("Exercise 8")
