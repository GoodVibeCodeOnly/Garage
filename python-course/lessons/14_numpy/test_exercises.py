import numpy as np
import pytest


# Exercise 1
def test_player_win_rates(ex):
    results = np.array([[True, True, False, False],
                        [True, True, True, False],
                        [False, False, False, False]])
    np.testing.assert_allclose(ex.player_win_rates(results), [0.5, 0.75, 0.0])


def test_player_win_rates_shape(ex):
    results = np.random.default_rng(0).random((7, 30)) < 0.5
    assert ex.player_win_rates(results).shape == (7,), "one rate per player (row)"


# Exercise 2
def test_count_above(ex):
    rates = np.array([0.4, 0.5, 0.51, 0.7, 0.2])
    assert ex.count_above(rates) == 2, "strictly above 0.5"
    assert ex.count_above(rates, 0.3) == 4
    assert isinstance(ex.count_above(rates), int)


# Exercise 3
def test_progressive_tax(ex):
    np.testing.assert_allclose(ex.progressive_tax([50, 150], 100, 0.1, 0.3), [5.0, 25.0])
    np.testing.assert_allclose(ex.progressive_tax(np.array([0, 100, 1000]), 100, 0.1, 0.5),
                               [0.0, 10.0, 460.0])


# Exercise 4
def test_simulate_win_rates_matches_spec(ex):
    expected = (np.random.default_rng(5).random((20, 50)) < 0.55).mean(axis=1)
    got = ex.simulate_win_rates(0.55, 50, 20, np.random.default_rng(5))
    np.testing.assert_allclose(got, expected)


def test_simulate_win_rates_stats(ex):
    rates = ex.simulate_win_rates(0.55, 100, 5000, np.random.default_rng(1))
    assert rates.shape == (5000,)
    assert rates.mean() == pytest.approx(0.55, abs=0.005)
    # About 13% of true-55% players show a sub-50% record after 100 games.
    assert (rates < 0.5).mean() == pytest.approx(0.135, abs=0.02)


# Exercise 5
def test_treasury_paths_deterministic_case(ex):
    paths = ex.treasury_paths(100, 10, 4, 3, 0.0, 999, np.random.default_rng(0))
    assert paths.shape == (3, 4), "shape is (n_runs, turns)"
    np.testing.assert_allclose(paths, [[110, 120, 130, 140]] * 3)
    paths = ex.treasury_paths(0, 10, 3, 2, 1.0, 25, np.random.default_rng(0))
    np.testing.assert_allclose(paths, [[-15, -30, -45]] * 2)


def test_treasury_paths_matches_spec(ex):
    draws = np.random.default_rng(9).random((1000, 50))
    expected = 200 + np.cumsum(8 - (draws < 0.1) * 100, axis=1)
    got = ex.treasury_paths(200, 8, 50, 1000, 0.1, 100, np.random.default_rng(9))
    np.testing.assert_allclose(got, expected)


# Exercise 6
def test_bankrupt_share(ex):
    paths = np.array([[10, 5, 1], [10, -1, 20], [-5, -6, -7], [0, 0, 0]])
    assert ex.bankrupt_share(paths) == pytest.approx(0.5)
    assert isinstance(ex.bankrupt_share(paths), float)


# Exercise 7
def test_final_summary(ex):
    paths = np.column_stack([np.zeros(101), np.arange(101)])
    s = ex.final_summary(paths)
    assert s["mean"] == pytest.approx(50)
    assert s["p05"] == pytest.approx(5)
    assert s["p95"] == pytest.approx(95)


# Exercise 8
def test_worst_drawdown(ex):
    assert ex.worst_drawdown([100, 120, 90, 130, 80]) == pytest.approx(50)
    assert ex.worst_drawdown([1, 2, 3, 4]) == 0.0
    assert ex.worst_drawdown(np.array([5, 1, 10, 9])) == pytest.approx(4)
