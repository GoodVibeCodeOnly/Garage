# 16 — pandas: groupby, merge, pivot, melt

Lesson 15 got you a DataFrame. This one is about the three moves you'll do constantly in research work: **split-apply-combine** (groupby), **joining tables** (merge), and **reshaping** (pivot/melt). The running question: *which pollsters lean which way, and by how much?*

## groupby: split, apply, combine

`df.groupby("pollster")` splits the rows into one bucket per pollster. Nothing happens until you apply something:

```python
polls.groupby("pollster").size()                  # rows per pollster
polls.groupby("pollster")["dem_share"].mean()     # one column, one stat -> Series
polls.groupby(["election_year", "state"])["dem_share"].mean()  # two keys -> MultiIndex
```

`.size()` counts rows. `.count()` counts non-missing values per column, which is a different thing once you have NaNs.

## Multiple aggregations: named agg

When you want several stats, use **named aggregation**: `new_col=(source_col, func)`:

```python
polls.groupby("pollster").agg(
    n_polls=("dem_share", "size"),
    mean_dem=("dem_share", "mean"),
    total_sample=("sample_size", "sum"),
)
```

You get a tidy DataFrame with flat column names you chose. The older `agg({"dem_share": ["mean", "std"]})` gives you MultiIndex columns. It works, but it's annoying to use.

## merge: SQL joins

```python
polls.merge(results, on=["election_year", "state"], how="left",
            suffixes=("_poll", "_result"))
```

- `how="inner"` keeps only keys present in both tables. `how="left"` keeps every row of the left table and fills NaN where there's no match.
- `suffixes` disambiguate columns that exist on both sides (`dem_share` in both here).

**The many-to-one pitfall.** Polls-to-results is many-to-one: many polls per (year, state), exactly one result. If the "one" side accidentally has a duplicate key (a data entry glitch, a bad concat), every matching poll gets **duplicated**. You get no error and no warning. Your row count just inflates, and any mean or sum afterwards is quietly wrong. Guard against it:

```python
polls.merge(results, on=[...], how="left", validate="many_to_one")
```

Now pandas raises `MergeError` if the right side's keys aren't unique. Make `len(before) == len(after)` a habit after a left merge. It's like checking that the books balance after a trade route update.

## pivot_table: two-key groupby, laid out as a grid

```python
polls.pivot_table(index="state", columns="election_year",
                  values="dem_share", aggfunc="mean")
```

That is `groupby(["state", "election_year"])["dem_share"].mean().unstack()` in one call. Use it when a human needs to read the result as a table.

## melt: wide to long

`results` has `dem_share` and `rep_share` as separate columns ("wide"). Plotting libraries and groupby often want one row per observation ("long"):

```python
results.melt(id_vars=["election_year", "state"],
             value_vars=["dem_share", "rep_share"],
             var_name="party", value_name="share")
```

`melt` and `pivot_table` are inverses, more or less.

## Worked example

`example.py` loads `data/polls.csv` (251 synthetic polls by 5 pollsters across 8 states and 3 elections) and `data/results.csv` (the "true" outcomes). `make_data.py` generated both, and it gave each pollster a hidden **house effect**, a consistent lean. The script:

1. Summarises each pollster with named aggregation.
2. Left-merges the true result onto every poll and checks the row count didn't change.
3. Shows the pitfall: one duplicated result row inflates the merge, and `validate="many_to_one"` catches it.
4. Computes **polling error on the margin**: (poll Dem − poll Rep) − (actual Dem − actual Rep). The per-pollster mean recovers the house effects. Delta leans about +3.5 toward the Democrats and Eagle about −3. Open `make_data.py` and compare.
5. Pivots error by pollster × year.
6. Melts results to long form.

Run it with `python example.py`.

## Exercises

In `exercises.py`:

1. `load_polls(path)`: read with parsed dates and add a `margin` column.
2. `polls_per_pollster(polls)`: count rows per pollster.
3. `pollster_summary(polls)`: named aggregation into `n_polls`, `mean_dem`, `total_sample`.
4. `attach_results(polls, results)`: a left merge with suffixes that refuses duplicate keys.
5. `polling_error_by_pollster(polls, results)`: mean margin error per pollster, sorted.
6. `state_year_pivot(polls)`: state × year table of mean Dem share.
7. `long_shares(results)`: melt to long form with tidy party labels.

## How to check

Double-click `check.bat` in the course folder and type `16`.
