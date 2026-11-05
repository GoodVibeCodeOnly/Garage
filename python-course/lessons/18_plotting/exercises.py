# Lesson 18 exercises: plotting with matplotlib.
# How to check: double-click check.bat in the course folder and type 18.
# Use the object-oriented style: fig, ax = plt.subplots(); ax.plot(...).
# Never call plt.show(). Each plotting function takes an optional `ax`:
# if ax is None, create a new figure with plt.subplots(); otherwise draw on
# the given ax (its figure is ax.figure). Return (fig, ax) unless stated otherwise.
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_treasury(years, treasuries, ax=None):
    """Exercise 1. `treasuries` is a dict {nation: list of balances}, one per year.
    Draw one line per nation (in dict order) with label=nation.
    Title "Treasury over time", x label "Year", y label "Ducats", and a legend."""
    raise NotImplementedError("Exercise 1")


def win_rate_bars(factions, wins, games, ax=None):
    """Exercise 2. Bar chart of win rate p = wins/games per faction (bars in the
    order given), with error bars of one standard error, sqrt(p*(1-p)/games)
    (hint: ax.bar(..., yerr=se)). Add a horizontal dashed line at 0.5 (ax.axhline).
    Title "Win rate by faction", y label "Win rate", y limits 0 to 1."""
    raise NotImplementedError("Exercise 2")


def error_histogram(errors, bins=20, ax=None):
    """Exercise 3. Histogram of `errors` with `bins` bins, plus a vertical line
    at 0 (ax.axvline). Title "Polling error", x label "Polling error (points)",
    y label "Number of polls"."""
    raise NotImplementedError("Exercise 3")


def scatter_sample_vs_error(sample_sizes, abs_errors, ax=None):
    """Exercise 4. Scatter plot, sample size on x, absolute error on y.
    x label "Sample size", y label "Absolute error (points)", any non-empty title."""
    raise NotImplementedError("Exercise 4")


def dashboard(years, treasuries, factions, wins, games, errors):
    """Exercise 5. One figure with three panels side by side (1 row, 3 columns):
    treasury lines, win-rate bars, error histogram, in that order. Reuse your
    functions from exercises 1-3 by passing each its ax. Return the FIGURE only."""
    raise NotImplementedError("Exercise 5")


def save_figure(fig, path, dpi=100):
    """Exercise 6. Save `fig` to `path` (a PNG) at the given dpi, close the figure,
    and return `path`."""
    raise NotImplementedError("Exercise 6")
