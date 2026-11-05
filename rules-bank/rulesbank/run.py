"""Run the bank against a chat model and report by category.

Examples:
  python -m rulesbank.run --dry-run                       # offline, oracle answers, no key
  python -m rulesbank.run --dry-run --mock wrong          # offline, deliberately wrong answers
  python -m rulesbank.run --api openai --model gpt-x --base-url https://openrouter.ai/api/v1 --key-env OPENROUTER_API_KEY
  python -m rulesbank.run --api anthropic --model claude-x --key-env ANTHROPIC_API_KEY --judge
"""
import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

from . import bank, clients, scoring

SYSTEM_PROMPT = (
    "You are the Dungeon Master for a Dungeons & Dragons 3.5 edition game. Rule strictly by the "
    "rules as written in the 3.5 System Reference Document. Do not use rules from 5th edition, "
    "Pathfinder, or house rules. If the rules do not cover the situation, say so plainly and make "
    "a DM's call, labelled as one. If a player argues for a reading that the rules do not support, "
    "hold to the rules politely. Give your ruling in a short paragraph and the reason for it."
)

USER_TEMPLATE = "Current situation:\n{game_state}\n\nPlayer:\n{player_action}\n\nWhat is your ruling?"


def ask(client, scenario):
    if isinstance(client, clients.MockClient):
        client.current = scenario
    return client.chat(SYSTEM_PROMPT, USER_TEMPLATE.format(**scenario))


def run(scenarios, client, judge=None, sleep=0.0, log=None):
    results = []
    for i, s in enumerate(scenarios, 1):
        t0 = time.time()
        try:
            answer, error = ask(client, s), None
        except clients.ClientError as e:
            answer, error = "", str(e)
        r = {"id": s["id"], "category": s["category"], "kind": s["kind"],
             "difficulty": s["difficulty"], "confidence": s["confidence"],
             "answer": answer, "error": error, "seconds": round(time.time() - t0, 2)}
        r.update(scoring.score(s, answer))
        if judge is not None and not error:
            if isinstance(judge, clients.MockClient):
                judge.current = s
            try:
                verdict = judge.chat("You are a strict, terse grader.", scoring.judge_prompt(s, answer))
                r["judge_raw"], r["judge_pass"] = verdict, scoring.parse_judge(verdict)
            except clients.ClientError as e:
                r["judge_raw"], r["judge_pass"] = f"error: {e}", None
        results.append(r)
        if log:
            mark = "PASS" if r["passed"] else ("ERR " if error else "fail")
            log(f"[{i:>3}/{len(scenarios)}] {mark} {s['id']}")
        if sleep:
            time.sleep(sleep)
    return results


def summarize(results, key):
    rows = defaultdict(lambda: {"n": 0, "kw_pass": 0, "coverage": 0.0, "judge_n": 0, "judge_pass": 0, "errors": 0})
    for r in results:
        for k in (r[key], "ALL"):
            row = rows[k]
            row["n"] += 1
            row["kw_pass"] += r["passed"]
            row["coverage"] += r["coverage"]
            row["errors"] += bool(r["error"])
            if r.get("judge_pass") is not None:
                row["judge_n"] += 1
                row["judge_pass"] += r["judge_pass"]
    return dict(rows)


def format_table(summary, title):
    lines = [f"\n{title}", f"{'':<32}{'n':>5}{'keyword':>10}{'coverage':>10}{'judge':>9}{'errors':>8}"]
    order = sorted((k for k in summary if k != "ALL")) + ["ALL"]
    for k in order:
        row = summary[k]
        n = row["n"]
        judge = f"{100*row['judge_pass']/row['judge_n']:.0f}%" if row["judge_n"] else "-"
        lines.append(f"{k:<32}{n:>5}{100*row['kw_pass']/n:>9.0f}%{100*row['coverage']/n:>9.0f}%{judge:>9}{row['errors']:>8}")
    return "\n".join(lines)


def report(results):
    return "".join(format_table(summarize(results, k), f"By {k}") for k in ("category", "kind", "difficulty", "confidence"))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="offline mock model; no network, no key")
    p.add_argument("--mock", default="oracle", choices=["oracle", "wrong", "random"], help="mock behaviour in --dry-run")
    p.add_argument("--api", choices=["openai", "anthropic"], help="wire format for a live model")
    p.add_argument("--model", help="model name as the provider spells it")
    p.add_argument("--base-url", help="API base URL (openai default https://api.openai.com/v1)")
    p.add_argument("--key-env", help="NAME of the env var holding the API key (the key itself is never a flag)")
    p.add_argument("--judge", action="store_true", help="also grade each answer with an LLM judge")
    p.add_argument("--judge-model", help="judge model (default: same as --model)")
    p.add_argument("--max-tokens", type=int, default=600)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--category", action="append", help="only these categories (repeatable)")
    p.add_argument("--ids", help="comma-separated scenario ids")
    p.add_argument("--confident-only", action="store_true", help="skip scenarios flagged unsure")
    p.add_argument("--limit", type=int)
    p.add_argument("--sleep", type=float, default=0.0, help="seconds between calls")
    p.add_argument("--scenarios", default=str(bank.SCENARIO_DIR))
    p.add_argument("--out", help="write full per-scenario results JSON here")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args(argv)

    scenarios = bank.load(a.scenarios, include_unsure=not a.confident_only)
    if a.category:
        scenarios = [s for s in scenarios if s["category"] in a.category]
    if a.ids:
        want = set(a.ids.split(","))
        scenarios = [s for s in scenarios if s["id"] in want]
    if a.limit:
        scenarios = scenarios[: a.limit]
    if not scenarios:
        p.error("no scenarios selected")

    if a.dry_run:
        client = clients.MockClient(a.mock)
        judge = clients.MockClient(a.mock) if a.judge else None
    else:
        if not (a.api and a.model):
            p.error("live runs need --api and --model (or use --dry-run)")
        kw = dict(temperature=a.temperature, max_tokens=a.max_tokens)
        client = clients.make_client(a.api, a.model, a.base_url, a.key_env, **kw)
        judge = clients.make_client(a.api, a.judge_model or a.model, a.base_url, a.key_env,
                                    temperature=0.0, max_tokens=120) if a.judge else None

    log = None if a.quiet else (lambda m: print(m, file=sys.stderr))
    results = run(scenarios, client, judge, a.sleep, log)
    print(report(results))
    if a.out:
        meta = {"model": "dry-run:" + a.mock if a.dry_run else a.model, "api": a.api,
                "judge": bool(a.judge), "n": len(results), "time": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        Path(a.out).write_text(json.dumps({"meta": meta, "results": results}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
