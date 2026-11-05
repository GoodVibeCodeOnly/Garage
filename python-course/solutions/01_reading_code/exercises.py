# Lesson 01 — Reading Code
# How to check: double-click check.bat in the course folder and type 01.
#
# Exercises 1-5: PREDICT THE OUTPUT. Trace the snippet in the docstring in your
# head (or on paper), then replace the `raise` line with `return <your answer>`.
# Don't run the snippet — the point is to practice reading.
# Exercises 6-8: small edits to real code.


def predict_reassignment():
    """What is the value of `gold` at the end?

        gold = 100
        gold = gold - 30
        gold = gold * 2
        gold = gold + 35

    Return the final value as an int.
    """
    # 100 -> 70 -> 140 -> 175. Each right-hand side uses the value bound on the line above.
    return 175


def predict_labels():
    """What are `income` and `budget` at the end?

        income = 400
        budget = income
        income = income + 100
        budget = budget - 50

    Return a tuple (income, budget), e.g. return (1, 2).
    """
    # `budget = income` binds budget to the value 400. Rebinding income later
    # moves only the income label, so budget is unaffected.
    return (500, 350)


def predict_function_call():
    """What is `total` at the end?

        def upkeep(regiments, cost):
            return regiments * cost + 10

        total = upkeep(5, 20)
        total = upkeep(2, total)

    Return the final value of total as an int.
    """
    # upkeep(5, 20) = 110; then upkeep(2, 110) = 2*110 + 10 = 230.
    return 230


def predict_print_vs_return():
    """What appears on screen, and what does `x` hold?

        def report(balance):
            print("Balance:", balance)

        x = report(500)

    Return a tuple (printed_text, x) where printed_text is the exact string that
    appears on screen (print puts one space between its arguments) and x is the
    actual value stored in x.
    """
    # print shows text but the function has no return, so it returns None.
    return ("Balance: 500", None)


def predict_traceback():
    """Read this traceback:

        Traceback (most recent call last):
          File "tick.py", line 12, in <module>
            monthly_report(state)
          File "tick.py", line 8, in monthly_report
            line = "Treasury: " + format_balance(state)
          File "tick.py", line 4, in format_balance
            return state["gold"] + " ducats"
        TypeError: unsupported operand type(s) for +: 'int' and 'str'

    Return a tuple (exception_type, line_number, function_name) describing where
    the error was actually raised: the exception type as a string, the line
    number as an int, and the function's name as a string.
    """
    # Bottom frame = where it was raised. The frames above are just the call chain.
    return ("TypeError", 4, "format_balance")


def net_income(taxes, upkeep, interest):
    """Monthly net income: taxes minus army upkeep minus loan interest.

    EDIT: this body has a bug. Find it and fix it.
    net_income(600, 360, 20) should be 220.
    """
    # Interest is an expense, so it is subtracted too.
    return taxes - upkeep - interest


def treasury_after(months, monthly_net, start):
    """Treasury after `months` months of constant `monthly_net` income.

    EDIT: calling this crashes. Run the tests, read the traceback, fix the line.
    treasury_after(3, 220, 500) should be 1160.
    """
    # The traceback says NameError: 'month' -- a typo for the parameter `months`.
    return start + months * monthly_net


def tick(balance, taxes, upkeep):
    """Run one monthly tick: return balance plus taxes minus upkeep.

    WRITE: replace the raise with a one-line return.
    tick(500, 600, 380) -> 720
    """
    return balance + taxes - upkeep
