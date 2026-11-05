"""Lesson 20 solutions: permutation tests, bootstrap, t-tests, multiple comparisons."""
import math

import numpy as np
from scipy import stats


def diff_in_win_rates(a, b):
    # 0/1 outcomes: the mean IS the win rate.
    return float(np.mean(a) - np.mean(b))


def permutation_test(a, b, n_perm, rng):
    a, b = np.asarray(a), np.asarray(b)
    observed = diff_in_win_rates(a, b)
    pooled = np.concatenate([a, b])
    # Under H0 the faction label is irrelevant, so shuffling labels generates
    # the distribution of differences that pure chance produces.
    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(pooled)
        d = perm[: len(a)].mean() - perm[len(a):].mean()
        if abs(d) >= abs(observed) - 1e-12:  # two-sided; tolerance for float ties
            count += 1
    # +1 on top and bottom: counts the observed labelling as one permutation,
    # so the p-value can never be exactly 0 (it can't be, from finite shuffles).
    return (count + 1) / (n_perm + 1)


def bootstrap_ci(x, stat, n_boot, rng, alpha=0.05):
    x = np.asarray(x)
    n = len(x)
    # Resample WITH replacement, same size as the data: each row is one
    # "alternative dataset we might have collected".
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = stat(x[idx], axis=1)
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def welch_t(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)  # squared SEs
    t = (a.mean() - b.mean()) / math.sqrt(va + vb)
    # Welch-Satterthwaite approximation of the degrees of freedom.
    df = (va + vb) ** 2 / (va**2 / (len(a) - 1) + vb**2 / (len(b) - 1))
    return float(t), float(df)


def t_test_pvalue(a, b):
    t, df = welch_t(a, b)
    # sf = survival function = 1 - cdf, more accurate in the far tail.
    return float(2 * stats.t.sf(abs(t), df))


def false_positive_count(n_factions, n_games, rng, alpha=0.05):
    wins = rng.binomial(n_games, 0.5, size=n_factions)  # every faction truly balanced
    pvals = [stats.binomtest(int(w), n_games, 0.5).pvalue for w in wins]
    return sum(p < alpha for p in pvals)


def bonferroni(pvalues, alpha=0.05):
    # Controls the chance of ANY false positive across m tests at alpha.
    # Conservative; Holm or Benjamini-Hochberg are less so.
    p = np.asarray(pvalues)
    return p < alpha / len(p)
