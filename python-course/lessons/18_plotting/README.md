# 18 — Plotting with matplotlib

A chart is often the fastest way to find out your data is wrong, and the fastest way to make an argument in a paper. matplotlib is ugly in places, but it's the standard library everything else builds on, so learn its mental model once.

## The model: Figure and Axes

- A **Figure** is the whole canvas, the PNG file.
- An **Axes** is one plot inside it, with its own x/y axes, title and data. One figure can hold many.

Always use the explicit, "object-oriented" style:

```python
import matplotlib
matplotlib.use("Agg")            # render to files, never pop up windows
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(years, balance, label="Castile")
ax.set_title("Treasury over time")
ax.set_xlabel("Year"); ax.set_ylabel("Ducats")
ax.legend()
fig.savefig("treasury.png", dpi=110)
plt.close(fig)
```

You'll see `plt.plot(...)` / `plt.title(...)` in tutorials. That style draws on whichever axes is "current", which falls apart once you have more than one panel. Stick to `ax.`.

## The core chart types

```python
ax.plot(x, y)                    # line: trajectories over time
ax.bar(names, heights)           # bar: compare categories
ax.hist(values, bins=20)         # histogram: the shape of one variable
ax.scatter(x, y)                 # scatter: relationship between two variables
ax.axhline(0.5); ax.axvline(0)   # reference lines: the baseline you're comparing to
```

## Error bars

A win rate without uncertainty is half a fact. `ax.bar(names, p, yerr=se, capsize=4)` draws ± `se` on each bar. With `yerr=1.96*se` you get an approximate 95% confidence interval (lesson 19 explains why). Add `axhline(0.5)` and anyone can see straight away which factions are clearly above a coin flip.

## Multiple panels

```python
fig, axes = plt.subplots(1, 3, figsize=(15, 4))   # axes is an array of 3 Axes
axes[0].plot(...); axes[1].bar(...); axes[2].hist(...)
fig.tight_layout()
```

A good design pattern: write each plot as a function that **takes an `ax` argument** and draws on it. Then the same function produces a stand-alone chart or one panel of a dashboard.

## Plots are inspectable objects

Everything you draw becomes an object attached to the Axes:

```python
ax.lines                     # list of Line2D (from plot, axhline, ...)
ax.lines[0].get_ydata()      # the actual numbers
ax.patches                   # bars and histogram rectangles
ax.collections[0].get_offsets()  # scatter points
ax.get_title(), ax.get_xlabel()
```

That's how the tests check your work. It's also handy for debugging: "did that line really get the data I think?"

## Worked example

`example.py` fakes three datasets: treasury random walks for Castile, Venice and the Ottomans; win/loss records for four factions; and 300 polling errors. It draws them as one 1×3 figure and saves `output/campaign_report.png`. Open the PNG. Gaul's 60% win rate looks impressive until you see its error bar dips below 50%: 30 games isn't enough. Then the script inspects its own axes the same way the tests will.

## Exercises

In `exercises.py`. Each plotting function takes an optional `ax` and returns `(fig, ax)`:

1. `plot_treasury(years, treasuries, ax=None)`: one labelled line per nation.
2. `win_rate_bars(factions, wins, games, ax=None)`: bars with standard-error bars and a 50% line.
3. `error_histogram(errors, bins=20, ax=None)`: a histogram with a zero line.
4. `scatter_sample_vs_error(sample_sizes, abs_errors, ax=None)`: a scatter plot.
5. `dashboard(...)`: three panels built from exercises 1-3. Returns the Figure.
6. `save_figure(fig, path, dpi=100)`: save, close, return the path.

## How to check

Double-click `check.bat` in the course folder and type `18`.
