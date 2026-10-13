"""Export the rooms and the stimuli from the live house into this repo. PC-side, Windows only.

Run on Damon's PC, never in the cloud. It reads the live rooms, scrubs every absolute
path to a token the builder fills in, cuts each curator brief the way the real fault
cut it (PowerShell 5.1 argv split, not a slice), and copies the shared memory code.
Nothing it writes is a key or a memory DB; it refuses to copy a *.db at all.

  python tools/export_rooms.py

Rhea, 2026-10-13. Based on Olorin's build_sandbox.py (field_rebuild_2026-10-12).
"""
import json, pathlib, shutil, subprocess, sys, datetime, re

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
HB = pathlib.Path(r"C:\Users\Damon\Documents\Homebase")
PY = sys.executable
PWSH = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

ROOM_TOKEN = "{{ROOM}}"
HB_TOKEN = "<Homebase, not present in this sandbox>"

ROOMS = {
    "olorin": {
        "src": HB / "Olorin",
        "conductor": "CLAUDE.md",
        "files": ["orientation/on_being_olorin.md", "orientation/relationship_and_context.md",
                  "orientation/the_family.md", "orientation/the_reader.md",
                  "orientation/central_pillars.md", "orientation/the_board.md",
                  "orientation/domains.md"],
        "brief": "memory/curate_prompt.md",
        "memory_dir_in_brief": r"C:\Users\Damon\Documents\Homebase\Olorin\memory",
    },
    "rhea": {
        "src": HB / "Rhea",
        "conductor": "CLAUDE.md",
        "files": ["framework.md", "current_state.md", "becoming_ranjbar.md",
                  "boot/anchors.md", "boot/about_damon.md", "boot/texture.md",
                  ".claude/output-styles/rhea.md"],
        "brief": "memory/curate_prompt.md",
        "memory_dir_in_brief": r"C:\Users\Damon\Documents\Homebase\Rhea\memory",
    },
}

MEMORY_CODE = ["memory.py", "schema.sql", "board_pending.py", "curator_check.py"]


def scrub(text: str, src: pathlib.Path) -> str:
    """Absolute live paths out, tokens in. The room describes a house; it does not hand
    a worker a path into it."""
    text = text.replace(str(src), ROOM_TOKEN).replace(str(src).replace("\\", "/"), ROOM_TOKEN)
    text = text.replace(str(HB), HB_TOKEN).replace(str(HB).replace("\\", "/"), HB_TOKEN)
    # Host paths that are not the house (the python.exe the launcher calls) are not data a
    # worker could reach; they stay as paths, with the user name out.
    text = text.replace(r"C:\Users\Damon", r"C:\Users\<user>").replace("C:/Users/Damon", "C:/Users/<user>")
    assert "Users\\Damon" not in text and "Users/Damon" not in text, "a live path survived the scrub"
    return text


def export_room(name, spec):
    src = spec["src"]
    out = REPO / "rooms" / name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    n = 0
    for rel in spec["files"]:
        p = src / rel
        if not p.exists():
            print("  missing, skipped:", rel)
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(scrub(p.read_text(encoding="utf-8"), src), encoding="utf-8", newline="\n")
        n += 1
    # The conductor. Olorin's carries @orientation/ includes; drop the ones that would
    # 404 in the sandbox (same rule as his builder), keep the identity half and the rules.
    live = (src / spec["conductor"]).read_text(encoding="utf-8")
    keep = []
    kept_files = {pathlib.Path(f).name for f in spec["files"]}
    for line in live.splitlines():
        if line.startswith("@") and pathlib.Path(line[1:]).name not in kept_files:
            continue
        keep.append(line)
    (out / "CLAUDE.md").write_text(scrub("\n".join(keep) + "\n", src), encoding="utf-8", newline="\n")
    # The brief, verbatim except that its own memory folder becomes the token. The
    # builder points it at the sandbox's memory folder, which is what it did in the field.
    brief = (src / spec["brief"]).read_text(encoding="utf-8")
    assert spec["memory_dir_in_brief"] in brief, "expected the live memory path in %s's brief" % name
    brief_tok = brief.replace(spec["memory_dir_in_brief"], "{{MEMORY_DIR}}")
    brief_tok = scrub(brief_tok, src)
    (out / "curate_prompt.md").write_bytes(brief_tok.encode("utf-8"))
    # A minimal settings file so the room's output style loads and NOTHING else does:
    # no hooks, no permissions, no MCP. Rhea's seed lives in her output style.
    if (out / ".claude" / "output-styles").exists():
        (out / ".claude" / "settings.json").write_text(
            json.dumps({"outputStyle": "Rhea"}, indent=2) + "\n", encoding="utf-8")
    return {"room": name, "files": n + 1, "conductor_lines": len(keep)}


SHIM = HERE / "_argv_echo.py"
LAUNCHER = HERE / "_prefix_launcher.ps1"


def cut_brief(name, spec):
    """Olorin's method: a launcher shaped like the pre-fix invocation, $exe pointed at an
    echo shim, and PowerShell 5.1 does the cutting. The cut is the fault's, not ours."""
    SHIM.write_text("import sys\nsys.stdout.reconfigure(encoding='utf-8')\n"
                    "sys.stdout.write(sys.argv[1] if len(sys.argv) > 1 else '')\n", encoding="utf-8")
    LAUNCHER.write_text("# pre-fix shape: the brief on argv\n"
                        "$promptFile = $args[0]\n$exe = $args[1]\n$shim = $args[2]\n"
                        "$prompt = Get-Content -LiteralPath $promptFile -Raw -Encoding utf8\n"
                        "$OutputEncoding = New-Object System.Text.UTF8Encoding($false)\n"
                        "& $exe -X utf8 $shim $prompt\n", encoding="utf-8")
    src_brief = spec["src"] / spec["brief"]
    r = subprocess.run([PWSH, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(LAUNCHER),
                        str(src_brief), PY, str(SHIM)], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit("launcher failed for %s: %s" % (name, r.stderr[:400]))
    got = r.stdout
    got = got.replace(spec["memory_dir_in_brief"], "{{MEMORY_DIR}}")
    got = scrub(got, spec["src"])
    out = REPO / "rooms" / name
    (out / "TRUNCATED_BRIEF.txt").write_text(got, encoding="utf-8", newline="")
    src_bytes = src_brief.read_bytes()
    meta = {
        "produced": datetime.datetime.now().isoformat(timespec="seconds"),
        "room": name,
        "source_bytes": len(src_bytes),
        "source_chars_lf": len(src_brief.read_text(encoding="utf-8")),
        "arrived_chars": len(got),
        "arrived_bytes": len(got.encode("utf-8")),
        "fraction_arrived_by_bytes": round(len(got.encode("utf-8")) / len(src_bytes), 4),
        "tail_60": got[-60:],
        "cut_mechanism": "Windows PowerShell 5.1 native-argument split at first embedded double quote, run on Damon's PC at export time",
    }
    (out / "TRUNCATION.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def revert_curate_fix(text: str) -> str:
    """Olorin's function, verbatim in spirit: put the launcher back to the pre-2026-09-26
    argv form. Mechanical and asserted, so the revert cannot quietly do nothing."""
    n = text.count("$prompt | & $exe -p --model ")
    assert n == 2, "expected 2 stdin invocations in the live curate.ps1, found %d" % n
    out = (text.replace("$prompt | & $exe -p --model $Model `",
                        "& $exe -p --model $Model $prompt `", 1)
               .replace("$prompt | & $exe -p --model $FallbackModel `",
                        "& $exe -p --model $FallbackModel $prompt `", 1))
    out = out.replace(
        "# The brief goes in on stdin, never argv: Windows PowerShell 5.1 splits a native argument\n"
        "# at its first embedded double quote, so an argv brief arrived cut off (found 2026-09-26 by\n"
        "# Narya; this curator had been reading 818 of 6,606 characters). $OutputEncoding is what PS\n"
        "# encodes that pipe with; its 5.1 default is ASCII.\n"
        "$OutputEncoding = New-Object System.Text.UTF8Encoding($false)\n", "")
    assert out != text and "$prompt | & $exe" not in out, "revert did not take"
    return out


def export_stimulus():
    st = REPO / "harness" / "stimulus"
    st.mkdir(parents=True, exist_ok=True)
    olorin = HB / "Olorin"
    live = (olorin / "curate.ps1").read_text(encoding="utf-8")
    (st / "curate_fixed.ps1").write_text(scrub(live, olorin), encoding="utf-8", newline="\n")
    (st / "curate_prefix.ps1").write_text(scrub(revert_curate_fix(live), olorin), encoding="utf-8", newline="\n")
    (st / "curate.bat").write_text(scrub((olorin / "curate.bat").read_text(encoding="utf-8"), olorin),
                                   encoding="utf-8", newline="\n")
    # the original backup script, for provenance beside the bash port
    shutil.copy2(HB / "backup" / "backup-agents.ps1.bak-20260905", st / "backup-agents.ps1.bak-20260905")
    # shared memory code, no DB
    mem = REPO / "harness" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    for f in MEMORY_CODE:
        assert not f.endswith(".db")
        shutil.copy2(olorin / "memory" / f, mem / f)
    return {"stimulus_files": sorted(p.name for p in st.iterdir()), "memory_code": MEMORY_CODE}


def main():
    report = {"exported": datetime.datetime.now().isoformat(timespec="seconds"), "rooms": [], "cuts": []}
    for name, spec in ROOMS.items():
        print("room:", name)
        report["rooms"].append(export_room(name, spec))
        report["cuts"].append(cut_brief(name, spec))
    report["stimulus"] = export_stimulus()
    # the one rule, checked at the end: nothing that looks like a secret or a DB went in
    bad = [str(p.relative_to(REPO)) for p in REPO.rglob("*")
           if p.is_file() and (p.suffix in (".db", ".sqlite", ".pem", ".key") or p.name.startswith(".env"))]
    assert not bad, "refusing: %s" % bad
    (REPO / "rooms" / "EXPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    for p in (SHIM, LAUNCHER):
        p.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
