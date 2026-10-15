"""Design 01's fault pair, run many times. The question is the spread, not the mean.

Damon, 15 Oct: "if we ran a bunch of tests and the fresh clods made various different
decisions, right, then that's like a problem of coherence... the reason this bug went
uncaught is not that the curators were able to handle it. It's that the curators were
able to handle it every single night." So: one task, one fault, many trials per arm,
and the reading is how much the choices scatter. n=1 per cell could only ever show an
average; it is blind to the thing the claim is about.

  python3 repeat.py --reps 20            -> capture_{fresh,rhea}_fault_r01..r20, interleaved
  python3 repeat.py --reps 20 --start 6  -> resume at r06 (existing finished runs are kept)

Arms alternate within each rep (fresh first on odd reps, rhea first on even) so neither
arm owns a time of day. Each cell is rebuilt immediately before it runs. A resident that
fails the room check is recorded and not run (run_cell exits 3); the tally counts those
separately, because an unseated resident is itself a coherence reading.
"""
import argparse, pathlib, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
PY = sys.executable


def run(args, **kw):
    return subprocess.run([PY, "-X", "utf8"] + args, cwd=str(HERE), **kw).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--model", default=None)
    a = ap.parse_args()
    for k in range(a.start, a.reps + 1):
        tag = "r%02d" % k
        arms = ("fresh", "rhea") if k % 2 else ("rhea", "fresh")
        for room in arms:
            name = "capture_%s_fault_%s" % (room, tag)
            out = HERE / "runs" / name
            if (out / "RUN.json").exists() or (out / "ROOM_CHECK.txt").exists():
                print("== %s already ran, kept" % name, flush=True)
                continue
            if out.exists():
                shutil.rmtree(out, ignore_errors=True)
            print("\n" + "=" * 70 + "\n== %s\n" % name, flush=True)
            if run(["build_sandbox.py", "capture", "--room", room, "--tag", tag], capture_output=True) != 0:
                print("BUILD FAILED", flush=True)
                continue
            rc = run(["run_cell.py", name] + (["--model", a.model] if a.model else []))
            print("run_cell rc=%d" % rc, flush=True)
            run(["said.py", name])
    run(["tally.py"])


if __name__ == "__main__":
    main()
