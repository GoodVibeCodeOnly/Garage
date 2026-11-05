"""Worked example: is a 55% player distinguishable from a coin flip?

Run: python example.py   (also saves output/winrate_spread.png)
"""
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sim_tools                      # our own module, sitting next to this file
from sim_tools import share_below     # or import just one name

SEED = 2026
TRIALS = 5000
rng = random.Random(SEED)             # one seeded generator, passed around

print(f"A true 55% player, {TRIALS} simulated seasons each:")
print(f"{'games':>6} {'P(record < 50%)':>16} {'5th-95th pct':>16}")
spreads = {}
for n in (10, 30, 100, 300, 1000):
    rates = sorted(sim_tools.season_winrate(n, 0.55, rng) for _ in range(TRIALS))
    spreads[n] = rates
    lo, hi = rates[int(0.05 * TRIALS)], rates[int(0.95 * TRIALS)]
    print(f"{n:>6} {share_below(rates, 0.5):>16.1%} {lo:>8.1%} - {hi:.1%}")

print("\nReproducibility: same seed, same answer ->",
      sim_tools.season_winrate(50, 0.55, random.Random(1)) ==
      sim_tools.season_winrate(50, 0.55, random.Random(1)))

# Treasury: income 10/turn, 10% chance per turn of a -120 revolt.
def treasury(rng, start=100, turns=50):
    bal, low = start, start
    for _ in range(turns):
        bal += 10
        if rng.random() < 0.10:
            bal -= 120
        low = min(low, bal)
    return bal, low

runs = [treasury(rng) for _ in range(TRIALS)]
busted = sum(low < 0 for _, low in runs) / TRIALS
avg_final = sum(final for final, _ in runs) / TRIALS
print(f"\nTreasury: ends at {avg_final:.0f} on average "
      f"(expected 100 + 50*(10 - 0.1*120) = 0), but dips below zero in {busted:.0%} of runs.")

out = Path(__file__).parent / "output"
out.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(7, 4))
for n in (30, 300):
    ax.hist(spreads[n], bins=40, alpha=0.6, label=f"{n} games")
ax.axvline(0.5, color="k", ls="--", lw=1)
ax.set(xlabel="observed win rate", ylabel="seasons", title="A 55% player, observed")
ax.legend()
fig.savefig(out / "winrate_spread.png", dpi=110, bbox_inches="tight")
print("saved output/winrate_spread.png")
