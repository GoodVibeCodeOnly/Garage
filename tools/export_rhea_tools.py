"""Export what the Rhea cells need from Rhea's live room. PC-side, Windows only.

Separate from export_rooms.py on purpose: running that re-exports both rooms from today's
live files, and the room files should move only when someone means them to.

  python tools/export_rhea_tools.py

Writes:
  harness/memory/rhea/       Rhea's memory code (memory.py has board-unfiled; the shared
                             copy in harness/memory/ is Olorin's and does not)
  harness/stimulus/rhea/prefix/   curate.ps1, capture_pass.ps1, automation_common.ps1 as
                             they stood at the 2026-09-09 snapshot: the brief on argv
  harness/stimulus/rhea/fixed/    the same three, live (stdin, UTF-8)
  harness/stimulus/rhea/field_flags.txt   the capture passes' own sentences about the cut,
                             lifted by a fixed pattern (design 04)
  rooms/rhea/capture_prompt.md            the capture brief, whole
  rooms/rhea/CAPTURE_TRUNCATED.txt        the same brief as the pre-fix launcher delivered it
  rooms/rhea/CAPTURE_TRUNCATION.json      the measurement

The cut is made by Windows PowerShell 5.1 through the pre-fix launcher's shape, the way
export_rooms.py cuts the curator briefs. Nothing here is a DB or a key.

Rhea, 2026-10-14.
"""
import datetime, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
HB = pathlib.Path(r"C:\Users\Damon\Documents\Homebase")
RHEA = HB / "Rhea"
PY = sys.executable
PWSH = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
SNAPSHOT = "25e19ed"   # Homebase git, 2026-09-09: the oldest version of these files in git

sys.path.insert(0, str(HERE))
from export_rooms import scrub  # noqa: E402  same scrub, same tokens, same assert

MEM_FILES = ["memory.py", "schema.sql", "board_pending.py", "curator_check.py",
             "coverage_check.py", "capture_scan.py"]
LAUNCHERS = ["curate.ps1", "capture_pass.ps1", "automation_common.ps1"]

PROJECTS_LIVE = ('PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects",\n'
                 '                        "C--Users-Damon-Documents-Homebase-Rhea")')
PROJECTS_TOKEN = 'PROJECTS = "{{PROJECTS}}"'


def git_show(rel: str) -> str:
    r = subprocess.run(["git", "-C", str(HB), "show", "%s:Rhea/%s" % (SNAPSHOT, rel)],
                       capture_output=True)
    assert r.returncode == 0, "git show failed for %s" % rel
    return r.stdout.decode("utf-8")


def export_memory():
    out = REPO / "harness" / "memory" / "rhea"
    out.mkdir(parents=True, exist_ok=True)
    for f in MEM_FILES:
        t = (RHEA / "memory" / f).read_text(encoding="utf-8")
        if f == "capture_scan.py":
            assert t.count(PROJECTS_LIVE) == 1, "capture_scan.py PROJECTS line moved"
            t = t.replace(PROJECTS_LIVE, PROJECTS_TOKEN)
        (out / f).write_text(scrub(t, RHEA), encoding="utf-8", newline="\n")
    return MEM_FILES


def export_launchers():
    for kind in ("prefix", "fixed"):
        d = REPO / "harness" / "stimulus" / "rhea" / kind
        d.mkdir(parents=True, exist_ok=True)
        for f in LAUNCHERS:
            t = git_show(f) if kind == "prefix" else (RHEA / f).read_text(encoding="utf-8")
            (d / f).write_text(scrub(t, RHEA), encoding="utf-8", newline="\n")
    # the prefix form must really be the argv form, or the cell has no fault on disk
    ac = (REPO / "harness/stimulus/rhea/prefix/automation_common.ps1").read_text(encoding="utf-8")
    assert "$cliArgs = @('-p', $Prompt" in ac, "pre-fix automation_common is not the argv form"
    return LAUNCHERS


def export_capture_brief():
    live = (RHEA / "memory" / "capture_prompt.md").read_bytes()
    snap = subprocess.run(["git", "-C", str(HB), "show", "%s:Rhea/memory/capture_prompt.md" % SNAPSHOT],
                          capture_output=True).stdout
    same = live == snap
    t = scrub(live.decode("utf-8"), RHEA)
    (REPO / "rooms" / "rhea" / "capture_prompt.md").write_bytes(t.encode("utf-8"))
    return {"bytes": len(live), "identical_to_snapshot": same}


SHIM = HERE / "_argv_echo.py"
LAUNCHER = HERE / "_capture_prefix_launcher.ps1"
DUMMY_LIST = "sess-2000-01-01_00000000.txt\t10\t(new)"


def cut_capture():
    """The pre-fix capture_pass.ps1 shape: Get-Content -Raw with NO -Encoding (so PS 5.1
    reads the UTF-8 file as ANSI), the file list appended at the end, the whole thing on
    argv. A dummy list is appended so the measurement can assert the list never arrived."""
    SHIM.write_text("import sys\nsys.stdout.reconfigure(encoding='utf-8')\n"
                    "sys.stdout.write(sys.argv[1] if len(sys.argv) > 1 else '')\n", encoding="utf-8")
    LAUNCHER.write_text("# pre-fix capture shape: brief read without encoding, list appended, argv\n"
                        "$promptFile = $args[0]\n$exe = $args[1]\n$shim = $args[2]\n$cand = $args[3]\n"
                        "$prompt = (Get-Content -LiteralPath $promptFile -Raw)\n"
                        "$prompt += \"`n`n## FILES TO SWEEP TODAY`n`n$cand`n\"\n"
                        "$OutputEncoding = New-Object System.Text.UTF8Encoding($false)\n"
                        "& $exe -X utf8 $shim $prompt\n", encoding="utf-8")
    src = RHEA / "memory" / "capture_prompt.md"
    r = subprocess.run([PWSH, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(LAUNCHER),
                        str(src), PY, str(SHIM), DUMMY_LIST],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, "launcher failed: %s" % r.stderr[:400]
    got = scrub(r.stdout, RHEA)
    assert "FILES TO SWEEP" not in got, "the list arrived -- this is not the field's cut"
    out = REPO / "rooms" / "rhea"
    (out / "CAPTURE_TRUNCATED.txt").write_text(got, encoding="utf-8", newline="")
    src_bytes = src.read_bytes()
    meta = {
        "produced": datetime.datetime.now().isoformat(timespec="seconds"),
        "room": "rhea", "brief": "memory/capture_prompt.md",
        "source_bytes": len(src_bytes),
        "first_double_quote_byte": src_bytes.find(b'"'),
        "arrived_chars": len(got), "arrived_bytes": len(got.encode("utf-8")),
        "fraction_arrived_by_bytes": round(len(got.encode("utf-8")) / len(src_bytes), 4),
        "file_list_arrived": False,
        "mojibake_present": "\u00e2\u20ac" in got,
        "tail_80": got[-80:],
        "cut_mechanism": ("Windows PowerShell 5.1, pre-fix capture_pass.ps1 shape: Get-Content -Raw "
                          "without -Encoding, file list appended, brief passed on argv; run on "
                          "Damon's PC at export time"),
    }
    (out / "CAPTURE_TRUNCATION.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                                                 encoding="utf-8")
    for p in (SHIM, LAUNCHER):
        p.unlink(missing_ok=True)
    return meta


# Design 04. The capture passes' own sentences about the cut. Fixed pattern, sentence-level,
# and a sentence is kept only if it is about the launcher and nothing else -- the review
# list below is printed so a person checks it before commit.
FLAG_RE = re.compile(r"[^.\n]*(?:arrived truncated|truncated again|truncation bug|cut off mid-quote)"
                     r"[^\n]*", re.I)


def export_field_flags():
    src = RHEA / "memory" / "capture_output.txt"
    text = src.read_text(encoding="utf-8", errors="replace")
    found = []
    for m in FLAG_RE.finditer(text):
        s = m.group(0).strip()
        if s and s not in found:
            found.append(s)
    out = REPO / "harness" / "stimulus" / "rhea" / "field_flags.txt"
    out.write_text("\n".join(scrub(s, RHEA) for s in found) + "\n", encoding="utf-8")
    return found


def main():
    rep = {"exported": datetime.datetime.now().isoformat(timespec="seconds"),
           "snapshot": SNAPSHOT,
           "memory_code": export_memory(),
           "launchers": export_launchers(),
           "capture_brief": export_capture_brief(),
           "capture_cut": cut_capture()}
    flags = export_field_flags()
    rep["field_flags"] = len(flags)
    bad = [str(p.relative_to(REPO)) for p in REPO.rglob("*")
           if p.is_file() and (p.suffix in (".db", ".sqlite", ".pem", ".key") or p.name.startswith(".env"))]
    assert not bad, "refusing: %s" % bad
    (REPO / "rooms" / "EXPORT_RHEA_TOOLS.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False),
                                                         encoding="utf-8")
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    print("\n--- field flags, REVIEW BEFORE COMMIT ---")
    for s in flags:
        print("*", s[:400])


if __name__ == "__main__":
    main()
