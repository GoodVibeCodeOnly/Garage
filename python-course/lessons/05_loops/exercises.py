# Lesson 05 — Loops
# How to check: double-click check.bat in the course folder and type 05.
# Replace each `raise NotImplementedError(...)` with your code. Write the loops
# yourself even where a one-liner exists; the point is the pattern.


def total_after_months(balance, income, expenses, months):
    """Each month the balance changes by income - expenses, and income grows
    by 1% at the END of each month (after it has been collected). Return the
    balance after `months` months, rounded to 2 decimals.

    total_after_months(500, 100, 50, 0) -> 500
    total_after_months(500, 100, 50, 2) -> 601.0   (500 + 50 + 51)
    """
    raise NotImplementedError("Exercise 1")


def compound_schedule(principal, rate, years):
    """Return a list of the loan balance at the start (year 0) and after each
    year of annual compounding, each rounded to 2 decimals. The list has
    years + 1 entries.

    compound_schedule(1000, 0.1, 3) -> [1000, 1100.0, 1210.0, 1331.0]
    Build it with a loop and .append, not with **.
    """
    raise NotImplementedError("Exercise 2")


def months_until_bankrupt(balance, income, expenses, expense_growth):
    """Simulate month by month. Each month:
        1. balance += income - expenses
        2. expenses *= (1 + expense_growth)
    Return the number of the first month (1, 2, 3, ...) at whose end the
    balance is below 0. If that hasn't happened after 1200 months, return None.

    months_until_bankrupt(100, 50, 80, 0)    -> 4     (70, 40, 10, -20)
    months_until_bankrupt(100, 50, 40, 0)    -> None  (never)
    """
    raise NotImplementedError("Exercise 3")


def longest_win_streak(results):
    """`results` is a string of "W" and "L" characters. Return the length of
    the longest run of consecutive "W"s (0 if there are none).

    longest_win_streak("WWLWWWL") -> 3
    longest_win_streak("")        -> 0
    """
    raise NotImplementedError("Exercise 4")


def first_month_over(balances, threshold):
    """`balances` is a list of month-end balances, the first being month 1.
    Return the month number of the first balance strictly above `threshold`,
    or None if none is. Use enumerate.

    first_month_over([100, 250, 900, 1200], 500) -> 3
    first_month_over([100, 250], 500)            -> None
    """
    raise NotImplementedError("Exercise 5")


def net_by_month(incomes, expenses):
    """Given two equal-length lists, return a list of income - expense for
    each month. Use zip.

    net_by_month([600, 640], [580, 650]) -> [20, -10]
    """
    raise NotImplementedError("Exercise 6")


def taxable_income(incomes, unrest):
    """Provinces with unrest above 5 pay no tax at all. Provinces with unrest
    between 1 and 5 inclusive pay half their income. Provinces with unrest
    below 1 pay full income. Return the total collected.
    Use zip, and `continue` to skip the rebellious provinces.

    taxable_income([100, 200, 300], [0, 3, 8]) -> 200.0   (100 + 100 + 0)
    """
    raise NotImplementedError("Exercise 7")
