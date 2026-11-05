"""Worked example: cleaning a messy poll dump without crashing.

Run: python example.py
"""
import traceback

RAW = [
    "YouGov, 2024-03-01, 1500, 45%",
    "Ipsos, 2024-03-02, 900, 41.5%",
    "Survation, 2024-03-03, n/a, 44%",   # bad sample
    "Opinium, 2024-03-04, 1200",         # missing field
    "Deltapoll, 2024-03-05, 1000, 147%",  # impossible share
    "Savanta, 2024-03-06, 2000, 43%",
]


def parse(line):
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 4:
        raise ValueError(f"expected 4 fields, got {len(parts)}")
    name, date, sample, share = parts
    sample = int(sample)                     # may raise ValueError
    share = float(share.rstrip("%")) / 100   # may raise ValueError
    if not 0 <= share <= 1:
        raise ValueError(f"share out of range: {share:.0%}")
    return {"pollster": name, "sample": sample, "share": share}


# 1. What an unhandled error looks like. We catch it only to print the
#    traceback and keep going - read it bottom-up.
print("=== A traceback, read bottom-up ===")
try:
    parse(RAW[2])
except ValueError:
    traceback.print_exc(limit=2)

# 2. try / except / else / finally over every line.
print("\n=== Parsing all lines ===")
good, bad = [], []
for i, line in enumerate(RAW, start=1):
    try:
        rec = parse(line)
    except ValueError as exc:
        bad.append((i, str(exc)))
        print(f"line {i}: SKIP  ({exc})")
    else:
        good.append(rec)
        print(f"line {i}: ok    {rec['pollster']:<10} {rec['share']:.1%}")
    finally:
        pass  # would close files / release locks; runs no matter what

# 3. Weighted average, with an assert guarding our own assumption.
total = sum(r["sample"] for r in good)
assert total > 0, "no valid samples - upstream parsing is broken"
avg = sum(r["share"] * r["sample"] for r in good) / total
print(f"\n{len(good)} good, {len(bad)} bad. Weighted share: {avg:.2%}")
