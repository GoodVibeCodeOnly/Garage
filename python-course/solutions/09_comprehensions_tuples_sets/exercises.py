"""Lesson 09 — Comprehensions, tuples, sets. Model solutions."""


def min_max(values):
    return min(values), max(values)  # the comma makes the tuple; parens optional


def partners(flows, nation):
    # Unpack each 4-tuple right in the comprehension; `_` = "don't care".
    exports_to = {imp for exp, imp, _, _ in flows if exp == nation}
    imports_from = {exp for exp, imp, _, _ in flows if imp == nation}
    return exports_to | imports_from


def shared_partners(flows, a, b):
    return partners(flows, a) & partners(flows, b)


def exclusive_goods(flows, nation):
    mine = {good for exp, _, good, _ in flows if exp == nation}
    others = {good for exp, _, good, _ in flows if exp != nation}
    return mine - others


def big_flows(flows, threshold):
    return [(exp, imp) for exp, imp, _, value in flows if value > threshold]


def export_totals(flows):
    totals = {}
    for exp, _, _, value in flows:
        totals[exp] = totals.get(exp, 0) + value
    return totals
    # A pure-comprehension version re-scans flows once per exporter (O(n^2)):
    #   {n: sum(v for e, _, _, v in flows if e == n) for n in {f[0] for f in flows}}
    # Fine for small data, but the loop is one pass — prefer it when it's clearer.


def top_exporters(flows, k):
    totals = export_totals(flows)
    # Tuple key: -total sorts descending, name breaks ties ascending.
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:k]


def goods_by_nation(flows):
    exporters = {exp for exp, _, _, _ in flows}
    return {n: {good for exp, _, good, _ in flows if exp == n} for n in exporters}
    # Single-pass alternative: setdefault(exp, set()).add(good) in a loop.
