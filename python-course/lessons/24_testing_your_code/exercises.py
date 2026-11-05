# Lesson 24 — Testing your code.
# How to check: double-click check.bat in the course folder and type 24.
# Your own tests go in my_tests.py (run: python -m pytest my_tests.py from this folder).
#
# Exercises 1-3: implement functions (try writing tests in my_tests.py FIRST).
# Exercises 4-5: break someone else's buggy code.
# Exercises 6-7: write test suites as functions; the grader runs them against a
#                correct implementation (must pass) and broken ones (must fail).
import statistics

import pytest


def clamp(x, lo, hi):
    """Exercise 1. Return x limited to the range [lo, hi].
    clamp(5, 0, 10) == 5; clamp(-3, 0, 10) == 0; clamp(99, 0, 10) == 10.
    Raise ValueError if lo > hi.
    """
    raise NotImplementedError("Exercise 1")


def win_rate(wins, games):
    """Exercise 2. Return wins / games as a float.
    Raise ValueError if games <= 0, wins < 0, or wins > games.
    """
    raise NotImplementedError("Exercise 2")


def parse_percent(text):
    """Exercise 3. Parse a percentage string into a fraction.
    "12.5%" -> 0.125, " 40 % " -> 0.4, "-3%" -> -0.03, "7" -> 0.07 (the % sign
    is optional). Surrounding whitespace and space before % are allowed.
    Raise ValueError for anything else: "", "%", "abc%", "12%%".
    """
    raise NotImplementedError("Exercise 3")


# --- Someone else's buggy code. Don't fix these; break them. ----------------

def buggy_median(values):
    """Supposed to return the median of a non-empty list of numbers."""
    s = sorted(values)
    return s[len(s) // 2]


def buggy_tax(income):
    """Supposed to be: 0% on income up to and including 10_000, then 20% on
    every unit ABOVE 10_000, and 40% on every unit above 50_000.
    E.g. income 60_000 -> 0.2 * 40_000 + 0.4 * 10_000 = 12_000."""
    if income < 10_000:
        return 0.0
    if income < 50_000:
        return 0.2 * (income - 10_000)
    return 0.2 * 40_000 + 0.4 * (income - 49_000)


def find_median_bug_cases():
    """Exercise 4. Return a list of AT LEAST 2 different input lists (non-empty
    lists of numbers) for which buggy_median gives a different answer from
    statistics.median. Think: what kind of input does the author not handle?
    """
    raise NotImplementedError("Exercise 4")


def find_tax_bug_incomes():
    """Exercise 5. Return a list of incomes (numbers >= 0) where buggy_tax is
    WRONG according to its docstring. Include at least one income at or below
    60_000. (Hint: test the boundaries, then something past them.)
    """
    raise NotImplementedError("Exercise 5")


# --- Write test suites as functions ----------------------------------------

def check_clamp(clamp_fn):
    """Exercise 6. Write assert statements that test `clamp_fn` against the
    clamp spec in Exercise 1 (you may use pytest.raises). Return nothing.

    The grader calls check_clamp(correct_clamp) — it must NOT raise — and
    check_clamp(broken_clamp) for several subtly broken versions — each must
    raise (an AssertionError, or whatever the broken code throws).
    Cover: inside, below, above, the exact boundaries, and lo > hi.
    """
    raise NotImplementedError("Exercise 6")


def check_win_rate(win_rate_fn):
    """Exercise 7. Same idea for the win_rate spec in Exercise 2.
    Cover normal cases, the return type (float, not int — check it for 0 wins and
    for all wins too), and every error case.
    """
    raise NotImplementedError("Exercise 7")
