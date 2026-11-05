"""Worked example: is Rome really better than Carthage? Run: python example.py"""
import math

import numpy as np
from scipy import stats

rng = np.random.default_rng(20)

# --- 1. Permutation test on win/loss records -------------------------------
rome = np.array([1] * 41 + [0] * 29)        # 41-29, 58.6%
carthage = np.array([1] * 30 + [0] * 40)    # 30-40, 42.9%
obs = rome.mean() - carthage.mean()
pooled = np.concatenate([rome, carthage])
diffs = np.empty(10_000)
for i in range(len(diffs)):
    perm = rng.permutation(pooled)
    diffs[i] = perm[:70].mean() - perm[70:].mean()
p_perm = (np.sum(np.abs(diffs) >= abs(obs) - 1e-12) + 1) / (len(diffs) + 1)
print(f"Rome {rome.mean():.1%} vs Carthage {carthage.mean():.1%}: diff {obs:+.1%}")
print(f"  shuffled labels gave a gap at least that big in {np.mean(np.abs(diffs) >= abs(obs) - 1e-12):.1%} of 10,000 shuffles")
print(f"  permutation p-value: {p_perm:.4f}\n")

# --- 2. Bootstrap CI for mean and median game length -----------------------
lengths = rng.lognormal(mean=3.3, sigma=0.5, size=80)   # minutes, right-skewed
for name, f in [("mean", np.mean), ("median", np.median)]:
    idx = rng.integers(0, len(lengths), size=(5000, len(lengths)))
    boot = f(lengths[idx], axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print(f"game length {name}: {f(lengths):.1f} min, 95% bootstrap CI [{lo:.1f}, {hi:.1f}]")

# --- 3. Welch t-test, by hand vs scipy -------------------------------------
gold_rome = rng.normal(520, 80, 40)     # gold at minute 20
gold_carth = rng.normal(480, 120, 35)
va, vb = gold_rome.var(ddof=1) / 40, gold_carth.var(ddof=1) / 35
t = (gold_rome.mean() - gold_carth.mean()) / math.sqrt(va + vb)
df = (va + vb) ** 2 / (va**2 / 39 + vb**2 / 34)
p = 2 * stats.t.sf(abs(t), df)
ref = stats.ttest_ind(gold_rome, gold_carth, equal_var=False)
print(f"\nWelch t by hand: t={t:.3f}, df={df:.1f}, p={p:.4f}")
print(f"scipy ttest_ind: t={ref.statistic:.3f}, df={ref.df:.1f}, p={ref.pvalue:.4f}\n")

# --- 4. Multiple comparisons: 20 perfectly balanced factions ---------------
trials = 300
any_hit = 0
for _ in range(trials):
    wins = rng.binomial(200, 0.5, size=20)
    pvals = np.array([stats.binomtest(int(w), 200).pvalue for w in wins])
    any_hit += (pvals < 0.05).any()
print(f"20 balanced factions, 200 games each, test each at 5%:")
print(f"  at least one 'significant' faction in {any_hit / trials:.0%} of patches "
      f"(theory ~ 1 - 0.95^20 = {1 - 0.95**20:.0%}; a bit lower since binomial tests are discrete)")
print(f"  Bonferroni threshold: 0.05/20 = {0.05 / 20}")
