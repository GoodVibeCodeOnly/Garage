"""Combat and adventuring-day engine.

Abstractions (also listed in FINDINGS.md):
- No grid. Everyone is engaged from round 1; in round 1 melee creatures (both sides)
  move and get only a single attack, casters act normally.
- Area spells catch each enemy independently with probability COVER[spell] * aoe_scale.
- Enemies pick a standing PC by weight (front-liners drawn more often).
- Helpless enemies (asleep, paralysed, unconscious) are coup-de-graced by martials (SRD:
  automatic critical, Fort DC 10 + damage or die).
"""
import math
from . import rules as R
from .content import build_party, make_monster, ENCOUNTERS

CLASSES = ("fighter", "cleric", "rogue", "wizard")

DEFAULTS = dict(
    policy="nova",            # nova | hold_early | threat
    aoe_scale=1.0,            # multiplies area coverage probabilities
    target_weights={"fighter": 4.0, "cleric": 2.5, "rogue": 2.0, "wizard": 1.0},
    flank_prob=0.5,           # chance a rogue attack gets sneak attack vs a non-denied target
    wand=False,               # wand of cure light wounds for out-of-combat healing
    loadout="mixed",          # mixed | blaster | controller
    known_length=True,        # casters know how many fights the day holds
    assumed_length=4,         # if not, what they plan for
    el_offsets=((-1, 0.2), (0, 0.5), (1, 0.2), (2, 0.1)),
    max_rounds=30,
)

COVER = {"fireball": 0.8, "ice storm": 0.8, "cone of cold": 0.7, "color spray": 0.6,
         "sleep": 0.7, "stinking cloud": 0.7, "glitterdust": 0.7, "flame strike": 0.5}

LOADOUTS = {
    "mixed": {1: ["color spray", "magic missile", "sleep", "magic missile", "color spray"],
              2: ["scorching ray", "glitterdust", "scorching ray", "glitterdust", "scorching ray"],
              3: ["fireball", "stinking cloud", "hold person", "fireball"],
              4: ["ice storm", "ice storm", "ice storm"],
              5: ["cone of cold", "hold monster"]},
    "blaster": {1: ["magic missile"] * 5, 2: ["scorching ray"] * 5, 3: ["fireball"] * 4,
                4: ["ice storm"] * 3, 5: ["cone of cold"] * 2},
    "controller": {1: ["sleep", "color spray"] * 3, 2: ["glitterdust"] * 5,
                   3: ["stinking cloud", "hold person"] * 2, 4: ["ice storm"] * 3,
                   5: ["hold monster"] * 2},
}
# cleric: offensive preparations by level; every other slot is a cure (and any slot can
# be spontaneously converted to a cure, SRD).
CLERIC_PREP = {2: ["spiritual weapon", "hold person"], 3: ["searing light"],
               5: ["flame strike"]}
CURE = {1: (1, 5), 2: (2, 10), 3: (3, 15), 4: (4, 20), 5: (5, 25)}  # (d8s, max CL bonus)

MIND_IMMUNE = {"undead"}
HUMANOID = {"humanoid"}


class Stats:
    """Per-fight accounting."""

    def __init__(self):
        self.damage = {c: 0 for c in CLASSES}
        self.kills = {c: 0 for c in CLASSES}
        self.takedowns = {c: 0 for c in CLASSES}  # kill credit to whoever disabled a helpless foe
        self.denied = {c: 0 for c in CLASSES}     # enemy turns lost to your conditions
        self.healing = 0
        self.slot_levels_spent = {"cleric": 0, "wizard": 0}
        self.spells_cast = {"cleric": 0, "wizard": 0}
        self.rounds = 0


# ---------------------------------------------------------------------------------- helpers

def living(group):
    return [c for c in group if c.standing]


def disabled(c):
    return any(k in c.conditions for k in ("asleep", "paralyzed", "unconscious", "stunned",
                                           "nauseated"))


def helpless(c):
    return any(k in c.conditions for k in ("asleep", "paralyzed", "unconscious"))


def denied_dex(c):
    return helpless(c) or "stunned" in c.conditions or "blinded" in c.conditions


def eff_ac(c, touch=False):
    ac = c.touch if touch else c.ac
    if helpless(c):
        ac -= 5   # Dex treated as 0 (approximated as -5 relative)
        ac -= 4   # +4 melee vs helpless, folded into AC
    elif "stunned" in c.conditions or "blinded" in c.conditions:
        ac -= 2
    return ac


def deal(state, src_cls, target, dmg, energy=None):
    if dmg <= 0 or target.dead:
        return
    dealt = min(dmg, max(target.hp, 0) + 10 if target.side == "party" else max(target.hp, 0))
    target.hp -= dmg
    state.stats.damage[src_cls] += dealt
    if energy in ("fire", "acid") and target.regen:
        target.flags.add("burned")
    if "asleep" in target.conditions:
        del target.conditions["asleep"]  # SRD: wounding wakes a sleeper
    if target.side == "enemy" and target.hp <= 0:
        kill(state, src_cls, target)


def kill(state, src_cls, target):
    target.dead = True
    state.stats.kills[src_cls] += 1
    controller = target.conditions.get("_disabled_by") if helpless(target) else None
    state.stats.takedowns[controller or src_cls] += 1
    target.conditions.clear()


def add_condition(target, cond, rounds, by):
    target.conditions[cond] = max(rounds, target.conditions.get(cond, 0))
    if cond in ("asleep", "paralyzed", "unconscious"):
        target.conditions["_disabled_by"] = by
    target.conditions.setdefault("_by", {})[cond] = by


def covered(state, spell, enemies):
    p = min(1.0, COVER[spell] * state.opts["aoe_scale"])
    return [e for e in enemies if state.rng.random() < p]


def exp_cover(state, spell):
    return min(1.0, COVER[spell] * state.opts["aoe_scale"])


# ---------------------------------------------------------------------------------- spells
# Each spell: (level, value(state, caster) -> expected neutralised HP, cast(state, caster)).

def dc(caster, level):
    return 10 + level + caster.cast_mod


def _dmg_value(targets, avg, pfail_fn=None, half=True):
    v = 0
    for t in targets:
        if pfail_fn is None:
            e = avg
        else:
            p = pfail_fn(t)
            e = avg * (p + (1 - p) * (0.5 if half else 0))
        v += min(e, t.hp)
    return v


def _control_value(targets, pfail_fn, weight=1.0):
    return sum(pfail_fn(t) * t.hp * weight for t in targets if not disabled(t))


def magic_missile(state, c, do=False):
    n = min(5, (c.caster_level + 1) // 2)
    foes = living(state.enemies)
    if not do:
        t = min(foes, key=lambda e: e.hp)
        return min(n * 3.5, t.hp) + max(0, n * 3.5 - t.hp) * 0.5
    for _ in range(n):  # missiles split to finish off targets
        foes = living(state.enemies)
        if not foes:
            return
        t = min(foes, key=lambda e: e.hp)
        deal(state, c.cls, t, R.roll(state.rng, 1, 4) + 1, "force")


def scorching_ray(state, c, do=False):
    rays = 1 if c.caster_level < 7 else (2 if c.caster_level < 11 else 3)
    bonus = R.bab(c.caster_level, "poor") + 2
    foes = living(state.enemies)
    if not do:
        t = max(foes, key=lambda e: e.hp)
        return rays * min(14 * R.hit_prob(bonus, eff_ac(t, True)), t.hp)
    for _ in range(rays):
        foes = living(state.enemies)
        if not foes:
            return
        t = max(foes, key=lambda e: e.hp)
        if state.rng.randint(1, 20) + bonus >= eff_ac(t, True):
            deal(state, c.cls, t, R.roll(state.rng, 4, 6), "fire")


def _area_damage(spell, dice_n, dice_d, save, energy, half=True):
    def fn(state, c, do=False):
        level = SPELLS[spell][0]
        foes = living(state.enemies)
        the_dc = dc(c, level)
        if not do:
            avg = dice_n(c) * (dice_d + 1) / 2
            pf = (lambda t: R.save_fail_prob(the_dc, t.saves[save])) if save else None
            return exp_cover(state, spell) * _dmg_value(foes, avg, pf, half)
        for t in covered(state, spell, foes):
            dmg = R.roll(state.rng, dice_n(c), dice_d)
            if spell == "ice storm":
                dmg += R.roll(state.rng, 2, 6)
            if save and R.saving_throw(state.rng, the_dc, t.saves[save]):
                dmg = dmg // 2 if half else 0
            deal(state, c.cls, t, dmg, energy)
    return fn


def sleep(state, c, do=False):
    the_dc = dc(c, 1)
    foes = sorted([e for e in living(state.enemies) if e.hd <= 4 and e.ctype not in MIND_IMMUNE
                   and not disabled(e)], key=lambda e: e.hd)
    budget, picked = 4, []
    for e in foes:
        if e.hd <= budget:
            picked.append(e)
            budget -= e.hd
    if not do:
        return exp_cover(state, "sleep") * _control_value(
            picked, lambda t: R.save_fail_prob(the_dc, t.saves["will"]))
    for t in covered(state, "sleep", picked):
        if not R.saving_throw(state.rng, the_dc, t.saves["will"]):
            add_condition(t, "asleep", 99, c.cls)


def color_spray(state, c, do=False):
    the_dc = dc(c, 1)
    foes = [e for e in living(state.enemies) if e.ctype not in MIND_IMMUNE]
    if not do:
        def w(t):
            return 1.0 if t.hd <= 2 else (0.6 if t.hd <= 4 else 0.1)
        return exp_cover(state, "color spray") * sum(
            R.save_fail_prob(the_dc, t.saves["will"]) * t.hp * w(t) for t in foes
            if not disabled(t))
    for t in covered(state, "color spray", foes):
        if R.saving_throw(state.rng, the_dc, t.saves["will"]):
            continue
        if t.hd <= 2:
            add_condition(t, "unconscious", R.roll(state.rng, 2, 4), c.cls)
        elif t.hd <= 4:
            add_condition(t, "stunned", R.roll(state.rng, 1, 4), c.cls)
            add_condition(t, "blinded", R.roll(state.rng, 1, 4) + 1, c.cls)
        else:
            add_condition(t, "stunned", 1, c.cls)


def glitterdust(state, c, do=False):
    the_dc = dc(c, 2)
    foes = [e for e in living(state.enemies) if "blinded" not in e.conditions]
    if not do:
        # blinded: 50% miss chance on its attacks, -2 AC, sneak-attackable: ~0.45 of a kill
        return exp_cover(state, "glitterdust") * _control_value(
            foes, lambda t: R.save_fail_prob(the_dc, t.saves["will"]), 0.45)
    for t in covered(state, "glitterdust", foes):
        if not R.saving_throw(state.rng, the_dc, t.saves["will"]):
            add_condition(t, "blinded", c.caster_level, c.cls)


def stinking_cloud(state, c, do=False):
    the_dc = dc(c, 3)
    foes = [e for e in living(state.enemies) if e.ctype not in MIND_IMMUNE]
    if not do:
        return exp_cover(state, "stinking cloud") * _control_value(
            foes, lambda t: R.save_fail_prob(the_dc, t.saves["fort"]), 0.8)
    for t in covered(state, "stinking cloud", foes):
        t.conditions["_cloud"] = c.caster_level  # re-save each round while it lasts
        t.conditions["_cloud_dc"] = the_dc
        if not R.saving_throw(state.rng, the_dc, t.saves["fort"]):
            add_condition(t, "nauseated", c.caster_level + R.roll(state.rng, 1, 4) + 1, c.cls)


def _hold(spell, level, allowed):
    def fn(state, c, do=False):
        the_dc = dc(c, level)
        foes = [e for e in living(state.enemies) if allowed(e) and not disabled(e)]
        if not foes:
            return 0
        t = max(foes, key=lambda e: R.save_fail_prob(the_dc, e.saves["will"]) * e.hp)
        if not do:
            return R.save_fail_prob(the_dc, t.saves["will"]) * t.hp
        if not R.saving_throw(state.rng, the_dc, t.saves["will"]):
            add_condition(t, "paralyzed", c.caster_level, c.cls)
            t.conditions["_hold_dc"] = the_dc
    return fn


def spiritual_weapon(state, c, do=False):
    if not do:
        return 0 if state.persistent.get("spiritual weapon") else \
            min(c.caster_level, 6) * 0.6 * (4.5 + min(5, c.caster_level // 3))
    state.persistent["spiritual weapon"] = c.caster_level


def searing_light(state, c, do=False):
    foes = living(state.enemies)
    bonus = R.bab(c.caster_level, "medium")
    t = max(foes, key=lambda e: e.hp)
    undead = t.ctype == "undead"
    n = min(10, c.caster_level) if undead else min(5, c.caster_level // 2)
    d = 6 if undead else 8
    if not do:
        return min(R.hit_prob(bonus, eff_ac(t, True)) * n * (d + 1) / 2, t.hp)
    if state.rng.randint(1, 20) + bonus >= eff_ac(t, True):
        deal(state, c.cls, t, R.roll(state.rng, n, d), "light")


SPELLS = {
    "magic missile": (1, magic_missile),
    "sleep": (1, sleep),
    "color spray": (1, color_spray),
    "scorching ray": (2, scorching_ray),
    "glitterdust": (2, glitterdust),
    "fireball": (3, _area_damage("fireball", lambda c: min(10, c.caster_level), 6, "ref", "fire")),
    "stinking cloud": (3, stinking_cloud),
    "hold person": (3, _hold("hold person", 3, lambda e: e.ctype in HUMANOID)),
    "ice storm": (4, _area_damage("ice storm", lambda c: 3, 6, None, "cold")),
    "cone of cold": (5, _area_damage("cone of cold", lambda c: min(15, c.caster_level), 6,
                                     "ref", "cold")),
    "hold monster": (5, _hold("hold monster", 5, lambda e: e.ctype not in MIND_IMMUNE)),
    # cleric
    "spiritual weapon": (2, spiritual_weapon),
    "cleric hold person": (2, _hold("hold person", 2, lambda e: e.ctype in HUMANOID)),
    "searing light": (3, searing_light),
    "flame strike": (5, _area_damage("flame strike", lambda c: min(15, c.caster_level), 6,
                                     "ref", "fire")),
}


# ---------------------------------------------------------------------------------- policies

def party_hp_frac(state):
    pcs = [p for p in state.party if not p.dead]
    return sum(max(p.hp, 0) for p in pcs) / max(1, sum(p.max_hp for p in state.party))


def emergency(state):
    for p in state.party:
        if not p.dead and (p.hp <= 0 or p.hp < 0.25 * p.max_hp):
            return True
    return party_hp_frac(state) < 0.5


def max_spend_level(state, caster):
    """Highest spell level the policy lets this caster spend right now (0 = none)."""
    pol = state.opts["policy"]
    if pol == "nova":
        return 9
    n = state.day_length if state.opts["known_length"] else state.opts["assumed_length"]
    k = state.fight_index  # 1-based
    last = k >= n
    if pol == "hold_early":
        early = k <= math.ceil(n / 2) and not last
        if early and not emergency(state):
            return 0
        return 9
    if pol == "threat":
        if last or emergency(state) or state.el >= state.level + 1:
            return 9
        # fight dragging on: enemies still have >half their HP after round 2
        tot = sum(e.max_hp for e in state.enemies)
        left = sum(max(0, e.hp) for e in state.enemies if not e.dead)
        if state.round >= 3 and left > 0.5 * tot:
            return 9
        # budget pacing: allow cheap spells if we are ahead of an even spend schedule
        remaining = sum(l * n_ for l, n_ in caster.slots.items())
        full = sum(l * n_ for l, n_ in caster.full_slots.items())
        if remaining / max(1, full) > (n - k + 1) / n + 0.15:
            return 2
        return 0
    raise ValueError(pol)


# ---------------------------------------------------------------------------------- actions

def choose_target(state):
    foes = living(state.enemies)
    active = [e for e in foes if not disabled(e)]
    pool = active or foes
    return min(pool, key=lambda e: e.hp) if pool else None


def martial_turn(state, pc, single):
    t = choose_target(state)
    if t is None:
        return
    if helpless(t):
        # coup de grace: automatic critical; Fort DC 10 + damage or die
        b, n, d, mod, cr, cm = pc.attacks[0]
        dmg = sum(R.roll(state.rng, n, d) + mod for _ in range(cm))
        if pc.precision and t.ctype != "undead":
            dmg += R.roll(state.rng, pc.precision, 6)
        by = t.conditions.get("_disabled_by") or pc.cls
        before = max(t.hp, 0)
        t.hp -= dmg
        state.stats.damage[pc.cls] += min(dmg, before)
        if t.hp <= 0 or not R.saving_throw(state.rng, 10 + dmg, t.saves["fort"]):
            t.dead = True
            state.stats.kills[pc.cls] += 1
            state.stats.takedowns[by] += 1
            t.conditions.clear()
        else:
            t.conditions.pop("asleep", None)
        return
    atks = pc.attacks[:1] if single else pc.attacks
    for (b, n, d, mod, cr, cm) in atks:
        t = choose_target(state)
        if t is None:
            return
        prec = 0
        if pc.precision and t.ctype != "undead":
            if denied_dex(t) or state.rng.random() < state.opts["flank_prob"]:
                prec = pc.precision
        dmg = R.attack(state.rng, b, eff_ac(t), n, d, mod, cr, cm, precision=prec,
                       crit_immune=t.ctype == "undead")
        deal(state, pc.cls, t, dmg)


def spend(caster, level, state):
    caster.slots[level] -= 1
    state.stats.slot_levels_spent[caster.cls] += level
    state.stats.spells_cast[caster.cls] += 1


def best_spell(state, caster, cap):
    best, best_v = None, 0
    for lvl in sorted(caster.slots):
        if lvl > cap or caster.slots[lvl] <= 0:
            continue
        for name in caster.prepared.get(lvl, []):
            if caster.cls == "cleric" and name == "hold person":
                name = "cleric hold person"
            v = SPELLS[name][1](state, caster)
            v = v - lvl * 0.5  # mild preference for cheaper slots at equal value
            if v > best_v:
                best, best_v = (lvl, name), v
    return best, best_v


def wizard_turn(state, wz):
    cap = max_spend_level(state, wz)
    if cap and living(state.enemies):
        choice, v = best_spell(state, wz, cap)
        b, n, d, mod, cr, cm = wz.attacks[0]
        t = choose_target(state)
        xbow = R.expected_attack(b, eff_ac(t), n, d, mod)
        if choice and v > 1.5 * xbow:
            lvl, name = choice
            spend(wz, lvl, state)
            SPELLS[name][1](state, wz, do=True)
            return
    martial_turn(state, wz, single=True)


def cure_amount(state, cleric, lvl):
    n, cap = CURE[lvl]
    return R.roll(state.rng, n, 8) + min(cap, cleric.caster_level)


def cast_cure(state, cleric, target, lvl):
    spend(cleric, lvl, state)
    before = target.hp
    target.hp = min(target.max_hp, target.hp + cure_amount(state, cleric, lvl))
    state.stats.healing += target.hp - before


def cleric_turn(state, cl, single):
    hurt = [p for p in state.party if not p.dead and (p.hp <= 0 or p.hp < 0.3 * p.max_hp)]
    avail = [l for l in sorted(cl.slots) if cl.slots[l] > 0]
    if hurt and avail:
        t = min(hurt, key=lambda p: p.hp / p.max_hp)
        need = t.max_hp * 0.5 - t.hp
        lvl = next((l for l in avail if CURE[l][0] * 4.5 + min(CURE[l][1], cl.caster_level)
                    >= need), avail[-1])
        cast_cure(state, cl, t, lvl)
        return
    cap = max_spend_level(state, cl)
    if cap and living(state.enemies):
        choice, v = best_spell(state, cl, cap)
        t = choose_target(state)
        b, n, d, mod, cr, cm = cl.attacks[0]
        melee = R.expected_attack(b, eff_ac(t), n, d, mod) * (1 if single else len(cl.attacks))
        if choice and v > 1.5 * melee:
            lvl, name = choice
            spend(cl, lvl, state)
            SPELLS[name][1](state, cl, do=True)
            return
    martial_turn(state, cl, single)


def spiritual_weapon_tick(state, cl):
    left = state.persistent.get("spiritual weapon", 0)
    if left <= 0:
        return
    state.persistent["spiritual weapon"] = left - 1
    t = choose_target(state)
    if t is None:
        return
    b = R.bab(cl.caster_level, "medium") + cl.cast_mod
    dmg = R.attack(state.rng, b, eff_ac(t, False), 1, 8, min(5, cl.caster_level // 3),
                   crit_immune=t.ctype == "undead")
    deal(state, "cleric", t, dmg, "force")


def enemy_turn(state, e, single):
    # condition upkeep (at start of its turn)
    conds = e.conditions
    if "_cloud" in conds:
        conds["_cloud"] -= 1
        if "nauseated" not in conds and conds["_cloud"] > 0 and \
                not R.saving_throw(state.rng, conds["_cloud_dc"], e.saves["fort"]):
            add_condition(e, "nauseated", conds["_cloud"] + 2, "wizard")
        if conds["_cloud"] <= 0:
            del conds["_cloud"]
    if "paralyzed" in conds and "_hold_dc" in conds:
        if R.saving_throw(state.rng, conds["_hold_dc"], e.saves["will"]):
            del conds["paralyzed"]
    lost = None
    for k in ("asleep", "paralyzed", "unconscious", "stunned", "nauseated"):
        if k in conds:
            lost = conds["_by"].get(k, "wizard") if "_by" in conds else "wizard"
            break
    for k in list(conds):
        if k in ("asleep",) or k.startswith("_"):
            continue
        conds[k] -= 1
        if conds[k] <= 0:
            del conds[k]
    if lost:
        state.stats.denied[lost] += 1
        return
    if e.regen and not e.dead:
        e.hp = min(e.max_hp, e.hp + e.regen)
    targets = [p for p in state.party if p.standing]
    if not targets:
        return
    w = state.opts["target_weights"]
    miss = 0.5 if "blinded" in conds else 0.0
    atks = e.attacks[:1] if single else e.attacks
    t = state.rng.choices(targets, weights=[w[p.cls] for p in targets])[0]
    for (b, n, d, mod, cr, cm) in atks:
        if not t.standing:
            targets = [p for p in state.party if p.standing]
            if not targets:
                return
            t = state.rng.choices(targets, weights=[w[p.cls] for p in targets])[0]
        t.hp -= R.attack(state.rng, b, t.ac, n, d, mod, cr, cm, miss_chance=miss)
        if t.hp <= -10:
            t.dead = True


# ---------------------------------------------------------------------------------- fight/day

class State:
    pass


def run_fight(state):
    state.stats = Stats()
    state.persistent = {}
    order = [(state.rng.randint(1, 20) + c.init, state.rng.random(), c)
             for c in state.party + state.enemies]
    order.sort(key=lambda x: (-x[0], x[1]))
    order = [c for _, _, c in order]
    for state.round in range(1, state.opts["max_rounds"] + 1):
        state.stats.rounds = state.round
        single = state.round == 1
        for c in order:
            if not living(state.enemies) or not any(p.standing for p in state.party):
                return
            if c.dead:
                continue
            if c.side == "enemy":
                if c.standing:
                    enemy_turn(state, c, single)
                continue
            if c.hp <= 0:
                # dying: lose 1 hp per round, 10% chance to stabilise (SRD)
                if c.hp < 0 and not getattr(c, "stable", False):
                    if state.rng.random() < 0.1:
                        c.stable = True
                    else:
                        c.hp -= 1
                        if c.hp <= -10:
                            c.dead = True
                continue
            if c.cls == "wizard":
                wizard_turn(state, c)
            elif c.cls == "cleric":
                spiritual_weapon_tick(state, c)
                cleric_turn(state, c, single)
            else:
                martial_turn(state, c, single)


def rest_between(state):
    """Out-of-combat recovery: allies stabilise downed PCs; cleric (or wand) cures."""
    cl = next(p for p in state.party if p.cls == "cleric")
    for p in state.party:
        if not p.dead and p.hp < 0:
            p.stable = True
    if state.opts["wand"]:
        for p in state.party:
            while not p.dead and p.hp < p.max_hp * 0.9 and state.wand_charges > 0:
                state.wand_charges -= 1
                p.hp = min(p.max_hp, p.hp + R.roll(state.rng, 1, 8) + 1)
    if cl.dead or cl.hp <= 0:
        return
    for _ in range(40):
        hurt = [p for p in state.party if not p.dead and p.hp < 0.6 * p.max_hp]
        avail = [l for l in sorted(cl.slots) if cl.slots[l] > 0]
        if not hurt or not avail:
            break
        t = min(hurt, key=lambda p: p.hp / p.max_hp)
        cast_cure(state, cl, t, avail[0])
    for p in state.party:
        if p.hp > 0:
            p.stable = False


def roll_encounter(state):
    offs, probs = zip(*state.opts["el_offsets"])
    el = max(2, min(13, state.level + state.rng.choices(offs, weights=probs)[0]))
    comp = state.rng.choice(ENCOUNTERS[el])
    return el, [make_monster(m, i) for i, m in enumerate(comp)]


def run_day(level, day_length, rng, **opts):
    o = dict(DEFAULTS)
    o.update(opts)
    state = State()
    state.rng, state.opts, state.level, state.day_length = rng, o, level, day_length
    state.party = build_party(level)
    state.wand_charges = 50
    for p in state.party:
        if hasattr(p, "slots"):
            p.full_slots = dict(p.slots)
            if p.cls == "wizard":
                p.prepared = {l: LOADOUTS[o["loadout"]][l][:n] for l, n in p.slots.items()}
            else:
                p.prepared = {l: CLERIC_PREP.get(l, []) for l in p.slots}
    fights = []
    for k in range(1, day_length + 1):
        state.fight_index = k
        if not any(p.standing for p in state.party):
            break
        state.el, state.enemies = roll_encounter(state)
        run_fight(state)
        won = not living(state.enemies)
        s = state.stats
        rec = dict(k=k, el=state.el, won=won, rounds=s.rounds, damage=dict(s.damage),
                   kills=dict(s.kills), takedowns=dict(s.takedowns), denied=dict(s.denied),
                   healing=s.healing, spent=dict(s.slot_levels_spent),
                   cast=dict(s.spells_cast),
                   dead=[p.cls for p in state.party if p.dead])
        fights.append(rec)
        if not won:
            break
        rest_between(state)
    out = dict(level=level, n=day_length, fights=fights,
               completed=len(fights) == day_length and fights[-1]["won"],
               deaths=[p.cls for p in state.party if p.dead],
               tpk=not any(p.standing for p in state.party),
               hp_left=party_hp_frac(state))
    for p in state.party:
        if hasattr(p, "full_slots"):
            full = sum(l * n for l, n in p.full_slots.items())
            out[f"{p.cls}_slots_left"] = sum(l * n for l, n in p.slots.items()) / full
    return out
