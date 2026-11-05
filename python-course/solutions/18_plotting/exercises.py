"""Lesson 18 solutions: matplotlib, object-oriented style."""
import math

import matplotlib

matplotlib.use("Agg")  # draw to files only, never open a window
import matplotlib.pyplot as plt
import numpy as np


def _fig_ax(ax):
    # Pattern: accept an optional Axes so the same function works stand-alone
    # AND as one panel of a bigger figure (exercise 5).
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
    return fig, ax


def plot_treasury(years, treasuries, ax=None):
    fig, ax = _fig_ax(ax)
    for nation, balances in treasuries.items():
        ax.plot(years, balances, label=nation)  # label= is what legend() shows
    ax.set_title("Treasury over time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Ducats")
    ax.legend()
    return fig, ax


def win_rate_bars(factions, wins, games, ax=None):
    fig, ax = _fig_ax(ax)
    wins, games = np.asarray(wins, float), np.asarray(games, float)
    p = wins / games
    se = np.sqrt(p * (1 - p) / games)  # standard error of a proportion (lesson 19)
    ax.bar(factions, p, yerr=se, capsize=4)
    # The baseline makes the question visible: is the bar clear of 50%?
    ax.axhline(0.5, linestyle="--", color="grey")
    ax.set_title("Win rate by faction")
    ax.set_ylabel("Win rate")
    ax.set_ylim(0, 1)
    return fig, ax


def error_histogram(errors, bins=20, ax=None):
    fig, ax = _fig_ax(ax)
    ax.hist(errors, bins=bins)
    ax.axvline(0, color="black")
    ax.set_title("Polling error")
    ax.set_xlabel("Polling error (points)")
    ax.set_ylabel("Number of polls")
    return fig, ax


def scatter_sample_vs_error(sample_sizes, abs_errors, ax=None):
    fig, ax = _fig_ax(ax)
    ax.scatter(sample_sizes, abs_errors, alpha=0.6)
    ax.set_title("Bigger samples, smaller errors?")
    ax.set_xlabel("Sample size")
    ax.set_ylabel("Absolute error (points)")
    return fig, ax


def dashboard(years, treasuries, factions, wins, games, errors):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    plot_treasury(years, treasuries, ax=axes[0])
    win_rate_bars(factions, wins, games, ax=axes[1])
    error_histogram(errors, ax=axes[2])
    fig.tight_layout()  # stop titles and labels overlapping
    return fig


def save_figure(fig, path, dpi=100):
    fig.savefig(path, dpi=dpi)
    plt.close(fig)  # free memory; important in loops that make many figures
    return path
