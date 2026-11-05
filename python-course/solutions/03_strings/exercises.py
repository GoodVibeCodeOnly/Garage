# Lesson 03 — Strings (solutions)


def parse_ledger_line(line):
    # Tuple unpacking also checks the shape: a line with 2 or 4 fields raises
    # ValueError instead of silently producing garbage.
    name, income, expenses = line.split(",")
    return name.strip().title(), int(income), int(expenses)


def format_ducats(amount):
    return f"{amount:,.2f} ducats"


def format_row(name, income, expenses):
    net = income - expenses
    # Format spec order: [align][sign][width][,]  e.g. >+10,
    return f"{name:<12}{income:>10,}{expenses:>10,}{net:>+10,}"


def margin_label(income, expenses):
    return f"{(income - expenses) / income:+.1%}"


def country_code(name):
    # Methods chain left to right: strip first, so leading spaces don't count.
    return name.strip()[:3].upper()


def to_csv_line(name, income, expenses):
    # join only accepts strings, hence str() on the numbers.
    # An f-string f"{name},{income},{expenses}" works too; join scales to any
    # number of fields once you have loops.
    return ",".join([name, str(income), str(expenses)])


def mask_account(number):
    # For len <= 4, len(number) - 4 is <= 0 and "*" * negative == "", so no
    # special case is needed -- and number[-4:] is the whole string.
    return "*" * (len(number) - 4) + number[-4:]
