# Lesson 19 exercises: statistics for win rates, by hand.
# How to check: double-click check.bat in the course folder and type 19.
# Implement with plain Python / math / numpy. Do NOT call scipy or
# statistics/np.var/np.std inside these functions (tests compare against them).
import math

import numpy as np


def mean(xs):
    """Exercise 1a. Arithmetic mean of a list of numbers."""
    raise NotImplementedError("Exercise 1")


def variance(xs, ddof=1):
    """Exercise 1b. Variance: sum of squared deviations from the mean divided by
    (n - ddof). ddof=1 gives the sample variance (default), ddof=0 the population one."""
    raise NotImplementedError("Exercise 1")


def std(xs, ddof=1):
    """Exercise 1c. Standard deviation = square root of variance(xs, ddof)."""
    raise NotImplementedError("Exercise 1")


def se_proportion(wins, n):
    """Exercise 2. Standard error of a win rate: p = wins/n, SE = sqrt(p(1-p)/n)."""
    raise NotImplementedError("Exercise 2")


def normal_ci(wins, n, z=1.96):
    """Exercise 3. Normal-approximation (Wald) confidence interval for the win
    rate: (p - z*SE, p + z*SE). Return a tuple (low, high). Do not clip."""
    raise NotImplementedError("Exercise 3")


def wilson_ci(wins, n, z=1.96):
    """Exercise 4. Wilson score interval. With p = wins/n:
        denom  = 1 + z^2/n
        centre = (p + z^2/(2n)) / denom
        half   = z * sqrt(p(1-p)/n + z^2/(4n^2)) / denom
    Return (centre - half, centre + half)."""
    raise NotImplementedError("Exercise 4")


def binom_pmf(k, n, p=0.5):
    """Exercise 5. Probability of exactly k wins in n games with win probability p:
    C(n, k) * p^k * (1-p)^(n-k). Use math.comb."""
    raise NotImplementedError("Exercise 5")


def binom_test_two_sided(wins, n, p=0.5):
    """Exercise 6. Exact two-sided binomial test p-value: the total probability
    (under win probability p) of every outcome k in 0..n whose pmf is <= the pmf
    of the observed `wins`. Compare with a tiny tolerance: include k if
    pmf(k) <= pmf(wins) * (1 + 1e-7). Cap the result at 1.0."""
    raise NotImplementedError("Exercise 6")


def simulate_win_rates(true_p, n_games, n_players, rng):
    """Exercise 7. Simulate n_players players who each play n_games games, each
    won with probability true_p. Return a numpy array (length n_players) of
    observed win rates. Use the numpy Generator `rng` passed in:
    exactly ONE call, rng.random((n_players, n_games)), and a game is a win
    where that number is < true_p."""
    raise NotImplementedError("Exercise 7")
