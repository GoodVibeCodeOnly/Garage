"""Pricing a war: loans, interest, inflation. Pure arithmetic, no loops."""
import math

treasury = 1_000           # int ducats
regiment_cost = 85         # one-off cost to raise a regiment

# How many regiments can we raise with cash on hand, and what's left?
regiments, leftover = divmod(treasury, regiment_cost)
print(f"Cash raises {regiments} regiments, {leftover} ducats left over")

# We want 20 regiments. Borrow the shortfall in 250-ducat loans.
target = 20
shortfall = target * regiment_cost - treasury
loan_size = 250
loans = math.ceil(shortfall / loan_size)          # partial loans don't exist
borrowed = loans * loan_size
print(f"Shortfall {shortfall}: take {loans} loans = {borrowed} ducats")

# The loans compound at 5% a year for a 4-year war.
rate, years = 0.05, 4
owed = borrowed * (1 + rate) ** years
print(f"After {years} years at {rate:.0%}, we owe {owed:.2f} (interest {owed - borrowed:.2f})")

# Equivalent monthly rate: the 12th root, not rate/12.
monthly = (1 + rate) ** (1 / 12) - 1
print(f"Monthly rate {monthly:.5%} vs naive {rate / 12:.5%}")

# Inflation at 3% erodes the real burden of a fixed nominal debt.
inflation = 0.03
real_owed = owed / (1 + inflation) ** years
print(f"In today's ducats that debt is worth {real_owed:.2f}")

# Rule of 72 vs the exact log formula
exact = math.log(2) / math.log(1 + rate)
print(f"Debt doubles in {exact:.2f} years (rule of 72 says {72 / (rate * 100):.1f})")

# Float traps
print("\n0.1 + 0.2 =", 0.1 + 0.2)
print("0.1 + 0.2 == 0.3 ?", 0.1 + 0.2 == 0.3)
print("math.isclose(0.1 + 0.2, 0.3) ?", math.isclose(0.1 + 0.2, 0.3))
print("round(2.5), round(3.5) =", round(2.5), round(3.5), "(banker's rounding)")
print("-7 // 2 =", -7 // 2, "and -7 % 2 =", -7 % 2)
