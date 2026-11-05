"""Worked example: a player's match history as lists.

Run:  python example.py   (also writes output/ratings.png)
"""
import pathlib
import random

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

random.seed(7)
# A player who is slightly better than average: wins 56% of games.
results = ["W" if random.random() < 0.56 else "L" for _ in range(60)]

# 1. Win rate vs the 50% baseline
wins = results.count("W")
print(f"Matches: {len(results)}, wins: {wins}, win rate: {wins / len(results):.1%} (baseline 50%)")
print("Last 10:", "".join(results[-10:]), f"-> {results[-10:].count('W') / 10:.0%}")

# 2. Rating series: start 1500, +16 for a win, -16 for a loss
ratings = []
current = 1500
for r in results:
    current += 16 if r == "W" else -16
    ratings.append(current)
print("First 5 ratings:", ratings[:5])
print("Final rating:   ", ratings[-1])

# 3. Peak: max() gives the value, .index() finds where it first occurred
best = max(ratings)
print(f"Peak rating {best} after match {ratings.index(best) + 1}")

# 4. Rolling 5-match average
k = 5
rolling = []
for i in range(k - 1, len(ratings)):
    window = ratings[i - k + 1 : i + 1]
    rolling.append(sum(window) / k)
print(f"{len(ratings)} ratings -> {len(rolling)} rolling values (n - k + 1)")

# 5. A small list-of-lists table, sorted by rating
table = [["Ana", 1612], ["Ben", 1490], ["You", ratings[-1]], ["Cy", 1530]]
print("Leaderboard:")
for name, rating in sorted(table, key=lambda row: row[1], reverse=True):
    print(f"  {name:<4} {rating}")

# 6. Chart
out = pathlib.Path("output")
out.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(range(1, len(ratings) + 1), ratings, label="rating", alpha=0.5)
ax.plot(range(k, len(ratings) + 1), rolling, label=f"{k}-match rolling mean")
ax.axhline(1500, color="grey", linestyle="--", linewidth=1, label="start")
ax.set_xlabel("match")
ax.set_ylabel("rating")
ax.legend()
fig.tight_layout()
fig.savefig(out / "ratings.png", dpi=100)
print("Saved", out / "ratings.png")
