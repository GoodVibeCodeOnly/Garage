import pytest

FLOWS = [
    ("Venice", "Genoa", "glass", 120),
    ("Venice", "Milan", "spices", 300),
    ("Genoa", "Venice", "iron", 80),
    ("Genoa", "Milan", "wine", 150),
    ("Milan", "Venice", "cloth", 200),
    ("Milan", "Florence", "iron", 90),
    ("Florence", "Genoa", "cloth", 110),
    ("Florence", "Venice", "wool", 160),
    ("Venice", "Florence", "wine", 70),
]


def test_min_max(ex):
    assert ex.min_max([3, 9, 1]) == (1, 9)
    assert ex.min_max([5]) == (5, 5)


def test_min_max_is_tuple(ex):
    assert isinstance(ex.min_max([1, 2]), tuple), "return a tuple: return low, high"


def test_partners(ex):
    assert ex.partners(FLOWS, "Venice") == {"Genoa", "Milan", "Florence"}
    assert ex.partners(FLOWS, "Genoa") == {"Venice", "Milan", "Florence"}


def test_partners_small(ex):
    flows = [("A", "B", "wine", 10), ("C", "A", "iron", 5)]
    assert ex.partners(flows, "A") == {"B", "C"}
    assert ex.partners(flows, "Z") == set()
    assert isinstance(ex.partners(flows, "A"), set)


def test_shared_partners(ex):
    assert ex.shared_partners(FLOWS, "Milan", "Florence") == {"Venice", "Genoa"}
    flows = [("A", "B", "x", 1), ("C", "D", "x", 1)]
    assert ex.shared_partners(flows, "A", "C") == set()


def test_exclusive_goods(ex):
    flows = [("A", "B", "wine", 1), ("A", "B", "glass", 1), ("B", "A", "wine", 1)]
    assert ex.exclusive_goods(flows, "A") == {"glass"}
    assert ex.exclusive_goods(flows, "B") == set()


def test_exclusive_goods_full(ex):
    assert ex.exclusive_goods(FLOWS, "Venice") == {"glass", "spices"}
    assert ex.exclusive_goods(FLOWS, "Florence") == {"wool"}
    assert ex.exclusive_goods(FLOWS, "Milan") == set()


def test_big_flows(ex):
    assert ex.big_flows(FLOWS, 150) == [("Venice", "Milan"), ("Milan", "Venice"), ("Florence", "Venice")]
    assert ex.big_flows(FLOWS, 1000) == []


def test_big_flows_strict(ex):
    assert ex.big_flows([("A", "B", "w", 60)], 60) == [], "strictly greater than"


def test_export_totals(ex):
    assert ex.export_totals(FLOWS) == {"Venice": 490, "Genoa": 230, "Milan": 290, "Florence": 270}
    assert ex.export_totals([]) == {}


def test_top_exporters(ex):
    assert ex.top_exporters(FLOWS, 2) == [("Venice", 490), ("Milan", 290)]


def test_top_exporters_tiebreak(ex):
    flows = [("Venice", "X", "g", 450), ("Milan", "X", "g", 300), ("Genoa", "X", "g", 300)]
    assert ex.top_exporters(flows, 3) == [("Venice", 450), ("Genoa", 300), ("Milan", 300)], \
        "ties broken alphabetically by name"
    assert ex.top_exporters(flows, 10) == [("Venice", 450), ("Genoa", 300), ("Milan", 300)]


def test_goods_by_nation(ex):
    flows = [("A", "B", "wine", 1), ("A", "C", "wine", 2), ("B", "A", "iron", 3)]
    assert ex.goods_by_nation(flows) == {"A": {"wine"}, "B": {"iron"}}


def test_goods_by_nation_full(ex):
    out = ex.goods_by_nation(FLOWS)
    assert out["Venice"] == {"glass", "spices", "wine"}
    assert out["Milan"] == {"cloth", "iron"}
    assert len(out) == 4
