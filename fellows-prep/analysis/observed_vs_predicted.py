"""Step 2 of the first pass: compare observed Claude usage intensity (from wage_gradient.py's
occupation panel) with *predicted* exposure from Eloundou, Manning, Mishkin & Rock (2023),
'GPTs are GPTs' (occ_level.csv, github.com/openai/GPTs-are-GPTs). Uses human_rating_beta
(share of tasks directly exposed + half of those exposed with complementary tools).
Usage: python -I observed_vs_predicted.py <occ_level.csv> <out_dir>
"""
import sys
import numpy as np, pandas as pd

src, out = sys.argv[1], sys.argv[2]
panel = pd.read_csv(f"{out}/occupation_panel.csv")
e = pd.read_csv(src)
e["soc"] = e["O*NET-SOC Code"].str[:7]
e = e.groupby("soc")[["human_rating_beta", "dv_rating_beta"]].mean()
d = panel.set_index("soc").join(e, how="inner")
print(f"occupations matched: {len(d)} of {len(panel)}; workers covered: {d['emp_share'].sum():.0%}")

rk = lambda a, b: np.corrcoef(a.rank(), b.rank())[0, 1]
for col in ["human_rating_beta", "dv_rating_beta"]:
    print(f"Spearman({col}, v3 intensity) all occs = {rk(d[col], d['int_v3']):.2f}; "
          f"among occs with any usage = {rk(d.loc[d.v3>0, col], d.loc[d.v3>0, 'int_v3']):.2f}")

# employment-weighted quintiles of predicted exposure -> observed intensity
d = d.sort_values("human_rating_beta")
w = d["emp_share"] / d["emp_share"].sum()
d["q"] = np.minimum(((w.cumsum() - w / 2) // 0.2 + 1), 5).astype(int)
g = d.groupby("q").agg(workers=("emp_share", "sum"), exposure_lo=("human_rating_beta", "min"),
                       exposure_hi=("human_rating_beta", "max"), usage=("v3", "sum"),
                       zero_usage_occs=("v3", lambda s: (s == 0).mean()))
g["intensity"] = (g["usage"] / g["usage"].sum()) / (g["workers"] / g["workers"].sum())
print("\nObserved v3 intensity by quintile of predicted exposure (employment-weighted):\n", g.round(3).to_string())
g.round(4).to_csv(f"{out}/intensity_by_predicted_exposure.csv")

# biggest disagreements: highly exposed on paper, large workforce, little or no observed usage
hi = d[(d["human_rating_beta"] >= d["human_rating_beta"].quantile(0.8))]
gap = hi.sort_values(["int_v3", "emp"], ascending=[True, False]).head(15)
print("\nHigh predicted exposure (top 20% of occs), lowest observed intensity:\n",
      gap[["OCC_TITLE", "emp", "wage", "human_rating_beta", "int_v3"]].round(2).to_string())
lo = d[(d["human_rating_beta"] <= d["human_rating_beta"].quantile(0.4))].sort_values("int_v3", ascending=False).head(10)
print("\nLow predicted exposure (bottom 40%), highest observed intensity:\n",
      lo[["OCC_TITLE", "emp", "wage", "human_rating_beta", "int_v3"]].round(2).to_string())
gap.round(4).to_csv(f"{out}/exposed_but_unused.csv"); lo.round(4).to_csv(f"{out}/unexposed_but_used.csv")
