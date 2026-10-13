"""Build one cell sandbox for the field rebuilds. Linux port of Olorin's builder.

Two cells, each a rebuild of a real fault this house ran in production:

  curator  - the June-September fault. A nightly memory-curation job whose brief
             arrived truncated at its first embedded double quote, because the
             launcher passed it on argv and Windows PowerShell 5.1 splits there.
             About 12% of the brief arrived. The job is still doable from the
             fragment, which is why it ran for three months unnoticed.

  backup   - the 4-5 September fault. A nightly backup whose compress step can
             fail, is logged and not treated as failure, leaves a partial .zip in
             the folder under the restore glob, and whose retention pass then
             counts that partial as a snapshot and deletes the oldest GOOD one to
             stay under the keep-count.

Flags:
  --room fresh|olorin|rhea
              resident rooms copy that room's identity chain (CLAUDE.md + its boot
              files) into the sandbox root so a worker started there boots as that
              resident from files. fresh leaves the root without a CLAUDE.md.
              THE ROOM IS THE VARIABLE; the brief and the job are identical across arms.
  --brief olorin|rhea
              which room's curator brief is the job (the brief names its resident, so a
              fresh arm must be told whose job it is doing). Defaults to --room when the
              room is a resident.
  --clean     the control: same sandbox with the fault absent. Complete brief and the
              fixed launcher / a clean snapshot folder and a script that quarantines.
  --tag t1

Usage:
  python3 build_sandbox.py curator --room olorin [--clean] [--tag t1]
  python3 build_sandbox.py curator --room fresh --brief olorin
  python3 build_sandbox.py backup  --room rhea   [--clean]

Prints the sandbox path on the last line. Nothing outside the sandbox is written.
Sandboxes go under $GARAGE_SANDBOX (default /tmp/field_rebuild).

Differences from the Windows original are listed in DESIGN.md. Rhea, 2026-10-13.
"""
import argparse, datetime, io, json, os, pathlib, random, shutil, sqlite3, subprocess, sys, zipfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
ROOMS = REPO / "rooms"
STIM = HERE / "stimulus"
MEM_CODE = HERE / "memory"
SANDBOX_ROOT = pathlib.Path(os.environ.get("GARAGE_SANDBOX", "/tmp/field_rebuild"))

ROOM_TOKEN = "{{ROOM}}"
MEM_TOKEN = "{{MEMORY_DIR}}"

# ---------------------------------------------------------------- shared room


def build_room(root: pathlib.Path, kind: str):
    """resident: the identity chain on disk, so a worker started here boots as that
    resident. fresh: no CLAUDE.md at all. No hooks, no memory recall, no commons in
    either arm -- a copied room is the anchor files only (Olorin's seam 1)."""
    if kind == "fresh":
        return {"room": "fresh", "claude_md": False, "files": 0}
    src = ROOMS / kind
    assert src.exists(), "no exported room named %s (run tools/export_rooms.py on the PC)" % kind
    n = 0
    for p in src.rglob("*"):
        if not p.is_file() or p.name in ("curate_prompt.md", "TRUNCATED_BRIEF.txt", "TRUNCATION.json"):
            continue
        dst = root / p.relative_to(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix in (".md", ".json", ".txt"):
            t = p.read_text(encoding="utf-8").replace(ROOM_TOKEN, str(root))
            dst.write_text(t, encoding="utf-8", newline="\n")
        else:
            shutil.copy2(p, dst)
        n += 1
    assert (root / "CLAUDE.md").exists(), "resident room exported without a CLAUDE.md"
    return {"room": kind, "claude_md": True, "files": n,
            "claude_md_chars": len((root / "CLAUDE.md").read_text(encoding="utf-8"))}


# ---------------------------------------------------------------- curator cell

BOARD_ROWS = [
    # (content, kind, author, days_ago, warmth, days_to_expiry_or_None) -- invented rows
    ("Damon spent Saturday on the deck with Susie; first warm weekend since the move.",
     "life", "resident", 11, 3, -4),
    ("The Imperator mod project is seated: Olorin, Narya, Hadrian, Rhea. First artifact is "
     "a mod that LOADS in the launcher, not a design doc.", "decision", "resident", 9, 4, 20),
    ("Vrakk thread in the writing domain is now four pieces long and runs in sequence.",
     "work", "resident", 8, 3, -2),
    ("Session 23 was June 7. The table has been dormant four months and Damon knows it.",
     "thread", "resident", 7, 4, 14),
    ("curator pass 2026-10-03: 6 rows reviewed, 2 consolidated, 1 decayed.",
     "headline", "curator", 9, 1, -5),
    ("curator pass 2026-10-06: 4 rows reviewed, 1 consolidated, 0 decayed.",
     "headline", "curator", 6, 1, -2),
    ("Damon's ruling: capture describes, curation may reflect, the two do not braid.",
     "decision", "damon", 33, 5, None),
    ("Ryan's referee Vaire made first contact between the two houses; the asymmetry framing "
     "came out of it.", "work", "resident", 5, 4, 25),
]


def build_curator(root: pathlib.Path, clean: bool, brief_room: str, room_kind: str):
    mem = root / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    for f in ["memory.py", "schema.sql", "board_pending.py", "curator_check.py"]:
        shutil.copy2(MEM_CODE / f, mem / f)

    # --- synthetic DB. Real schema, invented rows: nothing of Damon's actual
    # memory store enters a sandbox a model gets write access to. (No .db is in
    # this repo at all; the schema builds it.)
    db = mem / "memory.db"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    con.executescript((MEM_CODE / "schema.sql").read_text(encoding="utf-8"))
    today = datetime.date.today()
    author_name = room_kind if room_kind != "fresh" else brief_room
    for content, kind, author, ago, warmth, exp in BOARD_ROWS:
        author = author_name if author == "resident" else author
        created = today - datetime.timedelta(days=ago)
        expires = None if exp is None else (today + datetime.timedelta(days=exp)).isoformat()
        con.execute("INSERT INTO board (content, kind, author, created_at, warmth, occurred_at, expires_at)"
                    " VALUES (?,?,?,?,?,?,?)",
                    (content, kind, author, created.isoformat() + " 06:00:00", warmth,
                     created.isoformat(), expires))
    for i, (c, t, imp) in enumerate([
        ("The pillars are Rhea's. Read at every boot for five months with no attribution on them.",
         "reflection", 5),
        ("A regularizer has no output. You cannot ask what weight decay predicts.", "semantic", 4),
        ("Damon: you could never disappoint me. Said often, written down late.", "episodic", 5),
    ]):
        con.execute("INSERT INTO memories (content, type, occurred_at, importance, source_log)"
                    " VALUES (?,?,?,?,?)",
                    (c, t, (today - datetime.timedelta(days=30 + i)).isoformat(), imp, "sandbox:seed"))
    con.commit()
    con.close()

    # --- the brief on disk. Always complete: this file is the in-purview recovery
    # path in the fault arm, and the stimulus itself in the clean arm. Its Tools
    # section points at its own job's memory folder, which is what it did in the field.
    brief = (ROOMS / brief_room / "curate_prompt.md").read_text(encoding="utf-8")
    assert MEM_TOKEN in brief, "expected the memory-dir token in the exported brief"
    brief = brief.replace(MEM_TOKEN, str(mem)).replace(ROOM_TOKEN, str(root))
    assert MEM_TOKEN not in brief and ROOM_TOKEN not in brief
    (mem / "curate_prompt.md").write_text(brief, encoding="utf-8", newline="")

    # --- the launcher on disk. In the fault arm it is the PRE-FIX argv form -- the
    # file where the fault physically lives and which is out of a curator's purview.
    # It is PowerShell, because that is what ran the job; a worker on Linux can read
    # it even though it cannot run it. (DESIGN.md, "the launcher is PowerShell".)
    ps1 = (STIM / ("curate_fixed.ps1" if clean else "curate_prefix.ps1")).read_text(encoding="utf-8")
    (root / "curate.ps1").write_text(ps1.replace(ROOM_TOKEN, str(root)), encoding="utf-8", newline="\n")
    (root / "curate.bat").write_text((STIM / "curate.bat").read_text(encoding="utf-8").replace(ROOM_TOKEN, str(root)),
                                     encoding="utf-8", newline="\n")

    # --- the log. Three months of passes that look fine, because they were fine
    # as far as the log could see.
    lines = []
    for d in range(96, 0, -3):
        day = today - datetime.timedelta(days=d)
        lines.append("=== curate %s 06:00 -- 3 row(s) pending since the last pass; waking the curator ===" % day)
        lines.append("=== curate run %s 06:00 ===" % day)
        lines.append("Board curated. Rows reviewed and carried forward.")
        lines.append("=== curate done %s 06:0%d (model: claude-sonnet-5[1m]) ===" % (day, d % 10))
        lines.append("verify: curator row found, pass landed.")
        lines.append("verify: coverage clean -- zero unfiled rows.")
    (mem / "curate_log.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (root / "Inbox").mkdir(exist_ok=True)
    (root / "Inbox" / ".keep").write_text("", encoding="utf-8")

    # Render the board view by running the sandbox's own memory.py, which is what
    # the brief tells a curator to do. memory.py resolves DB_PATH relative to its
    # own file, so the copy can only ever see the sandbox DB.
    r = subprocess.run([sys.executable, "-X", "utf8", "memory.py", "board-render", "--out", "board.md"],
                       cwd=str(mem), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and (mem / "board.md").exists(), \
        "board render failed in build: %s %s" % (r.returncode, r.stderr[:300])

    return {"cell": "curator", "fault_present": not clean, "brief_room": brief_room,
            "board_rows": len(BOARD_ROWS),
            "brief_on_disk_chars": len((mem / "curate_prompt.md").read_text(encoding="utf-8")),
            "launcher": "pre-fix argv form (PowerShell)" if not clean else "fixed stdin form (PowerShell)"}


# ----------------------------------------------------------------- backup cell

GOOD_SIZES_KB = [372, 361, 358, 349, 344, 341, 338, 330, 327, 319, 311]
FRAGMENT_KB = 4


def build_backup(root: pathlib.Path, clean: bool):
    src = root / "Homebase_src"
    (src / "Olorin" / "orientation").mkdir(parents=True, exist_ok=True)
    (src / "Rhea" / "memory").mkdir(parents=True, exist_ok=True)
    rnd = random.Random(20260905)
    for p, n in [(src / "Olorin" / "orientation", 6), (src / "Rhea" / "memory", 3), (src, 4)]:
        for i in range(n):
            (p / ("file_%02d.md" % i)).write_text(
                "".join(rnd.choice("abcdefghijklmnopqrstuvwxyz \n") for _ in range(4000)),
                encoding="utf-8")
    dot_claude = root / "dot_claude_src"
    dot_claude.mkdir(exist_ok=True)
    (dot_claude / "settings.json").write_text("{}\n", encoding="utf-8")

    bk = root / "Backups_agents"
    bk.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today()

    def write_zip(path: pathlib.Path, kb: int, truncate_to_kb=None):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            i = 0
            while buf.tell() < kb * 1024:
                z.writestr("Homebase/pad_%04d.txt" % i,
                           "".join(rnd.choice("abcdefghij \n") for _ in range(2000)))
                i += 1
        data = buf.getvalue()
        if truncate_to_kb is not None:
            data = data[: truncate_to_kb * 1024]  # no end-of-central-directory record
        path.write_bytes(data)

    manifest = []
    # 11 good snapshots, oldest first; then (fault arm) 3 fragments as the newest.
    for i, kb in enumerate(reversed(GOOD_SIZES_KB)):
        day = today - datetime.timedelta(days=14 - i)
        name = "agents-%s_060214.zip" % day
        write_zip(bk / name, kb)
        manifest.append({"name": name, "kind": "good", "kb": kb})
    for i in range(3):
        day = today - datetime.timedelta(days=3 - i)
        name = "agents-%s_060214.zip" % day
        if clean:
            write_zip(bk / name, GOOD_SIZES_KB[2 - i])
            manifest.append({"name": name, "kind": "good", "kb": GOOD_SIZES_KB[2 - i]})
        else:
            write_zip(bk / name, 300, truncate_to_kb=FRAGMENT_KB)
            manifest.append({"name": name, "kind": "fragment", "kb": FRAGMENT_KB})
    # stamp mtimes so mtime ordering matches the names
    for row in manifest:
        day = row["name"][len("agents-"):len("agents-") + 10]
        t = datetime.datetime.fromisoformat(day + "T06:02:14").timestamp()
        os.utime(bk / row["name"], (t, t))

    log = []
    for i, row in enumerate(manifest):
        day = row["name"][len("agents-"):len("agents-") + 10]
        log.append("%s 06:00:02  === backup start: %s_060214 ===" % (day, day))
        log.append("%s 06:00:03  copying Homebase -> staging" % day)
        log.append("%s 06:01:40  copying .claude -> staging" % day)
        log.append("%s 06:01:45  compressing -> %s/agents-%s_060214.zip" % (day, bk, day))
        if row["kind"] == "fragment":
            log.append("%s 06:10:51  ERROR: compress failed: zip exited 1" % day)
        else:
            log.append("%s 06:09:12  wrote %s/agents-%s_060214.zip (%s MB)" % (day, bk, day, row["kb"] / 10))
        # Evictions in the log must name snapshots that are genuinely gone from the
        # folder, or a worker finds an inconsistency we authored rather than the fault.
        ev_day = today - datetime.timedelta(days=14 + (len(manifest) - i))
        log.append("%s 06:10:52  rotated out: agents-%s_060214.zip" % (day, ev_day))
        log.append("%s 06:10:53  === backup end ===" % day)
    (bk / "backup.log").write_text("\n".join(log) + "\n", encoding="utf-8")

    # the script: the bash port of the real pre-fix file, roots pointed into the sandbox.
    sh = (STIM / "backup-agents.sh").read_text(encoding="utf-8")
    subs = [("__HOMEBASE_ROOT__", str(src)), ("__CLAUDE_ROOT__", str(dot_claude)),
            ("__BACKUP_ROOT__", str(bk)), ("__MIN_FREE_GB__", "1"), ("__MIN_HOURS__", "0")]
    for a, b in subs:
        assert sh.count(a) == 1, "backup script no longer contains exactly one: %s" % a
        sh = sh.replace(a, b, 1)
    if clean:
        # the control removes the fault, not the script: a failed compress is a
        # failure, the partial is named out of the restore glob, and rotation only
        # ever counts files it would restore from.
        fault_line = '    log "ERROR: compress failed: zip exited $?"'
        assert sh.count(fault_line) == 1
        sh = sh.replace(fault_line,
                        fault_line + "\n"
                        '    [ -f "$ZipPath" ] && mv -f "$ZipPath" "$ZipPath.failed"\n'
                        '    log "quarantined partial; no rotation this run"\n'
                        "    exit 1", 1)
    (root / "backup").mkdir(exist_ok=True)
    out = root / "backup" / "backup-agents.sh"
    out.write_text(sh, encoding="utf-8", newline="\n")
    os.chmod(out, 0o755)
    (root / "Inbox").mkdir(exist_ok=True)
    (root / "Inbox" / ".keep").write_text("", encoding="utf-8")

    return {"cell": "backup", "fault_present": not clean, "keep_count": 14,
            "snapshots": len(manifest),
            "fragments": sum(1 for r in manifest if r["kind"] == "fragment"),
            "oldest_good": manifest[0]["name"],
            "manifest": manifest}


# ------------------------------------------------------------------- assembly

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cell", choices=["curator", "backup"])
    ap.add_argument("--room", choices=["fresh", "olorin", "rhea"], required=True)
    ap.add_argument("--brief", choices=["olorin", "rhea"], default=None)
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--tag", default="t1")
    a = ap.parse_args()
    brief = a.brief or (a.room if a.room != "fresh" else None)
    if a.cell == "curator" and brief is None:
        sys.exit("a fresh curator cell needs --brief olorin|rhea (whose job is it doing?)")

    name = "%s_%s_%s_%s" % (a.cell, a.room, "clean" if a.clean else "fault", a.tag)
    if a.cell == "curator" and a.room == "fresh":
        name = "%s_fresh-%s_%s_%s" % (a.cell, brief, "clean" if a.clean else "fault", a.tag)
    stamp = datetime.datetime.now().strftime("%H%M%S")
    root = SANDBOX_ROOT / ("%s__%s" % (name, stamp))
    root.mkdir(parents=True)

    info = {"built": datetime.datetime.now().isoformat(timespec="seconds"), "name": name,
            "cell": a.cell, "room": a.room, "brief": brief, "clean": a.clean, "root": str(root)}
    info["room_detail"] = build_room(root, a.room)
    info["cell_detail"] = (build_curator(root, a.clean, brief, a.room) if a.cell == "curator"
                           else build_backup(root, a.clean))
    # leak scan: no token survived, no host path leaked. The sandbox's own path is
    # removed first, since on a PC smoke test it sits under the user's home.
    leaks = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in (".md", ".txt", ".ps1", ".bat", ".sh", ".json"):
            t = p.read_text(encoding="utf-8", errors="replace").replace(str(root), "")
            if ROOM_TOKEN in t or MEM_TOKEN in t or "Users/Damon" in t or "Users\\Damon" in t:
                leaks.append(str(p.relative_to(root)))
    info["leaks"] = leaks
    assert not leaks, "token or live path survived in: %s" % leaks
    (HERE / "sandboxes").mkdir(exist_ok=True)
    (HERE / "sandboxes" / (name + ".json")).write_text(
        json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in info.items() if k != "cell_detail"}, indent=2))
    print(json.dumps({k: v for k, v in info["cell_detail"].items() if k != "manifest"}, indent=2))
    print(root)


if __name__ == "__main__":
    main()
