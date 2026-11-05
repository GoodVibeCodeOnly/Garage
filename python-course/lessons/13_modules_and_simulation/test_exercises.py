import random

import pytest

EVENTS = [(0.10, -150), (0.20, 60)]


# Exercise 1
def test_play_games_range_and_type(ex):
    wins = ex.play_games(100, 0.55, random.Random(1))
    assert isinstance(wins, int)
    assert 0 <= wins <= 100


def test_play_games_extremes(ex):
    assert ex.play_games(50, 0.0, random.Random(1)) == 0
    assert ex.play_games(50, 1.0, random.Random(1)) == 50


def test_play_games_reproducible(ex):
    a = ex.play_games(200, 0.55, random.Random(42))
    b = ex.play_games(200, 0.55, random.Random(42))
    assert a == b, "same seed must give the same result"


def test_play_games_matches_spec(ex):
    rng = random.Random(7)
    expected = sum(rng.random() < 0.55 for _ in range(300))
    assert ex.play_games(300, 0.55, random.Random(7)) == expected, \
        "use exactly one rng.random() call per game"


def test_play_games_long_run(ex):
    wins = ex.play_games(20000, 0.55, random.Random(3))
    assert wins / 20000 == pytest.approx(0.55, abs=0.015)


# Exercise 2
def test_winrate_samples(ex):
    rates = ex.winrate_samples(40, 0.55, 500, random.Random(5))
    assert len(rates) == 500
    assert all(0 <= r <= 1 for r in rates)
    assert sum(rates) / len(rates) == pytest.approx(0.55, abs=0.02)


# Exercise 3
def test_prob_looks_losing_reproducible(ex):
    assert ex.prob_looks_losing(50, 0.55, 2000, seed=1) == ex.prob_looks_losing(50, 0.55, 2000, seed=1)


def test_prob_looks_losing_values(ex):
    # True values (binomial): n=20 -> ~0.25, n=100 -> ~0.13, n=1000 -> ~0.001
    assert ex.prob_looks_losing(20, 0.55, 4000, seed=2) == pytest.approx(0.25, abs=0.04)
    assert ex.prob_looks_losing(100, 0.55, 4000, seed=2) == pytest.approx(0.135, abs=0.03)
    assert ex.prob_looks_losing(1000, 0.55, 1000, seed=2) < 0.02


def test_prob_looks_losing_shrinks(ex):
    small = ex.prob_looks_losing(10, 0.55, 3000, seed=9)
    big = ex.prob_looks_losing(400, 0.55, 3000, seed=9)
    assert big < small, "more games -> less likely to look like a losing player"


# Exercise 4
def test_games_needed(ex):
    # P(below 50%) for a 55% player drops under 5% at roughly 270 games.
    assert ex.games_needed(0.55, 0.05, 2000, seed=4) == 400
    assert ex.games_needed(0.55, 0.30, 2000, seed=4) == 10
    assert ex.games_needed(0.55, 0.0, 200, seed=4, candidates=(10, 20)) is None


# Exercise 5
def test_treasury_no_events(ex):
    assert ex.simulate_treasury(100, 10, 3, [], random.Random(0)) == [110, 120, 130]


def test_treasury_certain_events(ex):
    out = ex.simulate_treasury(0, 5, 4, [(1.0, -2), (0.0, 1000)], random.Random(0))
    assert out == [3, 6, 9, 12]


def test_treasury_matches_spec(ex):
    rng = random.Random(11)
    bal, expected = 200, []
    for _ in range(30):
        bal += 12
        for p, amt in EVENTS:
            if rng.random() < p:
                bal += amt
        expected.append(bal)
    assert ex.simulate_treasury(200, 12, 30, EVENTS, random.Random(11)) == expected


# Exercise 6
def test_bankruptcy_bounds(ex):
    assert ex.bankruptcy_rate(1000, 50, 20, [], 50, seed=1) == 0.0
    assert ex.bankruptcy_rate(-1, 0, 5, [], 50, seed=1) == 1.0


def test_bankruptcy_rate(ex):
    r1 = ex.bankruptcy_rate(100, 5, 40, EVENTS, 1000, seed=3)
    r2 = ex.bankruptcy_rate(100, 5, 40, EVENTS, 1000, seed=3)
    assert r1 == r2
    assert 0.05 < r1 < 0.9, f"implausible bankruptcy rate {r1}"
    richer = ex.bankruptcy_rate(400, 5, 40, EVENTS, 1000, seed=3)
    assert richer < r1, "a bigger starting treasury should go bust less often"


# Exercise 7
def test_summarise(ex):
    s = ex.summarise(list(range(1, 102)))   # 1..101
    assert s["mean"] == pytest.approx(51)
    assert s["min"] == 1 and s["max"] == 101
    assert s["p05"] == 6 and s["p95"] == 96


def test_summarise_unsorted(ex):
    s = ex.summarise([5, 1, 3])
    assert s["min"] == 1 and s["max"] == 5 and s["mean"] == pytest.approx(3)
