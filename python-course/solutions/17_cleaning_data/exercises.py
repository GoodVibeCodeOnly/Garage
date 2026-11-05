"""Lesson 17 solutions: cleaning messy data."""
import pandas as pd

NATION_ALIASES = {"Gb": "Great Britain", "Britain": "Great Britain"}


def clean_nation(s):
    # Order matters: strip + normalise case FIRST, then map aliases, so the
    # alias table only needs one spelling per alias ("Gb", not "GB"/"gb"/" GB").
    s = s.str.strip().str.title()
    # .replace with a dict leaves unmatched values alone. (.map would turn
    # anything not in the dict into NaN -- a classic silent bug.)
    return s.replace(NATION_ALIASES)


def clean_good(s):
    return s.str.strip().str.lower()


def parse_number(s):
    # Work on strings: astype(str) is safe even if some values are already NaN
    # ("nan" just becomes unparseable -> NaN again).
    cleaned = (s.astype(str)
                .str.strip()
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False))
    # errors="coerce": anything unparseable ("N/A", "-", "") becomes NaN
    # instead of crashing. Then *count* the NaNs so you know what you lost.
    return pd.to_numeric(cleaned, errors="coerce").astype(float)


def parse_dates(s):
    # An explicit format is faster and refuses ambiguous guesses; coerce turns
    # "unknown" and "1836-13-45" into NaT (Not a Time, the datetime NaN).
    return pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")


def drop_duplicate_trades(df):
    return df.drop_duplicates(subset="trade_id", keep="first").reset_index(drop=True)


def iqr_outliers(s, k=1.5):
    # Quantile-based rule: robust because one 999999 barely moves Q1/Q3,
    # whereas it drags the mean and SD a long way (mean +/- 3 SD can miss it).
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    # NaN compares False on both sides, so missing values are never flagged.
    return (s < q1 - k * iqr) | (s > q3 + k * iqr)


def clean_trades(path):
    # dtype=str: read everything as text and decide types ourselves, instead
    # of letting pandas guess column by column.
    df = pd.read_csv(path, dtype=str)
    df = drop_duplicate_trades(df)
    df["trade_id"] = df["trade_id"].astype(int)
    df["date"] = parse_dates(df["date"])
    df["nation"] = clean_nation(df["nation"])
    df["good"] = clean_good(df["good"])
    df["quantity"] = parse_number(df["quantity"])
    df["price"] = parse_number(df["price"])
    df = df[df["quantity"].notna() & ~iqr_outliers(df["quantity"], k=3)]
    # .assign returns a new frame -- no SettingWithCopy worries on a filtered slice.
    df = df.assign(value=df["quantity"] * df["price"])
    return df.reset_index(drop=True)
