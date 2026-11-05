"""Worked example: cleaning an 1836 trade log, step by step. Run: python example.py"""
import pathlib

import pandas as pd

DATA = pathlib.Path(__file__).parent / "data"

# Read everything as text: we decide the types, not pandas.
raw = pd.read_csv(DATA / "trades_messy.csv", dtype=str)
print(f"raw rows: {len(raw)}")
print("raw nation spellings:", raw["nation"].nunique())
print("sample quantities:", raw["quantity"].head(8).tolist(), "\n")

df = raw.copy()
df["trade_id"] = df["trade_id"].astype(int)

# 1. Duplicates: the same trade_id logged twice.
print(f"duplicate trade_ids: {df.duplicated(subset='trade_id').sum()}")
df = df.drop_duplicates(subset="trade_id").reset_index(drop=True)

# 2. Inconsistent categories: strip -> title-case -> aliases.
df["nation"] = (df["nation"].str.strip().str.title()
                .replace({"Gb": "Great Britain", "Britain": "Great Britain"}))
df["good"] = df["good"].str.strip().str.lower()
print("clean nations:", sorted(df["nation"].unique()))

# 3. Numbers stored as text with junk in them.
for col in ["quantity", "price"]:
    cleaned = df[col].astype(str).str.replace(",", "").str.replace("$", "", regex=False)
    df[col] = pd.to_numeric(cleaned, errors="coerce")
print(f"quantities that failed to parse (N/A, -, blank): {df['quantity'].isna().sum()}")

# 4. Dates: invalid -> NaT.
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
print(f"unparseable dates: {df['date'].isna().sum()}")

# 5. Outliers: mean/SD vs IQR.
q = df["quantity"]
print(f"\nquantity mean {q.mean():.0f}, median {q.median():.0f}  <- the mean is wrecked")
q1, q3 = q.quantile([0.25, 0.75])
fence = q3 + 3 * (q3 - q1)
print(f"IQR upper fence (k=3): {fence:.0f}; flagged values: {sorted(q[q > fence].unique().tolist())}")
df = df[q.notna() & (q <= fence)].reset_index(drop=True)

# 6. Now the data can answer questions.
df["value"] = df["quantity"] * df["price"]
print(f"\nclean rows: {len(df)}")
print(df.dtypes.to_string(), "\n")
print("Trade value by nation (thalers):")
print(df.groupby("nation")["value"].sum().sort_values(ascending=False).round(0).to_string())
