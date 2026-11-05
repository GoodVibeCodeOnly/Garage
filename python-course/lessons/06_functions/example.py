"""Worked example: composing game-economy formulas with functions.

Run:  python example.py
"""


def production(workers, output_per_worker, efficiency=1.0):
    """Goods produced per month."""
    return workers * output_per_worker * efficiency


def upkeep(units, cost_per_unit=2.0):
    """Monthly cost of maintaining military units."""
    return units * cost_per_unit


def flat_tariff(import_value):
    """Policy A: 10% on everything."""
    return import_value * 0.10


def protectionist_tariff(import_value):
    """Policy B: 25%, but small importers (< 300) pay nothing."""
    if import_value < 300:
        return 0.0
    return import_value * 0.25


def net_income(workers, units, import_value, tariff_fn, price=1.2):
    """Compose the formulas. `tariff_fn` is a FUNCTION passed in as a value."""
    revenue = production(workers, 1.5) * price
    return revenue + tariff_fn(import_value) - upkeep(units)


def bad_upkeep(units):
    print(units * 2.0)  # shows a number but returns None


def main():
    print("Production of 120 workers:", production(120, 1.5))
    print("Same, at 80% efficiency:  ", production(120, 1.5, efficiency=0.8))
    print("Upkeep for 40 units:      ", upkeep(40))
    print()

    # Same economy, two policies: only the function we pass in differs.
    for policy in (flat_tariff, protectionist_tariff):
        print(f"{policy.__name__:<22}", end="")
        for imports in (200, 500, 1000):
            print(f"  imports={imports:>4}: net={net_income(120, 40, imports, policy):7.1f}", end="")
        print()
    print()

    # Functions live in data structures too.
    policies = {"flat": flat_tariff, "protectionist": protectionist_tariff}
    best = max(policies, key=lambda name: policies[name](800))
    print("Best tariff policy at imports=800:", best)
    print()

    print("print-vs-return bug:")
    result = bad_upkeep(10)
    print("bad_upkeep returned:", result, "<- so `result + 5` would crash")


if __name__ == "__main__":
    main()
