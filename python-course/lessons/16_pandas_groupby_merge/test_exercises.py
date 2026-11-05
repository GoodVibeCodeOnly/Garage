import pandas as pd
import pytest


@pytest.fixture
def polls(data_dir):
    df = pd.read_csv(data_dir / "polls.csv", parse_dates=["date"])
    return df


@pytest.fixture
def results(data_dir):
    return pd.read_csv(data_dir / "results.csv")


def test_load_polls_dates_and_margin(ex, data_dir):
    df = ex.load_polls(data_dir / "polls.csv")
    assert pd.api.types.is_datetime64_any_dtype(df["date"]), "date should be parsed as datetime"
    assert "margin" in df.columns
    assert df["margin"].iloc[0] == pytest.approx(df["dem_share"].iloc[0] - df["rep_share"].iloc[0])
    assert len(df) == 251


def test_polls_per_pollster(ex, polls):
    s = ex.polls_per_pollster(polls)
    assert list(s.index) == sorted(polls["pollster"].unique())
    assert s.sum() == len(polls)
    assert s["Acme Research"] == (polls["pollster"] == "Acme Research").sum()


def test_pollster_summary_columns(ex, polls):
    df = ex.pollster_summary(polls)
    assert list(df.columns) == ["n_polls", "mean_dem", "total_sample"]
    assert df.index.name == "pollster"


def test_pollster_summary_values(ex, polls):
    df = ex.pollster_summary(polls)
    sub = polls[polls["pollster"] == "Eagle Survey"]
    assert df.loc["Eagle Survey", "n_polls"] == len(sub)
    assert df.loc["Eagle Survey", "mean_dem"] == pytest.approx(sub["dem_share"].mean())
    assert df.loc["Eagle Survey", "total_sample"] == sub["sample_size"].sum()


def test_attach_results_shape_and_names(ex, polls, results):
    m = ex.attach_results(polls, results)
    assert len(m) == len(polls), "a left many-to-one merge must not change the row count"
    for col in ["dem_share_poll", "dem_share_result", "rep_share_poll", "rep_share_result"]:
        assert col in m.columns, f"missing column {col}"
    assert m["dem_share_result"].notna().all()


def test_attach_results_rejects_duplicate_keys(ex, polls, results):
    dup = pd.concat([results, results.iloc[[0]]], ignore_index=True)
    with pytest.raises(pd.errors.MergeError):
        ex.attach_results(polls, dup)


def test_polling_error_order(ex, polls, results):
    err = ex.polling_error_by_pollster(polls, results)
    assert list(err.index) == ["Delta Insights", "Acme Research", "Crossroads Data",
                               "Bluegrass Polling", "Eagle Survey"], \
        "pollsters should be ordered from most Dem-leaning to most Rep-leaning"
    assert err.is_monotonic_decreasing


def test_polling_error_values(ex, polls, results):
    err = ex.polling_error_by_pollster(polls, results)
    m = polls.merge(results, on=["election_year", "state"], suffixes=("_p", "_r"))
    e = (m.dem_share_p - m.rep_share_p) - (m.dem_share_r - m.rep_share_r)
    expected = e.groupby(m.pollster).mean()
    for p in expected.index:
        assert err[p] == pytest.approx(expected[p])


def test_state_year_pivot(ex, polls):
    pt = ex.state_year_pivot(polls)
    assert pt.shape == (8, 3)
    assert list(pt.columns) == [2012, 2016, 2020]
    sub = polls[(polls.state == "Ohio") & (polls.election_year == 2016)]
    assert pt.loc["Ohio", 2016] == pytest.approx(sub["dem_share"].mean())


def test_long_shares(ex, results):
    long = ex.long_shares(results)
    assert list(long.columns) == ["election_year", "state", "party", "share"]
    assert len(long) == 2 * len(results)
    assert set(long["party"]) == {"dem", "rep"}
    assert list(long.index) == list(range(len(long)))
    first = long.iloc[0]
    assert first["election_year"] == 2012 and first["state"] == "Arizona" and first["party"] == "dem"
    row = results[(results.election_year == 2012) & (results.state == "Arizona")].iloc[0]
    assert first["share"] == pytest.approx(row["dem_share"])
