# Lesson 05 — Loops (solutions)


def total_after_months(balance, income, expenses, months):
    for _ in range(months):          # `_` = "I don't need the loop counter"
        balance += income - expenses
        income *= 1.01               # growth applied after collection
    return round(balance, 2)


def compound_schedule(principal, rate, years):
    schedule = [principal]           # year 0
    balance = principal
    for _ in range(years):
        balance *= 1 + rate
        # Round only what we store; keep full precision in `balance` so
        # rounding errors don't compound year after year.
        schedule.append(round(balance, 2))
    return schedule


def months_until_bankrupt(balance, income, expenses, expense_growth):
    month = 0
    while month < 1200:              # the cap guarantees the loop ends
        month += 1
        balance += income - expenses
        expenses *= 1 + expense_growth
        if balance < 0:
            return month             # return inside a loop = break + answer
    return None
    # Equivalent with for: `for month in range(1, 1201): ...` -- when the
    # number of iterations has a known upper bound, for is often simpler.


def longest_win_streak(results):
    current = best = 0
    for r in results:
        if r == "W":
            current += 1
            best = max(best, current)
        else:
            current = 0              # a loss resets the running count
    return best
    # One-liner once you know split and generators:
    #   max((len(run) for run in results.split("L")), default=0)


def first_month_over(balances, threshold):
    for month, bal in enumerate(balances, start=1):
        if bal > threshold:
            return month
    return None


def net_by_month(incomes, expenses):
    nets = []
    for inc, exp in zip(incomes, expenses):
        nets.append(inc - exp)
    return nets
    # List comprehension (later lesson): [i - e for i, e in zip(incomes, expenses)]


def taxable_income(incomes, unrest):
    total = 0.0
    for income, u in zip(incomes, unrest):
        if u > 5:
            continue                 # rebels pay nothing: skip the rest
        if u >= 1:
            total += income / 2
        else:
            total += income
    return total
