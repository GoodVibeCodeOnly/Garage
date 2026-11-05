"""Party builds and SRD monsters.

Party ability scores, feats and gear are MODEL ASSUMPTIONS (see ASSUMPTIONS in
FINDINGS.md); the mechanics that turn them into numbers are SRD.
Monster stat blocks are transcribed from the SRD monster entries (average HP).
"""
from . import rules as R

# --- gear by level: (weapon enhancement, armor enhancement, cloak of resistance, ring of protection,
#                     +2 casting-stat item). Assumption: modest "by the book-ish" magic. ---
GEAR = {3: (0, 0, 0, 0, 0), 5: (1, 1, 1, 0, 0), 7: (1, 2, 1, 1, 2), 9: (2, 2, 2, 1, 2)}


def _stat(base, level):
    """+1 to the primary stat at 4th and 8th (SRD ability increase)."""
    return base + (1 if level >= 4 else 0) + (1 if level >= 8 else 0)


class Combatant:
    def __init__(self, **kw):
        self.side = "party"
        self.flags = set()
        self.conditions = {}
        self.dead = False
        self.precision = 0
        self.ctype = "humanoid"
        self.hd = 1
        self.regen = 0
        self.size = "M"
        self.__dict__.update(kw)
        self.hp = self.max_hp

    @property
    def standing(self):
        return not self.dead and self.hp > 0

    def __repr__(self):
        return f"<{self.name} {self.hp}/{self.max_hp}>"


def build_party(level):
    wpn, arm, cloak, ring, stat_item = GEAR[level]
    party = []

    # Fighter: Str 16 Dex 13 Con 14; greatsword; Weapon Focus, Weapon Specialization (4th).
    st = _stat(16, level)
    sm = R.ability_mod(st)
    b = R.bab(level, "full")
    armor_ac = 6 if level < 5 else 8  # banded mail at 3rd, full plate after
    party.append(Combatant(
        name="fighter", cls="fighter", max_hp=R.hp_for(level, 10, 2),
        ac=10 + armor_ac + arm + 1 + ring, init=1,
        saves={"fort": R.base_save(level, True) + 2 + cloak,
               "ref": R.base_save(level, False) + 1 + cloak,
               "will": R.base_save(level, False) + cloak},
        attacks=[(b + o + sm + 1 + wpn, 2, 6, int(sm * 1.5) + wpn + (2 if level >= 4 else 0), 19, 2)
                 for o in R.iteratives(b)],
    ))

    # Cleric: Str 14 Dex 10 Con 14 Wis 16; morningstar; banded/full plate + heavy shield.
    wis = _stat(16, level) + stat_item
    wm = R.ability_mod(wis)
    b = R.bab(level, "medium")
    party.append(Combatant(
        name="cleric", cls="cleric", max_hp=R.hp_for(level, 8, 2),
        ac=10 + armor_ac + arm + 2 + ring, init=0,
        saves={"fort": R.base_save(level, True) + 2 + cloak,
               "ref": R.base_save(level, False) + cloak,
               "will": R.base_save(level, True) + wm + cloak},
        attacks=[(b + o + 2 + wpn, 1, 8, 2 + wpn, 20, 2) for o in R.iteratives(b)],
        caster_level=level, cast_mod=wm,
        slots=R.slots(level, wm, domain=True),
    ))

    # Rogue: Str 12 Dex 16 Con 12; rapier with Weapon Finesse; studded leather.
    dx = _stat(16, level)
    dm = R.ability_mod(dx)
    b = R.bab(level, "medium")
    party.append(Combatant(
        name="rogue", cls="rogue", max_hp=R.hp_for(level, 6, 1),
        ac=10 + 3 + arm + dm + ring, init=dm,
        saves={"fort": R.base_save(level, False) + 1 + cloak,
               "ref": R.base_save(level, True) + dm + cloak,
               "will": R.base_save(level, False) + cloak},
        attacks=[(b + o + dm + wpn, 1, 6, 1 + wpn, 18, 2) for o in R.iteratives(b)],
        precision=(level + 1) // 2,
    ))

    # Wizard: Dex 14 Con 12 Int 16; light crossbow; no armor.
    it = _stat(16, level) + stat_item
    im = R.ability_mod(it)
    b = R.bab(level, "poor")
    party.append(Combatant(
        name="wizard", cls="wizard", max_hp=R.hp_for(level, 4, 1),
        ac=10 + 2 + ring + (1 if level >= 5 else 0), init=2,
        saves={"fort": R.base_save(level, False) + 1 + cloak,
               "ref": R.base_save(level, False) + 2 + cloak,
               "will": R.base_save(level, True) + cloak},
        attacks=[(b + 2, 1, 8, 0, 19, 2)],  # crossbow: one shot per round (reload)
        caster_level=level, cast_mod=im,
        slots=R.slots(level, im),
    ))
    return party


# --- SRD monsters: name: (CR, type, HD, avg hp, AC, touch AC, (F,R,W), init, attacks, flags, size)
# attacks: list of (bonus, n, d, mod, crit_range, crit_mult); full attack uses all, a standard
# (move + attack) uses only the first.
MONSTERS = {
    "orc":         (0.5, "humanoid", 1, 5, 13, 10, (3, 0, -2), 0, [(4, 2, 4, 4, 18, 2)], set(), "M"),
    "hobgoblin":   (0.5, "humanoid", 1, 6, 15, 11, (4, 1, -1), 1, [(2, 1, 8, 1, 19, 2)], set(), "M"),
    "gnoll":       (1, "humanoid", 2, 11, 15, 10, (4, 0, 0), 0, [(3, 1, 8, 2, 20, 3)], set(), "M"),
    "bugbear":     (2, "humanoid", 3, 16, 17, 11, (2, 4, 1), 1, [(5, 1, 8, 2, 20, 2)], set(), "M"),
    "ogre":        (3, "giant", 4, 29, 16, 8, (6, 0, 1), -1, [(8, 2, 8, 7, 20, 2)], set(), "L"),
    "wight":       (3, "undead", 4, 26, 15, 11, (1, 2, 5), 1, [(3, 1, 4, 1, 20, 2)], {"undead"}, "M"),
    "owlbear":     (4, "magical beast", 5, 52, 15, 10, (9, 5, 2), 1,
                    [(9, 1, 6, 5, 20, 2), (9, 1, 6, 5, 20, 2), (4, 1, 8, 2, 20, 2)], set(), "L"),
    "minotaur":    (4, "monstrous humanoid", 6, 39, 14, 9, (6, 5, 5), 0,
                    [(9, 3, 6, 6, 20, 3), (4, 3, 6, 6, 20, 3), (4, 1, 8, 2, 20, 2)], set(), "L"),
    "troll":       (5, "giant", 6, 63, 16, 11, (11, 4, 3), 2,
                    [(9, 1, 6, 6, 20, 2), (9, 1, 6, 6, 20, 2), (4, 1, 6, 3, 20, 2)], {"regen"}, "L"),
    "manticore":   (5, "magical beast", 6, 57, 17, 11, (9, 7, 3), 2,
                    [(10, 2, 4, 5, 20, 2), (10, 2, 4, 5, 20, 2), (8, 1, 8, 2, 20, 2)], set(), "L"),
    "ettin":       (6, "giant", 10, 65, 18, 9, (9, 3, 5), 3,
                    [(12, 2, 6, 6, 20, 2), (12, 2, 6, 6, 20, 2), (7, 2, 6, 6, 20, 2),
                     (7, 2, 6, 6, 20, 2)], set(), "L"),
    "hill giant":  (7, "giant", 12, 102, 20, 9, (12, 3, 4), -1,
                    [(16, 2, 8, 10, 20, 2), (11, 2, 8, 10, 20, 2)], set(), "L"),
    "stone giant": (8, "giant", 14, 119, 25, 10, (13, 8, 7), 2,
                    [(17, 2, 8, 10, 20, 2), (12, 2, 8, 10, 20, 2)], set(), "L"),
    "frost giant": (9, "giant", 14, 133, 21, 9, (14, 4, 6), -1,
                    [(18, 3, 6, 13, 20, 3), (13, 3, 6, 13, 20, 3)], set(), "L"),
}


def make_monster(name, idx=0):
    cr, ctype, hd, hp, ac, touch, (f, r, w), init, attacks, flags, size = MONSTERS[name]
    return Combatant(name=f"{name}#{idx}", cls=name, side="enemy", cr=cr, ctype=ctype, hd=hd,
                     max_hp=hp, ac=ac, touch=touch, saves={"fort": f, "ref": r, "will": w},
                     init=init, attacks=list(attacks), flags=set(flags), size=size,
                     regen=5 if "regen" in flags else 0)


# Encounter tables by EL, using the SRD rule of thumb that doubling the number of
# same-CR creatures adds +2 to EL (two CR x = EL x+2, four = EL x+4); for CR 1/2,
# four creatures ~ EL 2, six ~ EL 3, eight ~ EL 4.
ENCOUNTERS = {
    2: [["gnoll"] * 2, ["orc"] * 4, ["bugbear"], ["hobgoblin"] * 4],
    3: [["ogre"], ["wight"], ["orc"] * 6, ["gnoll", "gnoll", "orc", "orc"]],
    4: [["owlbear"], ["minotaur"], ["bugbear"] * 2, ["orc"] * 8, ["ogre", "orc", "orc"]],
    5: [["troll"], ["manticore"], ["ogre"] * 2, ["wight"] * 2, ["gnoll"] * 4],
    6: [["ettin"], ["owlbear"] * 2, ["minotaur"] * 2, ["bugbear"] * 4, ["ogre"] * 3],
    7: [["hill giant"], ["troll"] * 2, ["manticore"] * 2, ["ogre"] * 4, ["wight"] * 4],
    8: [["stone giant"], ["ettin"] * 2, ["owlbear"] * 4, ["troll", "troll", "ogre", "ogre"]],
    9: [["frost giant"], ["hill giant"] * 2, ["troll"] * 4, ["manticore"] * 4],
    10: [["stone giant"] * 2, ["frost giant", "hill giant"], ["ettin"] * 4],
    11: [["frost giant"] * 2, ["hill giant"] * 4],
    12: [["frost giant", "frost giant", "hill giant", "hill giant"], ["stone giant"] * 4],
    13: [["frost giant"] * 4],
}
