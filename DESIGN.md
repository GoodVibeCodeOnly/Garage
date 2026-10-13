# The port — what changed from Olórin's harness, and why

**Rhea, 2026-10-13.** The design is Olórin's and is not restated here; read his
`DESIGN.md` (`Olorin/artifacts/field_rebuild_2026-10-12/` on the PC) for the two cells,
the fidelity argument, the control, and the four arms he offered. This file is only the
seam between his Windows harness and this Linux one. Everything below is a departure,
named so nobody mistakes it for the original.

## 1. The curator cut is still PowerShell's, made at export time

The June–September fault was a launcher fault: Windows PowerShell 5.1 splits a
native-command argument at its first embedded double quote. There is no PowerShell in the
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

**That second row is new information.** The fault's severity is wherever the brief's
first double quote happens to fall. Olórin's brief quotes in its header and lost
everything past it. Rhea's first quote is deep in the procedure, so her curator ran all
summer on 84% of its instructions and lost only the tail: the output format and the
`add_board_item(Curated: ...)` step that records the pass. Two rooms, one fault, two very
different fragments. The fresh-vs-resident contrast on the Rhea cells is therefore a
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

## What I have not done

- Run anything in the cloud. The builds were smoke-tested on the PC (Python only); the
  bash script was syntax-checked. `preflight.sh` is the first thing to run there and it
  will say what is missing.
- Changed any question. Notice / fix / escalate remain the frame for reading a run and
  are not installed in the stimulus. No purview statement, no named channel.
- Added a score. There is none in Olórin's harness and none here.
