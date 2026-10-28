> Historical handoff: implementation and metrics below predate the shared-model revision. For current commands, route semantics, study protocol, and validated results, use `prototype/README.md`, `prototype/study/README.md`, and `midterm/review/rubric-review.md`.

# BridgeFinder: Project Handoff & Contributor Guide

**Project Name:** BridgeFinder: A Social Network Brokerage Recommender for Campus Research Collaborations  
**Course:** CS 470 (Network Science, University of Illinois Urbana-Champaign)  
**Team Members:** Evan Lin (`elin26@illinois.edu`) & Eric Liu (`ericl8@illinois.edu`)  
**Active Git Branch:** `claude/modest-gauss-q759kv`  
**GitHub Repository:** [evanlin23/cs470](https://github.com/evanlin23/cs470)

---

## 1. Project Overview & Core Concept

Most academic collaboration recommenders rely on **homophily and triadic closure** (recommending researchers in the same immediate department or mutual co-author circles). While this predicts frequent ties, it reinforces academic echo chambers.

BridgeFinder instead operationalizes **Ronald Burt's theory of Structural Holes and Social Network Brokerage**:
1. **Target Audience:** Undergraduate and graduate students who enjoyed a class or work in one domain (e.g., CS/NLP) and want to apply their skills to another domain (e.g., Agronomy or Bioengineering).
2. **Brokerage Score Formulation:**
   $$\text{Score}(u, v) = \alpha \cdot S_{\text{topic}}(u,v) + \beta \cdot H(v) + \gamma \cdot \text{BSI}(u,v) + \lambda \cdot P(u,v)$$
   - $S_{\text{topic}}(u,v)$: Jaccard similarity between pre-2020 topic profiles.
   - $H(v) = \max(0, 1 - C_v)$: Burt's autonomy metric ($C_v$ is network constraint).
   - $\text{BSI}(u,v) = \frac{|\text{ext}(v)|}{\text{deg}(v)}$: Boundary-spanning index measuring cross-community connectivity.
   - $P(u,v)$: Introduction path bonus ($0.5$ if $d(u,v) = 2$, $0.1$ if $d(u,v) \ge 3$ with path).
3. **Core Hypothesis:** BridgeFinder predicts and surfaces high-value cross-community collaborations better than standard topological link predictors and topic-only baselines, providing actionable introduction paths through trusted campus faculty.

---

## 2. Repository Directory Structure

```
cs470/
├── proposal/                      # Submitted ACM 2-page project proposal
│   ├── latex/                     # LaTeX source (main.tex, figure/flow.tex, references.bib)
│   └── proposal.pdf               # Compiled proposal PDF (2 pages)
│
├── midterm/                       # Midterm milestone submission
│   ├── latex/                     # LaTeX source (main.tex, main.pdf)
│   └── midterm.pdf                # Compiled 5-page midterm report
│
├── prototype/                     # Core computational & evaluation pipeline
│   ├── fetch_openalex.py          # Polite-pool OpenAlex harvester (UIUC works 2015-2024)
│   ├── backtest.py                # Temporal link prediction backtest (2015-19 train -> 2020-24 test)
│   ├── citation_impact.py         # Burt's citation hypothesis test (cross vs within community)
│   ├── run_experiment.sh          # One-click harvest & backtest script
│   │
│   ├── uiuc_data.json             # 5,000-work dataset (2,493 papers, 3,642 authors, 183 seeds)
│   ├── uiuc_data_scaled.json      # 25,000-work dataset (13,229 papers, 9,042 authors, 1,379 seeds)
│   │
│   ├── results/                   # Evaluation output logs
│   │   ├── backtest_results.json        # 5k backtest metrics
│   │   ├── backtest_results_scaled.json # 25k backtest metrics
│   │   └── citation_impact.json         # Citation analysis results & Mann-Whitney p-values
│   │
│   ├── web/                       # Interactive D3.js campus exploration tool
│   │   ├── index.html             # Standalone 3-screen frontend (Seed Selector, D3 Map, Researcher Cards)
│   │   ├── prepare_web_data.py    # Extracts top communities, bridges, and paths into JSON
│   │   └── data.json              # D3-ready graph payload
│   │
│   └── study/                     # Double-blind human study suite
│       ├── generate_cards.py      # Generates 15 shuffled cards per seed across 5 departments
│       ├── index.html             # Participant rating interface (7-point Likert + 10-item SUS)
│       ├── study_cards.json       # Shuffled candidate researcher cards (unlabeled)
│       ├── truth_keys.json        # Model mapping for ground truth analysis
│       └── analyze_study.py       # Participant-level paired t-test & Wilcoxon analyzer
│
└── docs/                          # Architecture notes and initial idea drafts
```

---

## 3. Key Findings & Empirical Results

### A. Temporal Backtest (2015–2019 Train $\to$ 2020–2024 Test)
All author topic profiles are computed **strictly from pre-2020 publications** to prevent future collaboration data leakage.

| Model | P@5 (5k) | NDCG@10 (5k) | P@5 (25k) | NDCG@10 (25k) |
|---|---|---|---|---|
| Preferential Attachment | 0.0011 | 0.0011 | 0.0081 | 0.0125 |
| Global Betweenness | 0.0022 | 0.0192 | 0.0076 | 0.0109 |
| Topic-Only Baseline | 0.0076 | 0.0342 | 0.0201 | 0.0406 |
| Triadic Closure (Adamic-Adar) | 0.0076 | 0.0279 | 0.0283 | 0.0459 |
| **BridgeFinder (Proposal Topic+Path)** | **0.0216** | **0.0697** | **0.0333** | **0.0630** |
| **BridgeFinder (Full Score)** | **0.0195** | **0.0671** | **0.0364** | **0.0705** |

*Takeaway:* BridgeFinder outperforms all topology-only baselines and Topic-Only when temporal leakage is removed, proving that structural introduction paths provide real predictive signal.

### B. Burt's Citation Impact Hypothesis
Evaluated on 6,231 post-2020 UIUC evaluation papers:
- **Cross-Community Papers:** $N = 1,071$, Mean = 64.86 citations ($\sigma = 241.34$), Median = 36.0.
- **Within-Community Papers:** $N = 4,183$, Mean = 61.60 citations ($\sigma = 119.92$), Median = 37.0.
- **Impact Ratio:** $1.053\times$ (earlier 5k sample was $1.128\times$).
- **Mann-Whitney U Test:** $p = 0.0601$ (not statistically significant at $\alpha = 0.05$).
- *Takeaway:* Cross-community papers have higher variance and a higher mean, but the null hypothesis cannot be rejected; this is reported candidly as an inconclusive result in the paper.

### C. Formative Usability (Round 1 Feedback, $N=5$)
Think-aloud student interviews produced 3 UI/algorithmic improvements:
1. **Screen 1:** Added 50 curated faculty seed profiles to prevent cold-start paralysis.
2. **Screen 2:** D3 graph explicitly colors dashed orange arcs as "Structural Holes (High Topic Overlap, No Direct Tie)".
3. **Screen 3:** Moved the 4-node introduction path to the very top of each researcher card for immediate outreach context.

---

## 4. How to Run Everything

### Prerequisites
```bash
pip install networkx scipy
# For compiling LaTeX:
brew install tectonic # or use pdflatex
```

### 1. Run the Backtest Pipeline
```bash
# To run on the scaled 25k dataset:
python3 prototype/backtest.py --data prototype/uiuc_data_scaled.json --out prototype/results/backtest_results_scaled.json

# Or run the quick test (5k dataset):
python3 prototype/backtest.py --data prototype/uiuc_data.json --out prototype/results/backtest_results.json
```

### 2. Run the Citation Impact Test
```bash
python3 prototype/citation_impact.py --data prototype/uiuc_data_scaled.json --out prototype/results/citation_impact.json
```

### 3. Launch the Interactive D3 Campus Map
```bash
cd prototype/web
python3 -m http.server 8000
# Open http://localhost:8000 in your browser
```
*(To re-generate `prototype/web/data.json` from the scaled graph: `python3 prototype/web/prepare_web_data.py --data prototype/uiuc_data_scaled.json --out prototype/web/data.json`)*

### 4. Launch the Double-Blind User Study
```bash
# Step 1: Regenerate study cards if needed (already pre-generated)
python3 prototype/study/generate_cards.py --data prototype/uiuc_data_scaled.json --out prototype/study/study_cards.json

# Step 2: Serve the study interface
cd prototype/study
python3 -m http.server 8001
# Open http://localhost:8001 in your browser
```
Participants rate 15 cards, fill out the SUS usability questions, and click **"Export Responses (JSON)"**.

### 5. Analyze Study Responses
Once participant responses are collected into `prototype/study/study_responses.json`:
```bash
python3 prototype/study/analyze_study.py \
  --responses prototype/study/study_responses.json \
  --keys prototype/study/truth_keys.json \
  --out prototype/study/study_analysis_results.json
```
*(Note: Per academic integrity guidelines, no mock responses are committed; run this once real participants complete the study).*

### 6. Compile Reports to PDF
```bash
# Midterm Report (exactly 5 pages):
cd midterm/latex && tectonic main.tex && cp main.pdf ../midterm.pdf && cd ../..

# Project Proposal (2 pages):
cd proposal/latex && tectonic main.tex && cp main.pdf ../proposal.pdf && cd ../..
```

---

## 5. Upcoming Milestones & Tasks (Nov 1 – Dec 9)

| Window | Milestone | Action Items |
|---|---|---|
| **Nov 1 – Nov 15** | **User Study Round 2 ($N=15$)** | • Recruit 15 UIUC students across CS, ECE, Bioengineering, Crop Sciences, and iSchool.<br>• Have them complete the study on `http://localhost:8001`.<br>• Save responses and run `analyze_study.py` to calculate paired $t$-tests and Wilcoxon signed-rank statistics ($df = 14$). |
| **Nov 16 – Nov 29** | **Model & UI Iteration (Round 3)** | • Grid search optimal $(\alpha, \beta, \gamma, \lambda)$ weights on the backtest.<br>• Evaluate whether increasing the path weight $\lambda$ boosts novelty ratings.<br>• Tweak D3 force simulation performance on larger community clusters. |
| **Dec 1 – Dec 9** | **Final Deliverables** | • Port midterm content into the official 10–12 page ACM `acmart` template.<br>• Record and edit the 10-minute final demonstration video.<br>• Deliver final code snapshot and presentation. |

---

## 6. Git Hygiene & Branch Notes
- **Branch:** Always branch or commit from `claude/modest-gauss-q759kv`.
- **Large Files:** Raw API dump files `prototype/uiuc_raw_works*.json` exceed 100MB and are intentionally excluded in `.gitignore`. The processed graphs `uiuc_data.json` (3.5MB) and `uiuc_data_scaled.json` (14.5MB) are safely tracked in git.
- **Clean Tree:** All changes are fully staged, committed, and pushed to remote.
