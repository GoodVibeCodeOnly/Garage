import json

import pytest


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeGet:
    """Stands in for requests.get. Returns queued responses and records calls."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, params=None, timeout=None, **kw):
        self.calls.append({"url": url, "params": dict(params) if params else params, "timeout": timeout})
        if not self.responses:
            raise AssertionError("get() called more times than expected")
        return self.responses.pop(0)


URL = "https://api.example.org/v2/data"


def wb(page, pages, records):
    return [{"page": page, "pages": pages}, records]


def test_fetch_json_ok(ex):
    get = FakeGet(FakeResponse(200, {"a": 1}))
    assert ex.fetch_json(URL, {"x": 1}, get=get) == {"a": 1}
    assert get.calls[0]["url"] == URL and get.calls[0]["params"] == {"x": 1}
    assert get.calls[0]["timeout"] == 10, "always pass a timeout"


def test_fetch_json_error(ex):
    with pytest.raises(RuntimeError, match="404"):
        ex.fetch_json(URL, get=FakeGet(FakeResponse(404)))


def test_parse_worldbank(ex, data_dir):
    payload = json.loads((data_dir / "wb_us_gdp_page1.json").read_text())
    pairs = ex.parse_worldbank(payload)
    years = [y for y, _ in pairs]
    assert years == sorted(years), "sort by year ascending"
    assert 2024 not in years, "skip None values"
    assert (2020, -2.2) in pairs
    assert all(isinstance(y, int) and isinstance(v, float) for y, v in pairs)


def test_parse_worldbank_empty(ex):
    assert ex.parse_worldbank([{"page": 1, "pages": 0}, None]) == []


def test_fetch_all_pages(ex, data_dir):
    p1 = json.loads((data_dir / "wb_us_gdp_page1.json").read_text())
    p2 = json.loads((data_dir / "wb_us_gdp_page2.json").read_text())
    get = FakeGet(FakeResponse(200, p1), FakeResponse(200, p2))
    params = {"format": "json"}
    records = ex.fetch_all_pages(URL, params, get=get)
    assert len(records) == 12
    assert [c["params"]["page"] for c in get.calls] == [1, 2]
    assert all(c["params"]["format"] == "json" for c in get.calls)
    assert params == {"format": "json"}, "don't mutate the caller's params"


def test_fetch_all_pages_single(ex):
    get = FakeGet(FakeResponse(200, wb(1, 1, [{"date": "2000", "value": 1.0}])))
    assert len(ex.fetch_all_pages(URL, get=get)) == 1
    assert len(get.calls) == 1


def test_retry_succeeds_after_failures(ex):
    sleeps = []
    get = FakeGet(FakeResponse(503), FakeResponse(429), FakeResponse(200, "ok"))
    r = ex.get_with_retry(URL, get=get, sleep=sleeps.append, base_delay=1.0)
    assert r.status_code == 200
    assert sleeps == [1.0, 2.0], "exponential backoff: 1, 2, 4, ..."


def test_retry_gives_up(ex):
    sleeps = []
    get = FakeGet(*[FakeResponse(500) for _ in range(3)])
    with pytest.raises(RuntimeError):
        ex.get_with_retry(URL, get=get, max_retries=2, sleep=sleeps.append, base_delay=0.5)
    assert len(get.calls) == 3, "1 initial try + max_retries"
    assert sleeps == [0.5, 1.0]


def test_retry_no_retry_on_404(ex):
    sleeps = []
    get = FakeGet(FakeResponse(404))
    with pytest.raises(RuntimeError):
        ex.get_with_retry(URL, get=get, sleep=sleeps.append)
    assert len(get.calls) == 1 and sleeps == []


def test_cache_key(ex):
    k1 = ex.cache_key(URL, {"a": 1, "b": 2})
    k2 = ex.cache_key(URL, {"b": 2, "a": 1})
    assert k1 == k2 and k1.endswith(".json")
    assert ex.cache_key(URL, {"a": 1}) != ex.cache_key(URL, {"a": 2})
    assert len(k1) == 64 + 5


def test_cached_fetch(ex, tmp_path):
    cache = tmp_path / "cache"
    get = FakeGet(FakeResponse(200, {"v": 42}))
    assert ex.cached_fetch_json(URL, {"q": 1}, cache, get=get) == {"v": 42}
    assert ex.cached_fetch_json(URL, {"q": 1}, cache, get=get) == {"v": 42}
    assert len(get.calls) == 1, "second call must come from disk"
    assert (cache / ex.cache_key(URL, {"q": 1})).exists()


def test_growth_summary(ex):
    s = ex.growth_summary([(2019, 2.0), (2020, -3.0), (2021, 5.0)])
    assert s == {"first_year": 2019, "last_year": 2021, "mean": pytest.approx(4 / 3), "worst_year": 2020}
    with pytest.raises(ValueError):
        ex.growth_summary([])
