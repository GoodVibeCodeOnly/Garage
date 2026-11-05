# Lesson 21 — solutions.
import numpy as np
import pandas as pd
from scipy import stats


def ols_fit(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    # Use deviations from the mean; the 1/n vs 1/(n-1) factor cancels in the ratio,
    # so we don't even need np.cov here.
    dx, dy = x - x.mean(), y - y.mean()
    slope = (dx * dy).sum() / (dx ** 2).sum()
    intercept = y.mean() - slope * x.mean()   # the line passes through (x̄, ȳ)
    return float(slope), float(intercept)


def residuals(x, y, slope, intercept):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return y - (intercept + slope * x)


def r_squared(x, y, slope, intercept):
    y = np.asarray(y, dtype=float)
    ss_res = (residuals(x, y, slope, intercept) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    return float(1 - ss_res / ss_tot)


def slope_se(x, y):
    x = np.asarray(x, dtype=float)
    slope, intercept = ols_fit(x, y)
    n = len(x)
    s2 = (residuals(x, y, slope, intercept) ** 2).sum() / (n - 2)
    return float(np.sqrt(s2 / ((x - x.mean()) ** 2).sum()))


def slope_ci(x, y, level=0.95):
    slope, _ = ols_fit(x, y)
    se = slope_se(x, y)
    t = stats.t.ppf(1 - (1 - level) / 2, df=len(x) - 2)
    return float(slope - t * se), float(slope + t * se)


def multiple_ols(X, y):
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:                      # be forgiving with a single regressor
        X = X[:, None]
    design = np.column_stack([np.ones(len(X)), X])
    # lstsq is numerically safer than inv(X'X) @ X'y. rcond=None silences a warning.
    coef, *_ = np.linalg.lstsq(design, np.asarray(y, dtype=float), rcond=None)
    return coef


def election_model(path):
    df = pd.read_csv(path)
    slope, intercept = ols_fit(df["gdp_growth"], df["incumbent_vote"])
    r2 = r_squared(df["gdp_growth"], df["incumbent_vote"], slope, intercept)
    b = multiple_ols(df[["gdp_growth", "unemp_change"]], df["incumbent_vote"])
    pred = b[0] + b[1] * 3.0 + b[2] * -0.5
    return {
        "simple_slope": slope,
        "simple_r2": r2,
        "growth_coef": float(b[1]),
        "unemp_coef": float(b[2]),
        "predicted_vote": float(pred),
    }
