"""Lesson 12 exercises: files, CSV, JSON.

How to check: double-click `check.bat` in the course folder and type 12.
(Or from the course folder: python -m pytest lessons/12_files_csv_json)

Every function takes paths as ARGUMENTS. Never hard-code "data/matches.csv"
inside a function - the caller decides where files live.
Data: data/matches.csv and data/economy.json (made by make_data.py).
"""
import csv
import json
from pathlib import Path


# Exercise 1
def count_nonblank_lines(path):
    """Return the number of lines in the text file at `path` that contain
    something other than whitespace."""
    raise NotImplementedError("Exercise 1")


# Exercise 2
def write_lines(path, lines):
    """Write each string in `lines` to the file at `path`, one per line,
    each line ending in "\\n". Overwrite the file if it exists. Create the
    parent folder if it doesn't exist (Path.mkdir(parents=True, exist_ok=True)).
    Return the path as a pathlib.Path.
    """
    raise NotImplementedError("Exercise 2")


# Exercise 3
def read_matches(path):
    """Read the matches CSV with csv.DictReader and return a list of dicts,
    one per row, with types converted:
        match_id     -> int
        won          -> bool  (the file stores "1"/"0")
        duration_min -> float
    All other columns stay as strings.
    """
    raise NotImplementedError("Exercise 3")


# Exercise 4
def faction_win_rates(path):
    """Return {faction: win_rate} from the matches CSV at `path`, where
    win_rate = wins / games for matches where that faction was `faction`
    (ignore the `opponent` column here). Floats between 0 and 1.
    """
    raise NotImplementedError("Exercise 4")


# Exercise 5
def write_win_rates(rates, out_path):
    """Write a {faction: rate} dict to CSV at `out_path` with csv.DictWriter.

    Header: faction,win_rate
    Rows sorted by win_rate, highest first. Round win_rate to 4 decimals.
    Open with newline="" (see README). Return out_path as a Path.
    """
    raise NotImplementedError("Exercise 5")


# Exercise 6
def army_cost(config_path, army):
    """Load the economy JSON at `config_path` and return the total gold cost
    of `army`, a dict like {"levy": 10, "knights": 2}, using
    config["units"][name]["cost"]. Unknown unit -> let the KeyError happen.
    """
    raise NotImplementedError("Exercise 6")


# Exercise 7
def rebalance_costs(config_path, out_path, multipliers):
    """Patch-notes time. Load the config, multiply each listed unit's cost by
    its multiplier, round to the nearest int with round(), and write the
    WHOLE config (everything else unchanged) as JSON to `out_path` with
    indent=2. Return the new config dict.

    multipliers example: {"knights": 1.1, "horse_archers": 0.9}
    Raise KeyError if a multiplier names a unit that doesn't exist.
    Do not modify the file at config_path.
    """
    raise NotImplementedError("Exercise 7")


# Exercise 8
def list_files(folder, suffix):
    """Return a sorted list of the NAMES (not full paths) of files directly in
    `folder` whose suffix equals `suffix` (e.g. ".csv"). Ignore subfolders.
    """
    raise NotImplementedError("Exercise 8")
