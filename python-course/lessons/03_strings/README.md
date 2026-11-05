# 03 — Strings

Most real data reaches you as text: CSV lines, log output, report templates. This lesson covers turning text into numbers and numbers back into readable text. The theme is a treasury ledger.

## Basics

```python
name = "Prussia"
'single' == "double"      # True: same thing, pick one and be consistent
len(name)                 # 7
name + " & Austria"       # concatenation
"-" * 20                  # repetition: "--------------------"
"1200" + 5                # TypeError: convert first, int("1200") + 5
```

Strings are **immutable**. Every method returns a *new* string and leaves the original alone. `name.upper()` does nothing useful unless you keep the result: `name = name.upper()`.

## Indexing and slicing

```python
s = "Prussia"
s[0]      # 'P'      (zero-based)
s[-1]     # 'a'      (negative counts from the end)
s[0:3]    # 'Pru'    (start inclusive, stop exclusive)
s[:3]     # 'Pru'    (start defaults to 0)
s[3:]     # 'ssia'   (stop defaults to the end)
s[::-1]   # 'aissurP' (step -1 reverses)
```

The stop-exclusive rule means `s[:k] + s[k:] == s` for any `k`, and `s[a:b]` has length `b - a`. Slicing past the end doesn't error, it just stops.

## Methods worth memorising

```python
"  Prussia \n".strip()          # 'Prussia'  (also lstrip, rstrip)
"prussia".title()               # 'Prussia'  (also upper, lower)
"Prussia,1200,340".split(",")   # ['Prussia', '1200', '340']
"a  b   c".split()              # ['a', 'b', 'c']  (no arg = any whitespace)
" | ".join(["A", "B", "C"])     # 'A | B | C'  (join is called on the separator)
"war_loan".replace("_", " ")    # 'war loan'
"Prussia".startswith("Pru")     # True   (also endswith)
"ss" in "Prussia"               # True   (substring test)
"Prussia".find("ss")            # 3      (-1 if absent)
"1200".isdigit()                # True
```

`split` and `join` are inverses — learn them as a pair. `split` gives you a **list** of strings; you index into it (`parts[1]`) and convert each piece with `int()` or `float()`. Tuple unpacking makes this tidy:

```python
name, income, expenses = "Prussia,1200,340".split(",")
income = int(income)
```

## f-strings

Put `f` before the quote and expressions in `{}`:

```python
gold = 1234567.891
f"Treasury: {gold}"           # 'Treasury: 1234567.891'
f"{gold:,.2f}"                # '1,234,567.89'  thousands separator, 2 decimals
f"{gold:.0f}"                 # '1234568'
f"{0.0734:.1%}"               # '7.3%'          multiplies by 100 and adds %
f"{'Prussia':<10}|"           # 'Prussia   |'   left-align in 10 chars
f"{42:>6}|"                   # '    42|'       right-align
f"{'x':^5}|"                  # '  x  |'        centre
f"{7:03d}"                    # '007'           zero-pad
f"{gold:>15,.2f}"             # combine: width 15, right, commas, 2dp
f"{gold=}"                    # 'gold=1234567.891' -- great for debugging
```

The mini-language after the colon is `[fill][align][width][,][.precision][type]`. Types you need: `d` (int), `f` (fixed decimals), `%` (percent), `e` (scientific). Numbers right-align by default, strings left-align — which is exactly what you want in a table.

Signs: `f"{220:+}"` gives `'+220'`, handy for showing deltas.

## Worked example

`example.py` takes raw ledger lines like `"prussia, 1200 ,340"` (messy, as real data is), cleans and parses them, and prints an aligned report with totals and percentages. Run `python example.py`. Things to notice:

- `strip()` on every field after `split(",")`. `int(" 1200 ")` happens to tolerate spaces, but names and comparisons don't, so clean every field.
- The header and rows use the *same* width specs, so columns line up.
- A separator row built with `"-" * width`.

## Exercises

1. `parse_ledger_line(line)` — `"Prussia,1200,340"` → `("Prussia", 1200, 340)`, tolerating spaces and case.
2. `format_ducats(amount)` — `1234567.891` → `"1,234,567.89 ducats"`.
3. `format_row(name, income, expenses)` — a fixed-width ledger row.
4. `margin_label(income, expenses)` — net margin as a signed percentage string like `"+71.7%"`.
5. `country_code(name)` — first three letters, uppercased.
6. `to_csv_line(name, income, expenses)` — the inverse of exercise 1.
7. `mask_account(number)` — show only the last four characters.

## How to check

Double-click `check.bat` in the course folder and type `03`.
