"""Core D&D 3.5 SRD mechanics: progressions, dice, attacks, saves, spell slots.

Everything here comes from the System Reference Document (open content):
base attack bonus and save progressions, spells per day for clerics/wizards,
bonus spells from a high ability score, the d20 attack and saving-throw rules,
critical threat + confirmation, natural 1/20 rules.
"""
import math


def bab(level, prog):
    """Base attack bonus. prog: 'full' (fighter), 'medium' (cleric, rogue), 'poor' (wizard)."""
    if prog == "full":
        return level
    if prog == "medium":
        return (level * 3) // 4
    return level // 2


def iteratives(bab_value):
    """Iterative attack bonuses offsets for a full attack: +BAB, +BAB-5, ... while > 0."""
    out = [0]
    b = bab_value - 5
    while b > 0:
        out.append(out[-1] - 5)
        b -= 5
    return out


def base_save(level, good):
    return 2 + level // 2 if good else level // 3


# SRD spells per day, cleric and wizard share this table (excluding 0-level and domain slots).
SPELLS_PER_DAY = {
    1: {1: 1}, 2: {1: 2}, 3: {1: 2, 2: 1}, 4: {1: 3, 2: 2}, 5: {1: 3, 2: 2, 3: 1},
    6: {1: 3, 2: 3, 3: 2}, 7: {1: 4, 2: 3, 3: 2, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
    9: {1: 4, 2: 4, 3: 3, 4: 2, 5: 1}, 10: {1: 4, 2: 4, 3: 3, 4: 3, 5: 2},
}


def ability_mod(score):
    return (score - 10) // 2


def bonus_spells(mod, spell_level):
    """SRD Table: Ability Modifiers and Bonus Spells."""
    if spell_level < 1 or mod < spell_level:
        return 0
    return (mod - spell_level) // 4 + 1


def slots(level, casting_mod, domain=False):
    base = SPELLS_PER_DAY[level]
    out = {}
    for sl, n in base.items():
        out[sl] = n + bonus_spells(casting_mod, sl) + (1 if domain else 0)
    return out


def roll(rng, n, d):
    return sum(rng.randint(1, d) for _ in range(n))


def save_fail_prob(dc, save_bonus):
    """P(fail) on d20 + bonus vs DC; natural 1 always fails, natural 20 always succeeds."""
    succeed_faces = sum(1 for r in range(1, 21)
                        if r == 20 or (r != 1 and r + save_bonus >= dc))
    return 1 - succeed_faces / 20


def saving_throw(rng, dc, save_bonus):
    """True if the save succeeds."""
    r = rng.randint(1, 20)
    if r == 1:
        return False
    if r == 20:
        return True
    return r + save_bonus >= dc


def hit_prob(bonus, ac):
    faces = sum(1 for r in range(1, 21) if r == 20 or (r != 1 and r + bonus >= ac))
    return faces / 20


def attack(rng, bonus, ac, n, d, mod, crit_range=20, crit_mult=2,
           precision=0, crit_immune=False, miss_chance=0.0):
    """One SRD attack roll. Returns damage dealt (0 on miss).

    precision: extra d6 (sneak attack) - never multiplied on a crit (SRD).
    """
    r = rng.randint(1, 20)
    if r == 1:
        return 0
    if r != 20 and r + bonus < ac:
        return 0
    if miss_chance and rng.random() < miss_chance:
        return 0
    mult = 1
    if r >= crit_range and not crit_immune:
        c = rng.randint(1, 20)
        if c != 1 and (c == 20 or c + bonus >= ac):
            mult = crit_mult
    dmg = 0
    for _ in range(mult):
        dmg += roll(rng, n, d) + mod
    dmg = max(1, dmg)  # SRD: minimum 1 damage on a hit
    if precision:
        dmg += roll(rng, precision, 6)
    return dmg


def expected_attack(bonus, ac, n, d, mod, precision=0):
    return hit_prob(bonus, ac) * (n * (d + 1) / 2 + mod + precision * 3.5)


def hp_for(level, hd, con_mod):
    """Max HD at 1st level, then average (d/2 + 0.5) per level, + Con per level."""
    return hd + math.floor((level - 1) * (hd / 2 + 0.5)) + con_mod * level
