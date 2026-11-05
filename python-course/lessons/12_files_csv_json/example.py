"""Worked example: read match results + economy config, write a report.

Run: python example.py   (writes output/report.json)
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent          # fine in a script; not in exercise functions
DATA = HERE / "data"
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

# --- CSV in -----------------------------------------------------------------
with open(DATA / "matches.csv", newline="", encoding="utf-8") as f:
    matches = list(csv.DictReader(f))
print(f"{len(matches)} matches. First row as the csv module sees it:")
print(" ", matches[0])               # note: every value is a string

# Player records: wins and games
record = {}
for m in matches:
    wins, games = record.get(m["player"], (0, 0))
    record[m["player"]] = (wins + int(m["won"]), games + 1)

# --- JSON in ----------------------------------------------------------------
config = json.loads((DATA / "economy.json").read_text(encoding="utf-8"))
print(f"\nConfig v{config['version']}, units:", ", ".join(config["units"]))
cheapest = min(config["units"], key=lambda u: config["units"][u]["cost"])
print("Cheapest unit:", cheapest)

# --- CSV out ----------------------------------------------------------------
table = OUT / "player_records.csv"
with open(table, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["player", "wins", "games", "win_rate"])
    w.writeheader()
    for player, (wins, games) in sorted(record.items()):
        w.writerow({"player": player, "wins": wins, "games": games,
                    "win_rate": round(wins / games, 3)})
print(f"\nWrote {table.relative_to(HERE)}:")
print(table.read_text())

# --- JSON out ---------------------------------------------------------------
report = {"matches": len(matches), "cheapest_unit": cheapest,
          "best_player": max(record, key=lambda p: record[p][0] / record[p][1])}
(OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("report.json:", report)
