"""Lesson 23 worked example: fetch US GDP growth from the World Bank API.

Tries the live API (with a timeout, retries, and a disk cache). If there's no
network, falls back to the bundled sample JSON in data/. Either way it prints
the same summary.
"""
import json
import pathlib
import time

import requests

HERE = pathlib.Path(__file__).parent
URL = "https://api.worldbank.org/v2/country/US/indicator/NY.GDP.MKTP.KD.ZG"
PARAMS = {"format": "json", "per_page": 20, "date": "2010:2024"}


def get_json(url, params, get=requests.get, retries=2):
    for attempt in range(retries + 1):
        r = get(url, params=params, timeout=10)
        print(f"  GET {r.url if hasattr(r, 'url') else url} -> {r.status_code}")
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
            time.sleep(2 ** attempt)
            continue
        raise RuntimeError(f"status {r.status_code}")


def load_records():
    cache = HERE / "output" / "wb_cache.json"
    if cache.exists():
        print("Using disk cache:", cache.name)
        return json.loads(cache.read_text()), "cache"
    try:
        meta, records = get_json(URL, PARAMS)
        print(f"  meta: page {meta['page']} of {meta['pages']}, total {meta['total']}")
        cache.parent.mkdir(exist_ok=True)
        cache.write_text(json.dumps(records))
        return records, "live API"
    except (requests.RequestException, RuntimeError, ValueError) as e:
        print(f"  network unavailable ({type(e).__name__}); using bundled sample")
        records = []
        for page in sorted((HERE / "data").glob("wb_us_gdp_page*.json")):
            records += json.loads(page.read_text())[1]
        return records, "bundled sample"


records, source = load_records()
pairs = sorted((int(r["date"]), r["value"]) for r in records if r["value"] is not None)
print(f"\nUS real GDP growth (source: {source})")
for year, v in pairs:
    bar = "#" * int(abs(v) * 4)
    print(f"  {year}  {v:5.1f}  {'-' if v < 0 else ' '}{bar}")
vals = [v for _, v in pairs]
print(f"\nmean {sum(vals)/len(vals):.2f}%, worst year {min(pairs, key=lambda p: p[1])[0]}")
print("Example record keys:", sorted(records[0].keys()))
