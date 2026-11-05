# 24 — Testing your code

You direct AI to write code all day. Tests are how you know what it wrote does what you asked — they're the spec, written as executable claims. They also let you refactor without fear and they catch the bug you'd otherwise find in your published table. Every lesson in this course has been graded by pytest; today you write the tests.

## pytest in 60 seconds

A test is a function named `test_*` in a file named `test_*.py`, containing `assert`s. Run `python -m pytest`. pytest finds them, runs them, and on failure shows you the values involved.

```python
def test_win_rate():
    assert win_rate(7, 10) == 0.7
```

**Floats**: never `==`. `0.1 + 0.2 == 0.3` is False. Use `pytest.approx`:

```python
assert mean([0.1, 0.2]) == pytest.approx(0.15)
```

**Exceptions** are behaviour too — test them:

```python
with pytest.raises(ValueError):
    win_rate(5, 0)
```

## parametrize: one test, many cases

```python
@pytest.mark.parametrize("wins, games, expected", [
    (7, 10, 0.7), (0, 5, 0.0), (5, 5, 1.0),
])
def test_win_rate(wins, games, expected):
    assert win_rate(wins, games) == pytest.approx(expected)
```

Each tuple becomes its own test with its own pass/fail line. Adding a case is one line, so you add more of them.

## Fixtures and tmp_path

A fixture is setup pytest hands to your test by matching the argument name. `tmp_path` is built in: a fresh empty directory per test, so file-writing tests never clobber each other or your real data.

```python
def test_save(tmp_path):
    save_report({"x": 1}, tmp_path / "r.json")
    assert (tmp_path / "r.json").exists()
```

Custom fixtures are functions with `@pytest.fixture`. This course's `ex` and `data_dir` (in `conftest.py`) are exactly that — `ex` is why the same tests can grade your file and the solution.

## Where bugs live: edge cases

Bugs cluster at the edges. A checklist worth memorising:

- **Empty** inputs (`[]`, `""`, 0 games).
- **Boundaries**: exactly at a threshold — `<` vs `<=` is the most common bug in tax brackets, win conditions and loop guards.
- **One** element; **even vs odd** lengths.
- **Negative** numbers, zero, huge numbers.
- **Type** surprises: int where float expected, `"7"` where 7 expected, `None`.
- **Infinite** loops: what if the condition is never met?

## Test-first

Write the test before the function. It forces you to decide what the function *should* do — including the awkward cases — before you're anchored by what you built. With AI-generated code this is the move: write the tests yourself, let the model write the implementation, and the tests decide whether you accept it.

## Who tests the tests?

A test suite that passes everything is worthless. **Mutation testing** checks a suite by running it against deliberately broken versions ("mutants") of the code: a good suite kills them all. Exercises 6–7 grade you exactly this way.

## Worked example

`example.py` has a Paradox-style treasury function, `months_until_broke(treasury, income, expenses)`, in two versions. v1 has two bugs: it loops forever on a balanced budget, and it treats `treasury == 0` as solvent-and-done. A hand-rolled harness runs a case table against both and prints ok/FAIL — that's all pytest is doing underneath. v2 fixes both (guard clause; `>=`). The bottom of the file has the same cases as real `parametrize`d pytest tests plus `approx` and `tmp_path` examples. Run `python example.py`, then `python -m pytest example.py -q`.

## Exercises

In `exercises.py`:

1. `clamp(x, lo, hi)`.
2. `win_rate(wins, games)` with validation.
3. `parse_percent(text)` — do this one **test-first**: fill in `my_tests.py` before implementing.
4. `find_median_bug_cases()` — return inputs that break `buggy_median`.
5. `find_tax_bug_incomes()` — return incomes where `buggy_tax` is wrong (read its docstring carefully; the bug isn't where you'd first look).
6. `check_clamp(clamp_fn)` — write a test suite as a function; graded against a correct clamp and four mutants.
7. `check_win_rate(win_rate_fn)` — same, against five mutants.

`my_tests.py` is yours: ungraded practice with TODOs. Run it with `python -m pytest lessons/24_testing_your_code/my_tests.py` from the course folder.

## How to check

Double-click `check.bat` in the course folder and type 24.
