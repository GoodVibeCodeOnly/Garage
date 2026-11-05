# 11 — Errors and debugging

Real data is dirty. A pollster dump will have a missing column, an "n/a" where a sample size should be, a 147% vote share someone fat-fingered. Code that dies on line 3 of 40,000 is useless; code that silently swallows garbage is worse. This lesson is about the middle path: fail loudly on bugs, handle *expected* mess deliberately, and say exactly what was wrong.

## Reading a traceback

```
Traceback (most recent call last):
  File "example.py", line 33, in <module>
    parse(RAW[2])
  File "example.py", line 21, in parse
    sample = int(sample)
ValueError: invalid literal for int() with base 10: 'n/a'
```

Read it **bottom-up**. The last line is the exception type and message — usually enough on its own. Above it is the line that blew up, then who called that, and so on up the stack. When the bottom frame is inside a library, walk up until you hit *your* file: that's where the bad input came from.

## The usual suspects

| Exception | Typical cause |
|---|---|
| `TypeError` | wrong kind of thing: `"3" + 4`, `len(5)`, calling with the wrong number of args |
| `ValueError` | right type, bad value: `int("n/a")`, `float("")` |
| `KeyError` | dict key missing: `record["pollster"]` |
| `IndexError` | list position past the end: `polls[len(polls)]` |
| `ZeroDivisionError` | `x / 0` — e.g. a win rate with zero games |
| `AttributeError` | method on the wrong thing, very often `None.strip()` |

## try / except / else / finally

```python
try:
    sample = int(text)          # keep this block SMALL
except ValueError as exc:
    print("bad sample:", exc)   # runs only if that exception happened
else:
    total += sample             # runs only if NO exception
finally:
    print("done")               # runs no matter what (cleanup)
```

Rules of thumb:

- **Catch specific exceptions.** `except ValueError`, not bare `except:`. A bare except also catches your typos (`NameError`) and Ctrl-C, hiding real bugs.
- **Keep the `try` tiny.** Put follow-on work in `else` so you don't accidentally catch errors from code you didn't mean to guard.
- **EAFP vs LBYL.** Python culture leans "easier to ask forgiveness than permission": just try `a / b` and catch `ZeroDivisionError`, rather than pre-checking every condition. Both are fine; EAFP is often shorter and avoids race conditions.
- Don't need the error? `d.get("key", default)` beats try/except KeyError for dicts.

## Raising your own errors

When input is *parseable but wrong*, raise yourself — with a message a tired analyst can act on:

```python
if not 0 <= share <= 100:
    raise ValueError(f"share out of range: {share}")
```

Re-raising with a better message: `raise ValueError(f"bad sample: {text!r}") from None` (`from None` suppresses the noisier original traceback; `from exc` chains it).

## assert

`assert total > 0, "no valid samples"` states something that *must* be true if your code is correct. It's for catching your own bugs, not for validating user input (asserts can be disabled with `python -O`). Use `raise ValueError` for bad data, `assert` for "this can't happen".

## Print-debugging

Unglamorous and effective. When a number is wrong, print the intermediate values:

```python
print(f"{line=} {parts=}")   # the = shows name and value
```

Bisect: print halfway through the pipeline, see if it's already wrong, narrow down. Delete the prints when done. (`breakpoint()` drops you into the interactive debugger at that line if you want to poke around; `n` next, `p var` print, `c` continue.)

## Worked example

`example.py` parses six poll lines, three of them broken.

1. It deliberately triggers a `ValueError` and prints the traceback with `traceback.print_exc()` so you can see what a real one looks like without the script dying.
2. It loops with `try / except / else / finally`: bad lines are logged with their line number and the reason (from `str(exc)`), good lines go into a list in the `else` block.
3. It computes a sample-weighted average share, with an `assert` documenting the assumption that at least one sample survived.

Run `python example.py`. Then break it on purpose: remove the `try` and watch the traceback; change `except ValueError` to `except KeyError` and see the error escape.

## Exercises

In `exercises.py`:

1. `parse_share(text)` — `"45.5%"` → `0.455`; raise `ValueError` for junk or out-of-range.
2. `safe_ratio(a, b)` — divide, return `None` on `ZeroDivisionError` (EAFP).
3. `get_pollster(record, default)` — **fix the buggy version** in the docstring (KeyError / None).
4. `last_n(polls, n)` — **fix the buggy version** in the docstring (IndexError, wrong order).
5. `parse_record(line)` — full validated parser for one poll line.
6. `parse_all(lines)` — parse many lines, return `(records, errors)` with line numbers.
7. `weighted_share(records)` — sample-weighted average; raise on empty input.
8. `error_name(func, *args)` — return the name of the exception a call raises, or `"ok"`. Good for building intuition: predict before you run.

## How to check

Double-click `check.bat` in the course folder and type `11`.
