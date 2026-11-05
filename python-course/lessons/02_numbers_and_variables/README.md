# 02 — Numbers and Variables

Treasury maths: income, expenses, interest on war loans, inflation. Python's number model is small, but it has a few edges that bite economists in particular.

## int and float

```python
regiments = 12          # int: exact, unlimited size
tax_rate = 0.08         # float: binary floating point, ~15-16 significant digits
type(regiments)         # <class 'int'>
```

Mixing them gives a float: `12 * 0.08` is `0.96`. `int("1200")` and `float("3.5")` convert strings; `int(3.9)` **truncates** toward zero to `3` (it doesn't round).

## Arithmetic operators

| op | meaning | example | result |
|---|---|---|---|
| `+ - *` | the usual | `600 - 380` | `220` |
| `/` | true division, **always float** | `10 / 2` | `5.0` |
| `//` | floor division | `1000 // 45` | `22` |
| `%` | remainder (modulo) | `1000 % 45` | `10` |
| `**` | power | `1.05 ** 3` | `1.157625` |

`//` and `%` are a pair: "how many whole regiments can I afford, and what's left over?" `divmod(1000, 45)` returns both at once: `(22, 10)`. `%` is also how you do cycles: `month % 12` wraps 0..11, so `(month - 1) % 12 + 1` maps any month count onto a 1..12 calendar.

Watch negatives: `//` floors toward minus infinity, so `-7 // 2 == -4`, not `-3`.

Precedence follows maths: `**` first, then `* / // %`, then `+ -`. `-2 ** 2` is `-4` (the power binds tighter than the minus). When in doubt, parenthesise.

## Variables and augmented assignment

```python
balance = 500.0
balance += 220      # same as balance = balance + 220
balance *= 1.02     # same as balance = balance * 1.02
```

Names are `snake_case` by convention. Constants you don't intend to change are `UPPER_CASE`.

## Rounding

`round(x, 2)` rounds to 2 decimals. Two surprises:

- `round(2.5) == 2` and `round(3.5) == 4`. Python uses **banker's rounding** (round half to even), which avoids systematic upward bias when summing many rounded values.
- `round(2.675, 2)` gives `2.67`, because `2.675` can't be stored exactly — it's really `2.67499999...`.

`math.floor`, `math.ceil` round down/up to an int. Use `math.ceil` for "how many loans do I need to cover this deficit".

## Float imprecision

```python
0.1 + 0.2            # 0.30000000000000004
0.1 + 0.2 == 0.3     # False
```

Floats are binary fractions; 0.1 has no exact binary representation, just like 1/3 has none in decimal. Consequences:

- **Never compare floats with `==`.** Use `math.isclose(a, b)` (or `abs(a - b) < 1e-9`).
- Summing many small floats accumulates error. For research-grade numbers that's fine; for actual money, store integer cents or use `decimal.Decimal`.

## Compound growth

The single most useful formula in this course:

```python
value = principal * (1 + rate) ** periods
```

A 1000-ducat war loan at 4% per year, untouched for 10 years, becomes `1000 * 1.04 ** 10 ≈ 1480.24`. Inflation is the same thing in reverse: something costing 100 now costs `100 * (1 + inflation) ** years` later, and money's real value is `nominal / (1 + inflation) ** years`.

To go from an annual rate to a monthly one, don't divide by 12 — take the 12th root: `(1 + annual) ** (1 / 12) - 1`. Dividing by 12 slightly *overstates* the annual rate once compounded. And to invert growth — how many periods until something doubles? — use logarithms: `math.log(2) / math.log(1 + rate)`. (Rule of 72: at 6%, about 72/6 = 12 years.)

## Worked example

`example.py` prices a war: it borrows to fund an army, accrues interest annually, adds inflation to upkeep, and prints the treasury's real (inflation-adjusted) position. Run `python example.py` and match each printed line to the line of code that produced it. Pay attention to:

- `divmod` to work out regiments affordable and leftover gold.
- The `0.1 + 0.2` demo and `math.isclose`.
- Compounding via `**` instead of a loop (loops come in lesson 05).

## Exercises

In `exercises.py`:

1. `monthly_net(taxes, trade, upkeep, interest)` — income minus expenses.
2. `regiments_affordable(gold, cost)` — whole regiments and leftover gold, as a tuple.
3. `loan_balance(principal, annual_rate, years)` — compound interest.
4. `real_value(nominal, inflation, years)` — deflate a future amount.
5. `monthly_rate(annual_rate)` — the equivalent compounded monthly rate.
6. `years_to_double(rate)` — via logs, rounded up to whole years.
7. `loans_needed(deficit, loan_size)` — ceiling division.
8. `nearly_equal(a, b)` — safe float comparison.

## How to check

Double-click `check.bat` in the course folder and type `02`.
