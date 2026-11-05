"""Lesson 19 solutions: descriptive stats and win-rate uncertainty, by hand."""
import math

import numpy as np


def mean(xs):
    return sum(xs) / len(xs)


def variance(xs, ddof=1):
    # ddof=1 (divide by n-1, "Bessel's correction") estimates the POPULATION
    # variance from a sample; the sample mean is closer to its own data than
    # the true mean is, so dividing by n would underestimate the spread.
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def std(xs, ddof=1):
    return math.sqrt(variance(xs, ddof))


def se_proportion(wins, n):
    # Each game is a Bernoulli(p) draw with variance p(1-p); the mean of n of
    # them has variance p(1-p)/n. SE shrinks with sqrt(n), not n: 4x the games
    # for half the uncertainty.
    p = wins / n
    return math.sqrt(p * (1 - p) / n)


def normal_ci(wins, n, z=1.96):
    p = wins / n
    half = z * se_proportion(wins, n)
    return (p - half, p + half)


def wilson_ci(wins, n, z=1.96):
    # Wilson inverts the score test: it uses the SE *under the candidate p*
    # rather than under p_hat, so it never collapses to zero width at 0/n or
    # n/n and never leaves [0, 1].
    p = wins / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return (centre - half, centre + half)


def binom_pmf(k, n, p=0.5):
    return math.comb(n, k) * p**k * (1 - p) ** (n - k)


def binom_test_two_sided(wins, n, p=0.5):
    # Exact two-sided test (same rule scipy uses): add up the probability of
    # every outcome at least as unlikely as the one observed.
    observed = binom_pmf(wins, n, p)
    # Tiny tolerance so floating-point noise doesn't drop the mirror outcome.
    total = sum(pr for k in range(n + 1)
                if (pr := binom_pmf(k, n, p)) <= observed * (1 + 1e-7))
    return min(1.0, total)


def simulate_win_rates(true_p, n_games, n_players, rng):
    # Each row of the (n_players, n_games) matrix is one player's record.
    # Vectorised alternative: rng.binomial(n_games, true_p, n_players) / n_games
    games = rng.random((n_players, n_games)) < true_p
    return games.mean(axis=1)
