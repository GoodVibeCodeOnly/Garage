import copy

import pandas as pd
import pytest

G = {
    "A": {"B": 10.0, "C": 30.0},
    "B": {"C": 5.0},
    "C": {"D": 1.0},
    "D": {},
    "E": {"A": 2.0},
}


def test_build_graph_small(ex, tmp_path):
    p = tmp_path / "f.csv"
    p.write_text("exporter,importer,good,value\nX,Y,grain,1.5\nX,Y,wine,2.5\nY,Z,iron,4\n")
    g = ex.build_graph(p)
    assert g["X"] == {"Y": pytest.approx(4.0)}, "sum value over goods"
    assert g["Y"] == {"Z": pytest.approx(4.0)}
    assert g["Z"] == {}, "pure importers still need a key"


def test_build_graph_real(ex, data_dir):
    g = ex.build_graph(data_dir / "trade_flows.csv")
    df = pd.read_csv(data_dir / "trade_flows.csv")
    assert set(g) == set(df.exporter) | set(df.importer)
    total = sum(v for nbrs in g.values() for v in nbrs.values())
    assert total == pytest.approx(df.value.sum())


def test_degrees(ex):
    d = ex.degrees(G)
    assert d["A"] == (2, 1)
    assert d["C"] == (1, 2)
    assert d["D"] == (0, 1)
    assert d["E"] == (1, 0)


def test_export_strength(ex):
    s = ex.export_strength(G)
    assert s["A"] == pytest.approx(40.0)
    assert s["D"] == pytest.approx(0.0)


@pytest.mark.parametrize("start,goal,hops", [
    ("A", "A", 0), ("A", "C", 1), ("A", "D", 2), ("E", "D", 3), ("D", "A", None),
])
def test_shortest_hops(ex, start, goal, hops):
    assert ex.shortest_hops(G, start, goal) == hops


def test_reachable(ex):
    assert ex.reachable(G, "A") == {"B", "C", "D"}
    assert ex.reachable(G, "D") == set()
    assert ex.reachable(G, "E") == {"A", "B", "C", "D"}


def test_embargo_removes_node_and_edges(ex):
    original = copy.deepcopy(G)
    g2 = ex.embargo(G, "C")
    assert "C" not in g2
    assert all("C" not in nbrs for nbrs in g2.values())
    assert g2["A"] == {"B": 10.0}
    assert G == original, "embargo must not mutate the input graph"


def test_cut_off_by_embargo(ex):
    assert ex.cut_off_by_embargo(G, "E", "C") == {"D"}
    assert ex.cut_off_by_embargo(G, "E", "A") == {"B", "C", "D"}
    assert ex.cut_off_by_embargo(G, "A", "E") == set()


def test_cut_off_real_data(ex, data_dir):
    g = ex.build_graph(data_dir / "trade_flows.csv")
    # Ragusa's only link is Venice: embargo Venice and Ragusa reaches nothing.
    assert ex.reachable(ex.embargo(g, "Venice"), "Ragusa") == set()
    lost = ex.cut_off_by_embargo(g, "Ragusa", "Venice")
    assert lost == set(g) - {"Ragusa", "Venice"}


def test_import_hhi(ex):
    assert ex.import_hhi(G, "C") == pytest.approx((30 / 35) ** 2 + (5 / 35) ** 2)
    assert ex.import_hhi(G, "D") == pytest.approx(1.0), "single supplier -> 1.0"
    assert ex.import_hhi(G, "E") == 0.0


def test_import_hhi_spoke_is_monopoly(ex, data_dir):
    g = ex.build_graph(data_dir / "trade_flows.csv")
    assert ex.import_hhi(g, "Ragusa") == pytest.approx(1.0)
    assert ex.import_hhi(g, "Venice") < 0.5
