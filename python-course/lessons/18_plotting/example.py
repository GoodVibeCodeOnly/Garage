"""Worked example: a three-panel campaign report saved as PNG. Run: python example.py"""
import pathlib

import matplotlib

matplotlib.use("Agg")  # no windows; we only save files
import matplotlib.pyplot as plt
import numpy as np

OUT = pathlib.Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(18)

# --- Fake data -------------------------------------------------------------
years = np.arange(1444, 1500)
treasury = {}
for nation, drift in [("Castile", 4), ("Venice", 7), ("Ottomans", 10)]:
    # random walk with drift: income minus wars
    treasury[nation] = 100 + np.cumsum(rng.normal(drift, 25, len(years)))

factions = ["Rome", "Carthage", "Gaul", "Egypt"]
games = np.array([120, 90, 30, 200])
wins = np.array([70, 40, 18, 98])
p = wins / games
se = np.sqrt(p * (1 - p) / games)

errors = rng.normal(0.5, 3.5, 300)

# --- One figure, three Axes ------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 4.5))

for nation, bal in treasury.items():
    ax1.plot(years, bal, label=nation)
ax1.set(title="Treasury over time", xlabel="Year", ylabel="Ducats")
ax1.legend()

ax2.bar(factions, p, yerr=1.96 * se, capsize=5, color="steelblue")
ax2.axhline(0.5, ls="--", color="grey", label="coin flip")
ax2.set(title="Win rate by faction (95% CI)", ylabel="Win rate", ylim=(0, 1))
ax2.legend()

ax3.hist(errors, bins=25, color="indianred", edgecolor="white")
ax3.axvline(0, color="black")
ax3.axvline(errors.mean(), color="black", ls=":", label=f"mean {errors.mean():+.1f}")
ax3.set(title="Polling error", xlabel="Polling error (points)", ylabel="Number of polls")
ax3.legend()

fig.tight_layout()
path = OUT / "campaign_report.png"
fig.savefig(path, dpi=110)
plt.close(fig)

# --- Inspecting a plot programmatically (what the tests do) ----------------
print(f"saved {path}")
print(f"panel 1 has {len(ax1.lines)} lines: {[l.get_label() for l in ax1.lines]}")
print(f"panel 2 bar heights: {[round(float(b.get_height()), 3) for b in ax2.patches]}")
print(f"Gaul: {p[2]:.0%} win rate but CI +/-{1.96 * se[2]:.0%} -- the bar crosses 50%")
