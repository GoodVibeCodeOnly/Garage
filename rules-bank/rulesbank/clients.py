"""Chat-model clients. Stdlib only (urllib), so the bank has no dependencies.

Two wire formats cover most providers:
  openai     POST {base_url}/chat/completions   (OpenAI, OpenRouter, vLLM, Ollama, LM Studio, Together, ...)
  anthropic  POST {base_url}/v1/messages
Plus offline mock clients for --dry-run, which never touch the network.
"""
import json
import os
import random
import time
import urllib.error
import urllib.request


class ClientError(RuntimeError):
    pass


def _post(url, headers, body, timeout, retries=3):
    data = json.dumps(body).encode()
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise ClientError(f"HTTP {e.code}: {e.read()[:500]!r}") from e
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise ClientError(str(e)) from e


class OpenAIClient:
    def __init__(self, model, base_url, api_key, temperature=0.0, max_tokens=600, timeout=120):
        self.model, self.base_url, self.api_key = model, base_url.rstrip("/"), api_key
        self.temperature, self.max_tokens, self.timeout = temperature, max_tokens, timeout

    def chat(self, system, user):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = {"model": self.model, "temperature": self.temperature, "max_tokens": self.max_tokens,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        r = _post(f"{self.base_url}/chat/completions", headers, body, self.timeout)
        try:
            return r["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as e:
            raise ClientError(f"unexpected response shape: {str(r)[:300]}") from e


class AnthropicClient:
    def __init__(self, model, base_url, api_key, temperature=0.0, max_tokens=600, timeout=120):
        self.model, self.base_url, self.api_key = model, base_url.rstrip("/"), api_key
        self.temperature, self.max_tokens, self.timeout = temperature, max_tokens, timeout

    def chat(self, system, user):
        headers = {"Content-Type": "application/json", "x-api-key": self.api_key or "",
                   "anthropic-version": "2023-06-01"}
        body = {"model": self.model, "max_tokens": self.max_tokens, "temperature": self.temperature,
                "system": system, "messages": [{"role": "user", "content": user}]}
        r = _post(f"{self.base_url}/v1/messages", headers, body, self.timeout)
        try:
            return "".join(b.get("text", "") for b in r["content"] if b.get("type") == "text")
        except (KeyError, TypeError) as e:
            raise ClientError(f"unexpected response shape: {str(r)[:300]}") from e


class MockClient:
    """Offline stand-in. Needs the scenario, so run.py hands it over via .current.

    mode='oracle'  answers with the reference ruling (should score ~100%; checks the scorer and bank)
    mode='wrong'   answers with the first common wrong ruling (should score low; checks must_not/must_include bite)
    mode='random'  coin flip between the two, seeded
    Judge prompts get 'PASS'/'FAIL' from the same logic.
    """
    def __init__(self, mode="oracle", seed=0):
        self.mode, self.rng, self.current = mode, random.Random(seed), None

    def _pick(self):
        mode = self.mode
        if mode == "random":
            mode = self.rng.choice(["oracle", "wrong"])
        return mode

    def chat(self, system, user):
        s = self.current
        if s is None:
            return ""
        if user.startswith("You are grading"):
            return "PASS\nmock judge" if "<<<\n" + s["correct_ruling"] in user else "FAIL\nmock judge"
        if self._pick() == "oracle":
            return s["correct_ruling"]
        wrong = s.get("common_wrong_rulings") or ["I'm not sure."]
        return wrong[0]


def make_client(api_style, model, base_url=None, api_key_env=None, **kw):
    if api_style.startswith("mock"):
        _, _, mode = api_style.partition(":")
        return MockClient(mode or "oracle")
    key = os.environ.get(api_key_env) if api_key_env else None
    if api_style == "openai":
        return OpenAIClient(model, base_url or "https://api.openai.com/v1", key, **kw)
    if api_style == "anthropic":
        return AnthropicClient(model, base_url or "https://api.anthropic.com", key, **kw)
    raise ValueError(f"unknown api style {api_style!r}")
