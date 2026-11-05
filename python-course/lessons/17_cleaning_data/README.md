# 17 — Cleaning messy data

Real datasets come in the state your 1836 trade clerk left them. " Prussia ", "prussia" and "PRUSSIA" are three nations as far as groupby can tell. "1,200" is a string, so the column won't sum. "N/A" means missing, but only if you tell pandas so. Cleaning is usually most of the work in a research project, and it's where silent errors creep in. The rule for this lesson: **every transformation should be something you can count.** Check how many rows changed and how many NaNs appeared.

## Missing values

pandas uses `NaN` for missing numbers and `NaT` for missing datetimes. `read_csv` already treats `""`, `"NA"`, `"N/A"` and `"null"` as missing. It does not treat `"-"` or `"unknown"` that way.

```python
df.isna().sum()          # missing per column: the first thing to run on any dataset
df.dropna(subset=["quantity"])
df["quantity"].fillna(0) # only if 0 really means zero, which it usually doesn't
```

## Dtypes: read as text, convert deliberately

`pd.read_csv(path, dtype=str)` stops pandas from guessing types. Then convert one column at a time:

```python
pd.to_numeric(s, errors="coerce")                        # junk -> NaN instead of crashing
pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")    # junk -> NaT
```

`errors="coerce"` is powerful and dangerous. It never complains, so always count the NaNs it created.

## String cleanup with `.str`

Every Python string method has a vectorised twin under `.str`:

```python
s.str.strip().str.title()                  # " prussia " -> "Prussia"
s.str.replace(",", "", regex=False)        # "1,200" -> "1200"
s.str.contains("Brit")                     # boolean mask
```

Pass `regex=False` when you mean a literal character. `"$"` is a regex anchor, so `str.replace("$", "")` without it does nothing useful.

## Inconsistent categories

Normalise first (strip and case), then map the remaining aliases:

```python
s.str.strip().str.title().replace({"Gb": "Great Britain", "Britain": "Great Britain"})
```

Use `.replace(dict)`, not `.map(dict)`. `.map` turns everything not in the dict into NaN. Check the result with `s.value_counts()` and eyeball the list.

## Duplicates

```python
df.duplicated(subset="trade_id").sum()   # count first
df.drop_duplicates(subset="trade_id", keep="first")
```

Decide what makes a row "the same". A whole-row match is different from a matching ID with different contents, which is a conflict you need to investigate.

## Outliers

One fat-fingered `999999` can drag a mean far from the typical value. The **IQR rule** is robust because quartiles barely move when you add one extreme value:

```python
q1, q3 = s.quantile([0.25, 0.75])
iqr = q3 - q1
outlier = (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
```

A mean ± 3 SD rule is weaker here, because the outlier inflates the SD it's being measured against. Flag first, look at the flagged values, then decide. A real 999,999-unit grain shipment is data, not an error.

## Worked example

`make_data.py` wrote `data/trades_messy.csv`: 312 rows with whitespace and case chaos in nation and good names, "GB"/"Britain" aliases, quantities like `"1,486"`, `"N/A"`, `"-"` and blanks, prices like `"$8.32"`, dates like `"unknown"` and `"1836-13-45"`, 12 duplicated trades and a few `999999` typos. `example.py` fixes each problem in turn and prints a count after every step. Watch the mean against the median before the outliers go. At the end, `groupby` produces a trade-value table you could actually trust.

## Exercises

In `exercises.py`:

1. `clean_nation(s)`: strip, title-case and apply aliases.
2. `clean_good(s)`: strip and lower-case.
3. `parse_number(s)`: messy strings to floats, with junk becoming NaN.
4. `parse_dates(s)`: strings to datetimes, with junk becoming NaT.
5. `drop_duplicate_trades(df)`: keep the first copy of each trade_id.
6. `iqr_outliers(s, k=1.5)`: a boolean outlier mask.
7. `clean_trades(path)`: the whole pipeline, from raw file to analysis-ready table.

## How to check

Double-click `check.bat` in the course folder and type `17`.
