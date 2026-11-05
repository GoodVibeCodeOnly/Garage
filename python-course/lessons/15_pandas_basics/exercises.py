"""Lesson 15 exercises: pandas basics.

How to check: double-click `check.bat` in the course folder and type 15.
(Or from the course folder: python -m pytest lessons/15_pandas_basics)

Data: data/matches.csv - 2000 synthetic ranked matches with columns
match_id, player, faction, opponent_faction, map, won, duration_min, patch.
Except for Exercise 1, every function receives an already-loaded DataFrame.
No Python loops over rows - use column operations.
"""
import numpy as np
import pandas as pd


# Exercise 1
def load_matches(path):
    """Read the CSV at `path` into a DataFrame.

    Make sure `patch` is read as TEXT ("1.2", "1.3", "1.4"), not as a float:
    pass dtype={"patch": str} to pd.read_csv. (Why it matters: see README.)
    """
    raise NotImplementedError("Exercise 1")


# Exercise 2
def faction_win_rates(df):
    """Return a Series: index = faction, values = win rate (0..1) when playing
    that faction, sorted from highest to lowest.

    Without groupby (that's next lesson): count wins per faction with
    value_counts on the rows where won is True, divide by value_counts on
    all rows. pandas lines the two Series up by faction automatically.
    """
    raise NotImplementedError("Exercise 2")


# Exercise 3
def matchup_win_rate(df, faction, opponent):
    """Win rate (Python float) of `faction` in games against `opponent`.
    Return float("nan") if there are no such games.
    Combine two boolean conditions with & (and parentheses).
    """
    raise NotImplementedError("Exercise 3")


# Exercise 4
def filter_matches(df, map_name=None, patch=None, min_duration=None):
    """Return the rows matching every filter that is not None:
      map_name     -> df["map"] == map_name
      patch        -> df["patch"] == patch   (patch is a string like "1.3")
      min_duration -> df["duration_min"] >= min_duration
    With all filters None, return all rows. Keep the original index.
    """
    raise NotImplementedError("Exercise 4")


# Exercise 5
def add_columns(df):
    """Return a COPY of df (don't modify the input) with two new columns:
      "result": "W" where won is True, else "L"
      "length": "short" if duration_min < 20,
                "medium" if 20 <= duration_min < 40,
                "long" if duration_min >= 40
    Both columns should hold plain strings.
    Hint: np.where for result; np.select or pd.cut(..., right=False) for length.
    """
    raise NotImplementedError("Exercise 5")


# Exercise 6
def longest_games(df, n=5):
    """The n longest matches, longest first, with only the columns
    match_id, player, faction, duration_min (in that order), and a fresh
    0..n-1 index (reset_index(drop=True)).
    """
    raise NotImplementedError("Exercise 6")


# Exercise 7
def every_nth_id(df, n):
    """Return a list of the match_id of every n-th row BY POSITION, starting
    with the first row (positions 0, n, 2n, ...). Use .iloc.
    """
    raise NotImplementedError("Exercise 7")


# Exercise 8
def lookup(df, match_id):
    """Find the match with this match_id using .loc (hint: set_index first)
    and return {"player": ..., "faction": ..., "won": <Python bool>}.
    Let pandas raise KeyError if the id doesn't exist.
    """
    raise NotImplementedError("Exercise 8")
