"""Generate the synthetic data for lesson 12. Deterministic: run it any time.

Writes data/matches.csv and data/economy.json next to this script.
"""
import csv
import json
import pathlib
import random

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

rng = random.Random(12)
PLAYERS = ["Arminius", "Basil", "Cixi", "Dandolo", "Eleanor", "Fujiwara", "Gustav", "Hatshepsut"]
FACTIONS = ["Venice", "Ottomans", "Byzantium", "Mongols"]
# Built-in imbalance: Mongols are a bit overtuned, Byzantium a bit weak.
STRENGTH = {"Venice": 0.0, "Ottomans": 0.03, "Byzantium": -0.06, "Mongols": 0.07}

rows = []
for match_id in range(1, 241):
    player = rng.choice(PLAYERS)
    faction, opponent = rng.sample(FACTIONS, 2)
    p_win = 0.5 + STRENGTH[faction] - STRENGTH[opponent]
    won = rng.random() < p_win
    duration = round(rng.uniform(12, 55), 1)
    rows.append({
        "match_id": match_id,
        "date": f"2026-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}",
        "player": player,
        "faction": faction,
        "opponent": opponent,
        "won": int(won),
        "duration_min": duration,
    })

with open(DATA / "matches.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

economy = {
    "version": "1.4.2",
    "starting_gold": 500,
    "tax_rate": 0.15,
    "factions": {
        "Venice": {"income_bonus": 0.20, "capital": "Venice"},
        "Ottomans": {"income_bonus": 0.05, "capital": "Constantinople"},
        "Byzantium": {"income_bonus": 0.00, "capital": "Constantinople"},
        "Mongols": {"income_bonus": -0.10, "capital": "Karakorum"},
    },
    "units": {
        "levy": {"cost": 20, "upkeep": 1},
        "spearmen": {"cost": 45, "upkeep": 2},
        "crossbowmen": {"cost": 60, "upkeep": 3},
        "knights": {"cost": 150, "upkeep": 8},
        "horse_archers": {"cost": 110, "upkeep": 5},
    },
}
with open(DATA / "economy.json", "w", encoding="utf-8") as f:
    json.dump(economy, f, indent=2)

print(f"wrote {len(rows)} matches and economy.json to {DATA}")
