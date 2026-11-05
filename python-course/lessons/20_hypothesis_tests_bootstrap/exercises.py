# Lesson 20 exercises: hypothesis tests and the bootstrap.
# How to check: double-click check.bat in the course folder and type 20.
# Randomness ALWAYS comes from the numpy Generator `rng` passed in, used exactly
# as described, so results are reproducible and the tests can check exact values.
import math

import numpy as np
from scipy import stats


def diff_in_win_rates(a, b):
    """Exercise 1. a and b are sequences of game outcomes (1 = win, 0 = loss)
    for two factions. Return win rate of a minus win rate of b as a float."""
    raise NotImplementedError("Exercise 1")


def permutation_test(a, b, n_perm, rng):
    """Exercise 2. Two-sided permutation test for a difference in win rates.
    observed = diff_in_win_rates(a, b). Pool a and b (np.concatenate([a, b])).
    Repeat n_perm times: perm = rng.permutation(pooled); the first len(a) values
    are the fake "a", the rest the fake "b"; compute their difference.
    Count permutations with abs(diff) >= abs(observed) - 1e-12.
    Return (count + 1) / (n_perm + 1)."""
    raise NotImplementedError("Exercise 2")


def bootstrap_ci(x, stat, n_boot, rng, alpha=0.05):
    """Exercise 3. Percentile bootstrap confidence interval for stat(x).
    `stat` is a numpy function such as np.mean or np.median that accepts axis=.
    With n = len(x): idx = rng.integers(0, n, size=(n_boot, n)) (one call),
    resamples = x[idx] (convert x to a numpy array first), compute
    stat(resamples, axis=1), and return the (alpha/2, 1-alpha/2) percentiles
    (np.percentile with 100*alpha/2 and 100*(1-alpha/2)) as a tuple of floats."""
    raise NotImplementedError("Exercise 3")


def welch_t(a, b):
    """Exercise 4. Welch's two-sample t statistic BY HAND (no scipy here).
    va = var(a, ddof=1)/len(a), vb = var(b, ddof=1)/len(b)
    t  = (mean(a) - mean(b)) / sqrt(va + vb)
    df = (va + vb)^2 / (va^2/(len(a)-1) + vb^2/(len(b)-1))
    Return (t, df) as floats."""
    raise NotImplementedError("Exercise 4")


def t_test_pvalue(a, b):
    """Exercise 5. Two-sided p-value for Welch's t-test using your welch_t and
    the t distribution: 2 * stats.t.sf(abs(t), df). Should equal
    scipy.stats.ttest_ind(a, b, equal_var=False).pvalue."""
    raise NotImplementedError("Exercise 5")


def false_positive_count(n_factions, n_games, rng, alpha=0.05):
    """Exercise 6. Simulate n_factions factions that are ALL truly 50% win rate:
    wins = rng.binomial(n_games, 0.5, size=n_factions) (one call). Test each
    against 50% with stats.binomtest(int(w), n_games, 0.5).pvalue and return how
    many have p < alpha (an int). Every one of those is a false positive."""
    raise NotImplementedError("Exercise 6")


def bonferroni(pvalues, alpha=0.05):
    """Exercise 7. Bonferroni correction: return a boolean numpy array, True where
    p < alpha / m (m = number of p-values)."""
    raise NotImplementedError("Exercise 7")
