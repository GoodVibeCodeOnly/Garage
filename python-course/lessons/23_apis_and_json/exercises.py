# Lesson 23 — APIs and JSON.
# How to check: double-click check.bat in the course folder and type 23.
#
# RULE FOR THIS LESSON: every function that touches the network takes a `get`
# argument (default requests.get). Call it EXACTLY like this:
#
#     response = get(url, params=params, timeout=10)
#
# and use only response.status_code and response.json(). The tests pass in fake
# `get` functions, so they never touch the internet.
import hashlib
import json
import pathlib
import time

import requests

RETRYABLE = {429, 500, 502, 503, 504}


def fetch_json(url, params=None, get=requests.get):
    """Exercise 1. Call get(url, params=params, timeout=10).
    If status_code == 200 return response.json().
    Otherwise raise RuntimeError with a message that includes the status code.
    """
    raise NotImplementedError("Exercise 1")


def parse_worldbank(payload):
    """Exercise 2. A World Bank response is a 2-element list: [meta, records].
    Each record is a dict with "date" (a string like "2021") and "value"
    (a float or None).

    Return a list of (year, value) tuples with year as int and value as float,
    SKIPPING records whose value is None, sorted by year ascending.
    If records is None (the API does that for empty results) return [].
    """
    raise NotImplementedError("Exercise 2")


def fetch_all_pages(url, params=None, get=requests.get):
    """Exercise 3. Pagination. The World Bank API takes a "page" query param and
    reports meta["pages"] (the total number of pages) in every response.

    Request page 1, 2, ..., pages (copy params and add "page": n — don't mutate
    the caller's dict), using fetch_json. Return ALL records from all pages
    concatenated into one list, in page order.
    """
    raise NotImplementedError("Exercise 3")


def get_with_retry(url, params=None, get=requests.get, max_retries=3,
                   base_delay=1.0, sleep=time.sleep):
    """Exercise 4. Retry with exponential backoff.

    Call get(url, params=params, timeout=10).
      - status 200: return the response object.
      - status in RETRYABLE (429 / 5xx): sleep(base_delay * 2 ** attempt) where
        attempt = 0 for the first retry, 1 for the second, ... then try again.
        Make at most 1 + max_retries calls in total. If all fail, raise RuntimeError.
      - any other status (e.g. 404): raise RuntimeError immediately, no retry.
    `sleep` is injected so tests don't actually wait.
    """
    raise NotImplementedError("Exercise 4")


def cache_key(url, params=None):
    """Exercise 5. Return a deterministic filename for a request:
    the sha256 hex digest of  url + "?" + json.dumps(params or {}, sort_keys=True)
    followed by ".json".
    The same URL and params in a different dict order must give the same key.
    """
    raise NotImplementedError("Exercise 5")


def cached_fetch_json(url, params, cache_dir, get=requests.get):
    """Exercise 6. Disk cache in front of fetch_json.

    path = pathlib.Path(cache_dir) / cache_key(url, params)
    If path exists, return json.loads(path.read_text()) WITHOUT calling get.
    Otherwise fetch_json(url, params, get), create cache_dir if needed, write the
    JSON to path, and return the data.
    """
    raise NotImplementedError("Exercise 6")


def growth_summary(pairs):
    """Exercise 7. Given (year, value) pairs like parse_worldbank returns, return
    a dict {"first_year": int, "last_year": int, "mean": float,
            "worst_year": int (year with the lowest value)}.
    Raise ValueError if pairs is empty.
    """
    raise NotImplementedError("Exercise 7")
