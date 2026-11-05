# 25 — Capstone: Is the polling average biased?

This one is a research project, not a drill. You'll take messy poll-level data to a defensible answer with honest uncertainty, the way you would for a fellowship memo. Everything from the course shows up: pandas cleaning, groupby, merges, weighted means, t-tests, the bootstrap, plotting, testable functions.

Read this README as the memo you're building towards.

---

## Question

Across recent elections, does the final state polling average systematically miss in one direction? I.e., is the mean of (poll-average margin − actual margin) different from zero — and how sure can we be?

## Data

`data/` is synthetic, made by `make_data.py` (read its docstring — it states the true data-generating process, so you can check whether your method recovers it). Twelve elections (1980–2024) × ten swing states.

- `polls.csv` — one row per poll: `election, state, pollster, end_date, sample_size, dem, rep`. Deliberately messy: lower-case and space-padded state codes, missing sample sizes, missing toplines, duplicate rows.
- `results.csv` — `election, state, election_date, dem, rep`.

Margin = dem − rep, in points. Error = poll average − actual. Positive error = polls overstated the Democrat.

The generator builds in three error sources: a **shared election-level bias** (every state in a cycle misses in the same direction — think 2016, 2020), a race-specific miss, pollster **house effects**, plus sampling noise ≈ 100/√n. Polls taken further out are noisier.

## Method

1. **Clean** (`load_data`). Normalise the join key (`state`) *before* anything else, or " pa" silently becomes a separate race that matches no result. Drop incomplete and duplicate rows.
2. **Average** (`polling_averages`). Only polls ending 0–21 days before election day; weight by sample size. A weighted mean is `sum(w*x) / sum(w)` — in pandas, multiply into a helper column, then group-sum both. Weighting by n is approximately inverse-variance weighting, since sampling variance ∝ 1/n. Some races have no polls in the window — they drop out (note it in the memo).
3. **Error** (`race_errors`). Inner-merge averages to results.
4. **Per-election bias** (`election_bias`). Mean error over states, with a t-interval over states (n ≈ 10, so t, not 1.96). This CI says how precisely we've pinned down *that cycle's* shared miss, given race-level scatter.
5. **Overall test** (`bias_tests`). Here's the crux. You have ~110 race errors, but they are **not 110 independent observations**. Races in the same election share the same bias draw: once you know Pennsylvania overshot in 2016, you expect Wisconsin did too. The thing that varies independently is the *election*. So: collapse to one mean per election and run a one-sample t-test on those 12 numbers. Also run the naive t-test on all races, just to see how wrong it is.
6. **Bootstrap** (`bootstrap_bias`). Resample *elections* with replacement, recompute the mean, take percentiles. Assumption-light check on the t-interval with n = 12. Resampling races instead would repeat the clustering mistake.
7. **Plot** (`plot_bias`) per-election bias with CI error bars → `output/bias_by_election.png`.
8. **Report** (`report`) — numbers plus a two-to-four-sentence summary.

## Worked example

`example.py` makes the clustering argument concrete before you start. It first prints the raw data's problems (22 distinct "state codes" for 10 states, missing values, 15 duplicates). Then it simulates 2,000 worlds where polls are **unbiased on average** but each election has a shared shock, and runs both tests in each. At p < 0.05 the election-level test flags ~5% of worlds (correct — that's what α means). The naive race-level test flags **~47%**. That's the false-discovery machine you build by treating correlated rows as independent. It also prints the design effect, 1 + (m−1)ρ: with ρ ≈ 0.64 and 10 states per election, 120 races carry about as much information as ~18 independent ones. The p-value histogram goes to `output/false_positives.png`.

## Pitfalls (put these in any real memo)

- **Clustering.** Covered above. The same issue shows up whenever observations share a shock: students in classrooms, firms in industries, provinces in a country-year. Unit of analysis = level at which the treatment or shock varies.
- **Small n.** Twelve elections is all you get, and adding states doesn't add elections. Expect wide intervals; "not significant" here often means "not enough elections", not "no bias".
- **Non-stationarity.** Pollsters re-weight after a miss (by education after 2016, for example). Bias in 1984 may say nothing about 2028. A pooled mean assumes a stable process.
- **Overfitting the method.** Window length, weighting scheme, which states count — each choice moves the estimate. If you try ten and report the one with p < 0.05, the p-value means nothing. Fix the choices up front (or report all of them).
- **Selection.** Swing states get more polls and maybe different pollsters. Races with no polls in the window just drop out.

## Exercises

In `exercises.py`, in order — each feeds the next:

1. `load_data(polls_path, results_path)` → cleaned `(polls, results)`.
2. `polling_averages(polls, results, window_days=21)` → weighted average per race.
3. `race_errors(averages, results)` → error per race.
4. `election_bias(errors, level=0.95)` → per-election mean and t-CI.
5. `bias_tests(errors)` → clustered vs naive t-tests.
6. `bootstrap_bias(election_means, n_boot, seed)` → election-level bootstrap CI.
7. `plot_bias(bias_df, out_path)` → PNG with error bars.
8. `report(polls_path, results_path, out_dir)` → summary dict.

Once all tests pass, double-click `capstone.bat` in the course folder (or choose 6 in the `course.bat` menu). It imports **your** `exercises.py`, runs the pipeline on the real data and prints your memo summary. Then compare your estimate with the true biases that `make_data.py` prints.

## Extensions (if you want more)

- **House effects:** estimate each pollster's mean error relative to the race average; re-average after subtracting them. Does the election-level bias shrink?
- **Window sensitivity:** plot mean bias and CI for windows of 7, 14, 21, 45, 75 days. More polls vs staler polls.
- **Does bias persist?** Correlate each election's bias with the previous one's. Twelve points, so be humble.
- **Regression:** error ~ days_before + log(sample_size) + pollster dummies, using `lstsq` from lesson 21 — with cluster-aware thinking about the standard errors.
- **Real data:** swap in a public poll archive. Your functions should only need the column names changed — that's the payoff for writing them as testable units.

## How to check

Double-click `check.bat` in the course folder and type 25.
