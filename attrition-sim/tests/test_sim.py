"""Tests: SRD tables and rules, spell mechanics, determinism, metric sanity.
Run: python -m unittest discover -s tests   (from attrition-sim/)
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim import rules as R  # noqa: E402
from sim import engine as E  # noqa: E402
from sim.content import build_party, make_monster, MONSTERS, ENCOUNTERS  # noqa: E402


class TestSRDTables(unittest.TestCase):
    def test_bab(self):
        self.assertEqual([R.bab(9, p) for p in ("full", "medium", "poor")], [9, 6, 4])
        self.assertEqual(R.bab(3, "medium"), 2)

    def test_iteratives(self):
        self.assertEqual(R.iteratives(5), [0])
        self.assertEqual(R.iteratives(6), [0, -5])
        self.assertEqual(R.iteratives(11), [0, -5, -10])

    def test_saves(self):
        self.assertEqual(R.base_save(9, True), 6)
        self.assertEqual(R.base_save(9, False), 3)
        self.assertEqual(R.base_save(3, True), 3)

    def test_spells_per_day(self):
        self.assertEqual(R.SPELLS_PER_DAY[9], {1: 4, 2: 4, 3: 3, 4: 2, 5: 1})
        self.assertEqual(R.SPELLS_PER_DAY[5], {1: 3, 2: 2, 3: 1})

    def test_bonus_spells(self):
        self.assertEqual([R.bonus_spells(3, l) for l in (1, 2, 3, 4)], [1, 1, 1, 0])
        self.assertEqual(R.bonus_spells(5, 1), 2)  # Int 20: two bonus 1st-level spells
        self.assertEqual(R.slots(3, 3), {1: 3, 2: 2})
        self.assertEqual(R.slots(3, 3, domain=True), {1: 4, 2: 3})

    def test_hp(self):
        self.assertEqual(R.hp_for(1, 10, 2), 12)
        self.assertEqual(R.hp_for(3, 10, 2), 10 + 11 + 6)


class TestDice(unittest.TestCase):
    def test_save_prob_natural_rules(self):
        self.assertAlmostEqual(R.save_fail_prob(5, 30), 0.05)   # nat 1 always fails
        self.assertAlmostEqual(R.save_fail_prob(40, 0), 0.95)   # nat 20 always succeeds
        self.assertAlmostEqual(R.save_fail_prob(15, 4), 0.5)

    def test_hit_prob_matches_simulation(self):
        rng = random.Random(1)
        n = 20000
        hits = sum(R.attack(rng, 7, 18, 1, 6, 0) > 0 for _ in range(n)) / n
        self.assertAlmostEqual(hits, R.hit_prob(7, 18), delta=0.015)

    def test_crit_needs_confirmation_and_precision_not_multiplied(self):
        rng = random.Random(2)
        # vs impossible AC only natural 20s hit, confirmation fails unless nat 20 again
        dmgs = [R.attack(rng, 0, 100, 1, 1, 0, 20, 3, precision=0) for _ in range(20000)]
        self.assertTrue(all(d in (0, 1, 3) for d in dmgs))
        crit_rate = sum(d == 3 for d in dmgs) / len(dmgs)
        self.assertAlmostEqual(crit_rate, 1 / 400, delta=0.002)


class TestContent(unittest.TestCase):
    def test_party_numbers_level9(self):
        p = {c.cls: c for c in build_party(9)}
        f = p["fighter"]
        self.assertEqual(f.max_hp, 72)
        # BAB 9 + Str 18 (+4) + WF + 2 enh = 16
        self.assertEqual(f.attacks[0][0], 16)
        self.assertEqual(len(f.attacks), 2)
        self.assertEqual(p["rogue"].precision, 5)
        # wizard Int 18+2=20 (+5): 1st 4+2, 5th 1+1
        self.assertEqual(p["wizard"].slots, {1: 6, 2: 5, 3: 4, 4: 3, 5: 2})

    def test_every_encounter_monster_exists(self):
        for el, comps in ENCOUNTERS.items():
            for comp in comps:
                for m in comp:
                    self.assertIn(m, MONSTERS)


class _S:
    pass


def _state(enemies, level=5, **opts):
    s = E.State()
    s.rng = random.Random(3)
    o = dict(E.DEFAULTS)
    o.update(opts)
    s.opts = o
    s.level = level
    s.party = build_party(level)
    s.enemies = enemies
    s.stats = E.Stats()
    s.persistent = {}
    s.round, s.fight_index, s.day_length, s.el = 1, 1, 1, level
    return s


class TestSpells(unittest.TestCase):
    def test_sleep_hd_cap_and_undead_immunity(self):
        s = _state([make_monster("ogre"), make_monster("wight")], aoe_scale=10)
        wz = next(p for p in s.party if p.cls == "wizard")
        for _ in range(20):
            E.sleep(s, wz, do=True)
        self.assertNotIn("asleep", s.enemies[1].conditions)  # undead immune
        s2 = _state([make_monster("troll")], aoe_scale=10)
        E.sleep(s2, wz, do=True)
        self.assertNotIn("asleep", s2.enemies[0].conditions)  # 6 HD > 4 HD cap

    def test_fireball_damage_capped_at_10d6(self):
        s = _state([make_monster("frost giant")], aoe_scale=10)
        wz = next(p for p in s.party if p.cls == "wizard")
        wz.caster_level = 20
        s.enemies[0].max_hp = s.enemies[0].hp = 1000
        E.SPELLS["fireball"][1](s, wz, do=True)
        self.assertGreaterEqual(1000 - s.enemies[0].hp, 5)
        self.assertLessEqual(1000 - s.enemies[0].hp, 60)

    def test_hold_person_only_humanoids(self):
        s = _state([make_monster("ogre")])
        wz = next(p for p in s.party if p.cls == "wizard")
        self.assertEqual(E.SPELLS["hold person"][1](s, wz), 0)

    def test_helpless_target_dies_to_coup_de_grace_credit_to_controller(self):
        s = _state([make_monster("orc")])
        o = s.enemies[0]
        E.add_condition(o, "paralyzed", 5, "wizard")
        f = next(p for p in s.party if p.cls == "fighter")
        E.martial_turn(s, f, single=False)
        self.assertTrue(o.dead)
        self.assertEqual(s.stats.takedowns["wizard"], 1)
        self.assertEqual(s.stats.kills["fighter"], 1)


class TestPolicies(unittest.TestCase):
    def test_hold_early_blocks_first_fight_of_long_day(self):
        s = _state([make_monster("ogre")], policy="hold_early")
        s.day_length, s.fight_index = 6, 1
        wz = next(p for p in s.party if p.cls == "wizard")
        wz.full_slots = dict(wz.slots)
        self.assertEqual(E.max_spend_level(s, wz), 0)
        s.fight_index = 6
        self.assertEqual(E.max_spend_level(s, wz), 9)

    def test_emergency_overrides_hold(self):
        s = _state([make_monster("ogre")], policy="hold_early")
        s.day_length = 6
        s.party[0].hp = 1
        wz = next(p for p in s.party if p.cls == "wizard")
        self.assertEqual(E.max_spend_level(s, wz), 9)


class TestDay(unittest.TestCase):
    def test_deterministic(self):
        a = E.run_day(5, 4, random.Random(9), policy="threat")
        b = E.run_day(5, 4, random.Random(9), policy="threat")
        self.assertEqual(a, b)

    def test_slots_never_negative_and_accounting(self):
        rng = random.Random(4)
        for L in (3, 5, 7, 9):
            for pol in ("nova", "hold_early", "threat"):
                d = E.run_day(L, 6, rng, policy=pol)
                self.assertGreaterEqual(d["wizard_slots_left"], 0)
                self.assertLessEqual(d["wizard_slots_left"], 1)
                for f in d["fights"]:
                    self.assertGreaterEqual(min(f["damage"].values()), 0)
                    if f["won"]:
                        self.assertGreater(sum(f["kills"].values()), 0)
                        self.assertEqual(sum(f["kills"].values()),
                                         sum(f["takedowns"].values()))

    def test_nova_spends_more_than_hold_early_in_fight_one(self):
        rng = random.Random(5)
        spent = {}
        for pol in ("nova", "hold_early"):
            ds = [E.run_day(7, 6, rng, policy=pol) for _ in range(60)]
            spent[pol] = sum(d["fights"][0]["spent"]["wizard"] for d in ds)
        self.assertGreater(spent["nova"], spent["hold_early"])


if __name__ == "__main__":
    unittest.main()
