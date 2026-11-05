import math

import numpy as np
import pandas as pd
import pytest


def test_clean_nation_basic(ex):
    s = pd.Series([" Prussia ", "prussia", "PRUSSIA", "Prussia  "])
    assert list(ex.clean_nation(s)) == ["Prussia"] * 4


def test_clean_nation_aliases(ex):
    s = pd.Series(["GB", " Britain", "great britain", "france ", "Atlantis"])
    out = list(ex.clean_nation(s))
    assert out == ["Great Britain", "Great Britain", "Great Britain", "France", "Atlantis"], \
        "aliases should map, and unknown names must survive unchanged"


def test_clean_good(ex):
    assert list(ex.clean_good(pd.Series([" IRON", "coal ", "Wine"]))) == ["iron", "coal", "wine"]


def test_parse_number_formats(ex):
    out = ex.parse_number(pd.Series(["1,200", "$3.50", " 42 ", "7"]))
    assert list(out) == [1200.0, 3.5, 42.0, 7.0]
    assert out.dtype == np.float64


def test_parse_number_missing(ex):
    out = ex.parse_number(pd.Series(["N/A", "-", "", None, "12"], dtype=object))
    assert out.isna().tolist() == [True, True, True, True, False]
    assert out.iloc[4] == 12.0


def test_parse_dates(ex):
    out = ex.parse_dates(pd.Series(["1836-03-01", "unknown", "1836-13-45", ""]))
    assert pd.api.types.is_datetime64_any_dtype(out)
    assert out.iloc[0] == pd.Timestamp("1836-03-01")
    assert out.iloc[1:].isna().all()


def test_drop_duplicate_trades(ex):
    df = pd.DataFrame({"trade_id": [1, 1, 2, 3, 3], "x": ["a", "b", "c", "d", "e"]})
    out = ex.drop_duplicate_trades(df)
    assert list(out["trade_id"]) == [1, 2, 3]
    assert list(out["x"]) == ["a", "c", "d"], "keep the FIRST occurrence"
    assert list(out.index) == [0, 1, 2]


def test_iqr_outliers(ex):
    s = pd.Series([10, 11, 12, 13, 14, 15, 16, 100, -50, np.nan], dtype=float)
    flags = ex.iqr_outliers(s)
    assert flags.dtype == bool
    assert flags.tolist() == [False] * 7 + [True, True, False]


def test_iqr_outliers_k(ex):
    s = pd.Series([0.0, 1, 2, 3, 4, 5, 6, 7, 8, 20])
    # Q1=2.25, Q3=6.75, IQR=4.5 -> k=1.5 upper fence 13.5, k=3 fence 20.25
    assert ex.iqr_outliers(s, k=1.5).iloc[-1]
    assert not ex.iqr_outliers(s, k=3).iloc[-1]


def test_clean_trades_shape(ex, data_dir):
    df = ex.clean_trades(data_dir / "trades_messy.csv")
    assert list(df.columns) == ["trade_id", "date", "nation", "good", "quantity", "price", "value"]
    assert len(df) == 274, f"expected 274 clean rows (312 - 12 dupes - 20 missing qty - 6 outliers), got {len(df)}"
    assert df["trade_id"].is_unique
    assert list(df.index) == list(range(len(df)))


def test_clean_trades_values(ex, data_dir):
    df = ex.clean_trades(data_dir / "trades_messy.csv")
    assert sorted(df["nation"].unique()) == ["Austria", "France", "Great Britain", "Prussia", "Russia"]
    assert sorted(df["good"].unique()) == ["cloth", "coal", "grain", "iron", "wine"]
    assert df["quantity"].max() < 5000, "the 999999 typos should have been dropped"
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df["date"].isna().sum() == 9, "bad dates become NaT but the rows are kept"
    assert df["value"].sum() == pytest.approx(2874509.44, rel=1e-6)
