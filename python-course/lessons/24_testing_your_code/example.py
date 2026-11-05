"""Lesson 24 worked example: test a treasury function, find its bug, fix it.

Runs a tiny hand-rolled test harness so you can see what pytest automates.
Then, for real: python -m pytest example.py -q  (pytest collects test_* functions
from any file you name explicitly).
"""
import pytest


def months_until_broke_v1(treasury, income, expenses):
    """Months until treasury < 0 given a constant monthly balance. None if never."""
    months = 0
    while treasury > 0:
        treasury += income - expenses
        months += 1
    return months


def months_until_broke_v2(treasury, income, expenses):
    if income >= expenses:
        return None                       # never goes broke: guard the infinite loop
    months = 0
    while treasury >= 0:                  # "broke" means BELOW zero, so >= not >
        treasury += income - expenses
        months += 1
    return months


CASES = [
    # (treasury, income, expenses, expected)  — each line is a claim about behaviour
    (100, 10, 60, 3),     # 100 -> 50 -> 0 -> -50 : broke after 3 months
    (0, 0, 1, 1),         # edge: empty treasury still has 0 >= 0, goes broke month 1
    (500, 50, 50, None),  # balanced budget: never
    (500, 80, 50, None),  # surplus: never
]


def run(fn):
    print(f"\n{fn.__name__}")
    for t, i, e, exp in CASES:
        if exp is None and fn is months_until_broke_v1:
            print(f"  SKIP  ({t},{i},{e}) -> v1 would loop forever: that's a bug too")
            continue
        got = fn(t, i, e)
        status = "ok  " if got == exp else "FAIL"
        print(f"  {status}  ({t},{i},{e}) expected {exp}, got {got}")


run(months_until_broke_v1)
run(months_until_broke_v2)


# --- The same checks as real pytest tests --------------------------------

@pytest.mark.parametrize("t,i,e,exp", CASES)
def test_months_until_broke(t, i, e, exp):
    assert months_until_broke_v2(t, i, e) == exp


def test_float_money():
    assert 0.1 + 0.2 == pytest.approx(0.3)   # never == on floats


def test_writes_ledger(tmp_path):
    ledger = tmp_path / "ledger.csv"
    ledger.write_text("month,balance\n1,50\n")
    assert ledger.read_text().count("\n") == 2


if __name__ == "__main__":
    print("\nNow run:  python -m pytest example.py -q")
