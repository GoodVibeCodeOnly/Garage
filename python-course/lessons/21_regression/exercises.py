# Lesson 21 — Regression by hand.
# How to check: double-click check.bat in the course folder and type 21.
# Use numpy (and scipy.stats for t critical values). No statsmodels.
import numpy as np
import pandas as pd
from scipy import stats


def ols_fit(x, y):
    """Exercise 1. Simple OLS of y on x.

    Return a tuple (slope, intercept) as floats, where
        slope     = cov(x, y) / var(x)
        intercept = mean(y) - slope * mean(x)
    x and y are sequences (lists or arrays) of equal length.
    """
    raise NotImplementedError("Exercise 1")


def residuals(x, y, slope, intercept):
    """Exercise 2. Return a numpy array of residuals y - (intercept + slope * x)."""
    raise NotImplementedError("Exercise 2")


def r_squared(x, y, slope, intercept):
    """Exercise 3. Return R^2 = 1 - SS_res / SS_tot as a float.

    SS_res = sum of squared residuals; SS_tot = sum of (y - mean(y))^2.
    """
    raise NotImplementedError("Exercise 3")


def slope_se(x, y):
    """Exercise 4. Standard error of the OLS slope (float).

    se = sqrt( s^2 / sum((x - mean(x))^2) ),  where s^2 = SS_res / (n - 2).
    (n - 2 because we estimated two parameters.) Fit the line yourself inside.
    """
    raise NotImplementedError("Exercise 4")


def slope_ci(x, y, level=0.95):
    """Exercise 5. Confidence interval for the slope: (low, high).

    slope ± t * se, where t = stats.t.ppf(1 - (1 - level) / 2, df=n - 2).
    """
    raise NotImplementedError("Exercise 5")


def multiple_ols(X, y):
    """Exercise 6. Multiple regression via np.linalg.lstsq.

    X is a 2-D array-like of shape (n, k) WITHOUT an intercept column.
    Add a column of ones on the LEFT, solve least squares, and return a
    1-D numpy array of length k + 1: [intercept, b1, ..., bk].
    """
    raise NotImplementedError("Exercise 6")


def election_model(path):
    """Exercise 7. Load the elections CSV at `path` (columns gdp_growth,
    unemp_change, incumbent_vote) and return a dict:

        {
          "simple_slope":  slope of incumbent_vote on gdp_growth (simple OLS),
          "simple_r2":     R^2 of that simple fit,
          "growth_coef":   coefficient on gdp_growth in the multiple regression
                           incumbent_vote ~ gdp_growth + unemp_change,
          "unemp_coef":    coefficient on unemp_change in that regression,
          "predicted_vote": predicted incumbent vote from the multiple model
                            when growth = 3.0 and unemp_change = -0.5,
        }
    All values floats. Reuse your earlier functions.
    """
    raise NotImplementedError("Exercise 7")
