"""Stability rules and poll classification: if/elif/else in action."""


def stability_delta(at_war, exhaustion, balance, overextension):
    delta = 0
    # Independent modifiers: several can apply in the same month, so each is
    # its own `if`. Using elif here would silently skip later penalties.
    if at_war and exhaustion > 10:
        delta -= 1
    if balance < 0:
        delta -= 1
    if overextension >= 50:
        delta -= 1
    if not at_war and balance > 1000:
        delta += 1
    return delta


def classify(margin):
    # Mutually exclusive categories: one elif chain, most restrictive first.
    gap = abs(margin)
    if gap >= 5:
        strength = "safe"
    elif gap >= 2:
        strength = "lean"
    else:
        return "tossup"
    party = "Blue" if margin > 0 else "Red"
    return f"{strength} {party}"


stability = 1
scenarios = [
    ("Peace, rich", False, 0, 1500, 10),
    ("Long war, broke", True, 14, -200, 60),
    ("Short war", True, 4, 300, 0),
]
for label, war, exh, bal, oe in scenarios:
    d = stability_delta(war, exh, bal, oe)
    new = max(-3, min(3, stability + d))      # clamp to the -3..+3 range
    print(f"{label:<16} delta {d:+d} -> stability {new:+d}")

print()
for state, margin in [("Ohio", 1.4), ("Texas", -6.2), ("Arizona", -2.5), ("Maine", 3.0)]:
    print(f"{state:<8} {margin:+5.1f}  {classify(margin)}")

# Short-circuit: the division never runs when regiments == 0
regiments, gold = 0, 500
if regiments > 0 and gold / regiments > 50:
    print("Well-funded army")
else:
    print("\nNo regiments (and no ZeroDivisionError thanks to short-circuiting)")
