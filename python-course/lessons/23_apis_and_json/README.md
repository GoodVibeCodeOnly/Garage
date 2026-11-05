# 23 — APIs and JSON

Most research data you'll touch in a fellowship — World Bank, FRED, IMF, OECD, census, polling archives — sits behind an HTTP API that returns JSON. This lesson covers the full loop: request, check, parse, paginate, back off, cache. And one architectural idea worth more than all of that: **inject the thing that talks to the network** so your logic is testable without it.

## HTTP in one paragraph

You send a request (method `GET`, a URL, query parameters after `?`); the server sends a **status code** and a body. Codes you'll meet: `200` OK; `404` not found (your URL is wrong — retrying won't help); `400` bad request (your params are wrong); `429` too many requests (slow down); `5xx` the server broke (maybe temporary). Rule: retry 429/5xx, never retry 4xx.

## requests

```python
import requests
r = requests.get(
    "https://api.worldbank.org/v2/country/US/indicator/NY.GDP.MKTP.KD.ZG",
    params={"format": "json", "date": "2010:2024"},   # requests builds ?format=json&date=...
    timeout=10,                                        # ALWAYS. Default is wait forever.
)
r.status_code      # 200
data = r.json()    # parsed into lists/dicts/str/float/None
```

JSON maps to Python directly: object → `dict`, array → `list`, `null` → `None`, numbers → `int`/`float`. Then it's just nested indexing. The World Bank returns `[meta, records]`, where each record looks like `{"date": "2021", "value": 6.1, ...}`. Note `date` is a **string** and `value` can be `None` — APIs are full of these traps; convert and filter explicitly.

## Pagination

APIs cap results per response. The World Bank puts `page` and `pages` in `meta`; you loop:

```python
page, pages, out = 1, 1, []
while page <= pages:
    meta, recs = fetch_json(url, {**params, "page": page})
    pages = meta["pages"]
    out.extend(recs or [])
    page += 1
```

`{**params, "page": page}` makes a new dict — the caller's `params` stays untouched. Other APIs use a `next` URL or a cursor token; same loop shape.

## Rate limits and exponential backoff

When the server says 429 or 503, wait and retry with growing delays — 1s, 2s, 4s — so a thousand clients don't all hammer it again in lockstep. Cap the attempts; then fail loudly.

```python
for attempt in range(max_retries + 1):
    r = get(url, params=params, timeout=10)
    if r.status_code == 200: return r
    if r.status_code not in RETRYABLE: raise RuntimeError(...)
    if attempt < max_retries: sleep(base_delay * 2 ** attempt)
```

## Caching to disk

Re-downloading the same series on every run is slow, rude to the API, and makes your results depend on whether the network is up today. Cache responses keyed by a hash of URL + params:

```python
raw = url + "?" + json.dumps(params, sort_keys=True)   # sort_keys: dict order mustn't matter
key = hashlib.sha256(raw.encode()).hexdigest() + ".json"
```

For research, a cache doubles as a snapshot: you can say exactly what data your results were computed on.

## Dependency injection: the important bit

```python
def fetch_json(url, params=None, get=requests.get):
    response = get(url, params=params, timeout=10)
```

Normal use: `fetch_json(url)` hits the real API. In tests: `fetch_json(url, get=fake)` where `fake` returns an object with `.status_code` and `.json()`. The test runs in microseconds, offline, and can simulate a 503 or a malformed page on demand — things you can't make the real World Bank do. The same trick handles `sleep` in the retry function: inject it, and the test records the delays instead of waiting. Open `test_exercises.py` and read `FakeGet` — it's eight lines and it's the entire pattern. This is also how you'd make a `requests.Session` (connection reuse, shared headers) work: pass `session.get`.

## Worked example

`example.py` requests US real GDP growth from the World Bank with `timeout=10` and a small retry loop. On success it caches the records to `output/wb_cache.json`; the next run reads the cache and makes no request. If the network is down (or blocked), it catches the exception and loads the bundled two-page sample in `data/` (approximate values in the same shape as the real API, written by `make_data.py`). It then filters `None` values, converts year strings to ints, prints a text bar chart, the mean, and the worst year (2020). Delete `output/wb_cache.json` to force a fresh request.

## Exercises

In `exercises.py` (every network call goes through the injected `get`):

1. `fetch_json(url, params, get)` — status check + `.json()`.
2. `parse_worldbank(payload)` — `[meta, records]` → sorted `(year, value)` pairs.
3. `fetch_all_pages(url, params, get)` — follow `meta["pages"]`.
4. `get_with_retry(...)` — exponential backoff on 429/5xx, injected `sleep`.
5. `cache_key(url, params)` — deterministic sha256 filename.
6. `cached_fetch_json(url, params, cache_dir, get)` — disk cache.
7. `growth_summary(pairs)` — first/last year, mean, worst year.

## How to check

Double-click `check.bat` in the course folder and type 23.
