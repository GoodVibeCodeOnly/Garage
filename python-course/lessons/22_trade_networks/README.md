# 22 — Trade networks without a library

A trade network is a graph: countries are nodes, flows are directed, weighted edges. You'll build one from a CSV using nothing but dicts, then ask the questions a trade-policy analyst actually asks: who's central, how far apart are two economies, and who gets stranded if a hub is embargoed. No networkx — the point is to see that graph algorithms are twenty lines of loops.

## Representation: dict of dicts

```python
graph = {
    "Venice":  {"Genoa": 210.0, "Ragusa": 35.2},
    "Ragusa":  {"Venice": 28.1},
    "Corsica": {},                 # imports only — still a key
}
graph["Venice"]["Genoa"]           # value of Venice -> Genoa exports
"Genoa" in graph["Venice"]         # is there an edge? O(1)
```

Outer key = exporter, inner key = importer, value = total flow. Iterating `graph[a]` gives a's export partners. Imports require scanning everyone: `[nbrs[x] for nbrs in graph.values() if x in nbrs]`. (Store a reversed graph if you need that often.)

Building it from a long table: let pandas do the summing, then loop.

```python
totals = df.groupby(["exporter", "importer"])["value"].sum()
for (a, b), v in totals.items():
    graph[a][b] = float(v)
```

## Degree and strength

- **Out-degree**: `len(graph[a])` — number of export partners.
- **In-degree**: count how many inner dicts contain `a`.
- **Strength**: weighted degree — `sum(graph[a].values())` is total exports.

Degree says how *connected* you are, strength how *big*. A small entrepôt can have high degree and low strength; that's exactly the kind of node whose removal fragments a network.

## Breadth-first search

BFS finds shortest paths in hop count. It visits everything 1 hop away, then 2, then 3 — so the first time it reaches a node, that's the shortest route.

```python
from collections import deque
dist = {start: 0}
q = deque([start])
while q:
    node = q.popleft()               # FIFO: oldest first = ring by ring
    for nxt in graph[node]:
        if nxt not in dist:          # 'seen' check prevents infinite loops on cycles
            dist[nxt] = dist[node] + 1
            q.append(nxt)
```

`deque.popleft()` is O(1); `list.pop(0)` is O(n). Reachability is the same loop — the keys of `dist` are everything you can reach.

## Embargo = delete a node

```python
emb = {a: {b: v for b, v in nbrs.items() if b != X}
       for a, nbrs in graph.items() if a != X}
```

Comprehensions build new dicts, so the original graph survives (mutating shared state inside an analysis function is how you get "why did my second result change?" bugs). Then compare `reachable(graph, s)` with `reachable(emb, s)`: the set difference is what `s` loses. A node whose removal strands others is a **cut vertex** — the strategic chokepoint you'd want to hold in an EU4 trade-node map.

## Concentration: HHI

The Herfindahl-Hirschman Index measures how dependent an importer is on few suppliers:

```python
shares = [v / total for v in flows]
hhi = sum(s ** 2 for s in shares)    # 1.0 = monopoly supplier; 1/n = n equal suppliers
```

Competition authorities use the same formula (×10,000) for market concentration. High import HHI = exposure to a single partner's coercion.

## Worked example

`example.py` loads `data/trade_flows.csv` (synthetic late-medieval Europe from `make_data.py`: four hubs fully linked, mid-sized states linked to two hubs, and five small states — Ragusa, Corsica, Riga, Granada, Navarre — that trade only with one patron). It:

1. builds the dict-of-dicts and prints a degree/strength table — the hubs dominate both;
2. runs BFS from Ragusa: everything is ≤3 hops away, but every path goes through Venice;
3. embargoes Castile — Granada loses access to the whole world, Venice loses only Granada and Navarre;
4. prints import HHI per country: spokes score 1.00, hubs ~0.15–0.3.

## Exercises

In `exercises.py`:

1. `build_graph(path)` — CSV → dict-of-dicts, summing over goods, every node a key.
2. `degrees(graph)` — `{node: (out_degree, in_degree)}`.
3. `export_strength(graph)` — `{node: total exports}`.
4. `shortest_hops(graph, start, goal)` — BFS hops or `None`.
5. `reachable(graph, start)` — set of reachable nodes (excluding start).
6. `embargo(graph, node)` — new graph without node; don't mutate.
7. `cut_off_by_embargo(graph, source, node)` — what source loses.
8. `import_hhi(graph, importer)` — supplier concentration.

## How to check

Double-click `check.bat` in the course folder and type 22.
