"""Generate a deliberately messy trade log: data/trades_messy.csv. Run: python make_data.py"""
import pathlib

import numpy as np
import pandas as pd

rng = np.random.default_rng(17)
OUT = pathlib.Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

# Each clean nation name has some ugly spellings a careless clerk might type.
SPELLINGS = {
    "Prussia": ["Prussia", " Prussia ", "prussia", "PRUSSIA", "Prussia  "],
    "Austria": ["Austria", "austria", " Austria"],
    "France": ["France", "france ", "FRANCE"],
    "Great Britain": ["Great Britain", "great britain", "GB", "Britain", " Britain"],
    "Russia": ["Russia", "russia", "Russia "],
}
GOODS = ["grain", "iron", "cloth", "coal", "wine"]
PRICE = {"grain": 2.5, "iron": 6.0, "cloth": 9.0, "coal": 3.0, "wine": 12.0}

rows = []
for i in range(1, 301):
    nation = rng.choice(list(SPELLINGS))
    spelled = rng.choice(SPELLINGS[nation])
    good = rng.choice(GOODS)
    qty = int(rng.integers(50, 3000))
    r = rng.random()
    if r < 0.06:
        qty_s = rng.choice(["N/A", "", "-"])
    elif r < 0.30:
        qty_s = f"{qty:,}"          # "1,200"
    else:
        qty_s = str(qty)
    if rng.random() < 0.02:
        qty_s = "999999"             # fat-finger outlier
    price = round(PRICE[good] * rng.uniform(0.8, 1.2), 2)
    price_s = f"${price:.2f}" if rng.random() < 0.3 else f"{price}"
    day = pd.Timestamp("1836-01-01") + pd.Timedelta(days=int(rng.integers(0, 365)))
    date_s = day.strftime("%Y-%m-%d") if rng.random() > 0.04 else rng.choice(["unknown", "", "1836-13-45"])
    good_s = rng.choice([good, good.upper(), f" {good}"])
    rows.append({"trade_id": i, "date": date_s, "nation": spelled, "good": good_s,
                 "quantity": qty_s, "price": price_s})

df = pd.DataFrame(rows)
# Exact duplicate rows: the same trade logged twice.
dupes = df.sample(12, random_state=17)
df = pd.concat([df, dupes]).sort_values("trade_id", kind="stable").reset_index(drop=True)
df.to_csv(OUT / "trades_messy.csv", index=False)
print(f"wrote {len(df)} rows ({len(dupes)} duplicates) to {OUT / 'trades_messy.csv'}")
