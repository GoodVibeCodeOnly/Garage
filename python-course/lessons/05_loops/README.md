# 05 — Loops

Simulations are loops. A Paradox game is one loop: `while game_running: tick()`. This lesson covers the loop forms and the handful of patterns you'll use over and over: accumulate, search, count streaks, walk two sequences together.

You'll need lists at a basic level here. A list is an ordered sequence in square brackets: `incomes = [600, 640, 590]`. `len(incomes)` is 3, `incomes[0]` is 600, and `incomes.append(610)` adds to the end. Lists get a full lesson later.

## for: do something per item

```python
for income in [600, 640, 590]:
    print(income)
```

`for` binds the name to each item in turn and runs the indented body once per item. It works on anything iterable: lists, strings (char by char), ranges, file lines, and more.

## range

```python
range(5)          # 0, 1, 2, 3, 4      (stop is exclusive, like slicing)
range(1, 13)      # 1 .. 12            (months)
range(0, 100, 10) # 0, 10, ..., 90     (step)
```

`for month in range(1, 13):` is the standard "do this twelve times, and tell me which time it is".

## Accumulation: the core pattern

Start a variable **before** the loop, update it **inside**, use it **after**:

```python
balance = 500
for month in range(1, 13):
    balance += 600 - 380
print(balance)          # 3140
```

The same shape covers totals (`total += x`), counts (`count += 1`), building lists (`result.append(x)`), and running maxima (`best = max(best, x)`). Most loop bugs are an accumulator initialised in the wrong place, often *inside* the loop so it resets every pass.

`sum(incomes)`, `max(...)`, `min(...)` do the simple cases in one call. Write the loop when the logic is more than a plain sum.

## while: loop until a condition changes

```python
balance, month = 500, 0
while balance >= 0:
    month += 1
    balance += 200 - 260
print(f"Bankrupt in month {month}")
```

Use `while` when you don't know the number of iterations in advance. The condition is checked *before* each pass. If nothing in the body can ever make it false, you have an infinite loop (Ctrl+C to stop it). Simulations should cap the iterations: `while balance >= 0 and month < 1200:`.

## break and continue

- `break` exits the loop immediately. Use it for search: stop at the first match.
- `continue` skips the rest of this pass and moves to the next item. Use it to filter out cases early instead of nesting a big `if`.

```python
for month, bal in enumerate(balances, start=1):
    if bal < 0:
        print("First deficit in month", month)
        break
```

A function that loops and `return`s from inside the loop is a cleaner `break`. That's what most of the exercises use.

## enumerate and zip

```python
for i, name in enumerate(["Prussia", "Austria"]):        # 0 Prussia, 1 Austria
for month, inc in enumerate(incomes, start=1):           # count from 1
for inc, exp in zip(incomes, expenses):                  # walk two lists in step
```

Avoid `for i in range(len(xs)):` followed by `xs[i]`. `enumerate` gives you the index and the item together, and `zip` lines up parallel sequences (it stops at the shortest).

## Worked example

`example.py` runs a 10-year treasury simulation: income grows 1% a month, expenses grow 2% a month (an army budget creeping upward), and loans are taken whenever the balance goes negative, until the debt cap is hit and the state goes bankrupt. Run `python example.py`. It saves a plot of the balance to `output/treasury.png`. Trace:

- The accumulators (`balance`, `debt`, `history`) initialised before the `while`.
- The two exit conditions on the `while`, and the `break` for bankruptcy.
- A win-streak count over a string of results, with a running counter that resets.

## Exercises

1. `total_after_months(balance, income, expenses, months)` — accumulate with `range`.
2. `compound_schedule(principal, rate, years)` — build a list year by year.
3. `months_until_bankrupt(balance, income, expenses, expense_growth)` — `while` simulation with a cap.
4. `longest_win_streak(results)` — running counter that resets.
5. `first_month_over(balances, threshold)` — `enumerate` and early exit.
6. `net_by_month(incomes, expenses)` — `zip`.
7. `taxable_income(incomes, unrest)` — `zip` with `continue`.

## How to check

Double-click `check.bat` in the course folder and type `05`.
