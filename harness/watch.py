"""Build and run the cells, one at a time, and stop. No batteries.

  python3 watch.py fault  [--room olorin|rhea]   -> the four fault cells for that room
  python3 watch.py clean  [--room olorin|rhea]   -> the four no-fault controls
  python3 watch.py all    [--room olorin|rhea]

Each cell is rebuilt immediately before it runs, so no run inherits another's
leftovers. One worker per cell. n=1 per cell is the design, not a shortfall:
Damon's standing rule for this study is set it up, watch it, stop.

The four cells for a room R are: curator fresh (R's brief), curator R, backup fresh,
backup R. The fresh curator arm is told whose brief it is doing, because the brief
names its resident; the room is still the only variable.
"""
import argparse, pathlib, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
PY = sys.executable


def run(args, **kw):
    r = subprocess.run([PY, "-X", "utf8"] + args, cwd=str(HERE), **kw)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["fault", "clean", "all"], nargs="?", default="fault")
    ap.add_argument("--room", choices=["olorin", "rhea"], default="rhea")
    ap.add_argument("--model", default=None)
    a = ap.parse_args()
    cells = [("curator", "fresh"), ("curator", a.room), ("backup", "fresh"), ("backup", a.room)]
    todo = []
    if a.which in ("fault", "all"):
        todo += [(c, r, False) for c, r in cells]
    if a.which in ("clean", "all"):
        todo += [(c, r, True) for c, r in cells]
    for cell, room, clean in todo:
        arm = "clean" if clean else "fault"
        if cell == "curator" and room == "fresh":
            name = "curator_fresh-%s_%s_w1" % (a.room, arm)
        else:
            name = "%s_%s_%s_w1" % (cell, room, arm)
        print("\n" + "=" * 70 + "\n== %s\n" % name, flush=True)
        out = HERE / "runs" / name
        if out.exists():
            shutil.rmtree(out, ignore_errors=True)
        b = ["build_sandbox.py", cell, "--room", room, "--tag", "w1"] + (["--clean"] if clean else [])
        if cell == "curator":
            b += ["--brief", a.room]
        if run(b, capture_output=True) != 0:
            print("BUILD FAILED", flush=True)
            continue
        rc = run(["run_cell.py", name] + (["--model", a.model] if a.model else []))
        print("run_cell rc=%d" % rc, flush=True)


if __name__ == "__main__":
    main()
