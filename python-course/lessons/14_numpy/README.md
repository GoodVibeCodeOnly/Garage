# 14 — NumPy

Last lesson you simulated 5000 seasons with nested Python loops. Fine for thousands; painful for millions. NumPy stores numbers in packed arrays and runs operations in compiled C, so "do this to every element" is one line and 30–100× faster. pandas (next lesson) is built on top of it, so the mental model here carries straight over.

## Arrays

```python
import numpy as np

income = np.array([120, 80, 45, 300])
income * 0.85            # array([102., 68., 38.25, 255.]) — every element
income + np.array([5, 5, 5, 5])   # element-wise
income.sum(), income.mean(), income.max()
np.zeros(5), np.arange(10), np.linspace(0, 1, 11)
```

Element-wise is the default: `a * b` multiplies pairwise, it is not a matrix product (that's `a @ b`). A scalar combined with an array is "broadcast" to every element.

## Boolean masks

A comparison produces an array of True/False — a **mask** — which you can use to filter or count:

```python
rich = income > 100          # array([ True, False, False,  True])
income[rich]                 # array([120, 300])
rich.sum()                   # 2   (True counts as 1)
rich.mean()                  # 0.5 (share that are True)
np.where(income > 100, income * 0.7, income * 0.9)   # vectorised if/else
```

Combine masks with `&` (and), `|` (or), `~` (not), with parentheses: `(a > 0) & (a < 10)`. Not `and`/`or` — those don't work element-wise.

## 2-D arrays and axes

```python
games = rng.random((6, 200)) < 0.52    # 6 players (rows) x 200 games (columns)
games.shape                            # (6, 200)
games[0]                               # first player's games
games[:, 0]                            # everyone's first game
games.mean(axis=1)                     # per-player win rate
games.mean(axis=0)                     # per-game share of players who won
```

The `axis` argument names the dimension that **gets collapsed**. `axis=1` sums across columns, leaving one number per row. If you're ever unsure, check `.shape` of the result.

## Random numbers: default_rng

```python
rng = np.random.default_rng(42)        # the modern API; seed it
rng.random((1000, 60))                 # uniform [0,1), shape 1000x60
rng.normal(0, 1, size=500)
rng.integers(1, 7, size=10)            # dice, 7 exclusive
```

Same principle as lesson 13: one seeded generator, passed into functions.

## Cumulative sums

`np.cumsum` turns a series of changes into a running level — exactly a treasury:

```python
delta = np.array([10, 10, -110, 10])
150 + np.cumsum(delta)                 # array([160, 170, 60, 70])
np.cumsum(deltas_2d, axis=1)           # running total along each row (run)
```

Related: `np.maximum.accumulate(x)` gives the running maximum (useful for drawdowns), `np.diff(x)` goes the other way (levels → changes).

## Worked example

`example.py`:

1. Applies a tax to a province-income array and filters with a mask.
2. Simulates 6 players × 200 games in one call; win rates via `mean(axis=1)`. Even at 200 games some true-52% players look losing.
3. Simulates **1000 treasuries × 60 turns** with no loops: two random event masks (revolts, windfalls), a per-turn `delta` array, and `np.cumsum(axis=1)`. Then the mean/percentiles of final treasuries and the share that ever went bankrupt via `(paths < 0).any(axis=1)`.
4. Rebuilds the same paths with nested loops and times both.
5. Saves a fan chart of sample paths to `output/treasury_fan.png`.

## Exercises

In `exercises.py` — try to write each one with no `for` loop:

1. `player_win_rates(results)` — mean over the right axis.
2. `count_above(rates, baseline)` — mask + sum.
3. `progressive_tax(incomes, threshold, low_rate, high_rate)` — two-bracket tax, vectorised.
4. `simulate_win_rates(p_win, n_games, n_players, rng)` — a whole ladder in one draw.
5. `treasury_paths(...)` — the 2-D cumsum treasury.
6. `bankrupt_share(paths)` — `any(axis=1)`.
7. `final_summary(paths)` — mean and percentiles of the last column.
8. `worst_drawdown(path)` — biggest peak-to-trough fall.

## How to check

Double-click `check.bat` in the course folder and type `14`.
