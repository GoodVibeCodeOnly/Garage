"""Generate synthetic polls.csv and results.csv (deterministic). Run: python make_data.py"""
import pathlib

import numpy as np
import pandas as pd

rng = np.random.default_rng(16)
OUT = pathlib.Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

STATES = ["Ohio", "Florida", "Pennsylvania", "Michigan", "Wisconsin", "Arizona", "Georgia", "Nevada"]
YEARS = [2012, 2016, 2020]
# house effect = how many points a pollster leans toward the Democrat, on average
POLLSTERS = {"Acme Research": 2.0, "Bluegrass Polling": -1.5, "Crossroads Data": 0.0,
             "Delta Insights": 3.5, "Eagle Survey": -3.0}

results = []
for y in YEARS:
    for s in STATES:
        dem = round(rng.normal(48, 3), 1)
        rep = round(100 - dem - rng.uniform(1, 4), 1)
        results.append({"election_year": y, "state": s, "dem_share": dem, "rep_share": rep})
res = pd.DataFrame(results)

polls = []
for row in res.itertuples():
    for p, house in POLLSTERS.items():
        for _ in range(int(rng.integers(1, 4))):
            n = int(rng.choice([400, 600, 800, 1000, 1500]))
            noise = rng.normal(0, 100 / np.sqrt(n))
            dem = round(row.dem_share + house / 2 + noise, 1)
            rep = round(row.rep_share - house / 2 - noise + rng.normal(0, 0.5), 1)
            day = int(rng.integers(1, 60))
            date = pd.Timestamp(f"{row.election_year}-11-01") - pd.Timedelta(days=day)
            polls.append({"pollster": p, "election_year": row.election_year, "state": row.state,
                          "date": date.strftime("%Y-%m-%d"), "sample_size": n,
                          "dem_share": dem, "rep_share": rep})
pd.DataFrame(polls).to_csv(OUT / "polls.csv", index=False)
res.to_csv(OUT / "results.csv", index=False)
print(f"wrote {len(polls)} polls and {len(res)} results to {OUT}")
