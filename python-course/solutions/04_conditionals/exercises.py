# Lesson 04 — Conditionals (solutions)


def is_bankrupt(balance, monthly_net):
    # Comparisons already produce bools; no need for `if ...: return True`.
    return balance < 0 and monthly_net < 0


def classify_margin(margin):
    gap = abs(margin)
    party = "Blue" if margin > 0 else "Red"
    # Most restrictive first: an elif chain stops at the first match.
    if gap >= 5:
        return f"safe {party}"
    elif gap >= 2:
        return f"lean {party}"
    else:
        return "tossup"


def progressive_tax(income):
    # Work from the top bracket down: tax the slice above each threshold,
    # then add the full tax owed on every bracket below it.
    if income <= 10_000:
        return 0
    elif income <= 40_000:
        return (income - 10_000) * 0.2
    else:
        return 30_000 * 0.2 + (income - 40_000) * 0.4
    # Alternative without branches, which scales to many brackets:
    #   tax = 0.2 * max(0, min(income, 40_000) - 10_000)
    #       + 0.4 * max(0, income - 40_000)


def stability_change(at_war, exhaustion, balance):
    delta = 0
    # Separate ifs, because several rules can apply in the same month.
    if at_war and exhaustion > 10:
        delta -= 1
    if at_war and exhaustion > 20:
        delta -= 1
    if balance < 0:
        delta -= 1
    if not at_war and balance >= 1000:
        delta += 1
    return delta


def clamp_stability(value):
    # min caps the top, max floors the bottom. Equivalent to:
    #   if value > 3: return 3
    #   elif value < -3: return -3
    #   else: return value
    return max(-3, min(3, value))


def beats_baseline(wins, games):
    # Short-circuit: if games == 0 the right side never runs.
    return games > 0 and wins / games > 0.5


def describe_treasury(balance):
    if balance < 0:
        return "in debt"
    elif balance == 0:
        return "empty"
    elif balance < 500:          # we already know balance > 0 here
        return "tight"
    elif balance < 5000:
        return "healthy"
    else:
        return "overflowing"
