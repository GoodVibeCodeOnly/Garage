# Lesson 04 — Conditionals
# How to check: double-click check.bat in the course folder and type 04.
# Replace each `raise NotImplementedError(...)` with your code.


def is_bankrupt(balance, monthly_net):
    """A country is bankrupt if its balance is negative AND it is still losing
    money (monthly_net < 0). Return True or False.

    is_bankrupt(-100, -20) -> True
    is_bankrupt(-100, 50)  -> False   (recovering)
    is_bankrupt(100, -20)  -> False
    """
    raise NotImplementedError("Exercise 1")


def classify_margin(margin):
    """Classify a poll margin in points (positive = Blue leads, negative = Red
    leads) by its absolute size:
      - |margin| >= 5       -> "safe Blue" / "safe Red"
      - 2 <= |margin| < 5   -> "lean Blue" / "lean Red"
      - |margin| < 2        -> "tossup"   (no party)

    classify_margin(6.2)  -> "safe Blue"
    classify_margin(-2.5) -> "lean Red"
    classify_margin(1.9)  -> "tossup"
    """
    raise NotImplementedError("Exercise 2")


def progressive_tax(income):
    """Return total tax under a progressive schedule:
      - the first 10,000 is taxed at 0%
      - the part between 10,000 and 40,000 is taxed at 20%
      - the part above 40,000 is taxed at 40%
    Each rate applies only to the slice of income inside its bracket.

    progressive_tax(8_000)  -> 0
    progressive_tax(25_000) -> 3000.0     (15,000 * 0.2)
    progressive_tax(50_000) -> 10000.0    (30,000 * 0.2 + 10,000 * 0.4)
    """
    raise NotImplementedError("Exercise 3")


def stability_change(at_war, exhaustion, balance):
    """Return the monthly stability change (an int), adding up EVERY rule
    that applies (they are independent, not either/or):
      - at war with exhaustion above 10: -1
      - at war with exhaustion above 20: a further -1  (so -2 total from war)
      - balance below 0: -1
      - at peace AND balance at least 1000: +1

    stability_change(True, 25, -50)  -> -3
    stability_change(False, 0, 1500) -> 1
    stability_change(True, 5, 2000)  -> 0
    """
    raise NotImplementedError("Exercise 4")


def clamp_stability(value):
    """Stability is limited to the range -3 to +3. Return value unchanged if
    inside the range, otherwise the nearest limit.

    clamp_stability(5) -> 3; clamp_stability(-4) -> -3; clamp_stability(1) -> 1
    """
    raise NotImplementedError("Exercise 5")


def beats_baseline(wins, games):
    """Return True if the win rate wins / games is strictly greater than 50%.
    If games is 0, return False (and don't divide by zero).

    beats_baseline(11, 20) -> True
    beats_baseline(10, 20) -> False
    beats_baseline(0, 0)   -> False
    """
    raise NotImplementedError("Exercise 6")


def describe_treasury(balance):
    """Return a label for a treasury balance:
      - below 0               -> "in debt"
      - exactly 0             -> "empty"
      - above 0, below 500    -> "tight"
      - 500 up to below 5000  -> "healthy"
      - 5000 or more          -> "overflowing"

    describe_treasury(-1) -> "in debt"; describe_treasury(500) -> "healthy"
    """
    raise NotImplementedError("Exercise 7")
