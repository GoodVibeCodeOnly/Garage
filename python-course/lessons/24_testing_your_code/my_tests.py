# Your own pytest tests for lesson 24. NOT graded — this is practice.
# Run from the course folder:   python -m pytest lessons/24_testing_your_code/my_tests.py
#
# The `ex` fixture is your exercises.py module (same as in the graded tests).
# Workflow to try (test-first): write the tests for parse_percent below, watch
# them fail, THEN implement parse_percent in exercises.py until they pass.
import pytest


def test_clamp_inside(ex):
    assert ex.clamp(5, 0, 10) == 5


# TODO: test clamp below / above / at the boundaries / lo > hi raises ValueError


@pytest.mark.parametrize("text, expected", [
    ("12.5%", 0.125),
    # TODO: add more cases — whitespace, negative, no % sign
])
def test_parse_percent(ex, text, expected):
    assert ex.parse_percent(text) == pytest.approx(expected)


# TODO: a parametrized test that every bad string raises ValueError
# @pytest.mark.parametrize("bad", ["", "%", ...])
# def test_parse_percent_rejects(ex, bad):
#     with pytest.raises(ValueError):
#         ex.parse_percent(bad)


def test_win_rate_writes_and_reads_file(ex, tmp_path):
    # tmp_path is a fresh empty folder per test — perfect for file I/O tests.
    f = tmp_path / "record.txt"
    f.write_text("7 10")
    wins, games = map(int, f.read_text().split())
    assert ex.win_rate(wins, games) == pytest.approx(0.7)
