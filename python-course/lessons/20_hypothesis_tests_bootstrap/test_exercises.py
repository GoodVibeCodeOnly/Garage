import numpy as np
import pytest
from scipy import stats

A = np.array([1] * 34 + [0] * 16)  # 68% over 50 games
B = np.array([1] * 25 + [0] * 25)  # 50% over 50 games


def _ref_perm(a, b, n_perm, rng):
    obs = a.mean() - b.mean()
    pooled = np.concatenate([a, b])
    c = 0
    for _ in range(n_perm):
        p = rng.permutation(pooled)
        if abs(p[: len(a)].mean() - p[len(a):].mean()) >= abs(obs) - 1e-12:
            c += 1
    return (c + 1) / (n_perm + 1)


def test_diff_in_win_rates(ex):
    assert ex.diff_in_win_rates(A, B) == pytest.approx(0.18)
    assert ex.diff_in_win_rates([1, 0], [1, 1, 1, 0]) == pytest.approx(-0.25)


def test_permutation_exact(ex):
    got = ex.permutation_test(A, B, 2000, np.random.default_rng(42))
    assert got == pytest.approx(_ref_perm(A, B, 2000, np.random.default_rng(42)))


def test_permutation_sensible(ex):
    p = ex.permutation_test(A, B, 2000, np.random.default_rng(7))
    assert 0.05 < p < 0.12, "68% vs 50% over 50 games each is suggestive but not conclusive"
    same = ex.permutation_test(B, B.copy(), 500, np.random.default_rng(7))
    assert same == pytest.approx(1.0), "identical groups: every shuffle is at least as extreme"


def test_permutation_never_zero(ex):
    big_a = np.ones(100, dtype=int)
    big_b = np.zeros(100, dtype=int)
    p = ex.permutation_test(big_a, big_b, 199, np.random.default_rng(0))
    assert p == pytest.approx(1 / 200)


def test_bootstrap_exact(ex):
    x = np.random.default_rng(3).exponential(10, 60)
    lo, hi = ex.bootstrap_ci(x, np.mean, 3000, np.random.default_rng(11))
    idx = np.random.default_rng(11).integers(0, 60, size=(3000, 60))
    ref = np.percentile(x[idx].mean(axis=1), [2.5, 97.5])
    assert (lo, hi) == pytest.approx(tuple(ref))
    assert lo < x.mean() < hi


def test_bootstrap_median_and_alpha(ex):
    x = list(np.random.default_rng(4).normal(50, 5, 40))  # plain list input must work
    lo90, hi90 = ex.bootstrap_ci(x, np.median, 2000, np.random.default_rng(5), alpha=0.10)
    lo95, hi95 = ex.bootstrap_ci(x, np.median, 2000, np.random.default_rng(5), alpha=0.05)
    assert isinstance(lo90, float)
    assert lo95 <= lo90 < hi90 <= hi95, "a 95% interval is wider than a 90% one"


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_welch_matches_scipy(ex, seed):
    rng = np.random.default_rng(seed)
    a, b = rng.normal(10, 2, 30), rng.normal(11, 4, 45)
    t, df = ex.welch_t(a, b)
    ref = stats.ttest_ind(a, b, equal_var=False)
    assert t == pytest.approx(ref.statistic)
    assert df == pytest.approx(ref.df)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_t_pvalue_matches_scipy(ex, seed):
    rng = np.random.default_rng(seed)
    a, b = rng.normal(10, 2, 30), rng.normal(11, 4, 45)
    assert ex.t_test_pvalue(a, b) == pytest.approx(stats.ttest_ind(a, b, equal_var=False).pvalue)


def test_false_positive_exact(ex):
    got = ex.false_positive_count(20, 100, np.random.default_rng(2024))
    wins = np.random.default_rng(2024).binomial(100, 0.5, size=20)
    ref = sum(stats.binomtest(int(w), 100, 0.5).pvalue < 0.05 for w in wins)
    assert got == ref


def test_false_positive_rate(ex):
    rng = np.random.default_rng(99)
    counts = [ex.false_positive_count(20, 200, rng) for _ in range(150)]
    share_any = np.mean([c > 0 for c in counts])
    assert 0.3 < share_any < 0.8, "testing 20 balanced factions often 'finds' at least one imbalanced one"
    assert np.mean(counts) < 1.5


def test_bonferroni(ex):
    p = [0.001, 0.01, 0.03, 0.2]
    out = ex.bonferroni(p)  # threshold 0.0125
    assert isinstance(out, np.ndarray)
    assert out.tolist() == [True, True, False, False]
    assert ex.bonferroni([0.04] * 20, alpha=0.05).sum() == 0
