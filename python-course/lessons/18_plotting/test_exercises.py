import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

YEARS = [1444, 1445, 1446, 1447]
TREASURY = {"Castile": [100, 120, 90, 150], "Venice": [200, 210, 260, 240], "Ottomans": [50, 80, 130, 170]}
FACTIONS = ["Rome", "Carthage", "Gaul"]
WINS = [60, 45, 10]
GAMES = [100, 100, 25]
ERRORS = np.random.default_rng(0).normal(0, 3, 200)


@pytest.fixture(autouse=True)
def close_figs():
    yield
    plt.close("all")


def test_treasury_lines(ex):
    fig, ax = ex.plot_treasury(YEARS, TREASURY)
    assert len(ax.lines) == 3, "one line per nation"
    assert [l.get_label() for l in ax.lines] == ["Castile", "Venice", "Ottomans"]
    assert list(ax.lines[1].get_ydata()) == [200, 210, 260, 240]
    assert list(ax.lines[0].get_xdata()) == YEARS


def test_treasury_labels(ex):
    fig, ax = ex.plot_treasury(YEARS, TREASURY)
    assert ax.get_title() == "Treasury over time"
    assert ax.get_xlabel() == "Year" and ax.get_ylabel() == "Ducats"
    assert ax.get_legend() is not None, "call ax.legend()"
    assert fig is ax.figure


def test_treasury_uses_given_ax(ex):
    fig, axes = plt.subplots(1, 2)
    f2, a2 = ex.plot_treasury(YEARS, TREASURY, ax=axes[1])
    assert a2 is axes[1] and f2 is fig, "when ax is given, draw on it and return its figure"
    assert len(axes[1].lines) == 3 and len(axes[0].lines) == 0


def test_win_rate_bars_heights(ex):
    fig, ax = ex.win_rate_bars(FACTIONS, WINS, GAMES)
    heights = [p.get_height() for p in ax.patches]
    assert heights == pytest.approx([0.6, 0.45, 0.4])
    assert ax.get_ylim() == pytest.approx((0, 1))
    assert ax.get_title() == "Win rate by faction" and ax.get_ylabel() == "Win rate"


def test_win_rate_baseline(ex):
    fig, ax = ex.win_rate_bars(FACTIONS, WINS, GAMES)
    flat = [l for l in ax.lines if list(l.get_ydata()) == [0.5, 0.5]]
    assert flat, "expected a horizontal line at 0.5 (ax.axhline(0.5))"


def test_win_rate_error_bars(ex):
    fig, ax = ex.win_rate_bars(FACTIONS, WINS, GAMES)
    bars = [c for c in ax.containers if getattr(c, "errorbar", None) is not None]
    assert bars, "pass yerr= to ax.bar"
    segs = bars[0].errorbar.lines[2][0].get_segments()
    lengths = [s[1][1] - s[0][1] for s in segs]
    expected = [2 * math.sqrt(p * (1 - p) / n) for p, n in [(0.6, 100), (0.45, 100), (0.4, 25)]]
    assert lengths == pytest.approx(expected), "error bar = +/- one standard error"


def test_histogram(ex):
    fig, ax = ex.error_histogram(ERRORS, bins=15)
    assert len(ax.patches) == 15
    assert sum(p.get_height() for p in ax.patches) == len(ERRORS)
    assert any(list(l.get_xdata()) == [0, 0] for l in ax.lines), "vertical line at 0"
    assert ax.get_xlabel() == "Polling error (points)"
    assert ax.get_title() == "Polling error" and ax.get_ylabel() == "Number of polls"


def test_scatter(ex):
    n = [400, 800, 1500]
    e = [5.0, 3.0, 1.5]
    fig, ax = ex.scatter_sample_vs_error(n, e)
    pts = ax.collections[0].get_offsets()
    assert np.allclose(pts, [[400, 5.0], [800, 3.0], [1500, 1.5]])
    assert ax.get_xlabel() == "Sample size" and ax.get_ylabel() == "Absolute error (points)"
    assert ax.get_title() != ""


def test_dashboard(ex):
    fig = ex.dashboard(YEARS, TREASURY, FACTIONS, WINS, GAMES, ERRORS)
    assert isinstance(fig, matplotlib.figure.Figure), "return the Figure, not a tuple"
    assert len(fig.axes) == 3
    assert [a.get_title() for a in fig.axes] == ["Treasury over time", "Win rate by faction", "Polling error"]
    assert len(fig.axes[0].lines) == 3


def test_save_figure(ex, tmp_path):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3])
    out = tmp_path / "chart.png"
    assert ex.save_figure(fig, out) == out
    assert out.exists() and out.stat().st_size > 1000
    assert out.read_bytes()[:4] == b"\x89PNG"
