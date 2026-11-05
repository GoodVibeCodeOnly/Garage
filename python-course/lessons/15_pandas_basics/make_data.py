"""Generate data/matches.csv for lesson 15: ~2000 synthetic ranked matches.

Deterministic (fixed seed). Built-in imbalances worth finding:
  - Mongols are overtuned on patch 1.3, then nerfed in 1.4
  - Byzantium is weak overall but strong on the map "Bosphorus"
  - Venice vs Ottomans is a lopsided matchup in Venice's favour
  - Mongols games are shorter; Byzantium games run long
  - a couple of players are genuinely good, most are ~50%
"""
import pathlib

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent
(HERE / "data").mkdir(exist_ok=True)

rng = np.random.default_rng(15)
N = 2000

FACTIONS = ["Venice", "Ottomans", "Byzantium", "Mongols", "Genoa"]
FACTION_POP = [0.20, 0.22, 0.13, 0.27, 0.18]
MAPS = ["Bosphorus", "Steppe", "Adriatic", "Anatolia"]
PATCHES = ["1.2", "1.3", "1.4"]
PLAYERS = [f"player_{i:02d}" for i in range(1, 41)]
skill = rng.normal(0, 0.15, len(PLAYERS))
skill[[3, 17]] = [0.45, 0.35]   # two smurfs
SKILL = dict(zip(PLAYERS, skill))

base = {"Venice": 0.0, "Ottomans": 0.05, "Byzantium": -0.35, "Mongols": 0.10, "Genoa": -0.02}
patch_adj = {("Mongols", "1.3"): 0.25, ("Mongols", "1.4"): -0.15}
map_adj = {("Byzantium", "Bosphorus"): 0.55, ("Mongols", "Steppe"): 0.15, ("Venice", "Adriatic"): 0.15}
matchup_adj = {("Venice", "Ottomans"): 0.75}
length = {"Mongols": -6, "Byzantium": 7}

rows = []
for i in range(N):
    player = rng.choice(PLAYERS)
    faction = rng.choice(FACTIONS, p=FACTION_POP)
    others = [f for f in FACTIONS if f != faction]
    pop = np.array([FACTION_POP[FACTIONS.index(f)] for f in others])
    opp = rng.choice(others, p=pop / pop.sum())
    m = rng.choice(MAPS)
    patch = rng.choice(PATCHES, p=[0.3, 0.35, 0.35])

    def power(f):
        return (base[f] + patch_adj.get((f, patch), 0) + map_adj.get((f, m), 0))

    logit = (SKILL[player] + power(faction) - power(opp)
             + matchup_adj.get((faction, opp), 0) - matchup_adj.get((opp, faction), 0))
    won = rng.random() < 1 / (1 + np.exp(-logit))
    dur = rng.gamma(9, 3.2) + length.get(faction, 0) + length.get(opp, 0)
    rows.append({
        "match_id": 10000 + i,
        "player": player,
        "faction": faction,
        "opponent_faction": opp,
        "map": m,
        "won": bool(won),
        "duration_min": round(max(dur, 6), 1),
        "patch": patch,
    })

df = pd.DataFrame(rows)
df.to_csv(HERE / "data" / "matches.csv", index=False)
print(f"wrote {len(df)} rows to data/matches.csv")
print(df.groupby("faction")["won"].mean().round(3))
