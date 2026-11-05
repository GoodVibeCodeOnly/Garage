"""Lesson 22 worked example: who matters in the trade network, and what breaks under embargo?"""
import pathlib
from collections import deque

import pandas as pd

HERE = pathlib.Path(__file__).parent
df = pd.read_csv(HERE / "data" / "trade_flows.csv")

# Build dict-of-dicts: graph[exporter][importer] = total value over goods
graph = {n: {} for n in set(df.exporter) | set(df.importer)}
for (a, b), v in df.groupby(["exporter", "importer"])["value"].sum().items():
    graph[a][b] = float(v)

# Degree and strength
indeg = {n: 0 for n in graph}
for a in graph:
    for b in graph[a]:
        indeg[b] += 1
table = pd.DataFrame({
    "out_deg": {n: len(graph[n]) for n in graph},
    "in_deg": indeg,
    "exports": {n: sum(graph[n].values()) for n in graph},
}).sort_values("exports", ascending=False)
print("Top exporters:\n", table.head(6).round(1), "\n")


def bfs(graph, start):
    """Return {node: hops} for everything reachable from start."""
    dist = {start: 0}
    q = deque([start])
    while q:
        node = q.popleft()
        for nxt in graph[node]:
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                q.append(nxt)
    return dist


d = bfs(graph, "Ragusa")
print("Hops from Ragusa:", dict(sorted(d.items(), key=lambda kv: kv[1])), "\n")

# Embargo Castile: remove node and edges into it
emb = {a: {b: v for b, v in nbrs.items() if b != "Castile"} for a, nbrs in graph.items() if a != "Castile"}
for src in ["Granada", "Venice"]:
    lost = set(bfs(graph, src)) - set(bfs(emb, src)) - {"Castile"}
    print(f"Embargo Castile -> {src} loses access to: {sorted(lost) or 'nothing'}")

# Import concentration (HHI)
print("\nImport HHI (1.0 = single supplier):")
for n in sorted(graph):
    flows = [nbrs[n] for nbrs in graph.values() if n in nbrs]
    tot = sum(flows)
    print(f"  {n:9s} {sum((v / tot) ** 2 for v in flows):.2f}")
