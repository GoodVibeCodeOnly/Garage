# Lesson 25 — Capstone: Is the polling average biased across elections?
# How to check: double-click check.bat in the course folder and type 25.
# When everything passes, run:  python run_capstone.py   (from this folder)
#
# Conventions: margin = dem - rep in percentage points (positive = Democrat ahead).
# error = poll average margin - actual margin (positive = polls overstated D).
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def load_data(polls_path, results_path):
    """Exercise 1. Load and clean. Return (polls, results) DataFrames.

    polls (from polls_path; columns election, state, pollster, end_date,
    sample_size, dem, rep):
      - state: strip whitespace and upper-case (" pa" -> "PA")
      - drop rows with missing dem, rep or sample_size
      - then drop exact duplicate rows
      - sample_size as int; end_date as datetime (pd.to_datetime)
      - add column margin = dem - rep
      - reset the index (0..n-1)
    results (from results_path; columns election, state, election_date, dem, rep):
      - election_date as datetime
      - return ONLY columns [election, state, election_date, actual_margin]
        where actual_margin = dem - rep
    """
    raise NotImplementedError("Exercise 1")


def polling_averages(polls, results, window_days=21):
    """Exercise 2. Final polling average per race.

    For each poll, days_before = (election_date - end_date) in days (merge the
    election_date in from results on [election, state]). Keep polls with
    0 <= days_before <= window_days. For each (election, state) compute the
    sample-size-weighted mean margin: sum(margin * sample_size) / sum(sample_size).

    Return a DataFrame with columns [election, state, poll_avg, n_polls]
    (one row per race that has at least one poll in the window).
    """
    raise NotImplementedError("Exercise 2")


def race_errors(averages, results):
    """Exercise 3. Merge averages with results on [election, state] (inner join)
    and return columns [election, state, poll_avg, actual_margin, error],
    where error = poll_avg - actual_margin.
    """
    raise NotImplementedError("Exercise 3")


def election_bias(errors, level=0.95):
    """Exercise 4. Per-election mean error with a t-based CI over its states.

    Return a DataFrame INDEXED BY election (sorted ascending) with columns
    [mean_error, ci_low, ci_high, n_states]:
      mean_error = mean of error across that election's races
      se = sample sd (ddof=1) / sqrt(n_states)
      ci = mean_error ± t * se, t = stats.t.ppf(1 - (1 - level)/2, df=n_states - 1)
    """
    raise NotImplementedError("Exercise 4")


def bias_tests(errors):
    """Exercise 5. Is the average bias across elections different from 0?

    CLUSTERED (correct): collapse to one mean error per election, then a
    one-sample t-test of those means against 0 (stats.ttest_1samp).
    NAIVE (wrong, for contrast): t-test of ALL race errors against 0, as if
    every race were independent.

    Return a dict with floats (n_elections int):
      mean_bias    mean of the election means
      se           sd(election means, ddof=1) / sqrt(n_elections)
      t_stat, p_value   from the clustered t-test
      ci_low, ci_high   mean_bias ± t(0.975, n_elections-1) * se
      n_elections
      naive_se     sd(race errors, ddof=1) / sqrt(number of races)
      naive_p_value     p-value of the naive t-test
    """
    raise NotImplementedError("Exercise 5")


def bootstrap_bias(election_means, n_boot=5000, seed=0):
    """Exercise 6. Bootstrap over ELECTIONS. Do exactly this (so results match):

        values = np.asarray(election_means, dtype=float); n = len(values)
        rng = np.random.default_rng(seed)
        idx = rng.integers(0, n, size=(n_boot, n))
        boots = values[idx].mean(axis=1)

    Return {"mean": values.mean(), "ci_low": 2.5th percentile of boots,
            "ci_high": 97.5th percentile, "share_above_zero": fraction of boots > 0}
    (all floats; use np.percentile).
    """
    raise NotImplementedError("Exercise 6")


def plot_bias(bias_df, out_path):
    """Exercise 7. Plot per-election mean error with CI error bars.

    bias_df is the output of election_bias. Draw points at mean_error with
    asymmetric error bars to ci_low/ci_high (ax.errorbar with yerr of shape
    (2, n)), a horizontal line at 0, axis labels and a title. Create the parent
    folder if needed, save to out_path as PNG, close the figure, and return
    out_path as a pathlib.Path.
    """
    raise NotImplementedError("Exercise 7")


def report(polls_path, results_path, out_dir, window_days=21):
    """Exercise 8. Run the whole pipeline and return a dict:

      n_elections, n_races (ints), mean_bias, p_value, naive_p_value (floats),
      ci (tuple of the clustered t CI), bootstrap_ci (tuple, from bootstrap_bias
      on the election means with default n_boot/seed),
      most_biased_election (int: election with the largest ABSOLUTE mean error),
      plot_path (str: out_dir / "bias_by_election.png", created by plot_bias),
      summary (str: 2-4 sentences a reader of a research memo would want —
               the estimate, its uncertainty, and the naive-vs-clustered contrast).
    """
    raise NotImplementedError("Exercise 8")
