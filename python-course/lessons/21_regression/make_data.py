"""Generate synthetic data for lesson 21. Run: python make_data.py"""
import pathlib
import numpy as np
import pandas as pd

rng = np.random.default_rng(21)
out = pathlib.Path(__file__).parent / "data"
out.mkdir(exist_ok=True)

# 40 elections: incumbent vote share responds to GDP growth and unemployment change.
n = 40
growth = rng.normal(2.0, 2.0, n).round(2)            # % real GDP growth in election year
unemp = rng.normal(0.0, 1.0, n).round(2)             # change in unemployment rate, pp
vote = 47.0 + 1.6 * growth - 1.2 * unemp + rng.normal(0, 2.5, n)
pd.DataFrame({
    "year": np.arange(1868, 1868 + 4 * n, 4),
    "gdp_growth": growth,
    "unemp_change": unemp,
    "incumbent_vote": vote.round(2),
}).to_csv(out / "elections.csv", index=False)
print("wrote", out / "elections.csv")
