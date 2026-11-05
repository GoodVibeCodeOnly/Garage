import numpy as np
import pandas as pd
import pytest
from scipy import stats

X = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
Y = [2.1, 3.9, 6.2, 7.8, 10.1, 12.2]


def test_ols_fit_perfect_line(ex):
    slope, intercept = ex.ols_fit([0, 1, 2, 3], [1, 3, 5, 7])
    assert slope == pytest.approx(2.0)
    assert intercept == pytest.approx(1.0)


def test_ols_fit_matches_polyfit(ex):
    slope, intercept = ex.ols_fit(X, Y)
    s, i = np.polyfit(X, Y, 1)
    assert slope == pytest.approx(s), "slope should be cov(x,y)/var(x)"
    assert intercept == pytest.approx(i), "intercept should be mean(y) - slope*mean(x)"


def test_residuals(ex):
    r = ex.residuals([0, 1, 2], [1, 4, 5], 2.0, 1.0)
    assert np.allclose(r, [0.0, 1.0, 0.0])


def test_residuals_sum_to_zero_at_ols(ex):
    s, i = np.polyfit(X, Y, 1)
    assert np.sum(ex.residuals(X, Y, s, i)) == pytest.approx(0.0, abs=1e-9)


def test_r_squared(ex):
    s, i = np.polyfit(X, Y, 1)
    expected = stats.linregress(X, Y).rvalue ** 2
    assert ex.r_squared(X, Y, s, i) == pytest.approx(expected)
    assert ex.r_squared([0, 1, 2], [1, 3, 5], 2.0, 1.0) == pytest.approx(1.0)


def test_slope_se_matches_scipy(ex):
    assert ex.slope_se(X, Y) == pytest.approx(stats.linregress(X, Y).stderr)


def test_slope_ci(ex):
    lr = stats.linregress(X, Y)
    t = stats.t.ppf(0.975, len(X) - 2)
    lo, hi = ex.slope_ci(X, Y)
    assert lo == pytest.approx(lr.slope - t * lr.stderr)
    assert hi == pytest.approx(lr.slope + t * lr.stderr)


def test_slope_ci_level_widens(ex):
    lo95, hi95 = ex.slope_ci(X, Y, 0.95)
    lo99, hi99 = ex.slope_ci(X, Y, 0.99)
    assert hi99 - lo99 > hi95 - lo95, "a 99% interval must be wider than a 95% one"


def test_multiple_ols_recovers_coefs(ex):
    rng = np.random.default_rng(0)
    Xm = rng.normal(size=(200, 2))
    y = 3.0 + 1.5 * Xm[:, 0] - 2.0 * Xm[:, 1]
    b = ex.multiple_ols(Xm, y)
    assert len(b) == 3, "return [intercept, b1, b2]"
    assert np.allclose(b, [3.0, 1.5, -2.0])


def test_multiple_ols_single_regressor_matches_simple(ex):
    b = ex.multiple_ols(np.array(X)[:, None], Y)
    s, i = np.polyfit(X, Y, 1)
    assert np.allclose(b, [i, s])


def test_election_model(ex, data_dir):
    res = ex.election_model(data_dir / "elections.csv")
    df = pd.read_csv(data_dir / "elections.csv")
    lr = stats.linregress(df["gdp_growth"], df["incumbent_vote"])
    assert res["simple_slope"] == pytest.approx(lr.slope)
    assert res["simple_r2"] == pytest.approx(lr.rvalue ** 2)
    A = np.column_stack([np.ones(len(df)), df["gdp_growth"], df["unemp_change"]])
    b = np.linalg.lstsq(A, df["incumbent_vote"], rcond=None)[0]
    assert res["growth_coef"] == pytest.approx(b[1])
    assert res["unemp_coef"] == pytest.approx(b[2])
    assert res["predicted_vote"] == pytest.approx(b[0] + 3 * b[1] - 0.5 * b[2])
