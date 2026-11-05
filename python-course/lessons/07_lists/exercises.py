"""Lesson 07 — Lists. Match histories and rating series.

How to check: double-click check.bat in the course folder and type 07.
Replace each `raise NotImplementedError(...)` with your code.
"""


def win_rate(results):
    """Exercise 1. `results` is a list of "W"/"L" strings.
    Return the fraction that are "W" as a float. Return 0.0 for an empty list.

    win_rate(["W", "L", "W", "W"]) -> 0.75
    """
    raise NotImplementedError("Exercise 1")


def last_n(results, n):
    """Exercise 2. Return a new list with the last n results.
    If n >= len(results), return a copy of the whole list. If n == 0, return [].

    last_n(["W", "L", "W"], 2) -> ["L", "W"]
    Careful: results[-0:] is the WHOLE list, not an empty one.
    """
    raise NotImplementedError("Exercise 2")


def rating_series(results, start=1500, k=16):
    """Exercise 3. Return the rating AFTER each match: +k for "W", -k for "L".
    The returned list has the same length as results (start itself is not included).

    rating_series(["W", "W", "L"]) -> [1516, 1532, 1516]
    rating_series([], start=1000)  -> []
    """
    raise NotImplementedError("Exercise 3")


def peak(ratings):
    """Exercise 4. Return a tuple (index, value) of the highest rating.
    If the max appears more than once, use the FIRST index.

    peak([1500, 1530, 1510, 1530]) -> (1, 1530)
    """
    raise NotImplementedError("Exercise 4")


def rolling_mean(values, k):
    """Exercise 5. Return the list of means of each full window of k consecutive values.
    Length of result is len(values) - k + 1 (or [] if k > len(values)).

    rolling_mean([1, 2, 3, 4, 5], 3) -> [2.0, 3.0, 4.0]
    """
    raise NotImplementedError("Exercise 5")


def longest_streak(results, kind="W"):
    """Exercise 6. Length of the longest run of consecutive `kind` entries.

    longest_streak(["W", "W", "L", "W", "W", "W", "L"])       -> 3
    longest_streak(["W", "L", "L", "W"], kind="L")            -> 2
    longest_streak([])                                        -> 0
    """
    raise NotImplementedError("Exercise 6")


def top_players(table, n):
    """Exercise 7. `table` is a list of [name, rating] lists.
    Return the n highest-rated rows, best first, as a NEW list (don't reorder `table`).
    Ties: keep their original relative order (sorted() does this automatically).

    top_players([["Ana", 1612], ["Ben", 1490], ["Cy", 1530]], 2)
        -> [["Ana", 1612], ["Cy", 1530]]
    """
    raise NotImplementedError("Exercise 7")


def record_matches(history, new_results):
    """Exercise 8. Add every item of `new_results` to the END of `history`,
    modifying `history` IN PLACE (the caller's list must change).
    Then return a tuple (total_matches, total_wins) for the updated history.

    h = ["W"]
    record_matches(h, ["L", "W"]) -> (3, 2)   and now h == ["W", "L", "W"]
    """
    raise NotImplementedError("Exercise 8")
