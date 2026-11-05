# 12 — Files, CSV and JSON

Most research work starts with "here's a file" and ends with "send me a file". This lesson covers the plumbing: paths, opening files safely, and the two formats you'll meet constantly — CSV for tables and JSON for nested config.

## pathlib: paths as objects

```python
from pathlib import Path

data = Path("data")
csv_path = data / "matches.csv"       # / joins paths, OS-independent
csv_path.exists(), csv_path.suffix    # True, ".csv"
csv_path.name, csv_path.stem          # "matches.csv", "matches"
csv_path.parent                       # Path("data")
list(data.glob("*.csv"))              # all CSVs in the folder
Path("out/reports").mkdir(parents=True, exist_ok=True)
```

Forget string concatenation with `"\\"` — `Path` handles Windows vs Mac for you.

**Design rule:** functions take a path as an argument; only the top of a script decides where files live. That makes functions testable (tests hand them a temporary folder) and reusable.

## open / with

```python
with open(path, encoding="utf-8") as f:   # "r" is the default mode
    for line in f:                        # lazily, one line at a time
        print(line.rstrip("\n"))
# file is closed here, even if an exception happened inside
```

Modes: `"r"` read, `"w"` write (truncates!), `"a"` append. Always pass `encoding="utf-8"` — Windows otherwise defaults to an older encoding and accented names break.

For small files, `Path` has one-liners: `path.read_text()` and `path.write_text(s)`.

## csv: tables

```python
import csv

with open(path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))     # each row: {"player": "Basil", "won": "1", ...}
```

Two things trip everyone up:

1. **Everything is a string.** `"1"`, `"23.5"`. Converting types is your job: `int(row["won"])`, `float(row["duration_min"])`. (`bool("0")` is `True`! Compare to `"1"` instead.)
2. **Open with `newline=""`** for both reading and writing. Without it, Windows gets a blank line between every row.

Writing:

```python
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["faction", "win_rate"])
    w.writeheader()
    w.writerow({"faction": "Venice", "win_rate": 0.52})
```

Why not just `line.split(",")`? Because the moment a field contains a comma (`"Smith, John"`) the csv module handles the quoting and you don't.

## json: nested data

JSON maps directly onto Python: objects → dicts, arrays → lists, numbers, strings, `true/false/null` → `True/False/None`.

```python
import json

with open("economy.json", encoding="utf-8") as f:
    config = json.load(f)              # file -> dict
config["units"]["knights"]["cost"]     # 150

with open("patched.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)     # dict -> file, human-readable
```

`json.loads(s)` / `json.dumps(obj)` are the string versions (the `s` is for string). Game configs, API responses, and most settings files look like this.

## Worked example

`example.py` does a round trip:

1. Reads `data/matches.csv` with `DictReader` and prints the first row so you can see every value is a string.
2. Builds a `{player: (wins, games)}` dict, converting `won` with `int()`.
3. Loads `data/economy.json`, finds the cheapest unit with `min(..., key=...)`.
4. Writes `output/player_records.csv` with `DictWriter`, then reads it back with `read_text()` to show what landed on disk.
5. Dumps a small summary to `output/report.json`.

Note that the *script* uses `Path(__file__).parent` to find its data — that's fine at the top level of a script. Your exercise functions must instead accept paths as arguments.

The data is synthetic: `make_data.py` generates it with a fixed seed (Mongols slightly overtuned, Byzantium slightly weak — see if you can spot it).

## Exercises

In `exercises.py`:

1. `count_nonblank_lines(path)` — count lines with content.
2. `write_lines(path, lines)` — write lines, creating parent folders.
3. `read_matches(path)` — `DictReader` + type conversion.
4. `faction_win_rates(path)` — `{faction: win rate}`.
5. `write_win_rates(rates, out_path)` — `DictWriter`, sorted, rounded.
6. `army_cost(config_path, army)` — price an army from the JSON config.
7. `rebalance_costs(config_path, out_path, multipliers)` — load, patch, `json.dump` with indent.
8. `list_files(folder, suffix)` — pathlib directory listing.

The tests write files into pytest's `tmp_path` — a fresh temporary folder per test — so nothing pollutes your course folder.

## How to check

Double-click `check.bat` in the course folder and type `12`.
