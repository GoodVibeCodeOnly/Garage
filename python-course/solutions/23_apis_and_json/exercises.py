# Lesson 23 — solutions.
import hashlib
import json
import pathlib
import time

import requests

RETRYABLE = {429, 500, 502, 503, 504}


def fetch_json(url, params=None, get=requests.get):
    # Dependency injection: the function doesn't care whether `get` is
    # requests.get, a Session's .get, or a test fake — only its shape matters.
    response = get(url, params=params, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"GET {url} failed with status {response.status_code}")
    return response.json()


def parse_worldbank(payload):
    _meta, records = payload
    if records is None:
        return []
    pairs = [(int(r["date"]), float(r["value"])) for r in records if r["value"] is not None]
    return sorted(pairs)               # tuples sort by first element (year) first


def fetch_all_pages(url, params=None, get=requests.get):
    params = dict(params or {})        # copy: never mutate the caller's dict
    out, page, pages = [], 1, 1
    while page <= pages:
        meta, records = fetch_json(url, {**params, "page": page}, get)
        pages = meta["pages"]          # trust the server's count, re-read each time
        out.extend(records or [])
        page += 1
    return out


def get_with_retry(url, params=None, get=requests.get, max_retries=3,
                   base_delay=1.0, sleep=time.sleep):
    for attempt in range(max_retries + 1):
        response = get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response
        if response.status_code not in RETRYABLE:
            # 404 / 400 won't fix themselves; retrying just hammers the server.
            raise RuntimeError(f"status {response.status_code}")
        if attempt < max_retries:
            sleep(base_delay * 2 ** attempt)   # 1s, 2s, 4s, ...
    raise RuntimeError(f"gave up after {max_retries + 1} attempts (last status {response.status_code})")


def cache_key(url, params=None):
    # sort_keys makes {"a":1,"b":2} and {"b":2,"a":1} serialise identically.
    raw = url + "?" + json.dumps(params or {}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest() + ".json"


def cached_fetch_json(url, params, cache_dir, get=requests.get):
    path = pathlib.Path(cache_dir) / cache_key(url, params)
    if path.exists():
        return json.loads(path.read_text())
    data = fetch_json(url, params, get)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return data


def growth_summary(pairs):
    if not pairs:
        raise ValueError("no data")
    years = [y for y, _ in pairs]
    values = [v for _, v in pairs]
    worst_year = min(pairs, key=lambda p: p[1])[0]
    return {"first_year": min(years), "last_year": max(years),
            "mean": sum(values) / len(values), "worst_year": worst_year}
