"""Lesson 11 exercises: errors and debugging.

How to check: double-click `check.bat` in the course folder and type 11.
(Or from the course folder: python -m pytest lessons/11_errors_and_debugging)

Theme: a pollster dump arrives as messy comma-separated lines like
    "YouGov, 2024-03-01, 1500, 45.5%"
Your job is to parse it without crashing on the junk, and to say clearly
what was wrong with each bad line.
"""


# Exercise 1
def parse_share(text):
    """Turn a vote-share string into a fraction.

    "45.5%" -> 0.455, " 12 % " -> 0.12, "60" -> 0.6 (the % sign is optional,
    surrounding whitespace is ignored).
    Raise ValueError if the text is not a number (float() already does this
    for you - let it propagate) or if the number is outside 0..100.
    """
    raise NotImplementedError("Exercise 1")


# Exercise 2
def safe_ratio(a, b):
    """Return a / b, or None if b is zero.

    Use try/except ZeroDivisionError - do NOT check `if b == 0` first.
    (Practising the EAFP style: easier to ask forgiveness than permission.)
    """
    raise NotImplementedError("Exercise 2")


# Exercise 3
def get_pollster(record, default="unknown"):
    """Fix this buggy function.

    The original version was:

        def get_pollster(record, default="unknown"):
            return record["pollster"].strip()

    It crashes with KeyError when the record has no "pollster" key, and with
    AttributeError when the value is None. Write a fixed version that returns
    the stripped pollster name, or `default` if the key is missing or None.
    """
    raise NotImplementedError("Exercise 3")


# Exercise 4
def last_n(polls, n):
    """Fix this buggy function: return the last n polls, in original order.

    The original version was:

        def last_n(polls, n):
            return [polls[len(polls) - i] for i in range(n)]

    It raises IndexError immediately (why? work it out from the traceback),
    returns things in reverse order, and blows up if n > len(polls).
    Fixed behaviour: last_n([1, 2, 3, 4], 2) -> [3, 4];
    if n exceeds the list length return the whole list; n <= 0 -> [].
    Always return a new list.
    """
    raise NotImplementedError("Exercise 4")


# Exercise 5
def parse_record(line):
    """Parse one line "pollster, date, sample, share" into a dict.

    "YouGov, 2024-03-01, 1500, 45.5%" ->
        {"pollster": "YouGov", "date": "2024-03-01", "sample": 1500, "share": 0.455}

    Strip whitespace from every field. Keep the date as a string.
    Raise ValueError (with a helpful message) if:
      - there are not exactly 4 fields
      - the pollster is empty
      - sample is not an integer, or is <= 0
      - share is invalid (reuse parse_share)
    """
    raise NotImplementedError("Exercise 5")


# Exercise 6
def parse_all(lines):
    """Parse many lines, collecting failures instead of crashing.

    Return a tuple (records, errors):
      records: list of dicts from parse_record, for the good lines, in order
      errors:  list of (line_number, message) for bad lines, where
               line_number counts from 1 and message is str(the ValueError)
    Skip blank / whitespace-only lines entirely (neither record nor error),
    but they still count for line numbering.
    Use try / except ValueError / else.
    """
    raise NotImplementedError("Exercise 6")


# Exercise 7
def weighted_share(records):
    """Sample-size-weighted average share across parsed records.

    sum(share * sample) / sum(sample).
    Raise ValueError("no records") if records is empty.
    Bonus: add an `assert` documenting an assumption you rely on.
    """
    raise NotImplementedError("Exercise 7")


# Exercise 8
def error_name(func, *args):
    """Call func(*args). Return the NAME of the exception class it raises
    (e.g. "KeyError", "TypeError"), or "ok" if it raises nothing.

    error_name(int, "abc")  -> "ValueError"
    error_name(len, 5)      -> "TypeError"
    error_name(abs, -3)     -> "ok"
    Hint: type(exc).__name__
    """
    raise NotImplementedError("Exercise 8")
