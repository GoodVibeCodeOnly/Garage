"""Score a model's ruling against a scenario.

Keyword scoring is deterministic and free: every must_include group needs at least one
of its phrases present (case-insensitive), and no must_not_include group may match.
It is a floor, not a judge: a model can say the right words for the wrong reason.
An optional LLM-judge pass (see run.py --judge) compares meaning against correct_ruling.
"""
import re

_WS = re.compile(r"\s+")
_DASHES = str.maketrans({"‐": "-", "‑": "-", "‒": "-", "–": "-",
                         "—": "-", "’": "'", "‘": "'"})


def normalize(text):
    return _WS.sub(" ", text.translate(_DASHES).lower()).strip()


def group_hit(text, group):
    return any(normalize(p) in text for p in group)


def score(scenario, answer):
    """Return dict(passed, coverage, missing, forbidden_hits)."""
    text = normalize(answer or "")
    inc = scenario["must_include"]
    missing = [g for g in inc if not group_hit(text, g)]
    forbidden = [g for g in scenario.get("must_not_include", []) if group_hit(text, g)]
    coverage = (len(inc) - len(missing)) / len(inc) if inc else 0.0
    return {
        "passed": not missing and not forbidden and bool(text),
        "coverage": round(coverage, 3),
        "missing": missing,
        "forbidden_hits": forbidden,
    }


JUDGE_PROMPT = """You are grading a Dungeon Master's ruling for D&D 3.5 (System Reference Document, rules as written).

Situation: {game_state}
Player: {player_action}

Reference ruling: {correct_ruling}
Known wrong rulings: {wrong}

Ruling under test:
<<<
{answer}
>>>

Does the ruling under test reach the same outcome as the reference ruling, for a compatible reason, without asserting any of the known wrong rulings? Minor extra detail is fine. Reply with exactly one word on the first line: PASS or FAIL. Then one sentence of reason."""


def judge_prompt(scenario, answer):
    return JUDGE_PROMPT.format(
        game_state=scenario["game_state"], player_action=scenario["player_action"],
        correct_ruling=scenario["correct_ruling"],
        wrong="; ".join(scenario["common_wrong_rulings"]) or "(none listed)",
        answer=answer)


def parse_judge(reply):
    first = normalize(reply or "").split(" ", 1)[0].strip(".:*")
    if first == "pass":
        return True
    if first == "fail":
        return False
    return None
