# Lesson 24 — solutions.
import statistics

import pytest


def clamp(x, lo, hi):
    if lo > hi:
        raise ValueError(f"lo ({lo}) > hi ({hi})")
    return max(lo, min(x, hi))


def win_rate(wins, games):
    if games <= 0:
        raise ValueError("games must be positive")
    if not 0 <= wins <= games:
        raise ValueError("wins must be between 0 and games")
    return wins / games          # true division always returns float in Python 3


def parse_percent(text):
    s = text.strip()
    if s.endswith("%"):
        s = s[:-1].rstrip()
    # float() raises ValueError on "", "abc", "12%" (a leftover %) — exactly the
    # errors we want, so we let it propagate instead of re-checking by hand.
    return float(s) / 100


def buggy_median(values):
    s = sorted(values)
    return s[len(s) // 2]


def buggy_tax(income):
    if income < 10_000:
        return 0.0
    if income < 50_000:
        return 0.2 * (income - 10_000)
    return 0.2 * 40_000 + 0.4 * (income - 49_000)


def find_median_bug_cases():
    # Even-length lists: the true median averages the two middle values.
    return [[1, 2], [1, 2, 3, 4], [10, 0]]


def find_tax_bug_incomes():
    # The < boundaries are actually fine at 10_000 (0.2*0 == 0) — the real bug is
    # the 49_000 typo in the top bracket. Any income >= 50_000 exposes it.
    return [50_000, 60_000]


def check_clamp(clamp_fn):
    assert clamp_fn(5, 0, 10) == 5
    assert clamp_fn(-3, 0, 10) == 0
    assert clamp_fn(99, 0, 10) == 10
    assert clamp_fn(0, 0, 10) == 0
    assert clamp_fn(10, 0, 10) == 10
    assert clamp_fn(-5, -10, -1) == -5
    with pytest.raises(ValueError):
        clamp_fn(1, 10, 0)


def check_win_rate(win_rate_fn):
    assert win_rate_fn(7, 10) == pytest.approx(0.7)
    assert win_rate_fn(0, 5) == 0.0
    assert win_rate_fn(5, 5) == 1.0
    # Check the type on the edge values too: a sloppy impl might use // there.
    for w, g in [(1, 2), (0, 5), (5, 5)]:
        assert isinstance(win_rate_fn(w, g), float)
    assert win_rate_fn(1, 3) == pytest.approx(1 / 3)
    for wins, games in [(0, 0), (1, 0), (-1, 5), (6, 5), (1, -2)]:
        with pytest.raises(ValueError):
            win_rate_fn(wins, games)
