# 09 — Comprehensions, Tuples, Sets

Three tools that make data-wrangling code short *and* readable: tuples for fixed
records, sets for membership and overlap, comprehensions for "transform/filter this
collection" in one line. Theme: a trade network between nations.

## Tuples and unpacking

A tuple is an immutable, fixed-length sequence — a record:

```python
flow = ("Venice", "Genoa", "wine", 120)    # exporter, importer, good, value
exporter, importer, good, value = flow     # unpacking
```

Use a tuple when position has meaning and the size is fixed (a coordinate, a
trade record, a `(key, value)` pair). Use a list when it's "many of the same thing"
that may grow. Tuples can be dict keys and set members; lists can't.

Unpacking is everywhere:

```python
for name, rating in [("Ana", 1612), ("Ben", 1490)]:  ...
for i, x in enumerate(values):  ...       # (index, value)
a, b = b, a                               # swap
best, *rest = sorted_scores               # star grabs the remainder
```

A function that "returns two things" returns one tuple: `return low, high`.

## Sets

A set is an unordered collection of **unique** items with fast `in` checks.

```python
venice = {"wine", "cloth", "glass", "spices"}
genoa  = {"wine", "iron", "cloth"}

venice | genoa     # union:        anything either exports
venice & genoa     # intersection: both export (competitors)
venice - genoa     # difference:   only Venice exports
venice ^ genoa     # symmetric difference: exactly one of them
```

`set(some_list)` deduplicates. `{}` is an empty **dict**; an empty set is `set()`.
Sets have no order and no indexing — `sorted(s)` when you need a stable output.

## Comprehensions

A list comprehension builds a list from an iterable, optionally filtering:

```python
values = [f[3] for f in flows]                         # transform
big    = [f for f in flows if f[3] > 100]              # filter
pairs  = [(exp, imp) for exp, imp, _, _ in flows]      # unpack inside
```

Read it as: *"`expression` for each `item` in `iterable` if `condition`"*. It's
equivalent to the `for` + `append` loop you'd otherwise write — no more, no less.

Same syntax with braces gives sets and dicts:

```python
exporters = {f[0] for f in flows}                          # set comprehension
totals    = {n: total_exports(n) for n in exporters}       # dict comprehension
inverted  = {v: k for k, v in mapping.items()}             # swap keys/values
```

Rule of thumb: if a comprehension needs more than one `for` and one `if`, or you
have to squint, write the loop instead. (`_` is the convention for "a value I'm
ignoring".)

## Sorting with tuples

Tuples compare element by element, left to right. That gives free multi-level
sorting:

```python
totals = [("Genoa", 300), ("Venice", 450), ("Milan", 300)]
sorted(totals, key=lambda t: (-t[1], t[0]))
# [("Venice", 450), ("Genoa", 300), ("Milan", 300)]
```

Negating the number sorts it descending while the name still sorts ascending —
a deterministic tie-break, which matters when tests (or reviewers) need the same
answer every time. Top-k is then just `[:k]`.

## Worked example

`example.py` defines a list of trade-flow tuples and answers:

- Who are each nation's trade partners (a set built with a comprehension)?
- Which partners do two nations share (`&`)?
- Which goods does each nation export exclusively (`-` against everyone else's union)?
- Total exports per nation (dict comprehension) and the top-3 exporters, tie-broken by name.

## Exercises

In `exercises.py` (each `flow` is `(exporter, importer, good, value)`):

1. `min_max(values)` — return a tuple; practice multiple return values.
2. `partners(flows, nation)` — set of nations it trades with, either direction.
3. `shared_partners(flows, a, b)` — intersection.
4. `exclusive_goods(flows, nation)` — goods only this nation exports.
5. `big_flows(flows, threshold)` — list comprehension with filter.
6. `export_totals(flows)` — dict of exporter → total value.
7. `top_exporters(flows, k)` — sorted with a tuple key for tie-breaks.
8. `goods_by_nation(flows)` — dict comprehension producing sets.

## How to check

Double-click `check.bat` in the course folder and type `09`.
