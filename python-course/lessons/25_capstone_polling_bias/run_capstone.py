"""Run the full capstone pipeline using YOUR exercises.py and print the report.

    python run_capstone.py            (from this folder)
"""
import importlib.util
import pathlib
import pprint

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("my_capstone", HERE / "exercises.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

try:
    rep = mod.report(HERE / "data" / "polls.csv", HERE / "data" / "results.csv", HERE / "output")
except NotImplementedError as e:
    raise SystemExit(f"Not finished yet: {e} is still a stub. Keep going!")

print(rep["summary"], "\n")
pprint.pprint({k: v for k, v in rep.items() if k != "summary"})
print("\nPlot saved to", rep["plot_path"])
