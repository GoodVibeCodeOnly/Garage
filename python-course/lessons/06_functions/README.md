# 06 — Functions

A function is a named formula. In a game economy you have a handful of formulas
(production, upkeep, tariffs) that get evaluated thousands of times with different
inputs. Writing them once, as functions, is what lets you change a rule in one place
and have the whole simulation follow.

## `def`, parameters, `return`

```python
def production(workers, output_per_worker):
    return workers * output_per_worker

production(120, 1.5)   # 180.0
```

`workers` and `output_per_worker` are **parameters** (names inside the function).
`120` and `1.5` are **arguments** (values you pass in). `return` hands a value back to
the caller and ends the function immediately.

## `return` vs `print`

This trips up almost everyone who learned from notebooks:

```python
def bad_upkeep(units):
    print(units * 2)       # shows a number on screen...

cost = bad_upkeep(10)      # prints 20
cost + 5                   # TypeError: None + int
```

`print` is for humans. `return` is for code. A function with no `return` returns
`None`. If you want to *use* the result (add it, compare it, feed it to another
function), you must `return` it. Tests in this course check return values, never
printed output.

## Defaults and keyword arguments

```python
def tariff(value, rate=0.10):
    return value * rate

tariff(500)              # 50.0  — rate defaults to 0.10
tariff(500, 0.25)        # 125.0 — positional
tariff(500, rate=0.25)   # 125.0 — keyword: self-documenting at the call site
```

Keyword arguments matter once functions have more than two or three parameters:
`simulate(1000, 0.02, 12, True)` is unreadable; `simulate(start=1000, growth=0.02,
months=12, compound=True)` is not.

One trap: never use a mutable default like `def f(items=[])` — the same list is
shared across calls. Use `None` and create the list inside.

## Docstrings

The string literal right under `def` is the docstring. `help(tariff)` shows it.
Write what goes in, what comes out, and any edge cases. That's the contract.

## Pure functions

A **pure** function's output depends only on its inputs, and it changes nothing
outside itself. `production(workers, rate)` is pure. A function that reads a global
`TAX_RATE` or appends to a global list is not. Pure functions are trivially testable
and safe to reuse — aim for them by default, especially in research code where you
want results to be reproducible.

## Scope

Names created inside a function are **local**: they exist only during that call.

```python
rate = 0.5
def f():
    rate = 0.9     # a new local name; the global is untouched
    return rate
f(); rate          # 0.9, then 0.5
```

A function *can read* a global, but relying on that makes it impure. Pass things in.

## Functions are values

A function is an object like any other. You can store it in a variable, put it in a
list, or pass it to another function:

```python
def apply_to_all(values, formula):
    return [formula(v) for v in values]

apply_to_all([100, 200], tariff)    # [10.0, 20.0]
```

Note `tariff`, not `tariff()` — you're passing the function itself, not calling it.
This is how `sorted(..., key=...)`, `map`, pandas `.apply`, and scipy optimizers all
work: you hand them a formula and they call it for you. `lambda` makes a tiny
anonymous function inline: `apply_to_all(prices, lambda p: p * 1.2)`.

## Worked example

`example.py` builds a mini province economy:

1. `production`, `upkeep` and `tariff` are separate pure functions.
2. `net_income` composes them — it calls the others and combines their results.
3. It compares two tariff policies by passing a *different tariff function* into
   the same `net_income` — functions as values.
4. It shows the `print`-vs-`return` bug live.

Run it: `python example.py`. Then try changing a default and re-running.

## Exercises

In `exercises.py`:

1. `production(workers, output_per_worker, efficiency=1.0)` — basic formula with a default.
2. `upkeep(units, cost_per_unit=2.0, discount=0.0)` — keyword-friendly upkeep.
3. `tariff_revenue(import_value, rate=0.1, exempt_below=0.0)` — threshold logic.
4. `net_income(workers, output_per_worker, units, import_value)` — compose 1–3.
5. `apply_policy(values, policy)` — call a passed-in function on each value.
6. `best_policy(import_value, policies)` — pick the name of the highest-revenue policy from a dict of functions.
7. `make_flat_tax(rate)` — return a *new function* (a closure).
8. `predict_scope()` — predict-the-output: return what a short snippet evaluates to.

## How to check

Double-click `check.bat` in the course folder and type `06`.
