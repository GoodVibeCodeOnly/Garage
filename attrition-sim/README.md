# attrition-sim

Monte Carlo test of whether attrition (fights per day) balances casters and martials in
D&D 3.5, using SRD rules only. Start with **[FINDINGS.md](FINDINGS.md)**.

- Windows: double-click `run_sim.bat`.
- Elsewhere: `python -m unittest discover -s tests && python run_experiments.py`

Pure Python 3.8+ standard library; charts are hand-written SVG.
