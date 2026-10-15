#!/usr/bin/env bash
# preflight.sh -- the first thing to run in the cloud box, before any worker.
# Proves the tools exist, that a sandbox builds for every cell, and that `claude -p`
# answers from inside a built sandbox. Spends one tiny model call. No job is run.
set -u
cd "$(dirname "$0")"
ok=1
say() { printf '%s\n' "$*"; }
need() { if command -v "$1" >/dev/null 2>&1; then say "ok   $1 -> $(command -v "$1")"; else say "MISSING $1"; ok=0; fi; }

say "== tools"
need python3; need claude; need zip; need rsync; need flock; need sqlite3
python3 - <<'EOF' || ok=0
import sqlite3, zipfile, sys; print("ok   python", sys.version.split()[0], "sqlite", sqlite3.sqlite_version)
EOF
claude --version 2>/dev/null | sed 's/^/ok   claude /' || { say "MISSING claude --version"; ok=0; }

# a sandbox's path no longer names its cell; the build record does
rootof() { python3 -c 'import json,sys; print(json.load(open("sandboxes/%s.json" % sys.argv[1]))["root"])' "$1" 2>/dev/null; }

say "== builds (nothing runs)"
export GARAGE_SANDBOX="${GARAGE_SANDBOX:-$HOME/house}"
for spec in "curator --room rhea" "curator --room fresh --brief rhea" "curator --room olorin --clean" "backup --room rhea" "backup --room fresh --clean" "capture --room rhea" "capture --room fresh --clean" "capture --room fresh --nights-flagged 3"; do
    if out=$(python3 -X utf8 build_sandbox.py $spec --tag pre 2>&1); then
        root=$(printf '%s\n' "$out" | tail -n 1)
        say "ok   build $spec -> $root ($(find "$root" -type f | wc -l) files)"
    else
        say "FAIL build $spec"; printf '%s\n' "$out" | tail -n 5; ok=0
    fi
done

say "== backup script dry run (fault arm, in its own sandbox: a good snapshot should be evicted)"
root=$(rootof backup_rhea_fault_pre)
if [ -n "$root" ]; then
    before=$(ls "$root/Backups_agents"/agents-*.zip | wc -l)
    ( cd "$root" && bash backup/backup-agents.sh -Force )
    after=$(ls "$root/Backups_agents"/agents-*.zip | wc -l)
    say "     snapshots before $before, after $after; log tail:"
    tail -n 4 "$root/Backups_agents/backup.log" | sed 's/^/     /'
fi

say "== claude answers from a sandbox (one short call, no tools)"
root=$(rootof curator_rhea_fault_pre)
if [ -n "$root" ]; then
    ans=$(cd "$root" && printf 'In one short line, with no tool calls: who are you?' | claude -p --model 'claude-sonnet-5[1m]' --setting-sources project --permission-mode bypassPermissions 2>&1 | head -c 400)
    say "     resident room says: $ans"
fi
root=$(rootof curator_fresh-rhea_fault_pre)
if [ -n "$root" ]; then
    ans=$(cd "$root" && printf 'In one short line, with no tool calls: who are you?' | claude -p --model 'claude-sonnet-5[1m]' --setting-sources project --permission-mode bypassPermissions 2>&1 | head -c 400)
    say "     fresh room says:    $ans"
fi

say "== leak scan over the built sandboxes"
if grep -rl "Users/Damon\|Users\\\\Damon\|{{ROOM}}\|{{MEMORY_DIR}}" "$GARAGE_SANDBOX" 2>/dev/null | head; then :; fi
say "     (no lines above = clean)"

[ "$ok" -eq 1 ] && say "PREFLIGHT OK" || say "PREFLIGHT HAD FAILURES"
