import math

import pandas as pd
import pytest


@pytest.fixture
def df(data_dir):
    # Loaded independently of Exercise 1, so one bug doesn't fail everything.
    return pd.read_csv(data_dir / "matches.csv", dtype={"patch": str})


# Exercise 1
def test_load_matches(ex, data_dir):
    out = ex.load_matches(data_dir / "matches.csv")
    assert isinstance(out, pd.DataFrame)
    assert out.shape == (2000, 8)
    assert list(out.columns) == ["match_id", "player", "faction", "opponent_faction",
                                 "map", "won", "duration_min", "patch"]
    assert set(out["patch"]) == {"1.2", "1.3", "1.4"}, "patch must be read as text"
    assert out["won"].dtype == bool


# Exercise 2
def test_faction_win_rates(ex, df):
    rates = ex.faction_win_rates(df)
    assert isinstance(rates, pd.Series)
    assert set(rates.index) == {"Venice", "Ottomans", "Byzantium", "Mongols", "Genoa"}
    for faction in rates.index:
        expected = df.loc[df["faction"] == faction, "won"].mean()
        assert rates[faction] == pytest.approx(expected), faction
    assert list(rates) == sorted(rates, reverse=True), "sort highest first"
    assert rates.index[0] == "Mongols"


# Exercise 3
def test_matchup_win_rate(ex, df):
    got = ex.matchup_win_rate(df, "Venice", "Ottomans")
    mask = (df["faction"] == "Venice") & (df["opponent_faction"] == "Ottomans")
    assert got == pytest.approx(df.loc[mask, "won"].mean())
    assert got > 0.55, "Venice should crush the Ottomans in this dataset"
    assert isinstance(got, float)


def test_matchup_win_rate_none(ex, df):
    assert math.isnan(ex.matchup_win_rate(df, "Venice", "Venice")), "no mirror matches -> nan"


# Exercise 4
def test_filter_matches(ex, df):
    assert len(ex.filter_matches(df)) == 2000
    bos = ex.filter_matches(df, map_name="Bosphorus")
    assert len(bos) == (df["map"] == "Bosphorus").sum()
    assert set(bos["map"]) == {"Bosphorus"}
    both = ex.filter_matches(df, map_name="Steppe", patch="1.3", min_duration=30)
    expected = df[(df["map"] == "Steppe") & (df["patch"] == "1.3") & (df["duration_min"] >= 30)]
    assert list(both.index) == list(expected.index), "keep the original index labels"


# Exercise 5
def test_add_columns(ex, df):
    before = df.copy()
    out = ex.add_columns(df)
    pd.testing.assert_frame_equal(df, before, obj="input DataFrame must not be modified")
    assert set(out["result"]) == {"W", "L"}
    assert (out.loc[out["won"], "result"] == "W").all()
    assert set(out["length"]) == {"short", "medium", "long"}
    assert (out.loc[out["duration_min"] < 20, "length"] == "short").all()
    assert (out.loc[out["duration_min"] >= 40, "length"] == "long").all()
    mid = (out["duration_min"] >= 20) & (out["duration_min"] < 40)
    assert (out.loc[mid, "length"] == "medium").all()


def test_add_columns_boundaries(ex):
    small = pd.DataFrame({"won": [True, False, True], "duration_min": [19.9, 20.0, 40.0]})
    out = ex.add_columns(small)
    assert list(out["length"]) == ["short", "medium", "long"]
    assert list(out["result"]) == ["W", "L", "W"]


# Exercise 6
def test_longest_games(ex, df):
    out = ex.longest_games(df, 3)
    assert list(out.columns) == ["match_id", "player", "faction", "duration_min"]
    assert list(out.index) == [0, 1, 2]
    expected = sorted(df["duration_min"], reverse=True)[:3]
    assert list(out["duration_min"]) == pytest.approx(expected)
    assert len(ex.longest_games(df)) == 5


# Exercise 7
def test_every_nth_id(ex, df):
    ids = ex.every_nth_id(df, 500)
    assert ids == [10000, 10500, 11000, 11500]
    shuffled = df.sample(frac=1, random_state=0)
    assert ex.every_nth_id(shuffled, 1000) == [shuffled["match_id"].iloc[0],
                                                shuffled["match_id"].iloc[1000]], \
        "use position (.iloc), not labels"


# Exercise 8
def test_lookup(ex, df):
    row = df[df["match_id"] == 10001].iloc[0]
    got = ex.lookup(df, 10001)
    assert got == {"player": row["player"], "faction": row["faction"], "won": bool(row["won"])}
    assert type(got["won"]) is bool


def test_lookup_missing(ex, df):
    with pytest.raises(KeyError):
        ex.lookup(df, 1)
