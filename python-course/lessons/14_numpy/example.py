"""Worked example: 1000 treasuries at once, and why loops become one-liners.

Run: python example.py   (also saves output/treasury_fan.png)
"""
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng(14)

# --- arrays and vectorised arithmetic ---------------------------------------
income = np.array([120, 80, 45, 300, 60])        # five provinces
print("income      :", income)
print("after 15% tax:", income * 0.85)           # no loop: applies to every element
rich = income > 100                              # boolean mask
print("rich mask   :", rich, "-> rich provinces:", income[rich])

# --- 2-D arrays and axes ----------------------------------------------------
# 6 players x 200 games, each a true 52% player
games = rng.random((6, 200)) < 0.52
print("\nwins per player (axis=1):", games.sum(axis=1))
print("win rate per player       :", games.mean(axis=1).round(3))
print("players looking sub-50%   :", (games.mean(axis=1) < 0.5).sum(), "of 6")

# --- the treasury: 1000 runs x 60 turns -------------------------------------
RUNS, TURNS = 1000, 60
start, base_income = 150, 10
revolt = rng.random((RUNS, TURNS)) < 0.08        # 8% chance per turn
windfall = rng.random((RUNS, TURNS)) < 0.15      # 15% chance per turn
delta = base_income - 120 * revolt + 40 * windfall
paths = start + np.cumsum(delta, axis=1)         # running balance per run

final = paths[:, -1]
ever_broke = (paths < 0).any(axis=1)
print(f"\n{RUNS} runs x {TURNS} turns")
print(f"final treasury mean {final.mean():.0f}, 5th pct {np.percentile(final, 5):.0f}, "
      f"95th pct {np.percentile(final, 95):.0f}")
print(f"runs that went bankrupt at some point: {ever_broke.mean():.1%}")

# --- speed: loop vs vectorised ----------------------------------------------
t0 = time.perf_counter()
loop_paths = []
for r in range(RUNS):
    bal, row = start, []
    for t in range(TURNS):
        bal += delta[r, t]
        row.append(bal)
    loop_paths.append(row)
t1 = time.perf_counter()
np.cumsum(delta, axis=1)
t2 = time.perf_counter()
print(f"\nsame result: {np.array_equal(np.array(loop_paths), paths)}; "
      f"loop {1000 * (t1 - t0):.1f} ms vs numpy {1000 * (t2 - t1):.2f} ms")

out = Path(__file__).parent / "output"
out.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(paths[:50].T, color="tab:blue", alpha=0.25, lw=0.8)
ax.plot(np.median(paths, axis=0), color="k", lw=2, label="median of 1000 runs")
ax.axhline(0, color="tab:red", ls="--", lw=1)
ax.set(xlabel="turn", ylabel="treasury", title="50 sample treasury paths")
ax.legend()
fig.savefig(out / "treasury_fan.png", dpi=110, bbox_inches="tight")
print("saved output/treasury_fan.png")
