def test_predict_reassignment(ex):
    assert ex.predict_reassignment() == 175, "100 -> 70 -> 140 -> 175: each line uses the value from the line above"


def test_predict_labels(ex):
    income, budget = ex.predict_labels()
    assert income == 500, "income was rebound to 400 + 100"
    assert budget == 350, "budget got its own copy of 400 before income changed; then -50"


def test_predict_function_call(ex):
    assert ex.predict_function_call() == 230, "first call: 5*20+10 = 110; second: 2*110+10"


def test_predict_print_vs_return_text(ex):
    printed, _ = ex.predict_print_vs_return()
    assert printed == "Balance: 500", "print separates arguments with one space"


def test_predict_print_vs_return_value(ex):
    _, x = ex.predict_print_vs_return()
    assert x is None, "report() prints but has no return, so it returns None"


def test_predict_traceback(ex):
    exc, line, func = ex.predict_traceback()
    assert exc == "TypeError"
    assert line == 4, "the bottom-most frame is where the error was raised"
    assert func == "format_balance"


def test_net_income(ex):
    assert ex.net_income(600, 360, 20) == 220
    assert ex.net_income(100, 0, 0) == 100
    assert ex.net_income(100, 50, 60) == -10, "interest is an expense"


def test_treasury_after(ex):
    assert ex.treasury_after(3, 220, 500) == 1160
    assert ex.treasury_after(0, 220, 500) == 500
    assert ex.treasury_after(12, -50, 400) == -200


def test_tick(ex):
    assert ex.tick(500, 600, 380) == 720
    assert ex.tick(0, 0, 100) == -100
