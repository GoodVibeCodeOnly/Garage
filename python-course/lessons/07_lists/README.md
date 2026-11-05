# 07 — Lists

A list is an ordered sequence: a match history, a monthly treasury series, a poll
time series. Most of what you'll do in pandas later is list operations scaled up,
so it pays to have these cold.

## Creating and indexing

```python
results = ["W", "L", "W", "W", "L"]
results[0]     # "W"   — first (zero-based)
results[-1]    # "L"   — last
len(results)   # 5
```

Zero-based indexing means `results[len(results)]` is an `IndexError`; the last
valid index is `len - 1`, which is why `-1` is so handy.

## Slicing

`seq[start:stop]` takes elements from `start` up to **but not including** `stop`.

```python
ratings = [1500, 1516, 1502, 1530, 1545, 1531]
ratings[1:4]    # [1516, 1502, 1530]
ratings[:3]     # first 3
ratings[-3:]    # last 3   <- "the last N matches" in one move
ratings[::2]    # every 2nd element
```

Slices never raise for out-of-range bounds; `ratings[-100:]` just gives the whole
list. A slice is a **new** list (a copy), so modifying it doesn't touch the original.

## Growing a list: `append` vs `extend`

```python
history = ["W", "L"]
history.append("W")           # ["W", "L", "W"]       — adds ONE item
history.extend(["L", "L"])    # ["W", "L", "W", "L", "L"] — adds each item
history.append(["W", "W"])    # nests a list inside! usually a bug
```

Both modify the list **in place** and return `None`. So `history = history.append(x)`
destroys your list. Same for `.sort()`.

## Sorting

```python
scores = [1530, 1490, 1612]
sorted(scores)                  # new list, ascending
sorted(scores, reverse=True)    # descending
scores.sort()                   # in place, returns None
```

`key=` is a function applied to each element to decide its rank — Lesson 06's
"functions as values" in action:

```python
players = [["Ana", 1612], ["Ben", 1490], ["Cy", 1530]]
sorted(players, key=lambda p: p[1], reverse=True)   # by rating, best first
```

## `sum`, `min`, `max`, `count`

```python
results.count("W")              # 3
sum(ratings) / len(ratings)     # mean
max(ratings) - min(ratings)     # range
```

A win rate is just `results.count("W") / len(results)`. Compare it to 0.5 and
you've got the start of every "is this strategy actually better than a coin flip?"
argument.

## Lists of lists

A table is a list of rows. `match_log[2][1]` = row 2, column 1.

```python
match_log = [
    ["Ana", "W", 16],
    ["Ana", "L", -14],
    ["Ben", "W", 12],
]
[row[2] for row in match_log]   # the rating-change column: [16, -14, 12]
```

(That `[... for ... in ...]` is a list comprehension; Lesson 09 covers it properly.
A plain `for` loop with `append` does the same thing.)

## Rolling windows

A rolling (moving) average smooths a noisy series. For window `k`, the value at
position `i` is the mean of `values[i-k+1 : i+1]`. With a list of length `n`
you get `n - k + 1` full windows:

```python
def rolling_mean(values, k):
    out = []
    for i in range(k - 1, len(values)):
        window = values[i - k + 1 : i + 1]
        out.append(sum(window) / k)
    return out
```

Getting the slice bounds right is the whole exercise — off-by-one errors live here.

## Worked example

`example.py` takes a W/L history, turns it into an Elo-style rating series (start
1500, +16 per win, -16 per loss), then reports: overall win rate vs 50%, last-10
win rate, peak rating and when it happened, and a 5-match rolling average.
It saves a chart to `output/ratings.png`.

## Exercises

In `exercises.py`:

1. `win_rate(results)` — fraction of `"W"`s.
2. `last_n(results, n)` — the last n results.
3. `rating_series(results, start=1500, k=16)` — cumulative rating after each match.
4. `peak(ratings)` — `(index, value)` of the highest rating.
5. `rolling_mean(values, k)` — rolling average.
6. `longest_streak(results, kind="W")` — longest run of consecutive results.
7. `top_players(table, n)` — sort a list of `[name, rating]` rows.
8. `record_matches(history, new_results)` — extend in place and return a summary.

## How to check

Double-click `check.bat` in the course folder and type `07`.
