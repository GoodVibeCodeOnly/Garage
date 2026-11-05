"""Lesson 13 solutions: modules, random, Monte Carlo."""
import random
import statistics


# Exercise 1
def play_games(n_games, p_win, rng):
    # rng.random() is uniform on [0, 1): it's < p_win with probability p_win.
    return sum(1 for _ in range(n_games) if rng.random() < p_win)


# Exercise 2
def winrate_samples(n_games, p_win, n_trials, rng):
    return [play_games(n_games, p_win, rng) / n_games for _ in range(n_trials)]


# Exercise 3
def prob_looks_losing(n_games, p_win, n_trials, seed):
    # One Random per call, seeded once: reproducible and independent of
    # anything else using the global `random` module.
    rng = random.Random(seed)
    rates = winrate_samples(n_games, p_win, n_trials, rng)
    return sum(r < 0.5 for r in rates) / n_trials


# Exercise 4
def games_needed(p_win, threshold, n_trials, seed, candidates=(10, 25, 50, 100, 200, 400, 800)):
    for n in candidates:
        if prob_looks_losing(n, p_win, n_trials, seed) < threshold:
            return n
    return None


# Exercise 5
def simulate_treasury(start, income, turns, events, rng):
    balance = start
    history = []
    for _ in range(turns):
        balance += income
        for prob, amount in events:
            if rng.random() < prob:
                balance += amount
        history.append(balance)
    return history


# Exercise 6
def bankruptcy_rate(start, income, turns, events, n_runs, seed):
    rng = random.Random(seed)
    broke = 0
    for _ in range(n_runs):
        path = simulate_treasury(start, income, turns, events, rng)
        if min(path) < 0:
            broke += 1
    return broke / n_runs


# Exercise 7
def summarise(values):
    ordered = sorted(values)
    n = len(ordered)
    # Simple nearest-rank percentiles; statistics.quantiles is an alternative.
    return {
        "mean": statistics.mean(ordered),
        "min": ordered[0],
        "max": ordered[-1],
        "p05": ordered[int(0.05 * (n - 1))],
        "p95": ordered[int(0.95 * (n - 1))],
    }
