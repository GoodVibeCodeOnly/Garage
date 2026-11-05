# First pass: who actually uses Claude, by wage, and does it match predicted "exposure"?

*Working draft, 5 Nov 2026. This is one evening's analysis, not a finding. Code: `analysis/wage_gradient.py`, `analysis/observed_vs_predicted.py`. Outputs: `analysis/out/`.*

## Question
Proposal A in `03_proposals.md` asks where observed AI usage falls across the US wage distribution, whether that pattern holds across data releases, and how it compares with the exposure scores economists predicted before usage data existed. This pass does the descriptive groundwork for that.

## Data, and how it was obtained (read this first)
The sandbox couldn't reach huggingface.co, bls.gov or onetcenter.org because the network policy blocked them. I used a **public mirror** instead: the Yale Budget Lab's repo [`Budget-Lab-Yale/AI-Employment-Model`](https://github.com/Budget-Lab-Yale/AI-Employment-Model) (`resources/`). It holds:

- **AEI task shares for three releases.** Files `onet_task_mappings.csv` ("v1"), `automation_vs_augmentation_by_task_v2.csv` ("v2") and `automation_vs_augmentation_by_task_v3.csv` ("v3"). The originals are on [huggingface.co/datasets/Anthropic/EconomicIndex](https://huggingface.co/datasets/Anthropic/EconomicIndex). **Unverified:** I'm inferring that these are byte-identical to Anthropic's releases, and which release dates v1, v2 and v3 match, from the file names. Before this is used for anything real, re-download from Hugging Face and diff.
- **O\*NET task statements** and the O\*NET 2010→2019 crosswalk.
- **BLS OEWS May 2024 national file** (`national_M2024_dl.csv`). The original is at [bls.gov/oes/tables.htm](https://www.bls.gov/oes/tables.htm).

Predicted exposure comes from Eloundou, Manning, Mishkin & Rock, "GPTs are GPTs" (2023), file `data/occ_level.csv` in [github.com/openai/GPTs-are-GPTs](https://github.com/openai/GPTs-are-GPTs). I used `human_rating_beta` and `dv_rating_beta`.

## Method
1. Match each AEI task (lower-cased text) to O\*NET task statements. Where the same text belongs to several occupations, split its usage share equally among them.
2. Sum to 6-digit SOC and join to OEWS detailed occupations (employment and median annual wage). For hourly-only occupations, wage = hourly median × 2080. Top-coded wages are set to $239,200.
3. **Usage intensity** = an occupation's share of usage ÷ its share of employment. A value of 1 means usage is proportional to headcount.
4. Group workers into employment-weighted wage deciles and wage bands. Bootstrap over occupations, 500 draws, for a rough 90% band.
5. Compare with predicted exposure using Spearman rank correlations and employment-weighted exposure quintiles.

## What came out (v3 unless stated)

**1. Usage is steeply concentrated in upper-middle wages and falls back above about $150k.**

| Median wage band | Share of workers | Share of usage | Intensity |
|---|---|---|---|
| ≤ $40k | 31% | 3% | 0.10 |
| $40–60k | 29% | 14% | 0.48 |
| $60–80k | 19% | 24% | 1.27 |
| $80–103k | 12% | 23% | 1.87 |
| $103–125k | 3% | 12% | 3.7 |
| $125–150k | 3% | 23% | 7.2 (mostly Software Developers) |
| $150–200k | 2% | 1.4% | 0.68 |
| $200k+ | 0.8% | 0.6% | 0.78 |

The bottom three wage deciles together hold about 30% of workers and about 3% of usage. Their bootstrap bands sit well below 1 (`out/v3_intensity_bootstrap.csv`). The fall-off at the top is mostly physicians, dentists and pilots. These are high-wage jobs that are hands-on or regulated. This matches what I remember of Anthropic's own first Economic Index report (Feb 2025), which said usage peaks in the upper-middle wage range and is lower at both ends. **I haven't re-checked that against the paper.** So this result is *consistent with* existing work, not new.

**2. The pattern is stable across releases.** The occupation-share rank correlation is 0.89 for v1 vs v2, 0.95 for v2 vs v3 and 0.87 for v1 vs v3. The wage–intensity rank correlation among used occupations is 0.32–0.34 in every release. Software Developers' share rose from 8.7% to 13.7% to 15.1%.

**3. Observed usage tracks predicted exposure, but loosely.** The Spearman correlation between predicted exposure and observed intensity is 0.63 across all occupations and 0.47 among occupations with any usage. Here is observed intensity by quintile of predicted exposure:

| Quintile | Intensity |
|---|---|
| Q1 | 0.05 |
| Q2 | 0.20 |
| Q3 | 0.33 |
| Q4 | 1.64 |
| Q5 | 2.79 |

So the ordering is right. The interesting part is the disagreements (`out/exposed_but_unused.csv`):

- Sales representatives of services (1.2M workers) show **zero** observed usage despite high predicted exposure.
- Medical secretaries (0.83M), receptionists (0.96M), management analysts (0.89M) and training specialists (0.44M) all have intensity at or below 0.16.

## What is probably wrong or fragile (I'd want a reviewer to push here)
- **Zeros are not reliable.** About 31% of occupations, holding about 20% of workers, have zero matched usage. An occupation can be heavily used and still show zero because Anthropic's classifier assigned the conversations to a near-duplicate task statement in a *different* occupation. I found a live example of this kind of failure in my own pipeline (next bullet).
- **I nearly published a pipeline bug.** In the mirror's O\*NET file, 4,253 task rows have a blank occupation code, including every "Accountants" and "Software Developers" task. In the first run those rows dropped out silently. Accountants (1.45M workers) showed zero usage, and Software Developers were missing entirely. Recovering the codes by exact title through the official crosswalk fixed it, and the run log now prints the count. The headline wage gradient survived the fix, and the correlation with predicted exposure rose from 0.49 to 0.63. The lesson is that every merge in this kind of work needs a coverage check printed beside it.
- **Tiny occupations produce absurd intensities.** For example, "Mathematical Science Occupations, All Other" scores 1,600× and "Timing Device Assemblers" 54×. One matched task divided by a few hundred workers gives a huge ratio. Any occupation-level ranking needs shrinkage or a minimum employment. The decile and band results are weighted and much less affected.
- **About 4–5% of v2/v3 usage mass doesn't map to an occupation.** I haven't diagnosed why.
- **"Directive" (automation-like) share fell between v2 and v3 in my numbers, in every decile but one** (`out/directive_by_decile.csv`). From memory, Anthropic's Sept 2025 report described directive use *rising* over time. I haven't verified that, and the gap is most likely a version or definition mismatch: my denominator includes the "filtered" category. **Don't cite this number.**
- **Claude.ai users are not a random sample of workers.** Usage share measures where *Claude* conversations go. It doesn't measure where AI adoption in general goes, or effects on jobs. Nothing here is causal.

## Null or not?
On the descriptive question, the result isn't null. The wage gradient and the "fall-off at the top" are clear, and they're stable across three releases. On novelty it's close to null, because it mostly replicates what Anthropic and others have already published. The part that could become original work is the **disagreement list**: large, highly exposed occupations with near-zero observed usage. Is that a measurement artifact, a real adoption gap, or a sign the exposure scores were wrong? That's the next step:

1. Re-pull the originals from Hugging Face and diff them against the mirror.
2. Hand-audit 20 "exposed but unused" occupations: read their O\*NET tasks and look for near-duplicate tasks elsewhere that are soaking up their usage.
3. Bring in a second, independent adoption measure to see whether the gap is real. Options are the Census BTOS AI-use question by sector, or the CPS/Pew worker-reported AI use questions.

## Reproduce
```bash
git clone --depth 1 https://github.com/Budget-Lab-Yale/AI-Employment-Model.git yale
```
```bash
git clone --depth 1 https://github.com/openai/GPTs-are-GPTs.git gpts
```
```bash
cd fellows-prep/analysis && python3 -I wage_gradient.py ../../yale/resources out && python3 -I observed_vs_predicted.py ../../gpts/data/occ_level.csv out
```
Requires pandas and numpy only. Data snapshot: mirror HEAD as cloned on 5 Nov 2026.
