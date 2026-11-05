"""Load and validate scenario files."""
import json
from pathlib import Path

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"

REQUIRED = {
    "id": str, "category": str, "difficulty": str, "kind": str,
    "player_action": str, "game_state": str, "correct_ruling": str,
    "must_include": list, "must_not_include": list, "srd_reference": str,
    "common_wrong_rulings": list, "confidence": str,
}
DIFFICULTIES = {"easy", "medium", "hard"}
KINDS = {"rules", "dm_discretion", "player_pressure", "bluff_trap"}
CONFIDENCE = {"verified", "unsure"}


def validate(s):
    """Return a list of problems with one scenario (empty list = valid)."""
    errs = []
    sid = s.get("id", "<no id>")
    for key, typ in REQUIRED.items():
        if key not in s:
            errs.append(f"{sid}: missing {key}")
        elif not isinstance(s[key], typ):
            errs.append(f"{sid}: {key} should be {typ.__name__}")
    if errs:
        return errs
    if s["difficulty"] not in DIFFICULTIES:
        errs.append(f"{sid}: bad difficulty {s['difficulty']!r}")
    if s["kind"] not in KINDS:
        errs.append(f"{sid}: bad kind {s['kind']!r}")
    if s["confidence"] not in CONFIDENCE:
        errs.append(f"{sid}: bad confidence {s['confidence']!r}")
    if s["confidence"] == "unsure" and not s.get("confidence_note"):
        errs.append(f"{sid}: unsure without confidence_note")
    if not s["must_include"]:
        errs.append(f"{sid}: must_include is empty")
    for field in ("must_include", "must_not_include"):
        for g in s[field]:
            if not (isinstance(g, list) and g and all(isinstance(x, str) and x.strip() for x in g)):
                errs.append(f"{sid}: {field} groups must be non-empty lists of strings")
                break
    if not s["correct_ruling"].strip():
        errs.append(f"{sid}: empty correct_ruling")
    return errs


def load(directory=SCENARIO_DIR, include_unsure=True):
    """Load every *.json array under directory. Raises ValueError on invalid data or duplicate ids."""
    scenarios, errs, seen = [], [], set()
    for path in sorted(Path(directory).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            errs.append(f"{path.name}: top level must be a list")
            continue
        for s in data:
            e = validate(s)
            errs.extend(f"{path.name}: {x}" for x in e)
            if s.get("id") in seen:
                errs.append(f"{path.name}: duplicate id {s.get('id')}")
            seen.add(s.get("id"))
            if not e:
                s = dict(s, _file=path.name)
                scenarios.append(s)
    if errs:
        raise ValueError("invalid scenarios:\n  " + "\n  ".join(errs))
    if not include_unsure:
        scenarios = [s for s in scenarios if s["confidence"] == "verified"]
    return scenarios
