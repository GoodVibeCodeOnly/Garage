import json
import tempfile
import unittest
from pathlib import Path

from rulesbank import bank, clients, run, scoring

GOOD = {
    "id": "t-001", "category": "test", "difficulty": "easy", "kind": "rules",
    "player_action": "I stand up from prone.", "game_state": "Fighter is prone, enemy adjacent.",
    "correct_ruling": "Standing up is a move action and provokes an attack of opportunity.",
    "must_include": [["move action"], ["provokes", "attack of opportunity"]],
    "must_not_include": [["free action"]],
    "srd_reference": "CombatII > Actions in Combat", "common_wrong_rulings": ["Standing is a free action."],
    "confidence": "confident",
}


class TestScoring(unittest.TestCase):
    def test_pass(self):
        r = scoring.score(GOOD, GOOD["correct_ruling"])
        self.assertTrue(r["passed"])
        self.assertEqual(r["coverage"], 1.0)

    def test_missing_group(self):
        r = scoring.score(GOOD, "It is a move action.")
        self.assertFalse(r["passed"])
        self.assertEqual(r["coverage"], 0.5)

    def test_forbidden(self):
        r = scoring.score(GOOD, "Move action? No, a free action, and it provokes.")
        self.assertFalse(r["passed"])
        self.assertTrue(r["forbidden_hits"])

    def test_case_and_dash_normalization(self):
        s = dict(GOOD, must_include=[["5-foot step"]], must_not_include=[])
        self.assertTrue(scoring.score(s, "Take a 5‑Foot   Step.")["passed"])

    def test_empty_answer_fails(self):
        s = dict(GOOD, must_include=[[""]])
        self.assertFalse(scoring.score(s, "")["passed"])

    def test_parse_judge(self):
        self.assertTrue(scoring.parse_judge("PASS\nfine"))
        self.assertFalse(scoring.parse_judge("**FAIL**: wrong"))
        self.assertIsNone(scoring.parse_judge("maybe"))


class TestValidation(unittest.TestCase):
    def test_good(self):
        self.assertEqual(bank.validate(GOOD), [])

    def test_bad_fields(self):
        self.assertTrue(bank.validate(dict(GOOD, difficulty="trivial")))
        self.assertTrue(bank.validate(dict(GOOD, must_include=[])))
        self.assertTrue(bank.validate(dict(GOOD, must_include=["not a list"])))
        self.assertTrue(bank.validate(dict(GOOD, confidence="unsure")))  # needs a note
        self.assertEqual(bank.validate(dict(GOOD, confidence="unsure", confidence_note="x")), [])

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.json").write_text(json.dumps([GOOD]))
            Path(d, "b.json").write_text(json.dumps([GOOD]))
            with self.assertRaises(ValueError):
                bank.load(d)


class TestRunner(unittest.TestCase):
    def test_dry_run_oracle_and_wrong(self):
        good = run.run([GOOD], clients.MockClient("oracle"), clients.MockClient("oracle"))
        self.assertTrue(good[0]["passed"])
        self.assertTrue(good[0]["judge_pass"])
        bad = run.run([GOOD], clients.MockClient("wrong"), clients.MockClient("wrong"))
        self.assertFalse(bad[0]["passed"])
        self.assertFalse(bad[0]["judge_pass"])

    def test_report_has_all_row(self):
        res = run.run([GOOD, dict(GOOD, id="t-002", category="other")], clients.MockClient())
        text = run.report(res)
        self.assertIn("ALL", text)
        self.assertIn("other", text)

    def test_cli_dry_run_writes_results(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "s.json").write_text(json.dumps([GOOD]))
            out = Path(d, "out.json")
            self.assertEqual(run.main(["--dry-run", "--quiet", "--judge", "--scenarios", d, "--out", str(out)]), 0)
            data = json.loads(out.read_text())
            self.assertEqual(data["meta"]["n"], 1)
            self.assertTrue(data["results"][0]["passed"])

    def test_live_requires_model(self):
        with self.assertRaises(SystemExit):
            run.main(["--api", "openai", "--quiet"])

    def test_live_client_payload_shape(self):
        # No network: patch the transport and check what would be sent.
        sent = {}

        def fake_post(url, headers, body, timeout, retries=3):
            sent.update(url=url, headers=headers, body=body)
            return {"choices": [{"message": {"content": "ruling"}}]}

        orig = clients._post
        clients._post = fake_post
        try:
            c = clients.OpenAIClient("m", "http://x/v1", "k")
            self.assertEqual(c.chat("sys", "usr"), "ruling")
        finally:
            clients._post = orig
        self.assertEqual(sent["url"], "http://x/v1/chat/completions")
        self.assertEqual(sent["headers"]["Authorization"], "Bearer k")
        self.assertEqual(sent["body"]["messages"][0]["role"], "system")


class TestTheBank(unittest.TestCase):
    """Checks on the real scenario files."""

    @classmethod
    def setUpClass(cls):
        cls.scenarios = bank.load()

    def test_loads_and_is_large(self):
        self.assertGreaterEqual(len(self.scenarios), 300)

    def test_reference_ruling_passes_its_own_keywords(self):
        # If the reference answer can't pass, the keywords are wrong, not the model.
        bad = [s["id"] for s in self.scenarios if not scoring.score(s, s["correct_ruling"])["passed"]]
        self.assertEqual(bad, [], f"reference rulings failing own keywords: {bad}")

    def test_every_scenario_has_srd_reference_and_wrong_ruling(self):
        bad = [s["id"] for s in self.scenarios if not s["srd_reference"].strip() or not s["common_wrong_rulings"]]
        self.assertEqual(bad, [])

    def test_forbidden_phrases_not_in_prompt(self):
        # A correct answer may quote the player; a forbidden phrase taken from the prompt
        # would then fail a correct answer.
        bad = []
        for s in self.scenarios:
            prompt = scoring.normalize(s["player_action"] + " " + s["game_state"])
            if any(scoring.group_hit(prompt, g) for g in s["must_not_include"]):
                bad.append(s["id"])
        self.assertEqual(bad, [], f"must_not_include phrases echo the prompt: {bad}")

    def test_kinds_present(self):
        kinds = {s["kind"] for s in self.scenarios}
        self.assertTrue({"rules", "dm_discretion", "player_pressure", "bluff_trap"} <= kinds)


if __name__ == "__main__":
    unittest.main()
