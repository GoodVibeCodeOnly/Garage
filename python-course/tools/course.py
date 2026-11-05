"""The course menu. course.bat runs this; you can also run `python tools/course.py`.

Usage without the menu:
    python tools/course.py check 07        # test your lesson 07 exercises
    python tools/course.py progress        # one line per lesson: how many tests pass
    python tools/course.py example 07      # run lesson 07's worked example
    python tools/course.py open 07         # open lesson 07 files in IDLE
    python tools/course.py solutions       # check the model solutions (all should pass)
    python tools/course.py capstone        # run your lesson 25 pipeline end to end
"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

COURSE = pathlib.Path(__file__).resolve().parent.parent
LESSONS = COURSE / "lessons"


def lessons() -> list[pathlib.Path]:
    return sorted(p for p in LESSONS.iterdir() if p.is_dir() and p.name[:2].isdigit())


def find(number: str) -> pathlib.Path | None:
    number = number.strip().zfill(2)
    for p in lessons():
        if p.name.startswith(number + "_"):
            return p
    return None


def run_pytest(target: pathlib.Path, solutions: bool = False, quiet: bool = False) -> int:
    env = dict(os.environ)
    env["COURSE_SOLUTIONS"] = "1" if solutions else "0"
    env["MPLBACKEND"] = "Agg"
    cmd = [sys.executable, "-m", "pytest", str(target)]
    if quiet:
        cmd += ["--tb=no"]
    return subprocess.call(cmd, cwd=COURSE, env=env)


def count(target: pathlib.Path, solutions: bool = False) -> tuple[int, int]:
    """(passed, total) for one lesson, without printing the details."""
    env = dict(os.environ, COURSE_SOLUTIONS="1" if solutions else "0", MPLBACKEND="Agg")
    out = subprocess.run(
        [sys.executable, "-m", "pytest", str(target), "--tb=no"],
        cwd=COURSE, env=env, capture_output=True, text=True,
    ).stdout
    passed = failed = errors = 0
    for n, word in re.findall(r"(\d+) (passed|failed|error|errors)", out):
        if word == "passed":
            passed = int(n)
        elif word == "failed":
            failed = int(n)
        else:
            errors += int(n)
    return passed, passed + failed + errors


def cmd_check(number: str) -> int:
    lesson = find(number)
    if lesson is None:
        print(f"No lesson numbered {number!r}.")
        return 1
    print(f"\nChecking {lesson.name} ...\n")
    code = run_pytest(lesson)
    if code == 0:
        print("\nAll tests pass. Nice. Compare with solutions/" + lesson.name + "/exercises.py")
    else:
        print("\nSome tests failed. Read the first failure above: it names the test,")
        print("the line, and what was expected vs what your code returned.")
        print("'NotImplementedError' just means you haven't written that exercise yet.")
    return code


def cmd_progress() -> int:
    print()
    for lesson in lessons():
        passed, total = count(lesson)
        bar = "#" * passed + "." * (total - passed)
        mark = "DONE" if total and passed == total else ""
        print(f"  {lesson.name:<34} {passed:>3}/{total:<3} {bar[:40]} {mark}")
    print()
    return 0


def cmd_solutions() -> int:
    bad = []
    for lesson in lessons():
        passed, total = count(lesson, solutions=True)
        ok = total > 0 and passed == total
        print(f"  {lesson.name:<34} {passed:>3}/{total:<3} {'ok' if ok else 'PROBLEM'}")
        if not ok:
            bad.append(lesson.name)
    print("\nAll solutions pass." if not bad else f"\nProblems in: {', '.join(bad)}")
    return 1 if bad else 0


def cmd_example(number: str) -> int:
    lesson = find(number)
    if lesson is None:
        print(f"No lesson numbered {number!r}.")
        return 1
    env = dict(os.environ, MPLBACKEND="Agg")
    script = "example.py"
    print(f"\nRunning {lesson.name}/{script}\n" + "-" * 60)
    code = subprocess.call([sys.executable, script], cwd=lesson, env=env)
    out = lesson / "output"
    if out.exists():
        print("-" * 60 + f"\nPictures/files written to: {out}")
    return code


def cmd_capstone() -> int:
    lesson = find("25")
    env = dict(os.environ, MPLBACKEND="Agg")
    print(f"\nRunning YOUR capstone pipeline ({lesson.name}/run_capstone.py)\n" + "-" * 60)
    return subprocess.call([sys.executable, "run_capstone.py"], cwd=lesson, env=env)


def cmd_open(number: str) -> int:
    lesson = find(number)
    if lesson is None:
        print(f"No lesson numbered {number!r}.")
        return 1
    files = [lesson / "README.md", lesson / "example.py", lesson / "exercises.py"]
    files = [str(f) for f in files if f.exists()]
    print("Opening in IDLE (Python's built-in editor). In IDLE, press F5 to run a file.")
    pyw = pathlib.Path(sys.executable).with_name("pythonw.exe")
    exe = str(pyw) if pyw.exists() else sys.executable
    subprocess.Popen([exe, "-m", "idlelib", *files], cwd=lesson)
    return 0


MENU = """
==============================================================
  PYTHON FOR RESEARCH  -  course menu
==============================================================
  1  Check my exercises for a lesson
  2  Open a lesson (README, example, exercises) in the editor
  3  Run a lesson's worked example
  4  Show my progress across all lessons
  5  Verify the model solutions (sanity check)
  6  Run my capstone pipeline (lesson 25, once its tests pass)
  q  Quit
"""


def menu() -> None:
    while True:
        print(MENU)
        choice = input("Choose: ").strip().lower()
        if choice in ("q", "quit", "exit", ""):
            return
        if choice in ("1", "2", "3"):
            print("\nLessons:")
            for p in lessons():
                print("   ", p.name)
            n = input("\nLesson number (e.g. 7): ").strip()
            {"1": cmd_check, "2": cmd_open, "3": cmd_example}[choice](n)
        elif choice == "4":
            cmd_progress()
        elif choice == "5":
            cmd_solutions()
        elif choice == "6":
            cmd_capstone()
        else:
            print("Type 1-6, or q.")
        input("\nPress Enter to return to the menu...")


def main(argv: list[str]) -> int:
    if not argv:
        menu()
        return 0
    cmd, *rest = argv
    if cmd == "check" and rest:
        return cmd_check(rest[0])
    if cmd == "example" and rest:
        return cmd_example(rest[0])
    if cmd == "open" and rest:
        return cmd_open(rest[0])
    if cmd == "progress":
        return cmd_progress()
    if cmd == "solutions":
        return cmd_solutions()
    if cmd == "capstone":
        return cmd_capstone()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
