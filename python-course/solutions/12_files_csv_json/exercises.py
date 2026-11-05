"""Lesson 12 solutions: files, CSV, JSON."""
import csv
import json
from pathlib import Path


# Exercise 1
def count_nonblank_lines(path):
    # Iterating a file object yields lines lazily - fine for huge files.
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())
    # Alternative: len([l for l in Path(path).read_text().splitlines() if l.strip()])


# Exercise 2
def write_lines(path, lines):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    return path


# Exercise 3
def read_matches(path):
    # csv gives you strings for everything; converting types is your job.
    with open(path, newline="", encoding="utf-8") as f:
        rows = []
        for row in csv.DictReader(f):
            row["match_id"] = int(row["match_id"])
            row["won"] = row["won"] == "1"
            row["duration_min"] = float(row["duration_min"])
            rows.append(row)
    return rows


# Exercise 4
def faction_win_rates(path):
    games, wins = {}, {}
    for m in read_matches(path):
        f = m["faction"]
        games[f] = games.get(f, 0) + 1
        wins[f] = wins.get(f, 0) + m["won"]  # True counts as 1
    return {f: wins[f] / games[f] for f in games}


# Exercise 5
def write_win_rates(rates, out_path):
    out_path = Path(out_path)
    ordered = sorted(rates.items(), key=lambda kv: kv[1], reverse=True)
    # newline="" stops csv writing blank lines between rows on Windows.
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["faction", "win_rate"])
        writer.writeheader()
        for faction, rate in ordered:
            writer.writerow({"faction": faction, "win_rate": round(rate, 4)})
    return out_path


# Exercise 6
def army_cost(config_path, army):
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    units = config["units"]
    return sum(units[name]["cost"] * count for name, count in army.items())


# Exercise 7
def rebalance_costs(config_path, out_path, multipliers):
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    for unit, mult in multipliers.items():
        if unit not in config["units"]:
            raise KeyError(unit)
        config["units"][unit]["cost"] = round(config["units"][unit]["cost"] * mult)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    return config


# Exercise 8
def list_files(folder, suffix):
    return sorted(p.name for p in Path(folder).iterdir()
                  if p.is_file() and p.suffix == suffix)
