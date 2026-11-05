# 13 — Modules and Monte Carlo simulation

Two ideas this lesson. First, how Python code is split across files (`import`). Second, the single most useful trick an economist with a laptop has: when the maths is annoying, **simulate it ten thousand times and count**.

## import

```python
import random                    # whole module; use random.Random(...)
import statistics as st          # alias
from math import sqrt, log       # specific names
import sim_tools                 # YOUR file sim_tools.py in the same folder
```

A module is just a `.py` file. Importing runs it top to bottom once and gives you its names. That's why reusable files guard their "demo" code:

```python
if __name__ == "__main__":       # True only when run directly, not on import
    print(season_winrate(100, 0.55, random.Random(0)))
```

Python finds modules in the folder of the script you ran, then the standard library, then installed packages. (Corollary: never name your own file `random.py` — it'll shadow the real one.)

## Writing reusable functions

The functions worth importing share a shape: **inputs in, result out, no hidden state**. Not "reads a global, prints a number" but "takes parameters, returns a value". Then you can call them in a loop, test them, and reuse them in the next project. Every exercise in this lesson has that shape.

## random, and why you pass a generator around

```python
rng = random.Random(42)   # an independent generator with its own seed
rng.random()              # float in [0, 1)
rng.randint(1, 6)         # int, both ends inclusive
rng.choice(["Venice", "Genoa"])
rng.gauss(0, 1)           # normal draw
```

You *can* call `random.random()` directly, but that uses one hidden global generator that any code anywhere might consume. For research you want **reproducibility**: same seed → same numbers → same results in your paper. So: create one `random.Random(seed)` at the top and pass it into functions as `rng`. Tests do exactly this.

The Bernoulli trick: "happens with probability p" is `rng.random() < p`.

## Monte Carlo

Recipe:

1. Write a function that simulates **one** run (one season, one 50-turn campaign).
2. Call it N times.
3. Count how often the thing you care about happened, or summarise the distribution.

Error shrinks like 1/√N: 10,000 trials gives roughly ±0.5 percentage points on a probability. Good enough for intuition, and you'll see the real formulas (binomial) later — simulation is how you check them.

### The punchline

A genuinely better player — 55% true win rate — shows a **losing** record after 10 games about a quarter of the time, after 100 games still ~13% of the time, and you need around 300 games before that drops below 5%. Every "this faction is OP" forum thread built on 40 games is mostly noise. Same logic applies to a 2-point poll lead with a ±3 margin of error.

## Worked example

`example.py`:

1. Imports our own `sim_tools.py` (look at it — it's tiny, with a `__main__` guard).
2. Simulates 5000 seasons of a 55% player at 10, 30, 100, 300 and 1000 games, printing P(record < 50%) and the 5th–95th percentile band. Watch the band narrow.
3. Shows reproducibility: same seed, identical result.
4. Runs a treasury: +10 income per turn, 10% chance of a −120 revolt. The *expected* final balance is about zero, but the treasury dips below zero in most runs — averages hide risk. That gap between mean outcome and path risk is the whole reason to simulate.
5. Saves a histogram to `output/winrate_spread.png`.

## Exercises

In `exercises.py` (all randomness via a passed-in `rng` or a `seed`):

1. `play_games(n_games, p_win, rng)` — count wins.
2. `winrate_samples(n_games, p_win, n_trials, rng)` — list of observed win rates.
3. `prob_looks_losing(n_games, p_win, n_trials, seed)` — the headline number.
4. `games_needed(p_win, threshold, n_trials, seed, candidates)` — smallest sample size that makes a losing-looking record rare.
5. `simulate_treasury(start, income, turns, events, rng)` — treasury path with random events.
6. `bankruptcy_rate(...)` — fraction of runs that ever go negative.
7. `summarise(values)` — mean, min, max, 5th and 95th percentile.

Follow the docstrings exactly on *how many* `rng.random()` calls to make and in what order — some tests check your output against a reference with the same seed.

## How to check

Double-click `check.bat` in the course folder and type `13`.
