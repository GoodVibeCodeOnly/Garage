# Three one-page proposals

Each proposal is meant to fit about one printed page. The budgets assume a self-funded independent researcher (plus about $50–200 of LLM API spend where noted), not the fellowship's compute budget.

---

## Proposal A: Exposed on paper, absent in practice: auditing the gap between predicted and observed AI use across US occupations

**Question.** Economists ranked occupations by *predicted* exposure to language models before usage data existed. The Anthropic Economic Index now gives *observed* usage. Where do the two disagree, among occupations large enough to matter, and is each disagreement a measurement artifact, a real adoption gap, or an error in the exposure scores?

**Why it matters.** Retraining budgets, forecasts and public anxiety are all still allocated by predicted exposure. Suppose 1M-worker occupations such as service sales representatives or medical secretaries are "highly exposed" but show almost no use. Then one of the following holds, and each has a different policy implication:
- the forecasts are wrong
- adoption is blocked (by regulation, workflow or employer tools)
- the measurement of usage is leaking

**Data.** All public:
- AEI releases ([Hugging Face](https://huggingface.co/datasets/Anthropic/EconomicIndex))
- O\*NET task statements and the 2010→2019 crosswalk
- BLS OEWS May 2024
- Eloundou et al. exposure ([GitHub](https://github.com/openai/GPTs-are-GPTs))
- Felten et al. AIOE
- for external validation: Census BTOS sector AI-use rates

**Method.**
1. Rebuild the occupation panel from original files, a hardened version of the existing first pass, and print a coverage check at every merge.
2. Compute usage intensity with empirical-Bayes shrinkage so tiny occupations can't dominate.
3. Rank disagreements, weighted by employment.
4. Hand-audit the top 20 in each direction. For each, read the O\*NET tasks, search AEI for near-duplicate task text in other occupations, and check BTOS or other adoption evidence.
5. Classify each as artifact, adoption gap or score error, with written evidence.
6. Repeat across three or more AEI releases to see which gaps are closing.

**What a good small result looks like.** A 10–15 page paper with:
- one wage-gradient figure
- one disagreement table with audit verdicts
- a short "lessons for users of the AEI" section on task-matching artifacts
- all code public

Even "most big gaps are artifacts" is a useful, publishable correction.

**What would prove it wrong.** If the audit finds no systematic pattern (gaps are random noise of the task classifier), the paper becomes a methods note on the error bounds of occupation-level AEI estimates. That's a smaller but still honest output.

**Feasibility.** The first pass already exists (`04_first_pass_writeup.md`). It's about 4–6 weeks part-time, needs no money, and pandas skill is enough.

---

## Proposal B: The entry-level squeeze, on public data

**Question.** Since ChatGPT's release (Nov 2022), have workers aged 22–27 lost employment share *relative to older workers in the same occupation* more in occupations with high observed AI usage than in low-usage ones?

**Why it matters.** Brynjolfsson, Chandar & Chen (2025) reported exactly this pattern in private ADP payroll data. Public data can't easily check that. If the pattern is real, early-career ladders are breaking first, and the fix is training pathways and apprenticeship policy rather than unemployment insurance. If it doesn't replicate on public data, the debate needs to know that too.

**Data.**
- CPS monthly basic microdata 2018–2026 via [IPUMS-CPS](https://cps.ipums.org/cps/) (free): age, occupation, employment, weights
- AEI usage intensity by occupation, from Proposal A's pipeline
- OEWS for occupation size
- comparison sources: [NY Fed recent-grad series](https://www.newyorkfed.org/research/college-labor-market); Yale Budget Lab's monthly labor-market tracker ([budgetlab.yale.edu](https://budgetlab.yale.edu/) ⚠)

**Method.**
1. Map CPS occupation codes to SOC using IPUMS/Census crosswalks.
2. Split occupations into usage terciles.
3. Run an event-study DiD:
   - outcome: young-worker share of employment in an occupation-month (or young employment counts)
   - treatment: high-usage × post-Nov 2022
   - fixed effects: occupation and month
   - standard errors: clustered by occupation
4. Pre-register the specification in the repo before looking at post-2022 data.
5. Run robustness checks:
   - drop software occupations, to separate the 2022 tech bust
   - use predicted instead of observed exposure
   - use a placebo "treatment" date in 2019

**What a good small result looks like.** One event-study figure with honest bands, and a pre-registered headline coefficient. It should also say clearly whether it agrees with the ADP results, and why it might not (CPS sample size within occupation × age cells is small).

**What would prove it wrong.** Any of these would refute the AI explanation:
- the high- and low-usage groups were already diverging before 2022
- the effect disappears once software and IT are dropped
- the effect is equal in size in low-usage occupations, which would point to interest rates or the hiring cycle

Say so plainly if that happens.

**Risks.** CPS cells are noisy. Expect wide intervals; a carefully bounded "can't tell" is a legitimate result. It's the most statistically demanding of the three proposals, and a good reason to learn fixed-effects regression properly (statsmodels / linearmodels).

**Feasibility.** 6–8 weeks part-time and free. IPUMS extracts are straightforward.

---

## Proposal C: How AI law spreads: diffusion of state AI legislation, 2019–2026

**Question.** Which US states pass AI laws, of which kind, and in what order? Is diffusion driven by neighbours, partisan networks, the local tech industry, or copying of template bills?

**Why it matters.** With no comprehensive federal statute, the state patchwork *is* US AI policy for businesses and workers. The mechanism of spread matters:
- model-bill copying means a few drafters shape national policy
- neighbour effects mean regional blocs
- industry presence means lobbying shapes outcomes

Policy diffusion is a well-established research tradition (Walker 1969; Berry & Berry 1990), so this has a strong theoretical base and plays directly to a history and economics background.

**Data.**
- [LegiScan](https://legiscan.com/datasets) bulk bill data and texts (free with registration)
- [NCSL AI legislation summaries](https://www.ncsl.org/technology-and-communication/artificial-intelligence-2025-legislation) ⚠ for hand-validation of bill type
- state covariates:
  - QCEW tech-sector employment
  - partisan control (NCSL)
  - legislature professionalism (Squire index)
  - adjacency matrix

**Method.**
1. Identify AI bills by keyword plus hand review, and code them by type: deepfakes/elections, employment and automated decisions, government use, frontier-model safety, and other.
2. Run a discrete-time event-history model of first enactment, by type, with a neighbour-adoption term and the covariates above.
3. Compute bill-text similarity (TF-IDF cosine or MinHash) to detect template families and trace each family to its first appearance.
4. Validate the type classification on a hand-coded random sample of 100 bills.

**What a good small result looks like.**
- A clean, public, typed dataset of state AI bills, which is useful to others in itself
- a map and timeline
- a hazard-model table
- a list of template families with their origin

**What would prove it wrong.** If enactment is explained by session length, calendar and bill volume alone (states that pass many bills pass AI bills too), the "diffusion" story fails and the honest finding is "AI law spreads like any other law."

**Feasibility.** 6–8 weeks part-time and free. The text work is introductory NLP, which is a good stretch for Python skills. Unlike A and B it isn't built on Anthropic data, which is a minus for fit with this track. Its policy focus is a plus.
