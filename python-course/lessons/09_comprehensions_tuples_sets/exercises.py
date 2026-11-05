"""Lesson 09 — Comprehensions, tuples, sets. A trade network.

How to check: double-click check.bat in the course folder and type 09.
Replace each `raise NotImplementedError(...)` with your code.

Every `flow` is a tuple: (exporter, importer, good, value).
Try to solve 2-8 with comprehensions and set operators rather than long loops.
"""


def min_max(values):
    """Exercise 1. Return a tuple (smallest, largest) of a non-empty list.

    min_max([3, 9, 1]) -> (1, 9)
    """
    raise NotImplementedError("Exercise 1")


def partners(flows, nation):
    """Exercise 2. Return the SET of nations that `nation` trades with in
    either direction (it exports to them OR imports from them).

    partners([("A", "B", "wine", 10), ("C", "A", "iron", 5)], "A") -> {"B", "C"}
    Unknown nation -> set()
    """
    raise NotImplementedError("Exercise 2")


def shared_partners(flows, a, b):
    """Exercise 3. Return the set of nations that are partners of BOTH a and b.
    (Use your partners function.)
    """
    raise NotImplementedError("Exercise 3")


def exclusive_goods(flows, nation):
    """Exercise 4. Return the set of goods that `nation` exports and that NO
    other nation exports.

    flows = [("A","B","wine",1), ("A","B","glass",1), ("B","A","wine",1)]
    exclusive_goods(flows, "A") -> {"glass"}
    """
    raise NotImplementedError("Exercise 4")


def big_flows(flows, threshold):
    """Exercise 5. Return a list of (exporter, importer) tuples for flows whose
    value is STRICTLY greater than threshold, in the original order.

    big_flows([("A","B","wine",100), ("B","C","iron",50)], 60) -> [("A", "B")]
    """
    raise NotImplementedError("Exercise 5")


def export_totals(flows):
    """Exercise 6. Return a dict exporter -> total value exported.
    Only nations that export at least once appear as keys.

    export_totals([("A","B","w",10), ("A","C","i",5), ("B","A","w",7)]) -> {"A": 15, "B": 7}
    """
    raise NotImplementedError("Exercise 6")


def top_exporters(flows, k):
    """Exercise 7. Return a list of the top-k (exporter, total) tuples, highest
    total first. Break ties by exporter name ALPHABETICALLY.

    flows totals: Genoa 300, Venice 450, Milan 300
    top_exporters(flows, 2) -> [("Venice", 450), ("Genoa", 300)]
    """
    raise NotImplementedError("Exercise 7")


def goods_by_nation(flows):
    """Exercise 8. Return a dict exporter -> set of goods it exports.

    goods_by_nation([("A","B","wine",1), ("A","C","wine",2), ("B","A","iron",3)])
        -> {"A": {"wine"}, "B": {"iron"}}
    Hint: a dict comprehension whose values are set comprehensions.
    """
    raise NotImplementedError("Exercise 8")
