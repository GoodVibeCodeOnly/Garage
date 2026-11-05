# 20 — Hypothesis tests and the bootstrap

Lesson 19 tested one win rate against 50%. Real questions compare things. Is Rome better than Carthage? Did the patch change game length? Is *any* of the 20 factions imbalanced? This lesson covers two simulation-based tools that work almost anywhere (permutation tests and the bootstrap), one classic formula (the t-test), and one trap (multiple comparisons).

## The logic of a test

1. **Null hypothesis H₀**: the boring explanation. "Rome and Carthage have the same true win rate."
2. **Test statistic**: a number that measures the effect. Here, the difference in observed win rates.
3. **p-value**: *if H₀ were true*, the probability of getting a statistic at least this extreme.

A small p means "this would be weird if nothing were going on". It is **not** the probability that H₀ is true, and it says nothing about how big the effect is. The 0.05 cut-off is a convention, not a law.

## Permutation test: simulate the null directly

If faction doesn't matter, the labels "Rome" and "Carthage" on each game are arbitrary. So shuffle them:

```python
pooled = np.concatenate([a, b])
for _ in range(n_perm):
    perm = rng.permutation(pooled)
    d = perm[:len(a)].mean() - perm[len(a):].mean()
    # count how often |d| >= |observed|
p = (count + 1) / (n_perm + 1)
```

The shuffled differences *are* the distribution of differences under the null. You need no formulas and no normality assumptions. The `+1`s count the real labelling as one of the permutations, so p is never exactly zero.

## Bootstrap: uncertainty without formulas

How uncertain is the median game length? There's no tidy SE formula for a median. The bootstrap treats your sample as the population and resamples from it **with replacement**:

```python
idx = rng.integers(0, n, size=(n_boot, n))   # n_boot fake datasets of size n
boot = np.median(x[idx], axis=1)
lo, hi = np.percentile(boot, [2.5, 97.5])    # percentile 95% CI
```

The spread of `boot` approximates the sampling distribution of your statistic. It works for means, medians, ratios and regression coefficients alike. It's weak at very small n, because a resample can't contain values your data never had.

## t-test: the classic for comparing means

For continuous outcomes (gold at minute 20), Welch's t-test compares means without assuming equal variances:

```python
va, vb = a.var(ddof=1)/len(a), b.var(ddof=1)/len(b)    # squared SEs
t  = (a.mean() - b.mean()) / sqrt(va + vb)
df = (va + vb)**2 / (va**2/(len(a)-1) + vb**2/(len(b)-1))
p  = 2 * stats.t.sf(abs(t), df)
```

`t` is "difference in means, measured in standard errors". `scipy.stats.ttest_ind(a, b, equal_var=False)` does the same thing. Prefer Welch over the equal-variance version by default.

## Multiple comparisons: the 20-faction trap

Test 20 perfectly balanced factions at α = 0.05 and you expect one false positive. The chance of at least one is `1 − 0.95²⁰ ≈ 64%`. "Faction 14 is significantly overpowered!" is exactly what pure noise looks like if you go looking. The same applies to 20 policy outcomes, 20 subgroups, or 20 model specifications. That's p-hacking, whether you meant to or not.

The fix (one of several): **Bonferroni**. Require p < α/m, so with 20 tests the threshold is 0.0025. It's conservative. Holm and Benjamini-Hochberg are less blunt, and worth looking up when you need them.

## Reproducibility

All randomness here goes through a numpy `Generator` passed in as `rng`. The same seed gives the same p-value, which is how the tests can check exact numbers, and how your research results stay replicable.

## Worked example

`example.py` runs four mini-analyses:

1. Rome (41-29) vs Carthage (30-40): a 15.7-point gap, but the permutation p ≈ 0.09.
2. Bootstrap 95% CIs for the mean and median of a skewed game-length sample.
3. Welch's t-test on gold at minute 20, by hand and with scipy. The two give identical numbers.
4. 300 simulated patches with 20 balanced factions each. More than half "find" an imbalanced faction at p < 0.05.

## Exercises

In `exercises.py`. Use the given `rng` exactly as each docstring says:

1. `diff_in_win_rates(a, b)`
2. `permutation_test(a, b, n_perm, rng)`
3. `bootstrap_ci(x, stat, n_boot, rng, alpha=0.05)`
4. `welch_t(a, b)`: by hand, returns `(t, df)`
5. `t_test_pvalue(a, b)`: matches `scipy.stats.ttest_ind`
6. `false_positive_count(n_factions, n_games, rng, alpha=0.05)`
7. `bonferroni(pvalues, alpha=0.05)`

## How to check

Double-click `check.bat` in the course folder and type `20`.
