# Lesson 22 — solutions.
from collections import deque

import pandas as pd


def build_graph(path):
    df = pd.read_csv(path)
    # Let pandas do the summing over goods, then turn rows into nested dicts.
    totals = df.groupby(["exporter", "importer"])["value"].sum()
    nodes = set(df["exporter"]) | set(df["importer"])
    graph = {n: {} for n in nodes}          # every node gets a key, even pure importers
    for (a, b), v in totals.items():
        graph[a][b] = float(v)
    return graph


def degrees(graph):
    indeg = {n: 0 for n in graph}
    for a, nbrs in graph.items():
        for b in nbrs:
            indeg[b] = indeg.get(b, 0) + 1
    return {n: (len(graph.get(n, {})), indeg[n]) for n in indeg}


def export_strength(graph):
    return {n: float(sum(nbrs.values())) for n, nbrs in graph.items()}


def shortest_hops(graph, start, goal):
    # BFS explores in rings of distance 0, 1, 2, ... so the first time we see
    # goal is via a shortest path. Track distance alongside the node.
    if start == goal:
        return 0
    seen = {start}
    queue = deque([(start, 0)])
    while queue:
        node, d = queue.popleft()
        for nxt in graph.get(node, {}):
            if nxt == goal:
                return d + 1
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, d + 1))
    return None


def reachable(graph, start):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, {}):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    seen.discard(start)
    return seen


def embargo(graph, node):
    # Dict comprehension builds fresh inner dicts, so the original is untouched.
    return {a: {b: v for b, v in nbrs.items() if b != node}
            for a, nbrs in graph.items() if a != node}


def cut_off_by_embargo(graph, source, node):
    before = reachable(graph, source)
    after = reachable(embargo(graph, node), source)
    return before - after - {node}


def import_hhi(graph, importer):
    flows = [nbrs[importer] for nbrs in graph.values() if importer in nbrs]
    total = sum(flows)
    if total == 0:
        return 0.0
    return float(sum((v / total) ** 2 for v in flows))
