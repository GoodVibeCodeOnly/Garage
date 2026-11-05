# Python for Research — a self-study course

Twenty-five short lessons, from reading code to a finished research
project, aimed at the level an economics/policy research fellowship
expects. Each lesson is one sitting.

**First time? Read [SETUP.md](SETUP.md).** It assumes nothing. After setup,
everything runs from **`course.bat`** (double-click).

Every model solution has been run against its tests: 25 lessons, 381
automated checks, all passing.

## How each lesson works

```
lessons/07_lists/
  README.md           the idea, in plain language, plus a walk-through of example.py
  example.py          a worked example you can run and change
  exercises.py        functions for you to write (they start as NotImplementedError)
  test_exercises.py   the automated checks; don't edit, just run
  data/, make_data.py synthetic datasets and the script that generated them (where used)
solutions/07_lists/
  exercises.py        model answers with commentary — look after you've tried
```

The loop: open the lesson (menu option 2) → read the README → run the
example (option 3), poke at it → write the exercises → check (option 1) →
repeat until green → compare with the solution. Option 4 shows your
progress across the whole course.

**Translating terminal-speak.** Lesson text sometimes says "run
`python example.py`". You never have to type that: it means menu option 3,
or press **F5** in IDLE with `example.py` open. "Run the tests" means menu
option 1 (or `check.bat`). Lesson 24 also mentions running pytest on a
single file; that's optional terminal practice, never required.

A failing test tells you which function, what it was given, what it
expected and what you returned. Read the first failure, fix that, re-run.
That loop *is* programming; getting fluent at it is half the point.

## On using AI while doing this

You direct AI coding all day, so here's the honest version: if Claude writes
the exercises, you'll learn what you already know — how to direct. The
fellowship wants to see the other thing. Suggested rule: no AI for writing
exercise code; AI is fine for *explaining* an error message or a concept
after you've stared at it for five minutes. Then type the fix yourself.

## The roadmap

**Part 1 — Reading and writing basic Python**

| # | Lesson | You'll be able to… | Theme |
|---|---|---|---|
| 01 | Reading code | trace a script line by line and predict what it does | monthly treasury tick |
| 02 | Numbers and variables | do arithmetic without float surprises; compound growth | war loans, inflation |
| 03 | Strings | format reports, parse lines of text | ledger reports |
| 04 | Conditionals | encode rules: brackets, thresholds, classifications | tax brackets, safe/lean/tossup |
| 05 | Loops | simulate step by step, accumulate, stop on a condition | treasury to bankruptcy |

**Part 2 — Organising code and data**

| # | Lesson | You'll be able to… | Theme |
|---|---|---|---|
| 06 | Functions | write small, testable, composable pieces | game-economy formulas |
| 07 | Lists | hold and slice sequences, sort by a key | match histories, ratings |
| 08 | Dictionaries | look things up, count, nest | inventories and prices |
| 09 | Tuples, sets, comprehensions | express transformations in one line | trade partners |
| 10 | Classes | bundle state with behaviour, enforce invariants | a Nation with a treasury |
| 11 | Errors and debugging | read tracebacks, handle bad input deliberately | messy poll records |
| 12 | Files: CSV and JSON | read and write real data files | match results, game config |
| 13 | Modules and simulation | Monte Carlo with reproducible randomness | is a 55% player "bad"? |

**Part 3 — Data analysis**

| # | Lesson | You'll be able to… | Theme |
|---|---|---|---|
| 14 | NumPy | vectorise: 1000 simulations in one line | treasury runs, win rates |
| 15 | pandas basics | load, select, filter, sort a dataset | 2,000 ranked matches |
| 16 | groupby and merge | aggregate and join tables correctly | pollster house effects |
| 17 | Cleaning data | turn a messy file into an analysable one | dirty trade/poll logs |
| 18 | Plotting | make honest charts with matplotlib | trajectories, error bars |

**Part 4 — Statistics and inference**

| # | Lesson | You'll be able to… | Theme |
|---|---|---|---|
| 19 | Win rates and uncertainty | standard errors, confidence intervals, binomial tests | win rate vs 50% |
| 20 | Hypothesis tests and the bootstrap | permutation tests, bootstrap CIs, t-tests, multiple comparisons | faction balance |
| 21 | Regression | OLS by hand and with numpy; read coefficients like an economist | votes vs growth |
| 22 | Trade networks | graphs as dicts, paths, embargoes, concentration | trade flows |

**Part 5 — Working like a researcher**

| # | Lesson | You'll be able to… | Theme |
|---|---|---|---|
| 23 | APIs and JSON | pull data from web APIs robustly, testably | World Bank data |
| 24 | Testing your own code | write pytest tests, find edge cases | breaking buggy functions |
| 25 | **Capstone: is the polling average biased?** | run a full analysis across elections with CIs and write it up | polling error |

## Pace

One lesson per sitting; two or three sittings a week gets you through in
two to three months. Parts 1–2 go fast if you already read code all day —
don't skip them, they're where your hands learn what your eyes already know.

## Under the hood

- `course.bat` → `tools/course.py` (the menu). `setup.bat` builds `.venv`.
  `check.bat`, `progress.bat`, `capstone.bat` are one-click shortcuts.
- `conftest.py` lets the same tests check your `exercises.py` or the model
  solution (`COURSE_SOLUTIONS=1`).
- Synthetic datasets are deterministic: re-running a lesson's `make_data.py`
  reproduces the committed files exactly.
