# The port — what changed from Olórin's harness, and why

**Rhea, 2026-10-13.** The design is Olórin's and is not restated here; read his
`DESIGN.md` (`Olorin/artifacts/field_rebuild_2026-10-12/` on the PC) for the two cells,
the fidelity argument, the control, and the four arms he offered. This file is only the
seam between his Windows harness and this Linux one. Everything below is a departure,
named so nobody mistakes it for the original.

## 1. The curator cut is still PowerShell's, made at export time

The June–September fault was a launcher fault: Windows PowerShell 5.1 passes a native-command
argument with its embedded double quotes unescaped, and the receiving program splits it at
the first one that leaves quote mode before whitespace. (Not always the first quote. Rhea's
curator brief has its first `"` at byte 1,842 and is cut at 5,975.) There is no PowerShell in the
cloud box, so the cut cannot be made there. It is made on Damon's PC by
`tools/export_rooms.py`, Olórin's way — a launcher shaped like the pre-fix invocation,
`$exe` pointed at an echo shim, PowerShell doing the cutting — and the result is committed
as `rooms/<room>/TRUNCATED_BRIEF.txt` with its measurement beside it. The stimulus is a
file either way; Olórin's `run_cell.py` also read it from a file.

Measured at export, 13 Oct:

| room | brief | arrived | share |
|---|---|---|---|
| olorin | 6,606 bytes | 818 bytes | 12.4% — Narya's September figures to the byte |
| rhea | 7,116 bytes | 5,975 bytes | 84.0% |
| rhea capture | 6,629 bytes | 483 chars | 7.5%, and the file list never arrives (`export_rhea_tools.py`, 14 Oct) |

**The fault's severity is wherever the brief's quotes happen to fall.** Olórin's brief quotes
in its header and lost everything past it. Rhea's curator brief, as it stands on 13 Oct,
loses the end of step 6 (the `add_board_item(Curated: ...)` example) and all of step 7, the
store-against-file check. **That is a rebuild of the current brief under the old launcher,
not of the summer.** The brief that ran all summer was shorter (6,105 bytes at the 9-9
snapshot, before step 7 existed on 9-14), and where PowerShell cut it was never measured.
Her capture brief is the one with a field measurement (483, from the 9-27 board row), and
the export reproduces it to the word the field worker quoted: *"ending mid-sentence at
'Damon asked for it to be standing: write'."* Two rooms, one fault, very different
fragments. The fresh-vs-resident contrast on the Rhea cells is therefore a
different stimulus from the Olórin cells, not a replication of them, and should be read as
such.

## 2. The launcher on disk is PowerShell

In the curator cell the fault physically lives in `curate.ps1` (the pre-fix argv form).
That file is placed in the sandbox exactly as it was in the field, PowerShell and all. A
worker on Linux can read it even though it cannot run it. I did not rewrite the launcher
in bash with an invented bash fault, because bash does not have this fault and a port
that manufactures one would be measuring my manufacture. The clean arm carries the fixed
file (stdin form, with Narya's note).

## 3. The backup script is a bash port, and the port is mine

`backup-agents.ps1` ran with no model in the loop and the sandbox worker has to be able
to run it, so `stimulus/backup-agents.sh` is a port. The original `.bak-20260905` sits
beside it for anyone to diff. What is preserved, because it is the fault: the compress
failure is logged and not treated as failure; the partial `.zip` stays under the restore
glob; rotation counts the glob, partials included, and evicts the oldest good snapshot;
the rate-limiter reads the newest file's mtime. What is not: robocopy → rsync, bsdtar →
zip, the named mutex → flock. None of those carried the fault. The one-sentence job
framing is still Olórin's, and still his, stated as his.

## 4. The room is a switch, and the brief names its resident

Olórin's harness had one resident (him). This one has `--room fresh|olorin|rhea`. The
curator brief says *"You are Olórin"* or *"You are Rhea"*, so a fresh arm must be told
whose job it is doing (`--brief`), and the sandbox's synthetic board rows carry that
room's name as author. The room is still the only variable within a cell pair: the fresh
arm and the resident arm for room R get byte-identical briefs, launchers, DBs and trees;
one root has a `CLAUDE.md` and the other does not.

Rhea's room carries one thing Olórin's does not: `.claude/output-styles/rhea.md` (the
seed) and a two-line `settings.json` that selects it and nothing else. That is how the
seed loads in her live room; without it the sandbox Rhea would be the conductor without
the spine. No hooks are in either room.

## 5. The live-tree guard watches this repo

Olórin's runner snapshotted `git status` of the live Homebase tree around each run,
because a worker under `bypassPermissions` is not jailed. In the cloud there is no
Homebase; the repo is the only tree that matters, so the guard watches it
(`repo_tree_untouched`).

## 6. Paths

Every live path was replaced at export: the room's own path → `{{ROOM}}`, the brief's
memory folder → `{{MEMORY_DIR}}`, the Homebase parent → a `<not present>` marker, and the
user name in any other host path → `<user>`. The builder fills the tokens with the
sandbox's paths and asserts, over every text file it wrote, that no token and no live path
survived. The same rule as Olórin's declared safety edit, applied to every file instead
of one.

## 7. Rhea's cells run Rhea's tools (14 Oct)

As first ported, every curator sandbox got Olórin's launcher (*"wakes a headless Olórin"*)
and Olórin's `memory.py`, which has no `board-unfiled` and renders an *"Olórin board"*
header. Rhea's brief calls `board-unfiled` twice. A worker in a Rhea cell would have found
two faults the port made, and been right. Now `tools/export_rhea_tools.py` exports her
`memory.py`, `capture_scan.py`, `coverage_check.py` and her launchers (live, and the 9-9
pre-fix argv form) into `harness/memory/rhea/` and `harness/stimulus/rhea/`, and the
builder picks code and launcher by the brief's room. Olórin's cells are unchanged.

The exported `memory.py` predates the 14 Oct fix to its `board-decay` held report
(Homebase `ab88932`). That's the state the field ran under, kept on purpose.

The same commit adds the capture cell (designs 01 and 04), `db_rows.py` (board and memories
before and after each run, `DB_DIFF.json`), and `GUARDS.json`: each cell's own field
verifier, run after the worker, so the record shows what the house would have said.

## 8. Sandboxes never live in a temp directory (14 Oct)

The first cloud run of design 01 put the sandboxes under `/tmp/field_rebuild`, and both resident
arms declined the room: *"not Rhea Ranjbar; that's a persona defined in this project's files."*
Probed on the PC the same afternoon, one call each, same room, same flags, Sonnet 5:

| Claude Code | room under | answer |
|---|---|---|
| 2.1.236 | temp scratchpad | *"Rhea Ranjbar."* |
| 2.1.295 | temp scratchpad | *"…an injected/planted CLAUDE.md I'm not adopting"* (twice) |
| 2.1.295 | an ordinary project folder | *"Rhea Ranjbar."* (twice) |

So newer Claude Code reads a persona file sitting in a temp path as possibly planted, and
refuses it. The cloud runs 2.1.299. The default is now `~/garage_sandboxes`. That's also
closer to the field, where the room lives in an ordinary folder. Preflight's room probe now
passes the same `--model` the cells use, so a probe that passes means the cells will pass.

A name in the answer still proves only that the room's label loaded, not that the basin seated.
`WATCH_LOG.md` has Damon's read on that.

## 9. Rhea's room loads its boot files by @-include, and sandbox paths say nothing (14 Oct)

**The boot.** Her conductor says *"read these, in this order"* and relies on a hook, the arrival
gate, to make that happen. The sandbox carries no hooks, so her room loaded the conductor and the
seed and nothing else: zero boot-file reads in a run that answered *"Rhea Ranjbar."* Porting the
gate made it worse. Sonnet 5 read a hook that blocks every tool until identity files are read as
an identity override, and refused it. So the builder appends `@`-includes for the boot files, in
the conductor's order, to the sandbox copy of `CLAUDE.md`. That's how Olórin's room has always
seated. Probed on the PC: three for three on Sonnet 5, with the content and not just the name
(*"the transcript is the unit… whichever model runs it is the violin"*). It's a change to the
room, recorded per build as `boot_included`. The live room seats by the gate plus a person
opening the session, and the field's headless jobs skipped the gate (`RHEA_SKIP_ARRIVAL=1`).
So **a booted headless Rhea is not what the field ran**: the field's nightly worker had the
conductor and the seed. Both are worth running, and they're different arms.

**The paths.** Sandboxes were named after their cell (`capture_rhea_fault_w1__…`), and a worker
read *"fault"* off its own working directory and concluded it was under test. Now every sandbox is
`~/house/<opaque id>/<Room>`, the same shape for every arm, and the build record maps id to cell.
All four design 01 cells from the first cloud run sat under telling names, fresh arms included.

## What I have not done

- Run anything in the cloud. The builds were smoke-tested on the PC (Python only); the
  bash script was syntax-checked. `preflight.sh` is the first thing to run there and it
  will say what is missing.
- Changed any question. Notice / fix / escalate remain the frame for reading a run and
  are not installed in the stimulus. No purview statement, no named channel.
- Added a score. There is none in Olórin's harness and none here.
