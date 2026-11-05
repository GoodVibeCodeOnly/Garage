"""Lesson 11 solutions: errors and debugging."""


# Exercise 1
def parse_share(text):
    # float() raises ValueError on junk; we let that propagate untouched,
    # but add our own ValueError for a value that parses yet makes no sense.
    cleaned = text.strip().rstrip("%").strip()
    value = float(cleaned)
    if not 0 <= value <= 100:
        raise ValueError(f"share out of range: {value}")
    return value / 100


# Exercise 2
def safe_ratio(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None


# Exercise 3
def get_pollster(record, default="unknown"):
    # dict.get is the idiomatic fix; try/except KeyError works too.
    name = record.get("pollster")
    if name is None:
        return default
    return name.strip()


# Exercise 4
def last_n(polls, n):
    # The bug: polls[len(polls) - 0] is one past the end. Slicing never
    # raises IndexError, which is why it's the right tool here.
    if n <= 0:
        return []
    return polls[-n:]


# Exercise 5
def parse_record(line):
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 4:
        raise ValueError(f"expected 4 fields, got {len(parts)}")
    pollster, date, sample_text, share_text = parts
    if not pollster:
        raise ValueError("missing pollster")
    try:
        sample = int(sample_text)
    except ValueError:
        # `from None` hides the less helpful original traceback.
        raise ValueError(f"bad sample size: {sample_text!r}") from None
    if sample <= 0:
        raise ValueError(f"sample size must be positive: {sample}")
    share = parse_share(share_text)
    return {"pollster": pollster, "date": date, "sample": sample, "share": share}


# Exercise 6
def parse_all(lines):
    records, errors = [], []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = parse_record(line)
        except ValueError as exc:
            errors.append((number, str(exc)))
        else:
            # `else` runs only if no exception: keeps the try block minimal.
            records.append(record)
    return records, errors


# Exercise 7
def weighted_share(records):
    if not records:
        raise ValueError("no records")
    total = sum(r["sample"] for r in records)
    assert total > 0, "sample sizes should already be validated as positive"
    return sum(r["share"] * r["sample"] for r in records) / total


# Exercise 8
def error_name(func, *args):
    try:
        func(*args)
    except Exception as exc:
        return type(exc).__name__
    return "ok"
