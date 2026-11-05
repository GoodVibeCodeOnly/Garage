"""A tiny reusable module. example.py imports it with `import sim_tools`.

Running this file directly (python sim_tools.py) executes the block at the
bottom; importing it does not. That's what `if __name__ == "__main__"` is for.
"""
import random


def season_winrate(n_games, p_win, rng):
    """Observed win rate over one season of n_games."""
    wins = sum(rng.random() < p_win for _ in range(n_games))
    return wins / n_games


def share_below(values, cutoff):
    """Fraction of values strictly below cutoff."""
    return sum(v < cutoff for v in values) / len(values)


if __name__ == "__main__":
    rng = random.Random(0)
    print("quick self-test:", season_winrate(100, 0.55, rng))
