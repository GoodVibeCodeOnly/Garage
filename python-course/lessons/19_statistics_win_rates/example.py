"""Worked example: is the new faction overpowered? Run: python example.py"""
import math

import numpy as np
from scipy import stats

# Patch notes: "Byzantium buffed". Community data after the patch:
records = {"Byzantium": (14, 20), "Mamluks": (530, 1000), "Hungary": (5, 5)}


def wald(w, n, z=1.96):
    p = w / n
    se = math.sqrt(p * (1 - p) / n)
    return p - z * se, p + z * se


def wilson(w, n, z=1.96):
    p = w / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def binom_p(w, n, p0=0.5):
    pmf = [math.comb(n, k) * p0**k * (1 - p0) ** (n - k) for k in range(n + 1)]
    return min(1.0, sum(x for x in pmf if x <= pmf[w] * (1 + 1e-7)))


print(f"{'faction':<10} {'record':>9} {'rate':>6}  {'Wald 95% CI':>16}  {'Wilson 95% CI':>16}  {'p (by hand)':>11} {'p (scipy)':>9}")
for name, (w, n) in records.items():
    lo, hi = wald(w, n)
    wl, wh = wilson(w, n)
    print(f"{name:<10} {w:>4}/{n:<4} {w / n:>6.1%}  [{lo:6.1%}, {hi:6.1%}]  [{wl:6.1%}, {wh:6.1%}]"
          f"  {binom_p(w, n):>11.4f} {stats.binomtest(w, n).pvalue:>9.4f}")

print("""
Read it like this:
 - Byzantium 70% over 20 games looks broken, but p ~ 0.12: a fair coin does that often.
 - Mamluks at 53% look boring, but 1000 games makes p ~ 0.06 -- a small edge, measured precisely.
 - Hungary 5/5: Wald says [100%, 100%] (nonsense). Wilson says roughly [57%, 100%].
""")

# Why small samples mislead: 10,000 perfectly average players (true p = 0.5)
rng = np.random.default_rng(19)
for n_games in [10, 20, 100, 1000]:
    rates = (rng.random((10_000, n_games)) < 0.5).mean(axis=1)
    print(f"{n_games:>5} games: SD of observed win rate {rates.std():.3f} "
          f"(theory {math.sqrt(0.25 / n_games):.3f}); "
          f"{(rates >= 0.65).mean():6.1%} of average players look like 65%+ players")
