# Lesson 17 exercises: cleaning messy data.
# How to check: double-click check.bat in the course folder and type 17.
# Every function takes a pandas Series/DataFrame (or a path) and returns a NEW one.
import pandas as pd

# Aliases to apply AFTER stripping whitespace and title-casing.
NATION_ALIASES = {"Gb": "Great Britain", "Britain": "Great Britain"}


def clean_nation(s):
    """Exercise 1. Given a Series of messy nation names (" Prussia ", "prussia",
    "GB", " Britain"), return a Series with surrounding whitespace removed,
    Title Case ("Great Britain"), and NATION_ALIASES applied.
    Names that are not aliases must be left as they are (not turned into NaN)."""
    raise NotImplementedError("Exercise 1")


def clean_good(s):
    """Exercise 2. Return the Series stripped of whitespace and lower-cased
    (" IRON" -> "iron")."""
    raise NotImplementedError("Exercise 2")


def parse_number(s):
    """Exercise 3. Convert a Series of messy number strings to float64.
    "1,200" -> 1200.0, "$3.50" -> 3.5, " 42 " -> 42.0.
    Anything that isn't a number ("N/A", "-", "", NaN) -> NaN. Must not raise."""
    raise NotImplementedError("Exercise 3")


def parse_dates(s):
    """Exercise 4. Convert a Series of "YYYY-MM-DD" strings to datetimes.
    Invalid entries ("unknown", "", "1836-13-45") become NaT. Must not raise."""
    raise NotImplementedError("Exercise 4")


def drop_duplicate_trades(df):
    """Exercise 5. Drop rows whose trade_id has already appeared (keep the first
    occurrence). Return with a fresh 0..n-1 index."""
    raise NotImplementedError("Exercise 5")


def iqr_outliers(s, k=1.5):
    """Exercise 6. Return a boolean Series, True where a value is an outlier by
    the IQR rule: below Q1 - k*IQR or above Q3 + k*IQR, where Q1/Q3 are the
    25th/75th percentiles (Series.quantile) and IQR = Q3 - Q1.
    NaN values are NOT outliers (False)."""
    raise NotImplementedError("Exercise 6")


def clean_trades(path):
    """Exercise 7. The full pipeline. Read the CSV at `path` with every column
    as text (dtype=str), then:
      - drop duplicate trade_ids (exercise 5)
      - trade_id -> int; date -> datetime (ex 4); nation (ex 1); good (ex 2);
        quantity and price -> float (ex 3)
      - drop rows where quantity is missing OR is an outlier with k=3
        (compute the outlier flags after dropping duplicates)
      - add column value = quantity * price
    Return with columns trade_id, date, nation, good, quantity, price, value
    and a fresh 0..n-1 index. Rows with a missing date are kept."""
    raise NotImplementedError("Exercise 7")
