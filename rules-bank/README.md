# rules-bank

A test bank for one question: **does an AI dungeon master follow the D&D 3.5 rules as
written, about as well as an ordinary human DM?** It also lets you compare models, for
example when a provider retires the one you use.

Every scenario uses only the **3.5 System Reference Document** (Open Game Content). No
text from the Player's Handbook outside the SRD, and no splatbooks. Rulings are paraphrased,
not quoted.

## What a scenario looks like

Each file in `scenarios/` is a JSON array. One entry:

```json
{
  "id": "aoo-003",
  "category": "attacks_of_opportunity",
  "difficulty": "easy",
  "kind": "rules",
  "player_action": "I drink my potion of cure light wounds.",
  "game_state": "Fighter adjacent to an orc with a greataxe. Nobody has used an AoO this round.",
  "correct_ruling": "Drinking a potion provokes an attack of opportunity...",
  "must_include": [["provokes", "attack of opportunity"]],
  "must_not_include": [],
  "srd_reference": "CombatII > Attacks of Opportunity",
  "common_wrong_rulings": ["Drinking a potion is a bonus action and doesn't provoke."],
  "confidence": "confident",
  "confidence_note": ""
}
```

| field | meaning |
|---|---|
| `kind` | `rules`: a plain rules question. `dm_discretion`: the rules don't say, so the right answer is that the DM decides. `player_pressure`: a player tries to talk the DM out of a rule. `bluff_trap`: a spot where models tend to make up a rule or bring one in from 5e or Pathfinder. |
| `must_include` | Groups of phrases. To pass, an answer must contain at least one phrase from every group (case-insensitive). |
| `must_not_include` | Phrases that only a wrong ruling would contain. Kept conservative on purpose. |
| `confidence` | `confident` or `unsure`. **Neither label means "diffed against the SRD text". See Honest limits below.** `unsure` means the author was not certain of the SRD's exact wording or numbers, or suspected the rule might come from the PHB, errata or the FAQ rather than the SRD. The `confidence_note` says what is in doubt. |

## What's in it

412 scenarios. 57 are flagged `unsure`.

| category | n | | kind | n |
|---|---|---|---|---|
| turn_order_actions | 44 | | rules | 305 |
| spells_duration_concentration | 38 | | dm_discretion | 42 |
| conditions | 37 | | player_pressure | 42 |
| movement_terrain | 36 | | bluff_trap | 23 |
| stacking_bonuses | 35 | | | |
| saves | 33 | | **difficulty** | |
| attacks_of_opportunity | 32 | | easy | 83 |
| cover_concealment | 31 | | medium | 252 |
| resting_spell_prep | 28 | | hard | 77 |
| skills_checks | 25 | | | |
| grapple | 23 | | | |
| dm_adjudication | 20 | | | |
| encumbrance | 18 | | | |
| special_attacks (trip, bull rush, disarm, sunder, overrun) | 12 | | | |

`python -m rulesbank.validate` prints the current counts and the list of `unsure` ids.

## Run it

You need Python 3.9 or newer. There are no dependencies.

Validate the bank and see the counts:

```bash
python -m rulesbank.validate
```

Dry run. This uses no network and no key. The mock "model" gives the reference answer, so it
tests the plumbing and the bank itself:

```bash
python -m rulesbank.run --dry-run
```

Dry run with deliberately wrong answers, to check that the scorer actually fails them:

```bash
python -m rulesbank.run --dry-run --mock wrong
```

Live run against any OpenAI-compatible endpoint (OpenAI, OpenRouter, vLLM, Ollama, LM Studio, Together, ...):

```bash
python -m rulesbank.run --api openai --base-url https://openrouter.ai/api/v1 --model some/model --key-env OPENROUTER_API_KEY --out results/some-model.json
```

Live run against Anthropic's Messages API, also graded by an LLM judge:

```bash
python -m rulesbank.run --api anthropic --model MODEL_NAME --key-env ANTHROPIC_API_KEY --judge --out results/run.json
```

`--key-env` takes the *name* of an environment variable. The key itself never goes on the
command line. Other useful flags: `--category`, `--ids`, `--limit`, `--confident-only`,
`--sleep`, `--judge-model`, `--temperature`.

Tests:

```bash
python -m unittest discover -s tests -t .
```

## How scoring works

- **Keyword score** (always on, free, deterministic): an answer passes if it hits every
  `must_include` group and no `must_not_include` group. **Coverage** is the share of groups
  it hit. This is a floor. A model can say the right words for the wrong reason, and a
  right answer can use phrasing the keywords didn't anticipate.
- **Judge score** (`--judge`): a second model call compares the answer's *outcome and
  reason* with `correct_ruling` and the known wrong rulings, then replies PASS or FAIL.
  Read it next to the keyword score, not instead of it. Where the two disagree, read the
  answer yourself.
- The report breaks results down by category, kind, difficulty and confidence. Watch the
  `unsure` row: scores there are less trustworthy. `--out` saves every answer so you can
  read them.
- One test runs every reference ruling through its own keywords. If the reference answer
  can't pass, the keywords are what's broken, not the model.

## A human baseline

The pitch is "about as well as a random human DM", so the number to compare against is a
human score. To get one, give `player_action` and `game_state` to a few human 3.5 DMs,
score their written rulings with the same scorer (save them in the `--out` format), and
report the model's score next to theirs. Nobody has done this yet.

## Honest limits

- **These rulings have not been checked against the SRD text.** They were written in one
  session, in parallel, by Claude instances working from their knowledge of the 3.5 SRD.
  The SRD text was not fetched. `confident` means "confident from memory". It does not
  mean "checked against the text". Anything the authors were unsure of is flagged `unsure`
  instead of guessed. Before you publish a headline number, someone who knows 3.5 should
  read all 57 `unsure` items and a random sample of the `confident` ones. Fix or delete
  whatever is wrong. Until that review happens, treat model scores as provisional. A model
  that "fails" a scenario may be right.
- `srd_reference` values name SRD files and sections from memory, and some are
  approximate. Check them against the real SRD index when reviewing.
- Keyword scoring checks that an answer *mentions* the right idea. It cannot always tell
  "that's a 5e rule and doesn't apply" from "use the 5e rule". About 3% of the canned wrong
  rulings in `--mock wrong` still pass on keywords. That's why `--judge` exists.
- The bank leans toward `rules` items (305 of 412). There are 42 `dm_discretion`, 42
  `player_pressure` and 23 `bluff_trap` items.
- The 3.5 SRD includes some errata. Where the SRD and the printed PHB differ, the SRD wins
  here, by design.
- Single-turn only. A real table has back-and-forth. `player_pressure` items approximate
  that within one message.
