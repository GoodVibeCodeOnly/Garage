"""Lesson 15 solutions: pandas basics."""
import numpy as np
import pandas as pd


# Exercise 1
def load_matches(path):
    # Without dtype, "1.2" / "1.3" / "1.4" become floats - and "1.10" would
    # silently turn into 1.1. Version numbers are labels, not quantities.
    return pd.read_csv(path, dtype={"patch": str})


# Exercise 2
def faction_win_rates(df):
    # wins per faction / games per faction; pandas aligns on the index.
    wins = df.loc[df["won"], "faction"].value_counts()
    games = df["faction"].value_counts()
    return (wins / games).sort_values(ascending=False)
    # Next lesson's shortcut: df.groupby("faction")["won"].mean()


# Exercise 3
def matchup_win_rate(df, faction, opponent):
    mask = (df["faction"] == faction) & (df["opponent_faction"] == opponent)
    games = df.loc[mask, "won"]
    if games.empty:
        return float("nan")
    return float(games.mean())


# Exercise 4
def filter_matches(df, map_name=None, patch=None, min_duration=None):
    mask = pd.Series(True, index=df.index)
    if map_name is not None:
        mask &= df["map"] == map_name
    if patch is not None:
        mask &= df["patch"] == patch
    if min_duration is not None:
        mask &= df["duration_min"] >= min_duration
    return df[mask]


# Exercise 5
def add_columns(df):
    out = df.copy()  # never mutate the caller's DataFrame by surprise
    out["result"] = np.where(out["won"], "W", "L")
    out["length"] = pd.cut(out["duration_min"], bins=[-np.inf, 20, 40, np.inf],
                           labels=["short", "medium", "long"], right=False).astype(str)
    return out


# Exercise 6
def longest_games(df, n=5):
    cols = ["match_id", "player", "faction", "duration_min"]
    return (df.sort_values("duration_min", ascending=False)
              .head(n)[cols]
              .reset_index(drop=True))
    # Alternative: df.nlargest(n, "duration_min")[cols]


# Exercise 7
def every_nth_id(df, n):
    # .iloc is position-based, so slicing works exactly like a list.
    return df.iloc[::n]["match_id"].tolist()


# Exercise 8
def lookup(df, match_id):
    # .loc selects by LABEL (here the match_id index), .iloc by POSITION.
    row = df.set_index("match_id").loc[match_id]
    return {"player": row["player"], "faction": row["faction"], "won": bool(row["won"])}
