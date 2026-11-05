def test_parse_basic(ex):
    assert ex.parse_ledger_line("Prussia,1200,340") == ("Prussia", 1200, 340)


def test_parse_messy(ex):
    assert ex.parse_ledger_line("  AUSTRIA , 1530,910\n") == ("Austria", 1530, 910), \
        "strip whitespace and title-case the name"


def test_parse_types(ex):
    _, inc, exp = ex.parse_ledger_line("Saxony,680,212")
    assert isinstance(inc, int) and isinstance(exp, int), "convert numbers with int()"


def test_format_ducats(ex):
    assert ex.format_ducats(1234567.891) == "1,234,567.89 ducats"
    assert ex.format_ducats(5) == "5.00 ducats"
    assert ex.format_ducats(-1500.5) == "-1,500.50 ducats"


def test_format_row(ex):
    assert ex.format_row("Prussia", 1200, 340) == "Prussia          1,200       340      +860"


def test_format_row_negative(ex):
    row = ex.format_row("Bavaria", 410, 455)
    assert row == "Bavaria            410       455       -45"
    assert len(row) == 42


def test_margin_label(ex):
    assert ex.margin_label(1200, 340) == "+71.7%"
    assert ex.margin_label(410, 455) == "-11.0%"
    assert ex.margin_label(100, 100) == "+0.0%"


def test_country_code(ex):
    assert ex.country_code("Prussia") == "PRU"
    assert ex.country_code("  austria ") == "AUS"


def test_to_csv_line(ex):
    assert ex.to_csv_line("Prussia", 1200, 340) == "Prussia,1200,340"


def test_roundtrip(ex):
    line = ex.to_csv_line("Saxony", 680, 212)
    assert ex.parse_ledger_line(line) == ("Saxony", 680, 212)


def test_mask_account(ex):
    assert ex.mask_account("DE89370400440532") == "************0532"
    assert ex.mask_account("12345") == "*2345"
    assert ex.mask_account("1234") == "1234"
    assert ex.mask_account("12") == "12"
