"""Run the full experiment grid, write results/*.csv, results/*.json and charts/*.svg.

Usage: python run_experiments.py [--days N] [--seed S] [--quick]
Pure standard library (no numpy/matplotlib) so it runs anywhere Python 3.8+ does.
"""
import argparse
import csv
import json
import os
import random

from sim.engine import run_day, CLASSES

LEVELS = (3, 5, 7, 9)
LENGTHS = tuple(range(1, 9))
POLICIES = ("nova", "hold_early", "threat")
HERE = os.path.dirname(os.path.abspath(__file__))

SENSITIVITY = {
    "baseline": {},
    "aoe_coverage_low": {"aoe_scale": 0.6},
    "aoe_coverage_high": {"aoe_scale": 1.25},
    "wizard_exposed": {"target_weights": {"fighter": 1, "cleric": 1, "rogue": 1, "wizard": 1}},
    "clw_wand": {"wand": True},
    "blaster_loadout": {"loadout": "blaster"},
    "controller_loadout": {"loadout": "controller"},
    "day_length_unknown": {"known_length": False, "assumed_length": 4},
    "flank_rare": {"flank_prob": 0.2},
    "easier_fights": {"el_offsets": ((-2, 0.3), (-1, 0.4), (0, 0.3))},
}


def summarize(days):
    tot = {m: {c: 0 for c in CLASSES} for m in ("damage", "kills", "takedowns", "denied")}
    for d in days:
        for f in d["fights"]:
            for m in tot:
                for c in CLASSES:
                    tot[m][c] += f[m][c]
    out = {"days": len(days)}
    for m, by in tot.items():
        s = sum(by.values()) or 1
        for c in CLASSES:
            out[f"{m}_share_{c}"] = by[c] / s
    out["wizard_denied_per_day"] = tot["denied"]["wizard"] / len(days)
    out["survival"] = sum(not d["deaths"] for d in days) / len(days)
    out["completed"] = sum(d["completed"] for d in days) / len(days)
    out["tpk"] = sum(d["tpk"] for d in days) / len(days)
    out["wizard_slots_left"] = sum(d["wizard_slots_left"] for d in days) / len(days)
    out["cleric_slots_left"] = sum(d["cleric_slots_left"] for d in days) / len(days)
    out["hp_left"] = sum(d["hp_left"] for d in days) / len(days)
    return out


def by_fight(days, n):
    rows = []
    for k in range(1, n + 1):
        fs = [f for d in days for f in d["fights"] if f["k"] == k]
        if not fs:
            continue
        row = {"k": k, "fights": len(fs)}
        for m in ("damage", "takedowns"):
            s = sum(f[m][c] for f in fs for c in CLASSES) or 1
            for c in CLASSES:
                row[f"{m}_share_{c}"] = sum(f[m][c] for f in fs) / s
        row["wizard_slot_levels_spent"] = sum(f["spent"]["wizard"] for f in fs) / len(fs)
        row["cleric_slot_levels_spent"] = sum(f["spent"]["cleric"] for f in fs) / len(fs)
        rows.append(row)
    return rows


def simulate(level, n, policy, days, seed, **opts):
    rng = random.Random(f"{seed}-{level}-{n}-{policy}-{sorted(opts.items())}")
    return [run_day(level, n, rng, policy=policy, **opts) for _ in range(days)]


# ------------------------------------------------------------------ minimal SVG line chart

PALETTE = ["#2b6cb0", "#c05621", "#2f855a", "#9b2c2c", "#6b46c1", "#4a5568"]


def svg_lines(path, title, xlabel, ylabel, xs, series, ymax=None, yfmt="{:.0%}", ref=None):
    W, H, L, Rm, T, B = 640, 380, 64, 150, 40, 48
    pw, ph = W - L - Rm, H - T - B
    ymax = ymax or max(max(v for v in ys if v is not None) for _, ys in series) * 1.1 or 1
    def X(x):
        return L + (x - xs[0]) / max(1, xs[-1] - xs[0]) * pw
    def Y(y):
        return T + ph - y / ymax * ph
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'font-family="sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="22" text-anchor="middle" font-size="14" '
         f'font-weight="bold">{title}</text>']
    for i in range(6):
        yv = ymax * i / 5
        o.append(f'<line x1="{L}" x2="{L+pw}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" '
                 f'stroke="#e2e8f0"/>')
        o.append(f'<text x="{L-6}" y="{Y(yv)+4:.1f}" text-anchor="end" fill="#4a5568">'
                 f'{yfmt.format(yv)}</text>')
    for x in xs:
        o.append(f'<text x="{X(x):.1f}" y="{T+ph+16}" text-anchor="middle" '
                 f'fill="#4a5568">{x}</text>')
    if ref is not None:
        o.append(f'<line x1="{L}" x2="{L+pw}" y1="{Y(ref):.1f}" y2="{Y(ref):.1f}" '
                 f'stroke="#718096" stroke-dasharray="4 4"/>')
    o.append(f'<text x="{L+pw/2}" y="{H-10}" text-anchor="middle">{xlabel}</text>')
    o.append(f'<text x="16" y="{T+ph/2}" text-anchor="middle" '
             f'transform="rotate(-90 16 {T+ph/2})">{ylabel}</text>')
    for i, (name, ys) in enumerate(series):
        col = PALETTE[i % len(PALETTE)]
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in zip(xs, ys) if y is not None)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5"/>')
        for x, y in zip(xs, ys):
            if y is not None:
                o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3" fill="{col}"/>')
        ly = T + 14 + i * 20
        o.append(f'<line x1="{L+pw+14}" x2="{L+pw+34}" y1="{ly}" y2="{ly}" stroke="{col}" '
                 f'stroke-width="3"/><text x="{L+pw+40}" y="{ly+4}">{name}</text>')
    o.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(o))


def write_csv(path, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=600)
    ap.add_argument("--seed", type=int, default=35)
    ap.add_argument("--quick", action="store_true", help="100 days per cell, for a smoke run")
    a = ap.parse_args()
    days = 100 if a.quick else a.days
    res_dir, ch_dir = os.path.join(HERE, "results"), os.path.join(HERE, "charts")
    os.makedirs(res_dir, exist_ok=True)
    os.makedirs(ch_dir, exist_ok=True)

    grid, per_fight = [], []
    raw = {}
    for L in LEVELS:
        for n in LENGTHS:
            for pol in POLICIES:
                ds = simulate(L, n, pol, days, a.seed)
                raw[(L, n, pol)] = ds
                grid.append({"level": L, "fights_per_day": n, "policy": pol, **summarize(ds)})
                if n in (1, 4, 6, 8):
                    for r in by_fight(ds, n):
                        per_fight.append({"level": L, "fights_per_day": n, "policy": pol, **r})
        print(f"level {L} done")
    write_csv(os.path.join(res_dir, "grid.csv"), grid)
    write_csv(os.path.join(res_dir, "per_fight.csv"), per_fight)

    sens = []
    for name, opts in SENSITIVITY.items():
        for L in (5, 9):
            for n in (1, 6):
                for pol in POLICIES:
                    ds = raw[(L, n, pol)] if name == "baseline" else \
                        simulate(L, n, pol, days, a.seed, **opts)
                    s = summarize(ds)
                    sens.append({"variant": name, "level": L, "fights_per_day": n,
                                 "policy": pol, **s})
        print(f"sensitivity {name} done")
    write_csv(os.path.join(res_dir, "sensitivity.csv"), sens)

    # one BIG fight a day: a single encounter at EL +2/+3/+4 (+4 ~ four EL=APL fights of XP)
    big = []
    for L in LEVELS:
        for off in (0, 2, 3, 4):
            for pol in POLICIES:
                ds = simulate(L, 1, pol, days, a.seed, el_offsets=((off, 1.0),))
                big.append({"level": L, "el_offset": off, "policy": pol, **summarize(ds)})
    write_csv(os.path.join(res_dir, "big_fight.csv"), big)
    print("big fight done")

    # ---- charts
    def g(L, n, pol, key):
        return next(r[key] for r in grid if r["level"] == L and r["fights_per_day"] == n
                    and r["policy"] == pol)
    xs = list(LENGTHS)
    for pol in POLICIES:
        svg_lines(os.path.join(ch_dir, f"wizard_takedown_share_{pol}.svg"),
                  f"Wizard share of enemies neutralised ({pol})", "fights per day",
                  "share of takedowns", xs,
                  [(f"level {L}", [g(L, n, pol, "takedowns_share_wizard") for n in xs])
                   for L in LEVELS], ymax=0.7, ref=0.25)
    for L in LEVELS:
        svg_lines(os.path.join(ch_dir, f"shares_level{L}.svg"),
                  f"Level {L}: wizard vs fighter takedown share", "fights per day",
                  "share of takedowns", xs,
                  [(f"wiz {p}", [g(L, n, p, "takedowns_share_wizard") for n in xs])
                   for p in POLICIES] +
                  [(f"ftr {p}", [g(L, n, p, "takedowns_share_fighter") for n in xs])
                   for p in ("nova", "hold_early")], ymax=0.7, ref=0.25)
        svg_lines(os.path.join(ch_dir, f"survival_level{L}.svg"),
                  f"Level {L}: days with no PC death", "fights per day", "share of days",
                  xs, [(p, [g(L, n, p, "survival") for n in xs]) for p in POLICIES], ymax=1.0)
    for L in LEVELS:
        rows = [r for r in per_fight if r["level"] == L and r["fights_per_day"] == 6]
        ks = list(range(1, 7))
        def pf(pol, key):
            d = {r["k"]: r[key] for r in rows if r["policy"] == pol}
            return [d.get(k) for k in ks]
        svg_lines(os.path.join(ch_dir, f"by_fight_level{L}.svg"),
                  f"Level {L}, 6-fight day: wizard takedown share by fight", "fight number",
                  "wizard share of takedowns", ks,
                  [(p, pf(p, "takedowns_share_wizard")) for p in POLICIES], ymax=0.8, ref=0.25)
    with open(os.path.join(res_dir, "meta.json"), "w") as f:
        json.dump({"days_per_cell": days, "seed": a.seed}, f)
    print("done: results/ and charts/ written")


if __name__ == "__main__":
    main()
