"""Validate the bank and print counts. python -m rulesbank.validate"""
import sys
from collections import Counter

from . import bank


def main():
    try:
        s = bank.load()
    except ValueError as e:
        print(e)
        return 1
    print(f"{len(s)} scenarios, all valid")
    for field in ("category", "kind", "difficulty", "confidence"):
        print(f"\n{field}:")
        for k, n in sorted(Counter(x[field] for x in s).items()):
            print(f"  {k:<32}{n:>4}")
    unsure = [x["id"] for x in s if x["confidence"] == "unsure"]
    if unsure:
        print(f"\nflagged unsure ({len(unsure)}): {', '.join(unsure)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
