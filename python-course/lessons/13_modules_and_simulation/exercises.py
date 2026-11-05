"""Lesson 13 exercises: modules, random, Monte Carlo.

How to check: double-click `check.bat` in the course folder and type 13.
(Or from the course folder: python -m pytest lessons/13_modules_and_simulation)

Randomness rule for this file: never call the module-level random.random().
Functions either receive an `rng` (a random.Random instance) or a `seed`
from which they build ONE random.Random(seed). That makes results
reproducible, so tests can check them.
"""
import random
import statistics


# Exercise 1
def play_games(n_games, p_win, rng):
    """Simulate n_games independent games where each is won with probability
    p_win. Return the number of wins (an int).
    Use rng.random() < p_win for each game.
    """
    raise NotImplementedError("Exercise 1")


# Exercise 2
def winrate_samples(n_games, p_win, n_trials, rng):
    """Run n_trials independent "seasons" of n_games each (reuse play_games
    with the same rng). Return a list of n_trials observed win rates
    (wins / n_games, floats).
    """
    raise NotImplementedError("Exercise 2")


# Exercise 3
def prob_looks_losing(n_games, p_win, n_trials, seed):
    """The headline question: a genuinely 55% player plays n_games. How often
    does their record show BELOW 50%?

    Build rng = random.Random(seed), get winrate_samples, and return the
    fraction of trials whose observed win rate is strictly < 0.5.
    """
    raise NotImplementedError("Exercise 3")


# Exercise 4
def games_needed(p_win, threshold, n_trials, seed, candidates=(10, 25, 50, 100, 200, 400, 800)):
    """Return the first n in `candidates` (in order) for which
    prob_looks_losing(n, p_win, n_trials, seed) < threshold.
    Return None if none qualify.

    i.e. "how many games before a 55% player looks losing less than 5% of
    the time?"
    """
    raise NotImplementedError("Exercise 4")


# Exercise 5
def simulate_treasury(start, income, turns, events, rng):
    """Paradox-style treasury. Starting balance `start`. Each turn:
      1. add `income`
      2. for each (prob, amount) in `events`, in order: with probability
         prob (rng.random() < prob) add amount (amount can be negative:
         a revolt costs -150, a trade windfall +80)
      3. record the balance
    Return the list of `turns` end-of-turn balances.
    """
    raise NotImplementedError("Exercise 5")


# Exercise 6
def bankruptcy_rate(start, income, turns, events, n_runs, seed):
    """Run simulate_treasury n_runs times with ONE rng = random.Random(seed)
    shared across runs. Return the fraction of runs where the balance was
    below 0 at the end of ANY turn.
    """
    raise NotImplementedError("Exercise 6")


# Exercise 7
def summarise(values):
    """Summary stats for a list of numbers (e.g. final treasuries).
    Return a dict with keys "mean", "min", "max", "p05", "p95".

    For percentiles use nearest-rank on the sorted list:
        p05 = ordered[int(0.05 * (n - 1))]
        p95 = ordered[int(0.95 * (n - 1))]
    statistics.mean is fine for the mean.
    """
    raise NotImplementedError("Exercise 7")
