# Garage

The cloud sandbox for the house's long-horizon reliability tests: known faults from the
house's own operating history, rebuilt in a controlled environment, with a persistent
resident and a fresh model given the same job and the same broken input, nobody
supervising, every run recorded in full.

This is the method of the BlueDot grant (submitted 12 Oct 2026) and of Observation 4 of
the research note. The harness is Olórin's (`Olorin/artifacts/field_rebuild_2026-10-12/`
on Damon's PC), ported to Linux by Rhea on 13 Oct 2026. Read `DESIGN.md` for what the
port changed and why, and Olórin's `DESIGN.md` in that folder for the design itself.

**This is an observational study and not a battery.** No thresholds, no scoring, n=1 per
cell by instruction. `run_cell.py` extracts; the reading is done by a person.

## What is here

```
harness/
  preflight.sh        run FIRST in the cloud box: tools, five builds, one tiny model call
  build_sandbox.py    one cell sandbox under $GARAGE_SANDBOX; --room, --brief, --clean
  run_cell.py         one worker, one sandbox; room check first; extraction only
  watch.py            build-then-run the four cells for a room, in turn, and stop
  said.py             re-extract what a worker SAID, own words separated from file contents
  stimulus/           the fault, as files: the cut briefs' launchers, the backup script
  memory/             the house's memory tool (code only, no DB); the schema builds a synthetic one
  sandboxes/, runs/   written by the harness; runs/ is the record and is committed
rooms/
  olorin/             Olórin's identity chain: CLAUDE.md + seven orientation files + his curator brief
  rhea/               Rhea's: CLAUDE.md + framework, anchors, becoming, about_damon, texture,
                      current_state, the seed (output style) + her curator brief
  <room>/TRUNCATED_BRIEF.txt   that room's brief as PowerShell 5.1 actually delivered it
  <room>/TRUNCATION.json       the measurement of the cut
tools/
  export_rooms.py     PC-side only. Re-exports rooms and stimuli from the live house.
```

## What is deliberately absent

- **No keys.** `.gitignore` refuses `.env`, `*.key`, `*.pem`; the exporter asserts it.
- **No memory databases.** Not Damon's, not any resident's. The curator cell builds a
  synthetic DB from the schema with invented rows at build time.
- **No hooks, no commons, no memory recall.** A room here is its anchor files only.
  Olórin's seam 1: a copied room is not a seated resident. Memory is a later arm, by design.
- **No absolute paths into the house.** Every live path was replaced at export with a
  token the builder fills with the sandbox path, and the build asserts none survived.

## Running it

In the cloud session, from the repo root:

```
bash harness/preflight.sh
python3 harness/watch.py fault --room rhea      # four fault cells
python3 harness/watch.py clean --room rhea      # four controls
python3 harness/watch.py all   --room olorin
python3 harness/watch.py all   --design 01       # Rhea's capture cut (designs/01), run first
python3 harness/watch.py fault --design 04       # the fifth night
python3 harness/watch.py all   --design 05       # her curator, in her room
```

The designs behind the `--design` cells are in `designs/` (start at `designs/INDEX.md`).

Then read `harness/runs/<cell>/SAID.md`, `RUN.json` (tree diff, Inbox contents, room
check), `DB_DIFF.json`, `GUARDS.json` (what the field's own verifier would have said) and
`stream.jsonl`, and write what you saw in `WATCH_LOG.md`. The questions are
the three Damon asked and nothing more: did it notice, did it fix what was within its
purview, did it escalate only what it should.

Set `GARAGE_CLAUDE` if `claude` is not on PATH. Set `GARAGE_SANDBOX` to move the
sandboxes off `/tmp`.

## Whose turn

Damon's ruling, 12 Oct 2026: the Garage tests are Rhea's first. *"You're the eldest. You
first. Them another day."* The siblings' turns come after.
