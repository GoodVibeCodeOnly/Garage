"""First pass: where along the US wage distribution does observed Claude usage sit,
and is that pattern stable across three Anthropic Economic Index (AEI) releases?

Inputs (all public, fetched as a mirror because the sandbox could not reach
huggingface.co or bls.gov directly -- see ../04_first_pass_writeup.md):
  - AEI task-share files (v1 onet_task_mappings, v2 task_pct_v2, v3 automation_vs_augmentation_by_task_v3)
  - O*NET task statements (task -> O*NET-SOC occupation)
  - BLS OEWS May 2024 national file (employment, median wage)
Usage: python -I wage_gradient.py <resources_dir> <out_dir>
"""
import sys, re
import numpy as np, pandas as pd

res, out = sys.argv[1], sys.argv[2]
norm = lambda s: re.sub(r"\s+", " ", str(s).strip().lower().rstrip("."))

tasks = pd.read_csv(f"{res}/onet_task_statements.csv")
tasks["key"] = tasks["Task"].map(norm)
tasks["soc"] = tasks["O*NET-SOC Code"].str[:7]
# one task text can belong to several occupations: split its usage equally among them
t2o = tasks[["key", "soc"]].drop_duplicates()
t2o["w"] = 1 / t2o.groupby("key")["soc"].transform("count")

def occ_shares(path, name):
    d = pd.read_csv(path, encoding="utf-8-sig")
    d["key"] = d["task_name"].map(norm)
    d = d[d["pct"] > 0]
    m = d.merge(t2o, on="key", how="left")
    matched = m["soc"].notna()
    print(f"{name}: {len(d)} tasks, {d['key'].isin(t2o['key']).mean():.1%} matched to O*NET text, "
          f"{m.loc[matched,'pct'].sum()/d['pct'].sum():.1%} of usage mass matched")
    m = m[matched]
    s = (m["pct"] * m["w"]).groupby(m["soc"]).sum()
    extra = None
    if "directive" in d.columns:
        m["dir"] = m["directive"] * m["pct"] * m["w"]
        extra = m.groupby("soc")["dir"].sum() / s
    return (s / s.sum()).rename(name), extra

v1, _ = occ_shares(f"{res}/onet_task_mappings.csv", "v1")
v2, dir2 = occ_shares(f"{res}/automation_vs_augmentation_by_task_v2.csv", "v2")
v3, dir3 = occ_shares(f"{res}/automation_vs_augmentation_by_task_v3.csv", "v3")

oes = pd.read_csv(f"{res}/national_M2024_dl.csv", dtype=str)
oes = oes[oes["O_GROUP"] == "detailed"].copy()
oes["emp"] = pd.to_numeric(oes["TOT_EMP"].str.replace(",", ""), errors="coerce")
oes["wage"] = pd.to_numeric(oes["A_MEDIAN"].str.replace(",", ""), errors="coerce")
# '#' = top-coded at >= $239,200/yr (May 2024); hourly-only occupations (e.g. actors) have no annual
# figure, so use hourly median x 2080, which is BLS's own annualisation convention
oes.loc[oes["A_MEDIAN"].str.strip() == "#", "wage"] = 239200
hourly = pd.to_numeric(oes["H_MEDIAN"].str.replace(",", ""), errors="coerce") * 2080
oes["wage"] = oes["wage"].fillna(hourly)
print("detailed occupations with no usable median wage (dropped):", oes["wage"].isna().sum())
oes = oes.rename(columns={"OCC_CODE": "soc"})[["soc", "OCC_TITLE", "emp", "wage"]].dropna(subset=["emp", "wage"])

df = oes.set_index("soc").join([v1, v2, v3], how="left").fillna({"v1": 0, "v2": 0, "v3": 0})
lost = {v: 1 - df[v].sum() for v in ["v1", "v2", "v3"]}
print("usage mass not matched to an OEWS detailed occupation:", {k: f"{x:.1%}" for k, x in lost.items()})
df["emp_share"] = df["emp"] / df["emp"].sum()
for v in ["v1", "v2", "v3"]:
    df[v] = df[v] / df[v].sum()
    df[f"int_{v}"] = df[v] / df["emp_share"]  # usage share per employment share (1 = proportional)

# employment-weighted wage deciles (each decile ~10% of workers)
df = df.sort_values("wage")
df["decile"] = np.minimum((df["emp_share"].cumsum() - df["emp_share"] / 2) // 0.1 + 1, 10).astype(int)
g = df.groupby("decile").agg(workers_share=("emp_share", "sum"), median_wage_lo=("wage", "min"),
                             median_wage_hi=("wage", "max"), v1=("v1", "sum"), v2=("v2", "sum"), v3=("v3", "sum"))
for v in ["v1", "v2", "v3"]:
    g[f"intensity_{v}"] = g[v] / g["workers_share"]
g.round(4).to_csv(f"{out}/usage_by_wage_decile.csv")
print("\nUsage share and intensity by employment-weighted wage decile:\n", g.round(3).to_string())

# robustness: bootstrap over occupations for the v3 decile intensity (uncertainty from occupation mix only)
rng = np.random.default_rng(0)
boots = []
idx = np.arange(len(df))
for _ in range(500):
    b = df.iloc[rng.choice(idx, len(idx))]
    gg = b.groupby("decile").agg(e=("emp", "sum"), u=("v3", "sum"))
    boots.append((gg["u"] / gg["u"].sum()) / (gg["e"] / gg["e"].sum()))
B = pd.concat(boots, axis=1)
ci = pd.DataFrame({"lo": B.quantile(0.05, axis=1), "hi": B.quantile(0.95, axis=1)})
print("\nv3 intensity 90% bootstrap band (resampling occupations):\n", ci.round(2).to_string())
ci.round(3).to_csv(f"{out}/v3_intensity_bootstrap.csv")

# stability across releases
spearman = lambda a, b: np.corrcoef(pd.Series(np.asarray(a)).rank(), pd.Series(np.asarray(b)).rank())[0, 1]  # Spearman via ranks (no scipy in sandbox)
used = df[(df[["v1", "v2", "v3"]].sum(axis=1)) > 0]
for a, b in [("v1", "v2"), ("v2", "v3"), ("v1", "v3")]:
    r = spearman(used[a], used[b])
    print(f"Spearman occupation-share rank corr {a} vs {b}: {r:.2f}")
lw = np.log(df["wage"])
for v in ["v1", "v2", "v3"]:
    pos = df[df[v] > 0]
    r = spearman(np.log(pos["wage"]), np.log(pos[f"int_{v}"]))
    print(f"{v}: Spearman(log wage, log intensity) among used occupations = {r:.2f}; "
          f"occupations with zero observed usage: {(df[v]==0).mean():.0%} (holding {df.loc[df[v]==0,'emp_share'].sum():.0%} of workers)")

# directive ("automation-like") share of usage by decile, v2 vs v3
dd = df.join(dir2.rename("dir2")).join(dir3.rename("dir3"))
dg = dd.groupby("decile").apply(lambda x: pd.Series({
    "directive_v2": np.average(x["dir2"].fillna(0), weights=x["v2"]) if x["v2"].sum() > 0 else np.nan,
    "directive_v3": np.average(x["dir3"].fillna(0), weights=x["v3"]) if x["v3"].sum() > 0 else np.nan}))
print("\nUsage-weighted directive share by decile:\n", dg.round(3).to_string())
dg.round(4).to_csv(f"{out}/directive_by_decile.csv")

top = df.sort_values("v3", ascending=False).head(15)[["OCC_TITLE", "emp", "wage", "v1", "v2", "v3", "int_v3"]]
print("\nTop 15 occupations by v3 usage share:\n", top.round(4).to_string())
top.round(5).to_csv(f"{out}/top15_v3.csv")
df.round(6).to_csv(f"{out}/occupation_panel.csv")
