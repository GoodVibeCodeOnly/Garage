"""Lesson 16 solutions: groupby, merge, pivot_table, melt."""
import pandas as pd


def load_polls(path):
    # parse_dates turns the text column into datetime64 so .dt works later.
    df = pd.read_csv(path, parse_dates=["date"])
    # Vectorised column arithmetic: one line, no loop.
    df["margin"] = df["dem_share"] - df["rep_share"]
    return df


def polls_per_pollster(polls):
    # .size() counts rows per group (including NaNs); .count() would count
    # non-missing values per column instead. groupby sorts keys by default.
    return polls.groupby("pollster").size()


def pollster_summary(polls):
    # Named aggregation: new_column=(source_column, function). Much clearer
    # than the old dict-of-lists form, and you get flat column names.
    return polls.groupby("pollster").agg(
        n_polls=("dem_share", "size"),
        mean_dem=("dem_share", "mean"),
        total_sample=("sample_size", "sum"),
    )


def attach_results(polls, results):
    # validate="many_to_one" makes pandas *check* that each (year, state)
    # appears at most once in results. Without it a duplicated result row
    # silently doubles every matching poll -- the classic merge pitfall.
    return polls.merge(
        results,
        on=["election_year", "state"],
        how="left",
        suffixes=("_poll", "_result"),
        validate="many_to_one",
    )


def polling_error_by_pollster(polls, results):
    merged = attach_results(polls, results)
    poll_margin = merged["dem_share_poll"] - merged["rep_share_poll"]
    true_margin = merged["dem_share_result"] - merged["rep_share_result"]
    merged["error"] = poll_margin - true_margin
    # Positive = leans Democrat. This is the pollster's "house effect".
    return merged.groupby("pollster")["error"].mean().sort_values(ascending=False)


def state_year_pivot(polls):
    # pivot_table = groupby on two keys + unstack, in one call.
    # Equivalent: polls.groupby(["state", "election_year"])["dem_share"].mean().unstack()
    return polls.pivot_table(index="state", columns="election_year",
                             values="dem_share", aggfunc="mean")


def long_shares(results):
    long = results.melt(
        id_vars=["election_year", "state"],
        value_vars=["dem_share", "rep_share"],
        var_name="party",
        value_name="share",
    )
    # "dem_share" -> "dem". .str methods work on whole columns at once.
    long["party"] = long["party"].str.replace("_share", "", regex=False)
    return long.sort_values(["election_year", "state", "party"]).reset_index(drop=True)
