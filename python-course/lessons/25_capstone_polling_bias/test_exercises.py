import pathlib

import numpy as np
import pandas as pd
import pytest
from scipy import stats

POLLS_CSV = """election,state,pollster,end_date,sample_size,dem,rep
2020,PA,A,2020-10-30,1000,50,45
2020, pa ,B,2020-10-25,500,48,46
2020,PA,C,2020-08-01,800,55,40
2020,PA,D,2020-10-31,,51,44
2020,MI,A,2020-11-01,400,47,47
2020,MI,A,2020-11-01,400,47,47
2020,mi,B,2020-10-20,600,,45
2016,PA,A,2016-11-05,1000,49,46
"""
RESULTS_CSV = """election,state,election_date,dem,rep
2020,PA,2020-11-03,50,49
2020,MI,2020-11-03,50,48
2016,PA,2016-11-08,47.5,48.2
2016,MI,2016-11-08,47.3,47.5
"""


@pytest.fixture
def small(tmp_path):
    p, r = tmp_path / "polls.csv", tmp_path / "results.csv"
    p.write_text(POLLS_CSV)
    r.write_text(RESULTS_CSV)
    return p, r


def load_real(ex, data_dir):
    # A plain helper, not a fixture, so an unfinished load_data shows as a FAIL.
    return ex.load_data(data_dir / "polls.csv", data_dir / "results.csv")


def make_errors():
    rng = np.random.default_rng(1)
    rows = []
    for e, b in zip(range(2000, 2024, 4), [2.0, -1.0, 3.0, 0.5, 1.5, 2.5]):
        for s in "ABCDEFGH":
            rows.append((e, s, b + rng.normal(0, 1.5)))
    return pd.DataFrame(rows, columns=["election", "state", "error"])


# ---- 1 load_data -----------------------------------------------------------

def test_load_data_cleaning(ex, small):
    polls, results = ex.load_data(*small)
    assert len(polls) == 5, "drop missing sample_size, missing dem, and the duplicate"
    assert set(polls["state"]) == {"PA", "MI"}
    assert list(polls.index) == list(range(len(polls)))
    assert pd.api.types.is_integer_dtype(polls["sample_size"])
    assert pd.api.types.is_datetime64_any_dtype(polls["end_date"])
    assert (polls["margin"] == polls["dem"] - polls["rep"]).all()


def test_load_data_results(ex, small):
    _, results = ex.load_data(*small)
    assert list(results.columns) == ["election", "state", "election_date", "actual_margin"]
    assert pd.api.types.is_datetime64_any_dtype(results["election_date"])
    pa20 = results[(results.election == 2020) & (results.state == "PA")]
    assert pa20["actual_margin"].iloc[0] == pytest.approx(1.0)


def test_load_data_real(ex, data_dir):
    polls, results = load_real(ex, data_dir)
    assert polls["state"].str.match(r"^[A-Z]{2}$").all()
    assert not polls.duplicated().any()
    assert polls[["dem", "rep", "sample_size"]].notna().all().all()
    assert len(results) == 120


# ---- 2 polling_averages ----------------------------------------------------

def test_polling_averages_small(ex, small):
    polls, results = ex.load_data(*small)
    avg = ex.polling_averages(polls, results, window_days=21)
    assert set(avg.columns) >= {"election", "state", "poll_avg", "n_polls"}
    pa = avg[(avg.election == 2020) & (avg.state == "PA")].iloc[0]
    # Aug poll is outside the window; weighted (5*1000 + 2*500) / 1500 = 4.0
    assert pa["poll_avg"] == pytest.approx(4.0)
    assert pa["n_polls"] == 2
    mi = avg[(avg.election == 2020) & (avg.state == "MI")].iloc[0]
    assert mi["poll_avg"] == pytest.approx(0.0)
    assert len(avg) == 3, "2016 MI has no polls -> no row"


def test_polling_averages_window(ex, small):
    polls, results = ex.load_data(*small)
    avg = ex.polling_averages(polls, results, window_days=100)
    pa = avg[(avg.election == 2020) & (avg.state == "PA")].iloc[0]
    assert pa["n_polls"] == 3
    assert pa["poll_avg"] == pytest.approx((5 * 1000 + 2 * 500 + 15 * 800) / 2300)


def test_polling_averages_real(ex, data_dir):
    polls, results = load_real(ex, data_dir)
    avg = ex.polling_averages(polls, results)
    assert 100 <= len(avg) <= 120
    assert (avg["n_polls"] >= 1).all()


# ---- 3 race_errors ---------------------------------------------------------

def test_race_errors(ex, small):
    polls, results = ex.load_data(*small)
    errs = ex.race_errors(ex.polling_averages(polls, results), results)
    assert list(errs.columns) == ["election", "state", "poll_avg", "actual_margin", "error"]
    pa = errs[(errs.election == 2020) & (errs.state == "PA")].iloc[0]
    assert pa["error"] == pytest.approx(3.0)
    assert len(errs) == 3


# ---- 4 election_bias -------------------------------------------------------

def test_election_bias(ex):
    errs = make_errors()
    eb = ex.election_bias(errs)
    assert list(eb.index) == sorted(errs.election.unique())
    sub = errs[errs.election == 2004]["error"]
    m, se = sub.mean(), sub.std(ddof=1) / np.sqrt(len(sub))
    t = stats.t.ppf(0.975, len(sub) - 1)
    assert eb.loc[2004, "mean_error"] == pytest.approx(m)
    assert eb.loc[2004, "ci_low"] == pytest.approx(m - t * se)
    assert eb.loc[2004, "ci_high"] == pytest.approx(m + t * se)
    assert eb.loc[2004, "n_states"] == 8


def test_election_bias_level(ex):
    eb90 = ex.election_bias(make_errors(), level=0.90)
    eb95 = ex.election_bias(make_errors())
    assert ((eb90.ci_high - eb90.ci_low) < (eb95.ci_high - eb95.ci_low)).all()


# ---- 5 bias_tests ----------------------------------------------------------

def test_bias_tests(ex):
    errs = make_errors()
    res = ex.bias_tests(errs)
    means = errs.groupby("election")["error"].mean()
    tt = stats.ttest_1samp(means, 0)
    assert res["n_elections"] == 6
    assert res["mean_bias"] == pytest.approx(means.mean())
    assert res["se"] == pytest.approx(means.std(ddof=1) / np.sqrt(6))
    assert res["t_stat"] == pytest.approx(tt.statistic)
    assert res["p_value"] == pytest.approx(tt.pvalue)
    t = stats.t.ppf(0.975, 5)
    assert res["ci_low"] == pytest.approx(means.mean() - t * res["se"])
    assert res["ci_high"] == pytest.approx(means.mean() + t * res["se"])
    assert res["naive_p_value"] == pytest.approx(stats.ttest_1samp(errs["error"], 0).pvalue)
    assert res["naive_se"] == pytest.approx(errs["error"].std(ddof=1) / np.sqrt(len(errs)))


def test_naive_is_overconfident_on_real_data(ex, data_dir):
    polls, results = load_real(ex, data_dir)
    errs = ex.race_errors(ex.polling_averages(polls, results), results)
    res = ex.bias_tests(errs)
    assert res["naive_se"] < res["se"], "pooling correlated races understates uncertainty"
    assert res["naive_p_value"] < res["p_value"]


# ---- 6 bootstrap -----------------------------------------------------------

def test_bootstrap_bias_exact(ex):
    vals = [2.0, -1.0, 3.0, 0.5, 1.5, 2.5]
    res = ex.bootstrap_bias(vals, n_boot=2000, seed=7)
    rng = np.random.default_rng(7)
    boots = np.array(vals)[rng.integers(0, 6, size=(2000, 6))].mean(axis=1)
    assert res["mean"] == pytest.approx(np.mean(vals))
    assert res["ci_low"] == pytest.approx(np.percentile(boots, 2.5))
    assert res["ci_high"] == pytest.approx(np.percentile(boots, 97.5))
    assert res["share_above_zero"] == pytest.approx((boots > 0).mean())


def test_bootstrap_constant(ex):
    res = ex.bootstrap_bias([1.0] * 5, n_boot=100)
    assert res["ci_low"] == pytest.approx(1.0) and res["ci_high"] == pytest.approx(1.0)


# ---- 7 plot ----------------------------------------------------------------

def test_plot_bias(ex, tmp_path):
    eb = ex.election_bias(make_errors())
    out = ex.plot_bias(eb, tmp_path / "sub" / "plot.png")
    assert isinstance(out, pathlib.Path)
    assert out.exists() and out.stat().st_size > 1000
    assert out.read_bytes()[:4] == b"\x89PNG"


# ---- 8 report --------------------------------------------------------------

def test_report(ex, data_dir, tmp_path):
    rep = ex.report(data_dir / "polls.csv", data_dir / "results.csv", tmp_path)
    for key in ["n_elections", "n_races", "mean_bias", "ci", "p_value", "bootstrap_ci",
                "naive_p_value", "most_biased_election", "plot_path", "summary"]:
        assert key in rep, f"missing key {key}"
    assert rep["n_elections"] == 12
    assert 100 <= rep["n_races"] <= 120
    assert rep["ci"][0] < rep["mean_bias"] < rep["ci"][1]
    assert rep["bootstrap_ci"][0] < rep["mean_bias"] < rep["bootstrap_ci"][1]
    assert 0 <= rep["p_value"] <= 1
    assert pathlib.Path(rep["plot_path"]) == tmp_path / "bias_by_election.png"
    assert pathlib.Path(rep["plot_path"]).exists()
    assert isinstance(rep["summary"], str) and len(rep["summary"]) > 80


def test_report_most_biased(ex, data_dir, tmp_path):
    rep = ex.report(data_dir / "polls.csv", data_dir / "results.csv", tmp_path)
    polls, results = ex.load_data(data_dir / "polls.csv", data_dir / "results.csv")
    eb = ex.election_bias(ex.race_errors(ex.polling_averages(polls, results), results))
    assert rep["most_biased_election"] == eb["mean_error"].abs().idxmax()
