"""Worked example: first look at 2000 ranked matches with pandas.

Run: python example.py
"""
from pathlib import Path

import pandas as pd

pd.set_option("display.width", 100)
df = pd.read_csv(Path(__file__).parent / "data" / "matches.csv", dtype={"patch": str})

print("=== head() ===")
print(df.head(), "\n")

print("=== info() ===")
df.info()

print("\n=== describe() (numeric columns) ===")
print(df.describe().round(2), "\n")

# Selecting: one column -> Series, list of columns -> DataFrame
print("factions played:\n", df["faction"].value_counts(), "\n")

# Boolean filtering: Mongols on patch 1.3 vs 1.4
mongols = df[df["faction"] == "Mongols"]
for patch in ["1.3", "1.4"]:
    sub = mongols[mongols["patch"] == patch]
    print(f"Mongols on {patch}: {sub['won'].mean():.1%} over {len(sub)} games")

# Combining conditions: Byzantium on Bosphorus vs everywhere else
byz = df["faction"] == "Byzantium"
bos = df["map"] == "Bosphorus"
print(f"Byzantium on Bosphorus: {df.loc[byz & bos, 'won'].mean():.1%}  "
      f"elsewhere: {df.loc[byz & ~bos, 'won'].mean():.1%}")

# New column + value_counts
df["length"] = pd.cut(df["duration_min"], [0, 20, 40, 1000], right=False,
                      labels=["short", "medium", "long"])
print("\ngame length mix (share):")
print(df["length"].value_counts(normalize=True).round(3))

# Sorting and .loc / .iloc
print("\n3 longest games:")
print(df.sort_values("duration_min", ascending=False)
        .loc[:, ["match_id", "player", "faction", "opponent_faction", "duration_min"]]
        .head(3))
# After sorting, position and label diverge - the classic .loc/.iloc trap.
by_len = df.sort_values("duration_min", ascending=False)
print("\nsorted by length: .iloc[0] (first POSITION) -> match", by_len.iloc[0]["match_id"],
      "| .loc[0] (index LABEL 0) -> match", by_len.loc[0, "match_id"])
