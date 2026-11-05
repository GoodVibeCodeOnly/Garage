# Lesson 02 — Numbers and Variables
# How to check: double-click check.bat in the course folder and type 02.
# Replace each `raise NotImplementedError(...)` with your code. No loops needed.
import math


def monthly_net(taxes, trade, upkeep, interest):
    """Return monthly net income: (taxes + trade) - (upkeep + interest).

    monthly_net(600, 150, 360, 40) -> 350
    """
    raise NotImplementedError("Exercise 1")


def regiments_affordable(gold, cost):
    """Return a tuple (regiments, leftover): how many whole regiments of the
    given cost `gold` can buy, and the gold left after buying them. Both ints.

    regiments_affordable(1000, 85) -> (11, 65)
    Hint: // and %, or divmod.
    """
    raise NotImplementedError("Exercise 2")


def loan_balance(principal, annual_rate, years):
    """Return what is owed on a loan after `years` of annual compounding,
    with no repayments, rounded to 2 decimal places.

    annual_rate is a fraction: 0.05 means 5%.
    loan_balance(1000, 0.04, 10) -> 1480.24
    """
    raise NotImplementedError("Exercise 3")


def real_value(nominal, inflation, years):
    """Return the value in today's money of `nominal` received `years` from now,
    given constant annual `inflation` (a fraction). Do not round.

    real_value(1000, 0.03, 4) -> about 888.49
    """
    raise NotImplementedError("Exercise 4")


def monthly_rate(annual_rate):
    """Return the monthly rate that, compounded 12 times, equals annual_rate.
    Do not round. (Not annual_rate / 12.)

    monthly_rate(0.12) -> about 0.009489
    """
    raise NotImplementedError("Exercise 5")


def years_to_double(rate):
    """Return the number of WHOLE years until something growing at `rate` per
    year at least doubles, as an int. Use logarithms (math.log), then round UP.

    years_to_double(0.05) -> 15   (exact value is ~14.21)
    years_to_double(1.0)  -> 1    (exactly doubles in one year)
    """
    raise NotImplementedError("Exercise 6")


def loans_needed(deficit, loan_size):
    """Return how many loans of `loan_size` are needed to cover `deficit`
    (an int >= 0). A partial loan counts as a whole loan.

    loans_needed(700, 250) -> 3
    loans_needed(750, 250) -> 3
    loans_needed(0, 250)   -> 0
    """
    raise NotImplementedError("Exercise 7")


def nearly_equal(a, b):
    """Return True if floats a and b are equal up to floating-point noise,
    otherwise False. Use math.isclose with its default tolerance.

    nearly_equal(0.1 + 0.2, 0.3) -> True
    nearly_equal(0.3, 0.31)      -> False
    """
    raise NotImplementedError("Exercise 8")
