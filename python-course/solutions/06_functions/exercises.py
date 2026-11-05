"""Lesson 06 — Functions. Model solutions."""


def production(workers, output_per_worker, efficiency=1.0):
    return workers * output_per_worker * efficiency


def upkeep(units, cost_per_unit=2.0, discount=0.0):
    # (1 - discount) applies the percentage off in one multiplication.
    return units * cost_per_unit * (1 - discount)


def tariff_revenue(import_value, rate=0.1, exempt_below=0.0):
    # Guard clause first: handle the special case and return early,
    # so the main formula reads cleanly at the bottom.
    if import_value < exempt_below:
        return 0.0
    return import_value * rate


def net_income(workers, output_per_worker, units, import_value):
    # Composition: each rule lives in exactly one place. Change the
    # tariff formula and net_income follows automatically.
    return (
        production(workers, output_per_worker)
        + tariff_revenue(import_value)
        - upkeep(units)
    )


def apply_policy(values, policy):
    # A list comprehension builds a new list; the input is untouched.
    # Equivalent: list(map(policy, values))
    return [policy(v) for v in values]


def best_policy(import_value, policies):
    # max() over the dict iterates its keys; key= says "rank each name by
    # the revenue its function produces". max keeps the first on ties.
    return max(policies, key=lambda name: policies[name](import_value))


def make_flat_tax(rate):
    # The inner function "remembers" `rate` from the enclosing call — a closure.
    def tax(amount):
        return amount * rate

    return tax  # no parentheses: return the function, don't call it
    # One-liner alternative: return lambda amount: amount * rate


def predict_scope():
    # Assigning to `treasury` inside spend() makes it local to spend().
    # spend(30) returns 70; the global treasury is still 100.
    return (70, 100)
