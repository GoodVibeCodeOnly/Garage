"""Lesson 21 worked example: does the economy predict the incumbent's vote?"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = pathlib.Path(__file__).parent
df = pd.read_csv(HERE / "data" / "elections.csv")
x, y = df["gdp_growth"].to_numpy(), df["incumbent_vote"].to_numpy()
n = len(x)

# 1. Slope and intercept by hand
dx = x - x.mean()
slope = (dx * (y - y.mean())).sum() / (dx ** 2).sum()
intercept = y.mean() - slope * x.mean()

# 2. Residuals and R^2
resid = y - (intercept + slope * x)
r2 = 1 - (resid ** 2).sum() / ((y - y.mean()) ** 2).sum()

# 3. Standard error and 95% CI on the slope
s2 = (resid ** 2).sum() / (n - 2)
se = np.sqrt(s2 / (dx ** 2).sum())
t = stats.t.ppf(0.975, n - 2)
print(f"incumbent_vote = {intercept:.2f} + {slope:.2f} * gdp_growth")
print(f"R^2 = {r2:.3f}   se(slope) = {se:.3f}   95% CI = [{slope - t*se:.2f}, {slope + t*se:.2f}]")
print("scipy check:", stats.linregress(x, y).slope.round(4), stats.linregress(x, y).stderr.round(4))

# 4. Multiple regression with lstsq
A = np.column_stack([np.ones(n), df["gdp_growth"], df["unemp_change"]])
b, *_ = np.linalg.lstsq(A, y, rcond=None)
print(f"\nmultiple: vote = {b[0]:.2f} + {b[1]:.2f}*growth + {b[2]:.2f}*unemp_change")
print("Read: +1pp growth ~ +%.1f pts of vote, HOLDING unemployment change fixed." % b[1])

# 5. Plot
out = HERE / "output"
out.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(x, y, s=18)
xs = np.linspace(x.min(), x.max(), 50)
ax.plot(xs, intercept + slope * xs, color="C1")
ax.set_xlabel("GDP growth (%)")
ax.set_ylabel("Incumbent vote share (%)")
ax.set_title(f"Slope {slope:.2f}, R² {r2:.2f}")
fig.tight_layout()
fig.savefig(out / "regression.png", dpi=100)
print("\nsaved", out / "regression.png")
