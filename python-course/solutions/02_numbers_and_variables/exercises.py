# Lesson 02 — Numbers and Variables (solutions)
import math


def monthly_net(taxes, trade, upkeep, interest):
    # Parentheses make the income/expense grouping explicit, even though
    # taxes + trade - upkeep - interest is the same thing.
    return (taxes + trade) - (upkeep + interest)


def regiments_affordable(gold, cost):
    # divmod returns (gold // cost, gold % cost) in one step.
    return divmod(gold, cost)


def loan_balance(principal, annual_rate, years):
    return round(principal * (1 + annual_rate) ** years, 2)


def real_value(nominal, inflation, years):
    # Deflating is compounding in reverse: divide by the growth factor.
    return nominal / (1 + inflation) ** years


def monthly_rate(annual_rate):
    # (1 + m) ** 12 == 1 + annual  =>  m = (1 + annual) ** (1/12) - 1
    return (1 + annual_rate) ** (1 / 12) - 1


def years_to_double(rate):
    # Solve (1 + rate) ** n == 2 for n. math.ceil turns 14.21 into 15.
    # Rounding guards against float noise turning an exact 1.0 into 1.0000000002.
    return math.ceil(round(math.log(2) / math.log(1 + rate), 9))


def loans_needed(deficit, loan_size):
    # Integer-only ceiling division: -(-a // b). Avoids floats entirely.
    # math.ceil(deficit / loan_size) also works for reasonable sizes.
    return -(-deficit // loan_size)


def nearly_equal(a, b):
    return math.isclose(a, b)
