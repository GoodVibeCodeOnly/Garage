# Lesson 03 — Strings
# How to check: double-click check.bat in the course folder and type 03.
# Replace each `raise NotImplementedError(...)` with your code. No loops needed.


def parse_ledger_line(line):
    """Parse a ledger line "name,income,expenses" into a tuple
    (name, income, expenses) with name as a title-cased string (strip spaces)
    and income/expenses as ints.

    parse_ledger_line("Prussia,1200,340")        -> ("Prussia", 1200, 340)
    parse_ledger_line("  AUSTRIA , 1530,910\\n") -> ("Austria", 1530, 910)
    """
    raise NotImplementedError("Exercise 1")


def format_ducats(amount):
    """Format a number with thousands separators and exactly 2 decimals,
    followed by " ducats".

    format_ducats(1234567.891) -> "1,234,567.89 ducats"
    format_ducats(5)           -> "5.00 ducats"
    """
    raise NotImplementedError("Exercise 2")


def format_row(name, income, expenses):
    """Return one fixed-width ledger row (no trailing newline), made of:
      - name, left-aligned in 12 characters
      - income, right-aligned in 10 characters, with thousands separators
      - expenses, same format as income
      - net (income - expenses), right-aligned in 10 characters, with
        thousands separators and an explicit sign (+ or -)

    format_row("Prussia", 1200, 340)
      -> "Prussia          1,200       340      +860"
    Total length is always 42 characters for short names and numbers.
    """
    raise NotImplementedError("Exercise 3")


def margin_label(income, expenses):
    """Return the net margin (income - expenses) / income as a percentage
    string with one decimal place and an explicit sign.

    margin_label(1200, 340) -> "+71.7%"
    margin_label(410, 455)  -> "-11.0%"
    Hint: the % format type multiplies by 100 for you, and + forces a sign.
    """
    raise NotImplementedError("Exercise 4")


def country_code(name):
    """Return the first three letters of a country name, uppercased, ignoring
    leading/trailing whitespace.

    country_code("Prussia")    -> "PRU"
    country_code("  austria ") -> "AUS"
    """
    raise NotImplementedError("Exercise 5")


def to_csv_line(name, income, expenses):
    """The inverse of parse_ledger_line: return "name,income,expenses".
    Use str.join (remember join needs strings).

    to_csv_line("Prussia", 1200, 340) -> "Prussia,1200,340"
    """
    raise NotImplementedError("Exercise 6")


def mask_account(number):
    """Mask a bank account string: replace every character except the last
    four with '*'. Strings of length 4 or less are returned unchanged.

    mask_account("DE89370400440532") -> "************0532"
    mask_account("1234")             -> "1234"
    Hint: slicing and string repetition.
    """
    raise NotImplementedError("Exercise 7")
