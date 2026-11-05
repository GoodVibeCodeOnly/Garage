"""Generate synthetic trade flows for lesson 22. Run: python make_data.py

Hub-and-spoke world: a few big hubs trade widely; small states route through one
patron. Written to data/trade_flows.csv (exporter, importer, good, value).
"""
import pathlib
import numpy as np
import pandas as pd

rng = np.random.default_rng(22)
out = pathlib.Path(__file__).parent / "data"
out.mkdir(exist_ok=True)

hubs = ["Venice", "Genoa", "Lubeck", "Castile"]
mids = ["Flanders", "Burgundy", "Milan", "Hungary", "Poland", "Portugal"]
# small state -> its single patron (only trade link out, plus patron sells back)
spokes = {"Ragusa": "Venice", "Corsica": "Genoa", "Riga": "Lubeck",
          "Granada": "Castile", "Navarre": "Castile"}
goods = ["grain", "cloth", "wine", "iron", "spices"]

edges = set()
for a in hubs:                     # hubs fully connected
    for b in hubs:
        if a != b:
            edges.add((a, b))
for m in mids:                     # mids trade with 2 hubs and 1 other mid
    for h in rng.choice(hubs, 2, replace=False):
        edges.add((m, h)); edges.add((h, m))
    other = rng.choice([x for x in mids if x != m])
    edges.add((m, other))
for s, p in spokes.items():
    edges.add((s, p)); edges.add((p, s))

rows = []
for a, b in sorted(edges):
    scale = 100 if a in hubs and b in hubs else 30 if (a in spokes or b in spokes) else 60
    for g in rng.choice(goods, rng.integers(1, 4), replace=False):
        rows.append((a, b, g, round(float(rng.lognormal(np.log(scale), 0.6)), 1)))
df = pd.DataFrame(rows, columns=["exporter", "importer", "good", "value"])
df.to_csv(out / "trade_flows.csv", index=False)
print(f"wrote {len(df)} rows to", out / "trade_flows.csv")
