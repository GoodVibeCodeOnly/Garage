"""Lesson 25 worked example: why the ELECTION, not the race, is the unit of analysis.

1. Peek at the raw polls to see what cleaning is needed.
2. Simulate a world where polls are UNBIASED on average (true mean bias = 0) but
   each election has a shared miss. Run the naive race-level t-test and the
   election-level t-test many times and count false positives at p < 0.05.
3. Plot the distribution of p-values to output/false_positives.png.
"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = pathlib.Path(__file__).parent

# 1. Raw data smells
raw = pd.read_csv(HERE / "data" / "polls.csv")
print("rows:", len(raw))
print("distinct raw state codes:", sorted(raw["state"].unique()))
print("missing values:\n", raw.isna().sum()[raw.isna().sum() > 0].to_string())
print("exact duplicates:", raw.duplicated().sum(), "\n")

# 2. Simulation: 12 elections x 10 states, true mean bias 0
rng = np.random.default_rng(0)
n_elec, n_states, sims = 12, 10, 2000
naive_p, clustered_p = [], []
for _ in range(sims):
    election_shock = rng.normal(0, 2.0, n_elec)                    # shared within election
    errors = election_shock[:, None] + rng.normal(0, 1.5, (n_elec, n_states))
    naive_p.append(stats.ttest_1samp(errors.ravel(), 0).pvalue)    # n = 120 "independent" races
    clustered_p.append(stats.ttest_1samp(errors.mean(axis=1), 0).pvalue)  # n = 12 elections
naive_p, clustered_p = np.array(naive_p), np.array(clustered_p)
print("True bias is ZERO. Share of simulations with p < 0.05 (should be ~5%):")
print(f"  naive (races as independent): {np.mean(naive_p < 0.05):.1%}")
print(f"  clustered (election means):   {np.mean(clustered_p < 0.05):.1%}")

# Design effect: how much the naive SE understates the truth
rho = 2.0**2 / (2.0**2 + 1.5**2)                                   # intra-election correlation
deff = 1 + (n_states - 1) * rho
print(f"\nintra-election correlation ~ {rho:.2f}; design effect ~ {deff:.1f}")
print(f"=> 120 correlated races carry about as much info as {120 / deff:.0f} independent ones.")

# 3. Plot
out = HERE / "output"
out.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(7, 4))
bins = np.linspace(0, 1, 21)
ax.hist(naive_p, bins=bins, alpha=0.6, label="naive (race-level)")
ax.hist(clustered_p, bins=bins, alpha=0.6, label="clustered (election-level)")
ax.axhline(sims / 20, color="grey", ls="--", lw=1, label="uniform (what a valid test gives)")
ax.set_xlabel("p-value when the true bias is 0")
ax.set_ylabel("simulations")
ax.legend()
fig.tight_layout()
fig.savefig(out / "false_positives.png", dpi=100)
print("\nsaved", out / "false_positives.png")
