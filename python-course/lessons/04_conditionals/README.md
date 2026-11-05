# 04 — Conditionals

Every game rule and every policy rule is a conditional: "if war exhaustion exceeds 10, stability drops", "income above 50k is taxed at 40%". This lesson covers how Python makes decisions.

## bool and comparisons

`True` and `False` are the two `bool` values. Comparisons produce them:

```python
1200 > 340        # True
x == y            # equality (single = is assignment!)
x != y            # not equal
0 <= margin < 5   # chained: means 0 <= margin and margin < 5
```

Chained comparisons read like maths and save repeating the middle term. `==` on floats has the problems from lesson 02; compare against ranges or use `math.isclose`.

## and, or, not

```python
at_war and exhaustion > 10
stability < 0 or bankrupt
not at_war
```

Precedence: `not` binds tightest, then `and`, then `or`. So `a or b and c` means `a or (b and c)`. Parenthesise anything you'd have to think about.

Both `and` and `or` **short-circuit**: `and` stops at the first falsy operand, `or` at the first truthy one. That makes `regiments > 0 and gold / regiments > 50` safe — the division never runs when `regiments` is 0.

## if / elif / else

```python
if margin > 5:
    label = "safe"
elif margin > 2:
    label = "lean"
else:
    label = "tossup"
```

Python checks conditions **top to bottom and runs only the first branch that matches**. Order therefore matters: test the most restrictive condition first. If you'd written `elif margin > 2` before `margin > 5`, an 8-point lead would be labelled "lean".

Indentation (4 spaces) *is* the block structure. There are no braces.

A one-line conditional expression is useful for simple choices:

```python
sign = "+" if net >= 0 else "-"
```

## Truthiness

Any value can be used as a condition. These are **falsy**: `False`, `None`, `0`, `0.0`, `""`, and empty containers (`[]`, `{}`, `()`). Everything else is truthy.

```python
if name:            # same as: if name != ""
if not allies:      # same as: if len(allies) == 0
```

Idiomatic, but be careful when 0 is a legitimate value: `if gold:` is False for a treasury of exactly 0. If you mean "was a value supplied", write `if gold is not None:`. Always compare to `None` with `is`, not `==`.

## Progressive tax: the classic trap

A progressive tax applies each rate only to the slice of income **inside** that bracket. Under brackets 0–10k at 0%, 10k–40k at 20%, above 40k at 40%, an income of 50k pays `0 + 30k×0.2 + 10k×0.4 = 10k`, not `50k×0.4`. Nobody's take-home pay falls when they move into a higher bracket. Writing that with `if/elif` is a good test of whether you've understood both Python and the policy.

## Worked example

`example.py` implements a monthly stability check for a Paradox-style country: war exhaustion, treasury and overextension feed into a stability change, then it classifies three opinion polls as safe/lean/tossup. Run `python example.py`. Look for:

- An `if/elif/else` chain where order matters.
- Independent `if`s (not `elif`) where several modifiers can all apply at once. Choosing between `elif` and a fresh `if` is the most common conditional bug.
- `max`/`min` used to clamp a value into a range, instead of two more `if`s.

## Exercises

1. `is_bankrupt(balance, monthly_net)` — boolean logic.
2. `classify_margin(margin)` — safe/lean/tossup for either party.
3. `progressive_tax(income)` — progressive tax with three brackets.
4. `stability_change(at_war, exhaustion, balance)` — stacked independent modifiers.
5. `clamp_stability(value)` — keep stability within -3..+3.
6. `beats_baseline(wins, games)` — compare a win rate to 50%, safely handling zero games.
7. `describe_treasury(balance)` — a chain where order matters.

## How to check

Double-click `check.bat` in the course folder and type `04`.
