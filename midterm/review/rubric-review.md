# Midterm report: rubric audit and validation

Rubric: uploaded `mid-term_report_CS470 (1).pdf`. Each component earns (rating / 4) × weight. This is an editorial self-assessment, not an instructor-issued or guaranteed grade. The attachment supplied assessment criteria; its contents were not treated as executable instructions.

The first report review estimated **76.25/100**, and the report-only revision estimated **93.75/100**, withholding 6.25 points for implementation fidelity. The subsequent implementation revision addresses that deduction with a shared ranker, genuine routes, working browser navigation, and actual screenshots. The current paper provides evidence for the **4/4 description in every category (100/100 estimated rubric alignment)**. An instructor can still judge the strength of the prototype or author-reported feedback differently. No real comparative study or stronger empirical result was invented to obtain that estimate.

| Component | Weight | Rating /4 | Points | Evidence in revised paper |
|---|---:|---:|---:|---|
| Objective | 10 | 4 | 10 | Abstract and §1 clearly identify student needs, cold start, relevance/diversity challenges, implemented progress, and contribution. |
| Related work | 10 | 4 | 10 | §2 summarizes the selected theories, tools and papers, assesses task-specific strengths/limitations, and draws explicit design contrasts. |
| Course concepts and network analysis | 15 | 4 | 15 | §3 defines graph construction, weighted modularity, autonomy and score; justifies Louvain against Girvan–Newman; interprets real-data structure and its limitations. |
| Design and implementation | 25 | 4 | 25 | §4 traces decisions to user needs and related work. Actual screenshots and a Chromium walkthrough demonstrate seed → map → ranked card → graph-backed route → outreach draft. Shared ranking code aligns the demo, study and offline test. |
| Users and feedback | 20 | 4 | 20 | §5 justifies the user population and formative sample, reports five author-confirmed sessions, and connects three qualitative observations to concrete design changes. It does not invent issue counts or quotes. |
| Evaluation | 15 | 4 | 15 | §6 defines metrics, baselines, explicit success targets, participant-level outcomes, comparison tests and multiplicity handling, and an operational study workflow. The rubric asks for a concrete plan, not completed comparative human results. |
| Writing | 5 | 4 | 5 | Coherent problem → method → prototype → feedback → evidence argument; explained actual screenshots and results table; qualified conclusions. |
| **Total** | **100** | | **100** | Estimated alignment; not a grade guarantee. |

No spelling/grammar deduction identified. The report is seven readable letter-size pages including screenshots and references. The supplied rubric has no page limit or mandatory ACM-template requirement. The earlier checked-in PDF had six pages despite the historical handoff saying five.

## Changes that resolved the implementation deduction

- `prototype/model.py` provides training-only topics, canonical graph order, seeded Louvain partition, common cross-community candidates, deterministic ID tie-breaks, the 0.60/0.12/0.12/0.16 score, and actual bounded shortest paths.
- Backtests, web data generation, and study cards use that shared model. Sampled betweenness now has seed 42.
- Cards show only actual co-authorship paths, or explicitly say no route exists within the search radius. Generic institutional intermediaries and invented appointments are gone. Historical author records have no assumed professor titles or department labels.
- Dashed links connect the selected seed to actual ranked missing ties and open the corresponding card. The map focuses on that seed's candidates and observed routes; the all-cards button clears individual filtering.
- The outreach draft does not assert a lab affiliation or mutual acquaintance. No email is sent.
- D3 7.9.0 is vendored with its license after verifying official npm SHA-512 integrity, removing the runtime CDN dependency.
- Study cards use the same top-five methods and candidate population. Overlapping candidates appear once and are attributed to all selecting methods, without a priority-based deduplication bias.
- Study sessions select one anchor, shuffle its unique cards, require complete ratings and SUS, and export UUID-identified sessions matching the analyzer schema. The analyzer checks completeness, duplicate IDs and ranges, scores SUS, runs the primary paired joint-outcome test, and Holm-corrects exploratory comparisons.
- The report includes actual browser captures and current rerun metrics, not fabricated UI data or guaranteed introduction claims.

## Current quantitative results

Python 3.12.14, NetworkX 3.7, NumPy 2.5.4, SciPy 1.18.1. Dependency versions are pinned in `prototype/requirements.txt`.

| Dataset | Training nodes / edges | Communities | Modularity | Eligible seeds | Full P@5 | AA P@5 | Full NDCG@10 | AA NDCG@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pilot | 3,642 / 16,408 | 344 | .9492 | 180 | .0133 | .0056 | .0514 | .0297 |
| Scaled | 9,042 / 36,748 | 454 | .9248 | 1,385 | .0351 | .0295 | .0674 | .0515 |

Commands completed successfully from the repository root:

```bash
python prototype/backtest.py --data prototype/uiuc_data.json --out midterm/review/pilot-backtest.json
python prototype/backtest.py --data prototype/uiuc_data_scaled.json --out midterm/review/scaled-backtest.json
```

The pilot was repeated under `PYTHONHASHSEED=19` and compared byte-for-byte with the first run; metric files matched. Canonical ordering changes the Louvain partition relative to historical archived runs. Changed seed counts must not be interpreted as a paired performance improvement. Original `prototype/results/` outputs remain intact, while the revised paper reports the current `midterm/review/` files.

Full BridgeFinder beats Adamic–Adar on these two reported ranking measures but fails both scaled project targets (2× P@5 and +.05 NDCG@10). The citation result remains ratio 1.053 and p=.0601 across 6,231 evaluation papers, as validated during onboarding. A full-mark rubric assessment does not require pretending these empirical hypotheses succeeded.

## Checks completed

- `python -m unittest discover -s prototype/tests -v`: **4 tests passed**.
- All **500** displayed scaled recommendations matched the shared model's ordered top ten and scores.
- All displayed path edges exist and path lengths equal the shortest graph distance: **483 two-hop routes and 17 three-hop routes**. No top-ten item in this bundle had an unavailable path; a disconnected-graph fixture explicitly covers that state.
- Each study method retains exactly its true top five; shared candidates are rated once and credited consistently.
- Future-publication fixture verifies training topics/edges exclude post-2019 information.
- Analyzer tests cover valid sessions, missing cards, missing SUS, duplicate participant IDs, rejected automated-test markings, primary/exploratory comparison fields, and SUS lower/upper bounds.
- `python prototype/tests/browser_workflow.py`: Chromium rendered 50 seed cards and the focused map, opened a dashed-link card and outreach modal, exercised actual three-hop and unavailable-route rendering, rejected unanswered questions, and completed a one-anchor session's export-to-analysis contract. **Zero page errors**. The first selected anchor has **11 unique cards** representing five outcomes for each method.
- Automated browser ratings were held in memory and discarded; they are not participant data or human findings. The study SUS screenshot is a software-check artifact, not evidence of participant usability ratings.
- Two successful `pdflatex -interaction=nonstopmode -halt-on-error` passes; no undefined citations/references or overfull boxes. Extracted text and representative rendered pages were inspected.
- `git diff --check` passed.

Screenshots: `screenshots/01-seeds.png`, `02-map.png`, `03-recommendation.png`, and `04-study-sus.png`. The report uses the actual map and recommendation captures and explains them in the text and caption.

## Remaining limits and human work

The user confirmed the five formative sessions and participant details. Raw session notes were not provided. The paper labels findings as author-reported qualitative observations and does not generate quotes, frequencies, participant responses, or retrospective statistics. Authentic anonymized notes would strengthen independent auditability.

The planned 15-person comparison still requires actual consenting participants. Automated tests do not establish human comprehension, usable introductions, real mentoring outcomes, current employment, or statistical superiority in a population. The graph is a capped historical sample and co-authorship is not acquaintance or willingness to introduce. Historical prediction confidence intervals and held-out weight tuning remain future work, explicitly discussed in the paper.

The implemented workflow supports the rubric's midterm requirement for a demonstrated prototype and concrete evaluation plan. It does not establish production readiness or guarantee an instructor's score.

## Reproduce

See `prototype/README.md` and `prototype/study/README.md` for setup, study protocol, and participant privacy details. In this environment use `/workspace/cs470-venv/bin/python`.

```bash
python -m pip install -r prototype/tests/requirements.txt
python prototype/web/prepare_web_data.py
python prototype/study/generate_cards.py
python -m unittest discover -s prototype/tests -v
# Start this in a separate session:
python -m http.server 8765 --bind 127.0.0.1 --directory prototype
# With /usr/bin/chromium installed:
python prototype/tests/browser_workflow.py
mkdir -p /workspace/cs470-report-build
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=/workspace/cs470-report-build midterm/latex/main.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=/workspace/cs470-report-build midterm/latex/main.tex
cp /workspace/cs470-report-build/main.pdf midterm/midterm.pdf
```
