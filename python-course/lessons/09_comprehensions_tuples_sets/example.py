"""Worked example: a trade network with tuples, sets and comprehensions.

Run:  python example.py
"""

# (exporter, importer, good, value)
flows = [
    ("Venice", "Genoa", "glass", 120),
    ("Venice", "Milan", "spices", 300),
    ("Genoa", "Venice", "iron", 80),
    ("Genoa", "Milan", "wine", 150),
    ("Milan", "Venice", "cloth", 200),
    ("Milan", "Florence", "iron", 90),
    ("Florence", "Genoa", "cloth", 110),
    ("Florence", "Venice", "wool", 160),
    ("Venice", "Florence", "wine", 70),
]

nations = {exp for exp, _, _, _ in flows} | {imp for _, imp, _, _ in flows}
print("Nations:", sorted(nations))


def partners(nation):
    return {imp for exp, imp, _, _ in flows if exp == nation} | \
           {exp for exp, imp, _, _ in flows if imp == nation}


print("\nTrade partners")
for n in sorted(nations):
    print(f"  {n:<9} {sorted(partners(n))}")

print("\nShared partners of Venice & Genoa:", sorted(partners("Venice") & partners("Genoa")))

# Exclusive goods: what I export minus what anyone else exports
print("\nExclusive exports")
for n in sorted(nations):
    mine = {g for exp, _, g, _ in flows if exp == n}
    others = {g for exp, _, g, _ in flows if exp != n}
    print(f"  {n:<9} {sorted(mine - others) or '-'}")

# Totals by exporter and top-k with deterministic tie-break
totals = {n: sum(v for exp, _, _, v in flows if exp == n) for n in nations}
print("\nExport totals:", dict(sorted(totals.items())))
ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
print("Top 3 exporters:")
for rank, (name, total) in enumerate(ranked[:3], start=1):
    print(f"  {rank}. {name:<9} {total}")

low, high = min(totals.values()), max(totals.values())
print(f"\nSpread of export totals: {low}..{high}")
