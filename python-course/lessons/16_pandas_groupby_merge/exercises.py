# Lesson 16 exercises: groupby, merge, pivot_table, melt.
# How to check: double-click check.bat in the course folder and type 16.
# Data lives in data/polls.csv and data/results.csv; tests pass paths/DataFrames in.
import pandas as pd


def load_polls(path):
    """Exercise 1. Read the polls CSV at `path` with the `date` column parsed
    as datetimes. Add a column `margin` = dem_share - rep_share. Return the DataFrame."""
    raise NotImplementedError("Exercise 1")


def polls_per_pollster(polls):
    """Exercise 2. Return a Series: number of polls (rows) per pollster,
    indexed by pollster name, sorted alphabetically by pollster."""
    raise NotImplementedError("Exercise 2")


def pollster_summary(polls):
    """Exercise 3. Return a DataFrame indexed by pollster with exactly these columns:
      n_polls       number of polls
      mean_dem      mean dem_share
      total_sample  sum of sample_size
    Hint: named aggregation, .agg(new_name=("column", "func"))."""
    raise NotImplementedError("Exercise 3")


def attach_results(polls, results):
    """Exercise 4. Left-merge `results` onto `polls` on election_year and state.
    Overlapping columns get suffixes "_poll" and "_result" (so: dem_share_poll,
    dem_share_result, rep_share_poll, rep_share_result).
    The result must have exactly as many rows as `polls`. If `results` contains
    a duplicated (election_year, state) pair, raise an error instead of silently
    duplicating polls (hint: merge's `validate=` argument raises pd.errors.MergeError)."""
    raise NotImplementedError("Exercise 4")


def polling_error_by_pollster(polls, results):
    """Exercise 5. For each poll, error = poll margin - actual margin, where
    margin = dem_share - rep_share. Return a Series of the MEAN error per pollster,
    sorted from most Democrat-leaning (largest) to most Republican-leaning."""
    raise NotImplementedError("Exercise 5")


def state_year_pivot(polls):
    """Exercise 6. Return a pivot table: rows = state, columns = election_year,
    values = mean dem_share across all polls in that state-year."""
    raise NotImplementedError("Exercise 6")


def long_shares(results):
    """Exercise 7. Reshape `results` from wide to long. Return a DataFrame with
    columns election_year, state, party, share where party is "dem" or "rep"
    (not "dem_share"). Sort by election_year, state, party and reset the index
    (0..n-1). It should have 2x as many rows as `results`."""
    raise NotImplementedError("Exercise 7")
