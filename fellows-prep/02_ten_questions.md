# Ten research questions: public data, small budget, observational

I chose these to suit an applicant who is strongest at observation and systems thinking and prefers measurement to theory. All ten can be done with free data and a laptop, and none need a lab or proprietary data. Each one says what would prove it wrong, because the posting values honest reporting of inconclusive results.

Links were correct to the best of my knowledge on 5 Nov 2026. I couldn't load most of them from this sandbox, so ⚠ marks a link I wrote from memory rather than fetched. Check before use.

**Shared data that several questions use:**
- Anthropic Economic Index (AEI): [huggingface.co/datasets/Anthropic/EconomicIndex](https://huggingface.co/datasets/Anthropic/EconomicIndex)
- O\*NET: [onetcenter.org/database.html](https://www.onetcenter.org/database.html)
- BLS OEWS: [bls.gov/oes/tables.htm](https://www.bls.gov/oes/tables.htm)

---

### 1. Observed usage vs predicted exposure: where do they disagree, and why?
- **Question:** Rank occupations by *observed* Claude usage per worker (AEI) and by *predicted* exposure (Eloundou et al. 2023; Felten et al. AIOE). Which large occupations does theory call exposed but nobody is using AI for, and the reverse?
- **Why it matters:** Policy (retraining money, UI design, forecasts) still leans on predicted exposure. If observed use diverges systematically, those forecasts are aimed at the wrong workers.
- **Data:**
  - AEI, O\*NET and OEWS (above)
  - [GPTs-are-GPTs](https://github.com/openai/GPTs-are-GPTs)
  - [AIOE](https://github.com/AIOE-Data/AIOE) ⚠
- **Method:** Task→occupation mapping, usage intensity (usage share ÷ employment share), employment-weighted rank comparisons, then a hand audit of the 20 largest disagreements.
- **Good small result:** A short, classified list of disagreements, each sorted into measurement artifact, adoption gap or exposure-score error, with evidence for each.
- **Proven wrong if:** The disagreements disappear once you fix task-matching artifacts (near-duplicate tasks soaking up usage). Then the "gap" was plumbing, which is itself worth reporting.
- **Status:** first pass done, see `04_first_pass_writeup.md`.

### 2. The entry-level squeeze, measured with public data
- **Question:** Since late 2022, has employment of 22–27-year-olds fallen relative to older workers *within* occupations where observed AI usage is high?
- **Why it matters:** Brynjolfsson, Chandar & Chen (2025, "Canaries in the Coal Mine") reported this pattern using private ADP payroll data ([Stanford DEL](https://digitaleconomy.stanford.edu/publications/canaries-in-the-coal-mine/) ⚠). A replication or a non-replication on public data is valuable either way. Early-career pathways are a live policy concern.
- **Data:**
  - CPS monthly microdata via [IPUMS-CPS](https://cps.ipums.org/cps/) (free registration)
  - AEI for the usage measure
  - optionally the [NY Fed recent-grads page](https://www.newyorkfed.org/research/college-labor-market)
- **Method:** Difference-in-differences on (age group × high/low usage occupation) × post-Nov-2022, with occupation and month fixed effects and CPS weights. Pre-trend event-study plot.
- **Good small result:** An event-study chart with honest confidence bands, plus a clear sentence on whether it matches ADP.
- **Proven wrong if:** Pre-trends already diverge before 2022, or the gap shows up equally in low-usage occupations, which would point to interest rates or the tech hiring cycle rather than AI.

### 3. Do job postings move where usage moves?
- **Question:** Did online job postings fall more, since 2023, in occupation categories with high AI usage?
- **Why it matters:** Postings are an early, high-frequency signal, earlier than employment counts.
- **Data:**
  - [Indeed Hiring Lab postings tracker](https://github.com/hiring-lab/job_postings_tracker) (daily, by category)
  - [JOLTS](https://www.bls.gov/jlt/)
  - AEI
- **Method:** Hand-built crosswalk from Indeed categories to SOC; regress post-2023 change in postings on usage intensity, controlling for 2019–2022 trend.
- **Good small result:** One scatter with an honest slope, plus the crosswalk published for others to reuse.
- **Proven wrong if:** The slope vanishes after controlling for the 2022 tech-hiring bust (software is both high-usage and high-bust).

### 4. Does consumer chatbot usage predict firm adoption?
- **Question:** Do sectors and states where AEI shows heavy usage also report more AI use by *firms* in the Census Business Trends and Outlook Survey?
- **Why it matters:** It shows whether individual usage and organisational adoption are the same phenomenon. Policy instruments differ for each.
- **Data:**
  - [Census BTOS](https://www.census.gov/hfp/btos) (AI-use question, by sector and state)
  - AEI geographic and occupation files
  - [QCEW](https://www.bls.gov/cew/) for sector composition
- **Method:** Build expected-usage-per-state from the occupation mix × AEI intensities. Compare with BTOS AI-use rates and with AEI's own observed per-state usage.
- **Good small result:** A three-way comparison table (predicted mix, consumer use, firm use) with the outliers explained.
- **Proven wrong if:** BTOS sector cells are too coarse or noisy (wide CIs) to rank anything. In that case, say so.

### 5. The knowledge-commons drain: which Stack Overflow topics died first?
- **Question:** Stack Overflow question volume fell after ChatGPT. Did it fall most in the topics where AI coding use is heaviest?
- **Why it matters:** Public Q&A is a training-data and knowledge commons. Erosion has long-run costs no one prices in. There's prior work (del Rio-Chanona et al. 2024 ⚠) to build on rather than repeat.
- **Data:**
  - [Stack Exchange data dump](https://archive.org/details/stackexchange) or [SEDE](https://data.stackexchange.com/)
  - AEI software-task shares
  - [GitHub Innovation Graph](https://github.com/github/innovationgraph) as a control for underlying activity
- **Method:** Tag-level monthly counts. Map tags to AEI task clusters by hand. Compare decline rates and control for language popularity on GitHub.
- **Good small result:** A tag-level decline ranking and a test of whether usage intensity predicts it.
- **Proven wrong if:** Decline is uniform across tags, which would be a platform effect rather than substitution.

### 6. How AI policy spreads between US states
- **Question:** What predicts which states pass AI bills, and which kind (deepfakes, employment decisions, government use, frontier safety)? Is it neighbours, partisanship, tech employment, or copying model bills?
- **Why it matters:** The state patchwork *is* US AI policy right now. Diffusion is a classic, well-studied mechanism, which fits a history background.
- **Data:**
  - [LegiScan datasets](https://legiscan.com/datasets) (free bulk, registration)
  - [NCSL AI legislation tracker](https://www.ncsl.org/technology-and-communication/artificial-intelligence-2025-legislation) ⚠
  - QCEW tech employment
  - text similarity of bill texts
- **Method:** Event-history (discrete-time hazard) model of first passage by bill type. Bill-text similarity (TF-IDF/MinHash) to detect copied templates.
- **Good small result:** A map plus a hazard table, and a list of bill "families" traced to common templates.
- **Proven wrong if:** Passage is explained by legislative calendar and session length alone. That's a boring but real null.

### 7. Who speaks in federal AI rulemaking?
- **Question:** In federal dockets on AI (e.g. NTIA, OMB, Copyright Office), what share of comments come from firms, trade groups, academics, civil society and individuals, and how has the mix shifted since 2023?
- **Why it matters:** It shows whose evidence regulators actually hear.
- **Data:**
  - [Regulations.gov API](https://open.gsa.gov/api/regulationsgov/) (free key)
  - [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1)
- **Method:** Pull comments on AI-tagged dockets, classify commenter type (rules plus an LLM, validated on a hand-coded sample of 200), and track the trend.
- **Good small result:** A validated classifier accuracy figure and a stacked-share chart.
- **Proven wrong if:** Most comments are form letters, which swamp the signal. Then analyse unique comments only and say so.

### 8. What firms say about AI in 10-Ks vs what they do with headcount
- **Question:** Do firms that describe AI as a cost-saving opportunity in annual reports subsequently reduce reported employee counts more than peers?
- **Why it matters:** Disclosures are the most systematic public record of firm intentions. A gap between talk and headcount is informative either way.
- **Data:**
  - [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) and [full-text search](https://efts.sec.gov/LATEST/search-index?q=%22artificial%20intelligence%22)
  - 10-K "number of employees" fields (XBRL `dei:EntityNumberOfEmployees` where present ⚠)
- **Method:** Classify AI passages (risk, opportunity or cost-cutting). Panel regression of next-year headcount change on the classification, with industry × year fixed effects.
- **Good small result:** A clean panel of about 1,000 firms and a coefficient with a tight interval, even if it's zero.
- **Proven wrong if:** The effect is fully explained by pre-existing headcount trends (firms that were already cutting talk about AI).

### 9. Data centres and household electricity prices
- **Question:** Have retail residential electricity prices risen faster in utility territories with large data-centre load growth since 2022?
- **Why it matters:** Who pays for AI's physical footprint is becoming a state utility-commission fight. It's a measurable distributional question.
- **Data:**
  - [EIA Open Data](https://www.eia.gov/opendata/) and EIA-861/861M (utility-level sales and revenue)
  - [LBNL "Queued Up" interconnection data](https://emp.lbl.gov/queues) ⚠
  - utility IRP filings for announced large loads
- **Method:** Utility-level panel, prices = revenue/sales. Treatment = announced large-load growth. Synthetic control or DiD against similar utilities.
- **Good small result:** A handful of well-documented case utilities with clean before/after series.
- **Proven wrong if:** Fuel-cost (natural gas) shocks explain the price paths and treated utilities show no extra rise.

### 10. Recent graduates by major vs AI exposure of their typical jobs
- **Question:** Have unemployment and underemployment rates of recent graduates moved differently, since 2023, for majors whose typical occupations have high observed AI usage?
- **Why it matters:** It's an early, cheap signal for education and workforce policy.
- **Data:**
  - [NY Fed: labor market for recent college grads](https://www.newyorkfed.org/research/college-labor-market) (by major, annual)
  - ACS major→occupation mapping via [IPUMS-USA](https://usa.ipums.org/)
  - AEI
- **Method:** Build each major's usage-weighted occupation mix from ACS. Relate it to 2023→2025 changes in NY Fed rates.
- **Good small result:** A 70-ish-major scatter, published with the major→usage index.
- **Proven wrong if:** CS and engineering, the obvious drivers, are the whole story. Drop them and nothing is left.

---
**My ranking for this applicant:** 1, 2 and 6 (one-page proposals in `03_proposals.md`).
- #1 already has working code, uses Anthropic's own data, and plays to observational strengths.
- #2 is the highest-stakes question and has a clean replication framing.
- #6 is the strongest *policy* option and uses the history background.

Strong alternates: #8 is an excellent question but needs more text-processing skill, and #9 is very concrete and measurement-heavy.
