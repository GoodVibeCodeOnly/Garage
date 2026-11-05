"""A toy Paradox-style monthly treasury tick. Read it top to bottom before running."""
import traceback

# --- Constants: defined once, read everywhere below ---
POPULATION = 12_000        # underscores are just visual separators
TAX_RATE = 0.05            # ducats per person per month
REGIMENTS = 8
UPKEEP_PER_REGIMENT = 45.0
LOAN_INTEREST = 20.0


def collect_taxes(population, rate):
    """Return tax income for one month."""
    return population * rate


def pay_upkeep(regiments, cost_each):
    """Return total army upkeep for one month."""
    return regiments * cost_each


def tick(balance, month):
    """Run one monthly tick and return the new balance."""
    income = collect_taxes(POPULATION, TAX_RATE)
    expenses = pay_upkeep(REGIMENTS, UPKEEP_PER_REGIMENT) + LOAN_INTEREST
    new_balance = balance + income - expenses
    print(f"Month {month}: +{income:.1f} -{expenses:.1f} -> {new_balance:.1f}")
    return new_balance


# Nothing above this line has *done* anything except define names.
# Execution of real work starts here.
balance = 500.0
print(f"Starting treasury: {balance:.1f} ducats")
balance = tick(balance, 1)   # 500 + 600 - 380 = 720
balance = tick(balance, 2)   # 720 + 220 = 940
balance = tick(balance, 3)   # 1160
print(f"After a quarter: {balance:.1f} ducats")

# --- Reading a traceback without crashing the script ---
print("\nNow a deliberate bug: average income per regiment with zero regiments.")


def income_per_regiment(regiments):
    return collect_taxes(POPULATION, TAX_RATE) / regiments


try:
    income_per_regiment(0)
except ZeroDivisionError:
    traceback.print_exc()   # prints the same traceback Python would on a crash
    print("^ Read it bottom-up: exception type, then the line in income_per_regiment.")
