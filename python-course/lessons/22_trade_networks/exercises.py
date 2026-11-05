# Lesson 22 — Trade networks as dict-of-dicts.
# How to check: double-click check.bat in the course folder and type 22.
# Pure Python + pandas. No networkx.
#
# A "graph" here is a dict of dicts: graph[exporter][importer] = total value.
# Edges are DIRECTED (exporter -> importer).
from collections import deque

import pandas as pd


def build_graph(path):
    """Exercise 1. Read the CSV at `path` (columns exporter, importer, good, value)
    and return a dict-of-dicts {exporter: {importer: total_value}}, summing value
    over goods. Every country that appears ANYWHERE (as exporter or importer)
    must be a key, even if it exports nothing (then its value is {}).
    Values are floats.
    """
    raise NotImplementedError("Exercise 1")


def degrees(graph):
    """Exercise 2. Return a dict {node: (out_degree, in_degree)} for every node,
    where out_degree = number of distinct countries it exports to and
    in_degree = number of distinct countries it imports from.
    """
    raise NotImplementedError("Exercise 2")


def export_strength(graph):
    """Exercise 3. Weighted out-strength: {node: total export value} for every
    node (0.0 for nodes that export nothing)."""
    raise NotImplementedError("Exercise 3")


def shortest_hops(graph, start, goal):
    """Exercise 4. Breadth-first search along directed edges. Return the minimum
    number of hops from start to goal (0 if start == goal), or None if goal is
    unreachable. Use collections.deque as the queue.
    """
    raise NotImplementedError("Exercise 4")


def reachable(graph, start):
    """Exercise 5. Return the set of nodes reachable from start by following
    directed edges, NOT including start itself (unless... no: never include it).
    """
    raise NotImplementedError("Exercise 5")


def embargo(graph, node):
    """Exercise 6. Return a NEW graph with `node` removed entirely: its own key,
    and every edge pointing to it. Do not mutate the input graph."""
    raise NotImplementedError("Exercise 6")


def cut_off_by_embargo(graph, source, node):
    """Exercise 7. Which countries does `source` lose access to if `node` is
    embargoed? Return the set of nodes reachable from source in the original
    graph but NOT reachable after embargo(graph, node), excluding `node` itself.
    """
    raise NotImplementedError("Exercise 7")


def import_hhi(graph, importer):
    """Exercise 8. Herfindahl-Hirschman Index of an importer's suppliers.

    share_i = value imported from supplier i / total imports of `importer`.
    HHI = sum(share_i ** 2), on the 0-1 scale (1.0 = a single supplier).
    Return 0.0 if the importer imports nothing.
    """
    raise NotImplementedError("Exercise 8")
