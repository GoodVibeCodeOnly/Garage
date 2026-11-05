"""Lesson 14 solutions: NumPy."""
import numpy as np


# Exercise 1
def player_win_rates(results):
    # Booleans average as 0/1, so mean over the games axis IS the win rate.
    return np.asarray(results).mean(axis=1)


# Exercise 2
def count_above(rates, baseline=0.5):
    # A comparison gives a boolean mask; sum counts the Trues.
    return int((np.asarray(rates) > baseline).sum())


# Exercise 3
def progressive_tax(incomes, threshold, low_rate, high_rate):
    incomes = np.asarray(incomes, dtype=float)
    # Vectorised "if": no Python loop over provinces.
    below = np.minimum(incomes, threshold)
    above = np.maximum(incomes - threshold, 0)
    return below * low_rate + above * high_rate
    # Alternative: np.where(incomes > threshold, ..., incomes * low_rate)


# Exercise 4
def simulate_win_rates(p_win, n_games, n_players, rng):
    games = rng.random((n_players, n_games)) < p_win
    return games.mean(axis=1)


# Exercise 5
def treasury_paths(start, income, turns, n_runs, event_prob, event_cost, rng):
    events = rng.random((n_runs, turns)) < event_prob
    # Each turn's change, then a running total along the turns axis.
    deltas = income - events * event_cost
    return start + np.cumsum(deltas, axis=1)


# Exercise 6
def bankrupt_share(paths):
    # any(axis=1): did this run (row) EVER go negative?
    return float((paths < 0).any(axis=1).mean())


# Exercise 7
def final_summary(paths):
    final = paths[:, -1]
    p05, p95 = np.percentile(final, [5, 95])
    return {"mean": float(final.mean()), "p05": float(p05), "p95": float(p95)}


# Exercise 8
def worst_drawdown(path):
    path = np.asarray(path, dtype=float)
    running_peak = np.maximum.accumulate(path)
    return float((running_peak - path).max())
