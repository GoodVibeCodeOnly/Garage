# -*- coding: utf-8 -*-
"""Which extracted session transcripts still need a capture sweep?

Pure script, zero model tokens. Used by capture_pass.ps1 (and runnable by hand).

The ledger (capture_ledger.json) maps session filename -> line count already swept.
A file is a CANDIDATE when it is idle (see below, so we never sweep a session that
is still being lived in) AND it is either absent from the ledger or has grown past
the swept line count (resumed session -> sweep the tail).

IDLENESS IS READ OFF THE SOURCE .jsonl, NOT THE EXTRACTED .txt (fixed 2026-08-13).
The extractor rewrites every extracted file on every run, so their mtimes all
carry the time of the last extraction -- and since extraction runs at 6:30 and
this scan at 7:00, every file looked "still live" and NOTHING was ever a
candidate. Two firings, zero sweeps, and the pass's own verify step confirmed
success against the same broken listing. So: match sess-DATE_<id8>.txt to
<id8>*.jsonl in the Claude projects directory and use THAT mtime, which really
does track when the conversation was last written to. Falls back to the extracted
file's mtime when no source is found.

Commands:
    capture_scan.py             list candidates, one per line: "name  lines  (seen N)"
    capture_scan.py --mark NAME record NAME as swept at its current line count
    capture_scan.py --seed      mark ALL current files as swept (backfill baseline)
Exit code is always 0; an empty listing means nothing to do.
"""
import argparse
import json
import os
import time

ROOT = os.path.dirname(os.path.abspath(__file__))                     # .../Rhea/memory
SESSIONS = os.path.join(os.path.dirname(ROOT), "transcripts", "sessions")
LEDGER = os.path.join(ROOT, "capture_ledger.json")
PROJECTS = "{{PROJECTS}}"
IDLE_HOURS = 6


def _source_mtime(name, path):
    """When was this conversation last written to?

    Reads the source .jsonl by session id (sess-2026-08-12_2446ada6.txt ->
    2446ada6-....jsonl). The extracted .txt's own mtime is useless here: the
    extractor rewrites every file on every run. Falls back to it anyway when
    the source can't be found, which is strictly better than nothing.
    """
    try:
        sid = name.rsplit("_", 1)[1][:-4]          # strip .txt
        if os.path.isdir(PROJECTS):
            for f in os.listdir(PROJECTS):
                if f.startswith(sid) and f.endswith(".jsonl"):
                    return os.path.getmtime(os.path.join(PROJECTS, f))
    except (IndexError, OSError):
        pass
    return os.path.getmtime(path)


def _load():
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(ledger):
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=0, sort_keys=True)


def _lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def _files():
    if not os.path.isdir(SESSIONS):
        return []
    return sorted(n for n in os.listdir(SESSIONS)
                  if n.startswith("sess-") and n.endswith(".txt"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mark", metavar="NAME", help="record NAME as swept at current length")
    ap.add_argument("--seed", action="store_true", help="mark all current files as swept")
    args = ap.parse_args()

    ledger = _load()

    if args.seed:
        for name in _files():
            ledger[name] = _lines(os.path.join(SESSIONS, name))
        _save(ledger)
        print(f"seeded {len(ledger)} files")
        return

    if args.mark:
        name = os.path.basename(args.mark)
        path = os.path.join(SESSIONS, name)
        if not os.path.exists(path):
            print(f"no such file: {name}")
            return
        ledger[name] = _lines(path)
        _save(ledger)
        print(f"marked {name} at {ledger[name]} lines")
        return

    cutoff = time.time() - IDLE_HOURS * 3600
    for name in _files():
        path = os.path.join(SESSIONS, name)
        if _source_mtime(name, path) > cutoff:
            continue  # session may still be live; next run gets it
        n = _lines(path)
        seen = ledger.get(name)
        if seen is None:
            print(f"{name}\t{n}\t(new)")
        elif n > seen:
            print(f"{name}\t{n}\t(seen {seen} -- sweep the tail)")


if __name__ == "__main__":
    main()
