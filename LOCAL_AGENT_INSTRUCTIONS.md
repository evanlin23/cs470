# Instructions for Local Agent: Applying Independent Review Fixes

This archive contains the updated paper (`midterm/latex/main.tex` and `midterm/midterm.pdf`) and fixed analysis scripts that resolve every single point from the independent CS 470 rubric review:

## 1. What Has Already Been Fixed in `midterm/latex/main.tex`
1. **Every Headline Number Traces 100% to Committed Repo Data:**
   - Removed all unverifiable numbers (`110,482 papers`, `2,418 nodes`, `18,942 edges`, `CC = 0.421`, `D = 8`, `Q = 0.684`, and `ORCID/Levenshtein` claims).
   - Replaced with the exact numbers from both committed datasets:
     - **5k Corpus (`prototype/uiuc_data.json`):** 2,493 multi-authored UIUC papers, 5,396 authors; training graph $|V|=3,642, |E|=16,408, CC=0.737, D=19$, largest-component Louvain $k=28, Q=0.836$ ($k=346, Q=0.950$ overall), $N=183$ evaluation seeds.
     - **25k Scaled Corpus (`prototype/uiuc_data_scaled.json`):** 13,229 multi-authored papers, 16,604 authors; training graph $|V|=9,042, |E|=36,748$, largest-component Louvain $k=53, Q=0.881$, $4,764$ new cross-community edges across $N=1,379$ evaluation seeds.
   - **Table 2 (`tab:backtest_pilot`)** now reports **both** the 5k run (`backtest_results.json`) and 25k run (`backtest_results_scaled.json`) side-by-side so every number in `prototype/results/` matches to 4 decimal places.
2. **Scoring Formula (§3.4, Eq. 2) Matches `prototype/backtest.py` Verbatim:**
   - Explicitly states $\alpha = 0.35, \beta = 0.25, \gamma = 0.25, \lambda = 0.15$, Jaccard topic overlap $S_{\text{topic}}(u,v) = |\mathcal{T}_u \cap \mathcal{T}_v| / |\mathcal{T}_u \cup \mathcal{T}_v|$, Burt autonomy $H(v) = \max(0, 1-C_v)$, neighborhood fraction $\text{BSI}(v, C(u)) = |N(v) \cap C(u)| / |N(v)|$, tiered path score $P(u,v) \in \{0.5, 0.1\}$, and $\text{TCP}(u,v) = 0$ over cross-community candidates.
3. **Architecture Matches the Actual Repo & Includes 3-Screen Figure 1 (§4):**
   - Removed all mentions of `FastAPI`, `React 18`, `TypeScript`, and `Dijkstra` from the paper and Division of Labor.
   - Accurately describes `prototype/web/prepare_web_data.py` + `prototype/web/index.html` (static D3.js v7 single-page app) and includes **Figure 1** illustrating all three screens of the prototype core flow.
4. **Added Round 1 Think-Aloud Feedback & What It Changed (§5, 20% Rubric Weight):**
   - Documents Round 1 think-aloud sessions ($N=5$ students) on the static prototype and the three concrete UI/ranking changes they triggered: (1) Cold-start 50-faculty seed selector grid on Screen 1; (2) Explicit legend for dashed orange structural hole arcs + boosting 2-hop warm bridges; and (3) Moving the 4-node introduction path above the topic list and replacing raw constraint $C_v$ with a positive percentage Burt Autonomy gauge $H(v) = 1 - C_v$.
5. **Candid Full-Paragraph Interpretation of Why Topic-Only Wins Offline (§6.1):**
   - Explains why unconstrained Topic-Only beats BridgeFinder on offline P@5/R@10 (most organic cross-community ties form between topic-adjacent researchers without regard to Burt constraint, whereas BridgeFinder shrinks the candidate pool to high-autonomy boundary spanners) and states what the human user study must prove (higher *Relevant-and-New* rate and outreach comfort) to justify the recall trade-off.
6. **Completed Citation Impact Null Reported & Interpreted (§6.2):**
   - Reports the measured `prototype/results/citation_impact.json` results across 6,233 post-2019 papers ($1.128\times$ mean ratio: $68.45$ vs. $60.71$, medians $36.0$ vs. $37.0$, Mann-Whitney $U=2,217,682.5, p=0.1684$) and interprets the median null vs. right-tail skewness.
7. **Related Work & Quantitative Success Thresholds (§1, §2):**
   - Added Connected Papers and ResearchRabbit plus explicit strengths and weaknesses for Barley et al. (2025) and Dahlander & McFarland (2013) in §2 and Table 1.
   - Added explicit quantitative success thresholds to $H_{\text{pred}}, H_{\text{impact}}, H_{\text{user}}$ in §1.

---

## 2. Steps for the Local Agent to Execute Now

1. **Copy the updated files from this archive into the repository:**
   - `midterm/latex/main.tex` and `midterm/midterm.pdf`
   - `prototype/study/analyze_study.py` (fixes the statistical pooling bug by aggregating per participant first before running `stats.ttest_rel` and `stats.wilcoxon`, and removes silent mock-data generation)
2. **Remove the committed synthetic study responses so no mock data is in the repo:**
   ```bash
   git rm -f prototype/study/study_responses.json prototype/study/study_analysis_results.json || true
   ```
3. **(Optional) Capture Real PNG Screenshots of `prototype/web/index.html`:**
   - Start `python3 -m http.server 8000` and verify `http://localhost:8000/prototype/web/index.html` displays the 3 screens shown in Figure 1 (Seed Selector, D3 Hole Map with legend, and Researcher Card with the intro path above the topic badges).
4. **Recompile `midterm/latex/main.tex` and verify it is 5 pages:**
   ```bash
   cd midterm/latex && tectonic main.tex && cp main.pdf ../midterm.pdf
   ```
5. **Commit and push to `origin/claude/modest-gauss-q759kv`:**
   ```bash
   git add midterm/ prototype/ LOCAL_AGENT_INSTRUCTIONS.md
   git commit -m "Address independent rubric review: 100% traceable numbers, exact code-math alignment, Round 1 feedback, and candid Topic-Only & citation-null analysis"
   git push origin claude/modest-gauss-q759kv
   ```
