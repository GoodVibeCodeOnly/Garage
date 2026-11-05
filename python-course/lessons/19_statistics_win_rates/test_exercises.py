import math
import statistics

import numpy as np
import pytest
from scipy import stats

XS = [3, 7, 7, 19, 24, 1, 8]


def test_mean(ex):
    assert ex.mean(XS) == pytest.approx(statistics.mean(XS))
    assert ex.mean([2.5]) == 2.5


def test_variance_sample(ex):
    assert ex.variance(XS) == pytest.approx(statistics.variance(XS))


def test_variance_population(ex):
    assert ex.variance(XS, ddof=0) == pytest.approx(statistics.pvariance(XS))


def test_std(ex):
    assert ex.std(XS) == pytest.approx(np.std(XS, ddof=1))
    assert ex.std(XS, ddof=0) == pytest.approx(np.std(XS))


def test_se_proportion(ex):
    assert ex.se_proportion(55, 100) == pytest.approx(math.sqrt(0.55 * 0.45 / 100))
    assert ex.se_proportion(0, 10) == 0.0


def test_normal_ci(ex):
    lo, hi = ex.normal_ci(60, 100)
    assert lo == pytest.approx(0.6 - 1.96 * math.sqrt(0.24 / 100))
    assert hi == pytest.approx(0.6 + 1.96 * math.sqrt(0.24 / 100))


def test_normal_ci_degenerate(ex):
    assert ex.normal_ci(10, 10) == pytest.approx((1.0, 1.0)), \
        "10/10 gives a zero-width Wald interval -- that's the flaw Wilson fixes"


def test_wilson_matches_scipy(ex):
    for w, n in [(60, 100), (7, 10), (0, 12), (30, 30), (512, 1000)]:
        ref = stats.binomtest(w, n).proportion_ci(confidence_level=0.95, method="wilson")
        lo, hi = ex.wilson_ci(w, n, z=stats.norm.ppf(0.975))
        assert (lo, hi) == pytest.approx((ref.low, ref.high), abs=1e-9), f"{w}/{n}"


def test_wilson_stays_in_bounds(ex):
    lo, hi = ex.wilson_ci(10, 10)
    assert 0 <= lo < hi <= 1.0 + 1e-12
    assert hi - lo > 0.1


def test_binom_pmf(ex):
    assert ex.binom_pmf(5, 10) == pytest.approx(stats.binom.pmf(5, 10, 0.5))
    assert ex.binom_pmf(3, 8, 0.3) == pytest.approx(stats.binom.pmf(3, 8, 0.3))
    assert sum(ex.binom_pmf(k, 12, 0.7) for k in range(13)) == pytest.approx(1.0)


@pytest.mark.parametrize("w,n,p", [(60, 100, 0.5), (7, 10, 0.5), (5, 10, 0.5),
                                   (62, 100, 0.5), (3, 20, 0.3), (0, 15, 0.5)])
def test_binom_test_matches_scipy(ex, w, n, p):
    assert ex.binom_test_two_sided(w, n, p) == pytest.approx(stats.binomtest(w, n, p).pvalue, rel=1e-6)


def test_binom_test_interpretation(ex):
    assert ex.binom_test_two_sided(7, 10) > 0.3, "7/10 is very compatible with a fair coin"
    assert ex.binom_test_two_sided(70, 100) < 0.001, "70/100 is not"


def test_simulate_shape_and_determinism(ex):
    a = ex.simulate_win_rates(0.5, 20, 1000, np.random.default_rng(1))
    b = ex.simulate_win_rates(0.5, 20, 1000, np.random.default_rng(1))
    assert isinstance(a, np.ndarray) and a.shape == (1000,)
    assert np.array_equal(a, b)
    expected = (np.random.default_rng(1).random((1000, 20)) < 0.5).mean(axis=1)
    assert np.allclose(a, expected), "use exactly one rng.random((n_players, n_games)) call"


def test_small_samples_mislead(ex):
    rates = ex.simulate_win_rates(0.5, 20, 1000, np.random.default_rng(2))
    share_looks_great = (rates >= 0.65).mean()
    assert 0.1 < share_looks_great < 0.2, \
        "~13% of perfectly average players hit >=65% over 20 games"
    big = ex.simulate_win_rates(0.5, 500, 1000, np.random.default_rng(2))
    assert (big >= 0.65).mean() == 0
