"""Worked example: which pollster leans which way? Run: python example.py"""
import pathlib

import pandas as pd

DATA = pathlib.Path(__file__).parent / "data"
polls = pd.read_csv(DATA / "polls.csv", parse_dates=["date"])
results = pd.read_csv(DATA / "results.csv")
print(f"{len(polls)} polls, {len(results)} actual results\n")

# 1. groupby + several aggregations at once (named aggregation)
summary = polls.groupby("pollster").agg(
    n=("dem_share", "size"),
    avg_n=("sample_size", "mean"),
    avg_dem=("dem_share", "mean"),
)
print("Per pollster:\n", summary.round(1), "\n")

# 2. merge: attach the true result to every poll (many polls -> one result)
merged = polls.merge(results, on=["election_year", "state"], how="left",
                     suffixes=("_poll", "_result"), validate="many_to_one")
print(f"rows before merge {len(polls)}, after {len(merged)} (should match)\n")

# 3. the pitfall: a duplicated key on the 'one' side silently multiplies rows
bad_results = pd.concat([results, results.iloc[[0]]])
bad = polls.merge(bad_results, on=["election_year", "state"], how="left")
print(f"with one duplicated result row: {len(bad)} rows -- polls got double-counted")
try:
    polls.merge(bad_results, on=["election_year", "state"], validate="many_to_one")
except pd.errors.MergeError as e:
    print(f"validate= catches it: {e}\n")

# 4. polling error per pollster = house effect
merged["error"] = ((merged.dem_share_poll - merged.rep_share_poll)
                   - (merged.dem_share_result - merged.rep_share_result))
house = merged.groupby("pollster")["error"].agg(["mean", "std", "size"])
print("Polling error on the margin (positive = leans Dem):\n",
      house.sort_values("mean", ascending=False).round(2), "\n")

# 5. pivot_table: mean error, pollster x year
print(merged.pivot_table(index="pollster", columns="election_year",
                         values="error", aggfunc="mean").round(1), "\n")

# 6. melt: wide -> long
long = results.melt(id_vars=["election_year", "state"],
                    value_vars=["dem_share", "rep_share"],
                    var_name="party", value_name="share")
print(long.head(4))
