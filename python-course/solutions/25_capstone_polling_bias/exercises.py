# Lesson 25 — Capstone solutions: is the polling average biased?
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def load_data(polls_path, results_path):
    polls = pd.read_csv(polls_path)
    # Clean the join key FIRST — " pa" and "PA" must be the same race.
    polls["state"] = polls["state"].str.strip().str.upper()
    polls = polls.dropna(subset=["dem", "rep", "sample_size"]).drop_duplicates()
    polls["sample_size"] = polls["sample_size"].astype(int)
    polls["end_date"] = pd.to_datetime(polls["end_date"])
    polls["margin"] = polls["dem"] - polls["rep"]

    results = pd.read_csv(results_path)
    results["election_date"] = pd.to_datetime(results["election_date"])
    results["actual_margin"] = results["dem"] - results["rep"]
    results = results[["election", "state", "election_date", "actual_margin"]]
    return polls.reset_index(drop=True), results


def polling_averages(polls, results, window_days=21):
    df = polls.merge(results[["election", "state", "election_date"]], on=["election", "state"])
    df["days_before"] = (df["election_date"] - df["end_date"]).dt.days
    df = df[(df["days_before"] >= 0) & (df["days_before"] <= window_days)]
    # Weighted mean = sum(w*x)/sum(w). Bigger samples = less sampling noise, so
    # more weight. (Inverse variance would be ~ n too, since var ~ 1/n.)
    df = df.assign(w_margin=df["margin"] * df["sample_size"])
    g = df.groupby(["election", "state"])
    out = pd.DataFrame({
        "poll_avg": g["w_margin"].sum() / g["sample_size"].sum(),
        "n_polls": g.size(),
    }).reset_index()
    return out


def race_errors(averages, results):
    df = averages.merge(results[["election", "state", "actual_margin"]], on=["election", "state"])
    df["error"] = df["poll_avg"] - df["actual_margin"]
    return df[["election", "state", "poll_avg", "actual_margin", "error"]]


def election_bias(errors, level=0.95):
    g = errors.groupby("election")["error"]
    out = pd.DataFrame({"mean_error": g.mean(), "sd": g.std(ddof=1), "n_states": g.size()})
    se = out["sd"] / np.sqrt(out["n_states"])
    t = stats.t.ppf(1 - (1 - level) / 2, out["n_states"] - 1)   # vectorised over elections
    out["ci_low"] = out["mean_error"] - t * se
    out["ci_high"] = out["mean_error"] + t * se
    return out[["mean_error", "ci_low", "ci_high", "n_states"]]


def bias_tests(errors):
    # Clustered: collapse to one number per election, THEN test. n = elections.
    means = errors.groupby("election")["error"].mean()
    n = len(means)
    se = means.std(ddof=1) / np.sqrt(n)
    res = stats.ttest_1samp(means, 0.0)
    t = stats.t.ppf(0.975, n - 1)
    # Naive: pretend every race is an independent draw. Same mean (roughly),
    # but se shrinks by ~sqrt(states) and p collapses — false confidence.
    naive = stats.ttest_1samp(errors["error"], 0.0)
    return {
        "mean_bias": float(means.mean()),
        "se": float(se),
        "t_stat": float(res.statistic),
        "p_value": float(res.pvalue),
        "ci_low": float(means.mean() - t * se),
        "ci_high": float(means.mean() + t * se),
        "n_elections": int(n),
        "naive_se": float(errors["error"].std(ddof=1) / np.sqrt(len(errors))),
        "naive_p_value": float(naive.pvalue),
    }


def bootstrap_bias(election_means, n_boot=5000, seed=0):
    values = np.asarray(election_means, dtype=float)
    n = len(values)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))     # resample ELECTIONS, not races
    boots = values[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"mean": float(values.mean()), "ci_low": float(lo), "ci_high": float(hi),
            "share_above_zero": float((boots > 0).mean())}


def plot_bias(bias_df, out_path):
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    x = bias_df.index.to_numpy()
    y = bias_df["mean_error"].to_numpy()
    yerr = np.vstack([y - bias_df["ci_low"].to_numpy(), bias_df["ci_high"].to_numpy() - y])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axhline(0, color="grey", lw=1)
    ax.errorbar(x, y, yerr=yerr, fmt="o", capsize=4)
    ax.axhline(y.mean(), color="C1", ls="--", lw=1, label=f"mean {y.mean():+.2f}")
    ax.set_xlabel("Election")
    ax.set_ylabel("Poll avg − actual margin (pts, D−R)")
    ax.set_title("Polling bias by election (95% CI over states)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)                                   # don't leak figures in loops/tests
    return out_path


def report(polls_path, results_path, out_dir, window_days=21):
    polls, results = load_data(polls_path, results_path)
    avgs = polling_averages(polls, results, window_days)
    errs = race_errors(avgs, results)
    eb = election_bias(errs)
    tests = bias_tests(errs)
    boot = bootstrap_bias(eb["mean_error"])
    plot_path = plot_bias(eb, pathlib.Path(out_dir) / "bias_by_election.png")
    worst = int(eb["mean_error"].abs().idxmax())
    direction = "toward D" if tests["mean_bias"] > 0 else "toward R"
    summary = (
        f"Across {tests['n_elections']} elections ({len(errs)} races), the final "
        f"{window_days}-day polling average missed by {tests['mean_bias']:+.2f} pts on average "
        f"({direction}); 95% CI [{tests['ci_low']:+.2f}, {tests['ci_high']:+.2f}], "
        f"p = {tests['p_value']:.3f} (election-level t-test). Bootstrap CI "
        f"[{boot['ci_low']:+.2f}, {boot['ci_high']:+.2f}]. Treating races as independent "
        f"would give p = {tests['naive_p_value']:.2g} — overconfident. Largest miss: {worst} "
        f"({eb.loc[worst, 'mean_error']:+.2f})."
    )
    return {
        "n_elections": tests["n_elections"],
        "n_races": int(len(errs)),
        "mean_bias": tests["mean_bias"],
        "ci": (tests["ci_low"], tests["ci_high"]),
        "p_value": tests["p_value"],
        "bootstrap_ci": (boot["ci_low"], boot["ci_high"]),
        "naive_p_value": tests["naive_p_value"],
        "most_biased_election": worst,
        "plot_path": str(plot_path),
        "summary": summary,
    }
