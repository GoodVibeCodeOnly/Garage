# 01 — Reading Code

You already direct AI to write Python. The skill that makes that safe is *reading* what comes back: tracing it line by line and knowing what each name holds at each moment. This lesson trains exactly that. Writing comes in the next four lessons.

## Statements run top to bottom

A Python file is a list of instructions executed in order, one at a time. Nothing runs "in parallel" and nothing looks ahead.

```python
gold = 100
gold = gold + 25     # right side evaluated first (100 + 25), THEN stored in gold
gold = gold * 2      # 250
```

`=` is not equality. It means "evaluate the right side, then make the name on the left point at the result." `gold = gold + 25` is perfectly sensible: take the current value, add 25, rebind the name.

## Names are labels, not boxes

A name (variable) is a label stuck onto a value. Re-assigning moves the label; it doesn't change other labels.

```python
income = 300
budget = income     # budget points at 300 too
income = 500        # move the 'income' label; budget still 300
```

For numbers and strings that is the whole story. (Lists behave differently — lesson on lists.)

Using a name before it's assigned is a `NameError`. Python only knows about names that have already been executed into existence above the current line.

## Calling functions

```python
def monthly_tax(population, rate):
    return population * rate

t = monthly_tax(1000, 0.1)   # 100.0
```

`def` *defines* a function — it does not run the body. The body runs only when the function is **called** with parentheses. At the call, arguments are matched to parameters by position (`population=1000, rate=0.1`), the body runs, and `return` hands a value back to the caller. A function with no `return` returns `None`.

Things to watch when reading:

- `print(x)` *displays* a value; `return x` *hands it back*. A function that prints but doesn't return gives the caller `None`.
- Code after `return` in the same block never runs.
- Names assigned inside a function are local — they vanish when the function returns and don't touch outer names with the same spelling.

## Reading a traceback

When something breaks, Python prints a traceback. Read it **bottom-up**:

```
Traceback (most recent call last):
  File "tick.py", line 9, in <module>
    run_month()
  File "tick.py", line 6, in run_month
    balance = balance - upkep
NameError: name 'upkep' is not defined. Did you mean: 'upkeep'?
```

1. Last line: the exception type (`NameError`) and message. This is usually enough.
2. The frame just above: file, line number, function, and the offending source line.
3. Further up: the chain of calls that got you there (most recent at the bottom).

Common types you'll meet: `NameError` (unknown name — typo or not yet assigned), `TypeError` (wrong kind of value, e.g. `"100" + 5`), `ZeroDivisionError`, `IndexError`/`KeyError` (missing position/key), `AttributeError` (value lacks that method), `SyntaxError` (file couldn't even be parsed — nothing ran).

## Worked example

`example.py` is a toy "monthly tick" like a Paradox game runs on the first of each month: collect taxes, pay army upkeep, pay interest on loans. Run it:

```
python example.py
```

Read it before running it. Predict the final balance by hand, then check. Notice:

- The constants at the top are defined once and read by the functions.
- `tick()` calls `collect_taxes()` and `pay_upkeep()` — follow each call into its body and back out.
- `tick()` is called three times at the bottom; each call starts from whatever `balance` came back from the previous one.
- The last section deliberately triggers a `ZeroDivisionError`, catches it, and prints the traceback so you can practice reading one without your script dying.

## Exercises

Open `exercises.py`. Exercises 1–5 are **predict the output**: each docstring shows a snippet; your function should simply `return` the value asked for. Work it out *in your head*, then type the literal answer (e.g. `return 175`). Don't paste the snippet and run it — that defeats the purpose. Exercises 6–7 are tiny edits.

1. `predict_reassignment()` — rebinding a name several times.
2. `predict_labels()` — two names, one reassigned.
3. `predict_function_call()` — trace a call with positional arguments.
4. `predict_print_vs_return()` — what does the caller actually get?
5. `predict_traceback()` — read a traceback, return the exception type name and line number.
6. `net_income(taxes, upkeep, interest)` — fix the provided buggy body.
7. `tick(balance, taxes, upkeep)` — write a three-line function from its docstring.

## How to check

Double-click `check.bat` in the course folder and type `01`.
