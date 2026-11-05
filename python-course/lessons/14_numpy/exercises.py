"""Lesson 14 exercises: NumPy.

How to check: double-click `check.bat` in the course folder and type 14.
(Or from the course folder: python -m pytest lessons/14_numpy)

Challenge: no Python `for` loops in any of these. Every one is a few lines
of array operations.
"""
import numpy as np


# Exercise 1
def player_win_rates(results):
    """`results` is a 2-D boolean array, shape (n_players, n_games):
    results[i, j] is True if player i won game j.
    Return a 1-D float array of each player's win rate.
    """
    raise NotImplementedError("Exercise 1")


# Exercise 2
def count_above(rates, baseline=0.5):
    """Return how many entries of `rates` are strictly above `baseline`,
    as a plain Python int. Use a boolean mask.
    """
    raise NotImplementedError("Exercise 2")


# Exercise 3
def progressive_tax(incomes, threshold, low_rate, high_rate):
    """Province incomes (array-like). Tax the part of each income up to
    `threshold` at low_rate and the part above at high_rate.
    Return a float array of tax per province.

    progressive_tax([50, 150], 100, 0.1, 0.3) -> [5.0, 25.0]
    (150: 100*0.1 + 50*0.3 = 25)
    Hint: np.minimum / np.maximum, or np.where.
    """
    raise NotImplementedError("Exercise 3")


# Exercise 4
def simulate_win_rates(p_win, n_games, n_players, rng):
    """Simulate n_players players, each playing n_games with win prob p_win.
    `rng` is a np.random.Generator (from np.random.default_rng(seed)).

    Draw rng.random((n_players, n_games)) ONCE, compare with p_win, and
    return each player's observed win rate (1-D array, length n_players).
    """
    raise NotImplementedError("Exercise 4")


# Exercise 5
def treasury_paths(start, income, turns, n_runs, event_prob, event_cost, rng):
    """Vectorised treasury simulation: n_runs campaigns of `turns` turns.

    Each turn every treasury gains `income`, and with probability
    event_prob a disaster costs `event_cost`.
    Draw rng.random((n_runs, turns)) ONCE; an event happens where the draw
    is < event_prob.
    Return a 2-D array of shape (n_runs, turns): the balance at the end of
    each turn (so column 0 is start + first turn's change).
    Hint: build the per-turn change array, then np.cumsum(..., axis=1).
    """
    raise NotImplementedError("Exercise 5")


# Exercise 6
def bankrupt_share(paths):
    """Given a (n_runs, turns) array of balances, return the fraction of runs
    (rows) that were below 0 at ANY turn, as a Python float.
    Hint: (paths < 0).any(axis=1)
    """
    raise NotImplementedError("Exercise 6")


# Exercise 7
def final_summary(paths):
    """Return {"mean": ..., "p05": ..., "p95": ...} of the FINAL balances
    (last column) as Python floats. Use np.percentile (default method).
    """
    raise NotImplementedError("Exercise 7")


# Exercise 8
def worst_drawdown(path):
    """For a single 1-D treasury path, return the largest fall from a previous
    peak (peak minus later value), as a float. 0.0 if it never falls.

    worst_drawdown([100, 120, 90, 130, 80]) -> 50.0   (130 -> 80)
    Hint: np.maximum.accumulate gives the running peak.
    """
    raise NotImplementedError("Exercise 8")
