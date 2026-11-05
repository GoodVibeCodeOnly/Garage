"""Generate synthetic polls and results for the capstone. Run: python make_data.py

Data-generating process (so you know the ground truth you're trying to recover):
  actual margin (D - R, points) = state lean + national swing + noise
  poll margin = actual + election_bias[e] + state_dev + house[pollster] + sampling noise
    election_bias[e] ~ N(1.0, 2.0)  -- shared by ALL states in election e (the clustering)
    state_dev        ~ N(0, 1.5)     -- race-specific polling miss
    house[pollster]  ~ N(0, 1.2)
    sampling noise   ~ N(0, 100/sqrt(n))  (approx SE of a margin with sample size n)
  Polls far from election day are noisier (opinion drifts) -- another reason to use a window.
Messiness added on purpose: whitespace/lower-case state codes, missing sample sizes,
missing toplines, exact duplicate rows.
"""
import datetime as dt
import pathlib

import numpy as np
import pandas as pd

rng = np.random.default_rng(2025)
out = pathlib.Path(__file__).parent / "data"
out.mkdir(exist_ok=True)

years = list(range(1980, 2025, 4))               # 12 elections
states = ["PA", "MI", "WI", "OH", "FL", "GA", "AZ", "NV", "NC", "VA"]
lean = dict(zip(states, rng.normal(0, 5, len(states))))
pollsters = ["Quill", "Meridian", "Harbor", "Atlas", "Keystone", "Lantern", "Northstar", "Vector"]
house = dict(zip(pollsters, rng.normal(0, 1.2, len(pollsters))))
bias = {y: rng.normal(1.0, 2.0) for y in years}


def election_day(year):
    d = dt.date(year, 11, 2)                     # first Tuesday after first Monday
    while d.weekday() != 1:
        d += dt.timedelta(days=1)
    return d


poll_rows, result_rows = [], []
for y in years:
    eday = election_day(y)
    swing = rng.normal(0, 3)
    for s in states:
        actual = lean[s] + swing + rng.normal(0, 2)
        share_d = 50 + actual / 2 - rng.uniform(0, 1.5)   # third parties eat a bit
        result_rows.append((y, s, eday.isoformat(), round(share_d, 2), round(share_d - actual, 2)))
        race_dev = rng.normal(0, 1.5)
        for _ in range(rng.integers(6, 16)):
            days = int(rng.integers(1, 75))
            n = int(rng.integers(400, 1600))
            p = rng.choice(pollsters)
            drift = rng.normal(0, days / 15)
            margin = actual + bias[y] + race_dev + house[p] + drift + rng.normal(0, 100 / np.sqrt(n))
            und = rng.uniform(3, 10)
            dem = 50 - und / 2 + margin / 2
            poll_rows.append([y, s, p, (eday - dt.timedelta(days=days)).isoformat(), n,
                              round(dem, 1), round(dem - margin, 1)])

polls = pd.DataFrame(poll_rows, columns=["election", "state", "pollster", "end_date",
                                         "sample_size", "dem", "rep"])
# messiness
idx = rng.choice(len(polls), 25, replace=False)
polls.loc[idx[:10], "state"] = polls.loc[idx[:10], "state"].str.lower()
polls.loc[idx[10:18], "state"] = " " + polls.loc[idx[10:18], "state"] + " "
polls["sample_size"] = polls["sample_size"].astype("Int64")
polls.loc[rng.choice(len(polls), 12, replace=False), "sample_size"] = pd.NA
polls.loc[rng.choice(len(polls), 6, replace=False), "dem"] = np.nan
polls = pd.concat([polls, polls.sample(15, random_state=1)]).sample(frac=1, random_state=2)
polls.to_csv(out / "polls.csv", index=False)

pd.DataFrame(result_rows, columns=["election", "state", "election_date", "dem", "rep"]) \
    .to_csv(out / "results.csv", index=False)
print(f"wrote {len(polls)} polls and {len(result_rows)} results to {out}")
print("true election biases:", {y: round(b, 2) for y, b in bias.items()})
print("true mean bias across these 12:", round(np.mean(list(bias.values())), 2))
