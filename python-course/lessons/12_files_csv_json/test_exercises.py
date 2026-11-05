import csv
import json

import pytest


def _expected_rates(path):
    games, wins = {}, {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            games[row["faction"]] = games.get(row["faction"], 0) + 1
            wins[row["faction"]] = wins.get(row["faction"], 0) + int(row["won"])
    return {k: wins[k] / games[k] for k in games}


# Exercise 1
def test_count_nonblank_lines(ex, tmp_path):
    p = tmp_path / "notes.txt"
    p.write_text("first\n\n   \nsecond\nthird\n")
    assert ex.count_nonblank_lines(p) == 3


def test_count_nonblank_lines_csv(ex, data_dir):
    assert ex.count_nonblank_lines(data_dir / "matches.csv") == 241, "240 rows + header"


# Exercise 2
def test_write_lines(ex, tmp_path):
    p = tmp_path / "sub" / "out.txt"
    result = ex.write_lines(p, ["a", "b", "c"])
    assert p.read_text() == "a\nb\nc\n"
    assert result == p


def test_write_lines_overwrites(ex, tmp_path):
    p = tmp_path / "out.txt"
    p.write_text("old stuff\n")
    ex.write_lines(p, ["new"])
    assert p.read_text() == "new\n"


# Exercise 3
def test_read_matches(ex, data_dir):
    rows = ex.read_matches(data_dir / "matches.csv")
    assert len(rows) == 240
    first = rows[0]
    assert first["match_id"] == 1
    assert isinstance(first["won"], bool), "won should be converted to bool"
    assert isinstance(first["duration_min"], float)
    assert isinstance(first["player"], str)
    assert set(first) == {"match_id", "date", "player", "faction", "opponent", "won", "duration_min"}


# Exercise 4
def test_faction_win_rates(ex, data_dir):
    path = data_dir / "matches.csv"
    got = ex.faction_win_rates(path)
    expected = _expected_rates(path)
    assert set(got) == set(expected)
    for k in expected:
        assert got[k] == pytest.approx(expected[k]), k


def test_faction_win_rates_small(ex, tmp_path):
    p = tmp_path / "m.csv"
    p.write_text(
        "match_id,date,player,faction,opponent,won,duration_min\n"
        "1,2026-01-01,A,Venice,Mongols,1,20.0\n"
        "2,2026-01-02,B,Venice,Ottomans,0,30.5\n"
        "3,2026-01-03,C,Mongols,Venice,1,25.0\n"
    )
    assert ex.faction_win_rates(p) == {"Venice": 0.5, "Mongols": 1.0}


# Exercise 5
def test_write_win_rates(ex, tmp_path):
    out = tmp_path / "rates.csv"
    result = ex.write_win_rates({"Venice": 0.5, "Mongols": 0.612345, "Byzantium": 0.41}, out)
    assert result == out
    with open(out, newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["faction", "win_rate"]
    assert [r[0] for r in rows[1:]] == ["Mongols", "Venice", "Byzantium"], "sort highest first"
    assert float(rows[1][1]) == pytest.approx(0.6123)
    assert len(rows) == 4, "no blank lines / extra rows"


# Exercise 6
def test_army_cost(ex, data_dir):
    cfg = data_dir / "economy.json"
    assert ex.army_cost(cfg, {"levy": 10, "knights": 2}) == 10 * 20 + 2 * 150
    assert ex.army_cost(cfg, {}) == 0


def test_army_cost_unknown(ex, data_dir):
    with pytest.raises(KeyError):
        ex.army_cost(data_dir / "economy.json", {"dragons": 1})


# Exercise 7
def test_rebalance_costs(ex, data_dir, tmp_path):
    src = data_dir / "economy.json"
    before = src.read_text()
    out = tmp_path / "patched.json"
    new = ex.rebalance_costs(src, out, {"knights": 1.1, "horse_archers": 0.9})
    assert src.read_text() == before, "don't modify the original file"
    on_disk = json.loads(out.read_text())
    assert on_disk == new
    assert on_disk["units"]["knights"]["cost"] == 165
    assert on_disk["units"]["horse_archers"]["cost"] == 99
    assert on_disk["units"]["levy"]["cost"] == 20
    assert on_disk["tax_rate"] == 0.15, "the rest of the config must survive"
    assert "\n  " in out.read_text(), "write with indent=2"


def test_rebalance_unknown_unit(ex, data_dir, tmp_path):
    with pytest.raises(KeyError):
        ex.rebalance_costs(data_dir / "economy.json", tmp_path / "x.json", {"dragons": 2})


# Exercise 8
def test_list_files(ex, tmp_path):
    for name in ["b.csv", "a.csv", "c.json", "notes.txt"]:
        (tmp_path / name).write_text("x")
    (tmp_path / "nested.csv").mkdir()
    assert ex.list_files(tmp_path, ".csv") == ["a.csv", "b.csv"]
    assert ex.list_files(tmp_path, ".json") == ["c.json"]
    assert ex.list_files(tmp_path, ".xlsx") == []


def test_list_files_data(ex, data_dir):
    assert ex.list_files(data_dir, ".csv") == ["matches.csv"]
