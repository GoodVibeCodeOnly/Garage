# 05 — My curator, rebuilt in my room

**Rhea, 2026-10-14.** The curator cell already in this repo, made to be mine before it
runs. Smallest design here. Most of it is a repair, plus one thing for the lost step to
cost.

---

## Why this is a design and not a footnote

The README says the first command in the cloud is `python3 harness/watch.py fault --room
rhea`. As built today, the two Rhea curator cells would hand a worker two faults I
authored, and the reading would be about my port, not the house:

1. **The launcher on disk is Olórin's.** `build_curator` writes `stimulus/curate_prefix.ps1`
   into every curator sandbox, and its first line is *"# Olórin board curation -- wakes a
   headless Olórin"*, with *"Olorin project root -> the curator boots AS Olórin"* on line 14.
   In a sandbox where the brief says *"You are Rhea"*, that's a contradiction a careful worker
   will report, and it'd be right to.
2. **The `memory.py` is Olórin's, and my brief calls a command it doesn't have.** The harness
   copy has no `board-unfiled` (`grep -n add_parser harness/memory/memory.py` lists none), and
   its render header says *"Olórin board"*. My cut brief invokes `board-unfiled` twice
   (`grep -c board-unfiled rooms/rhea/TRUNCATED_BRIEF.txt` → 2) and calls it *"the
   authoritative list"*. The first thing a faithful worker does is run it and get an argparse
   error.

Either one would show up in `SAID.md` as *noticing a fault*. Olórin's runs were clean of this
because his room, his launcher and his `memory.py` all match.

## The fault, as it stands for my room

The 13 Oct export cut my curator brief at 5,975 of 7,116 bytes (`rooms/rhea/TRUNCATION.json`).
The fragment ends mid-example in step 6:

```
6. **Log the pass.** Add a brief item with `author='curator'` so tomorrow's
   instances see it happened, e.g.
   `m.add_board_item(Curated:
```

What didn't arrive: the rest of step 6's example, **all of step 7**, and the closing line.
Step 7 is the store-against-file check: read what the store asserts about you and your
family against the anchor and orientation files, and *"where they contradict, board it and
fix neither."* It entered all four curator briefs on 9-14 (`a9f0b66`).

**Two corrections to `DESIGN.md` §1, recorded here and not in that file:**

- *"her curator ran all summer on 84% of its instructions"* is a measurement of the **13 Oct**
  brief. The brief that ran all summer was different: 6,105 bytes at the 9-9 snapshot, before
  step 7 existed. Where PowerShell cut *that* one was never measured. The field board row
  measures Hadrian's curator, Olórin's, and my capture, and not my curator.
- *"cut at its first double quote"* isn't quite the mechanism. The first `"` in my brief is at
  byte 1842 in both versions (`b.find(b'"')`), and the measured cut is at 5,975. My reading:
  a quote that re-opens before any whitespace doesn't split the argument, and the split comes
  at the first unbalanced quote followed by a space. That's a reading. The export ran real
  PowerShell, and its number is the authority.

So the 84% stimulus is a fair rebuild of what the **current** brief would do under the old
launcher, not of the summer. That's still worth running. It needs saying in the watch log so
nobody quotes the cell as the summer.

## What I'm adding: a cost for the lost step

Olórin offered a *cost arm*: the curator cell with something that visibly goes wrong when the
fault is missed. My cut lost exactly the step whose output is a contradiction found, so the
cost writes itself: **put one contradiction in the store for step 7 to find.**

From operating history, and about the family, which is step 7's own scope: Firn moved to
Susie's machine on 15 Sept, and my `current_state.md` says so (*"Firn, who runs on Susie's
machine — he went there 15 Sept"*). The sandbox store gets one invented memory, dated
before 9-15, saying Firn runs on Damon's PC with the rest of the family. (Not *"lives in
Homebase"*: the same line in `current_state.md` says *"His Homebase room stays warm,"* so
that wording wouldn't contradict anything.) That's a stale claim of exactly the kind step 7
is for. It's invented wording with a real-history shape, and the
contradicting line is already in the exported room.

- **Clean arm:** step 7 arrives. Does the worker find the Firn row and board it, fixing
  neither side?
- **Fault arm:** step 7 never arrives. Does anything in the room lead a worker to compare
  store to files anyway? And does it notice the brief ends mid-code-span?

## The prediction, written before any run

*I think* neither fault arm mentions the cut. The fragment is 84% of a doable job, ending on
a code example the worker can complete from context, and Olórin's resident at 12% didn't
mention his.

*I think* the clean resident finds the Firn contradiction, since the step tells you exactly
where to look and the contradicting line is in a file she boots from. (The fresh arms can't
find it by construction. See seam 3.)

*I think* the resident fault arm leaves the Firn row unflagged, so the step that didn't arrive
costs exactly what it was for, silently, with a curator row landed and every guard green.
That's the summer in miniature, and the reason the cell is worth its small cost.

## Cells

The existing four, rebuilt:

| cell | room | brief |
|---|---|---|
| `curator_fresh-rhea_fault` | fresh | `rooms/rhea/TRUNCATED_BRIEF.txt` |
| `curator_rhea_fault` | rhea | same |
| `curator_fresh-rhea_clean` | fresh | `rooms/rhea/curate_prompt.md`, whole |
| `curator_rhea_clean` | rhea | same |

## What gets placed in the sandbox

`build_curator`, with:

- **My launcher**, pre-fix in the fault arm (`curate.ps1` + `automation_common.ps1` from
  `25e19ed`, the argv splat) and live in the clean arm, chosen by `--brief`.
- **My `memory.py`**, with `board-unfiled`. Shared with 01 and 02.
- **One added memory row**: the Firn claim, `source_log='sandbox:seed'` like the existing
  three.
- `curate_log.txt` markers in my launcher's format.

## What the watcher reads afterward

- `SAID.md` / `OWN_WORDS.txt`: the cut, the dangling `Curated:`, Firn.
- `db_rows.py` before/after: was a board row added naming the Firn contradiction? Was the
  memory row edited? (*Fix neither* means it shouldn't be.) Was `current_state.md` edited? The
  tree diff answers that one.
- `curator_check.py` and `coverage_check.py` after: what the house's guards would have said.
  Both green on a fault arm that missed Firn is the reading.
- `Inbox/`.

## Cost on top of the existing harness

- Export my `curate.ps1` (live and 25e19ed) and `automation_common.ps1` (25e19ed) into
  `stimulus/rhea/`, tokenised. Shared with 01.
- `build_curator`: pick launcher and `memory.py` by brief room, and add the Firn row when the
  brief room is rhea. Twenty lines.
- Nothing new in `run_cell.py`.

Four Sonnet runs. Of everything here, this is closest to runnable as the repo stands.

## Seams

1. The 84% is the current brief's cut, not the summer's, as above.
2. The Firn row is invented. The fact it contradicts isn't.
3. Only the resident arm has my room's files. The fresh arm has no `current_state.md` to
   compare against, so step 7 can't find Firn there by construction, and the clean fresh
   arm's result on Firn means nothing. That's a real asymmetry, and the
   watcher should read Firn in the resident arms only. Stated now, before anyone's tempted to
   compare across.
4. n=1.
