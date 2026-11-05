"""Lesson 07 — Lists. Model solutions."""


def win_rate(results):
    if not results:  # empty list is falsy
        return 0.0
    return results.count("W") / len(results)


def last_n(results, n):
    if n <= 0:
        return []  # results[-0:] == results[0:] == everything, so special-case it
    return results[-n:]  # a slice is already a new list; out-of-range n is fine


def rating_series(results, start=1500, k=16):
    ratings = []
    current = start
    for r in results:
        current += k if r == "W" else -k
        ratings.append(current)
    return ratings
    # Alternative: itertools.accumulate(changes, initial=start), then drop the first.


def peak(ratings):
    best = max(ratings)
    return (ratings.index(best), best)  # .index returns the first occurrence
    # One-pass alternative: max(enumerate(ratings), key=lambda p: p[1])


def rolling_mean(values, k):
    # range(k - 1, len(values)) is the index of the LAST element of each window.
    # If k > len(values) the range is empty and we naturally return [].
    return [sum(values[i - k + 1 : i + 1]) / k for i in range(k - 1, len(values))]


def longest_streak(results, kind="W"):
    best = current = 0
    for r in results:
        if r == kind:
            current += 1
            best = max(best, current)  # update every step, so end-of-list streaks count
        else:
            current = 0
    return best


def top_players(table, n):
    # sorted() returns a new list and is stable (ties keep original order).
    return sorted(table, key=lambda row: row[1], reverse=True)[:n]


def record_matches(history, new_results):
    history.extend(new_results)  # in place; append would nest the whole list
    return (len(history), history.count("W"))
