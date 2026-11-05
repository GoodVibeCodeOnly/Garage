# 19 — Statistics for win rates

"Byzantium is broken, 70% win rate since the patch!" Over 20 games? A fair coin goes 14-6 more often than you'd guess. This lesson is the toolkit for answering "is this different from 50%, or is it noise?" You'll build the formulas by hand so they stop being magic, then check them against scipy.

## Mean, variance, standard deviation

```python
mean = sum(xs) / n
var  = sum((x - mean)**2 for x in xs) / (n - 1)   # sample variance
sd   = var ** 0.5
```

Why `n - 1`? The sample mean is fitted to this data, so deviations from it come out a bit smaller than deviations from the true mean would be. Dividing by `n - 1` (`ddof=1`) corrects for that. `np.var` defaults to `ddof=0` and pandas `.var()` defaults to `ddof=1`. That mismatch catches people out constantly.

## A win rate is a mean, so it has a standard error

Code each game as 1 (win) or 0 (loss). The win rate `p̂ = wins/n` is the mean of those 0/1 values, and one game has variance `p(1−p)`. The mean of `n` independent games therefore has

```python
se = math.sqrt(p * (1 - p) / n)
```

**The SE shrinks with √n.** You need four times the games to halve the uncertainty. At p ≈ 0.5: 20 games gives SE ≈ 11 points, 100 games ≈ 5, and 1000 games ≈ 1.6.

## Confidence intervals

**Normal approximation (Wald):** `p̂ ± 1.96·SE`. The 1.96 cuts off 2.5% in each tail of a normal distribution, so you get roughly 95% coverage. It's easy, and it's bad at small `n` or at extreme `p`. At 5/5 the SE is 0, so the interval is [100%, 100%], which is absurd.

**Wilson score interval:** it asks "which values of p would make this result unsurprising?" and uses the SE *under each candidate p*:

```python
denom  = 1 + z**2 / n
centre = (p + z**2 / (2*n)) / denom
half   = z * math.sqrt(p*(1-p)/n + z**2 / (4*n**2)) / denom
```

It pulls the centre toward 50%, never leaves [0, 1], and has close to the promised coverage even at small n. Default to Wilson for proportions.

## Binomial test: is it different from 50%?

If the true win rate were 50%, how surprising would `wins` out of `n` be? The probability of exactly k wins is

```python
math.comb(n, k) * p**k * (1 - p)**(n - k)
```

The exact two-sided **p-value** adds up the probabilities of every outcome *at least as unlikely* as the one you observed, in both directions. For 14/20 the answer is ≈ 0.115. Average factions produce a result this lopsided about one time in nine. `scipy.stats.binomtest(14, 20).pvalue` gives the same number. You'll write it by hand and compare.

A p-value is **not** "the probability the faction is balanced". It's P(data this extreme | balanced). Lesson 20 goes deeper.

## Why small samples mislead

Simulate 10,000 players, all *exactly* 50% at the game, each playing 20 games. About 13% of them finish at 65% or better. A leaderboard built from small samples mostly ranks luck. That's also why the "best" faction after a patch often regresses toward the middle a week later. Ask for the n and the interval before you believe the headline rate.

## Worked example

`example.py` takes three post-patch records: Byzantium 14/20, Mamluks 530/1000, Hungary 5/5. It prints each win rate with Wald and Wilson intervals and the binomial p-value both by hand and from scipy. They agree. Notice the reversal: the "broken" 70% isn't statistically clear, while the dull 53% over 1000 games nearly is. Then it simulates average players at 10, 20, 100 and 1000 games and shows the spread of observed win rates matching `sqrt(0.25/n)`.

## Exercises

In `exercises.py` (no scipy, `statistics`, or `np.var` inside your functions):

1. `mean`, `variance(xs, ddof=1)`, `std(xs, ddof=1)`
2. `se_proportion(wins, n)`
3. `normal_ci(wins, n, z=1.96)`
4. `wilson_ci(wins, n, z=1.96)`
5. `binom_pmf(k, n, p=0.5)` with `math.comb`
6. `binom_test_two_sided(wins, n, p=0.5)`: tested against `scipy.stats.binomtest`
7. `simulate_win_rates(true_p, n_games, n_players, rng)`: see how often luck looks like skill

## How to check

Double-click `check.bat` in the course folder and type `19`.
