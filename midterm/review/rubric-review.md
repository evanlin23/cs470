# Midterm report: final rubric review

Source: the uploaded `mid-term_report_CS470 (1).pdf`. Each component is rated 0–4 and contributes (rating / 4) × weight. This review uses the rubric's actual top-level descriptors, with evidence a reader can find in the submitted paper. It is an editorial assessment, not an instructor-issued grade.

## Review-and-revision loop

1. **Readability pass.** The earlier seven-page version was too much like a software audit. It was rewritten using the proposal's student-centered opening, direct wording, consistent “starting researcher” terminology, and a simpler explanation of the method. The initial 100/100 claim for that dense version was not justified and remains withdrawn.
2. **Strict content pass.** The five-page rewrite was assessed at 92.5: related work grouped comparators too broadly, and the feedback section did not clearly justify the sample and connect observations to the full flow. Those were revision tasks, not a reason to stop editing.
3. **Targeted revision pass.** Related work now names each tool's purpose, useful contribution, and limitation for the introduction task; gives Liben-Nowell/Kleinberg and Tang et al. separate contrasts; and explains what the theoretical and longitudinal studies do and do not establish. Official product references were added. The feedback section now explains why the sample fits an initial design round and connects each author-confirmed observation to a specific interface change, a visible artifact, and the next comprehension check. No new session facts, quotations, counts, or outcomes were invented.
4. **Submission pass.** Redundant implementation and conclusion prose was cut rather than shrinking the font. Empty screenshot space was cropped. The final paper remains five pages with 10-point body text. Source, extracted text, citations, tables, and rendered pages were checked again. The strongest rubric descriptors below are now supported without treating software tests as human evidence.

## Final criterion-by-criterion assessment

| Component | Weight | Rating /4 | Points | Why the top descriptor is supported |
|---|---:|---:|---:|---|
| Objective | 10 | 4 | 10 | The abstract and §1 state the student problem, why useful introductions matter, the relevance/discovery challenge, and the implemented progress. Readers learn what the app does before encountering network terminology. |
| Related work | 10 | 4 | 10 | §2 describes institutional search, Google Scholar, Connected Papers, and ResearchRabbit individually before contrasting their workflows with ours. It identifies the contribution and task-specific limitation of link prediction and cross-domain recommendation, and separates the motivation supplied by brokerage theory from what the longitudinal study explains. The contrasts lead to concrete choices: visual exploration, community filtering, explicit routes, and human evaluation. Limitations are framed for this task rather than asserting that every prior tool is generally deficient. |
| Course concepts and network analysis | 15 | 4 | 15 | §3 explains graph construction, weighted edges, Louvain versus Girvan–Newman, structural holes, and the score terms. Table 1 provides real-data graph sizes and modularity, followed by an interpretation that acknowledges disconnected components. The text states what would disappear if the network layer were removed. |
| Design and implementation | 25 | 4 | 25 | §4 explains the starting-person → map → card flow and why it serves students without publications. The map borrows the literature-discovery interaction; the card order follows feedback. Actual screenshots show the map and a readable route. The implemented core flow and real route extraction were browser-validated. |
| Users and feedback | 20 | 4 | 20 | §5 identifies the target students, reports the author-confirmed five-person composition and individual 30-minute think-aloud format, and explains why undergraduate entry needs and perspectives from application areas are useful for the initial round. It traces getting started, interpreting dashed edges, and choosing a next contact to three concrete changes visible in the app. The sample is justified for finding design problems, not for population-level estimates. The text does not claim that the changes have already solved those problems. |
| Evaluation | 15 | 4 | 15 | §6 names fair baselines, explains why P@5 and NDCG@10 matter, reports actual results and missed targets, and gives an operational participant study. Relevance/novelty, willingness to act, task comprehension and SUS each have a reason, measurement method, and explicit target or comparison. Participant-level inference and exploratory comparisons are distinguished. |
| Writing | 5 | 4 | 5 | The paper progresses from student need through related work, method, prototype, feedback, results, and next steps. Technical terms are explained, all figures/tables are referred to and interpreted, and conclusions distinguish working software from demonstrated mentoring benefits. The final pass removed audit narration and repeated qualifications while preserving factual limits. |
| **Total** | **100** | | **100** | **Editorial assessment against the supplied rubric after revision.** |

This does not restore the blanket claim that the earlier paper was already worth 100. It documents the specific subsequent improvements and the basis for the final judgment. An instructor can still disagree about their quality.

## Evidence limits that remain explicit

- The five formative sessions and participant details were confirmed by the author. Raw session notes were not supplied. The rubric requires a justified population, collected feedback and resulting design changes; it does not require a particular notes artifact, verbatim quotations, issue counts, a representative survey, or a completed comparative trial. Those should not be invented or silently added as new grading requirements. Authentic notes would still strengthen independent auditability.
- The feedback revision adds explanation and traceability to already confirmed observations. It does not add a reconstructed task script, participant motivations, recruitment facts, or measured design improvements. Sample rationale is the authors' justification, not a claim that every undergraduate has no publications.
- The numerical prediction targets are not all met, the citation comparison is not significant, and the 15-person comparative study remains planned. None is disguised as a successful empirical finding. The rubric rewards a sound evaluation and concrete plan, not favorable results.
- The ranking remains a heuristic on historical publication samples. The interface cannot confirm mentoring availability, personal acquaintance, or introduction willingness.
- Product URLs were added as references for the named tools. This revision does not claim a new live product study, systematic review, or fresh retrieval of full paper texts. Comparisons are limited to the described task and established scope of the cited work.

## Final readability and layout checks

- Five letter-size pages, 10-point body text, 0.7-inch margins, and normal paragraph spacing.
- One consistent term for the user's entry point: “starting researcher.”
- Definitions before use for community detection, modularity, topic match, autonomy, introduction routes, P@5, and NDCG@10.
- Main argument stands without reading filenames, response schemas, package integrity metadata, or implementation history; those remain in the engineering notes below.
- Actual map screenshot cropped only to remove unused space. The larger card capture makes the observed intermediary chain readable. The caption names the selected researcher, intermediary and candidate and explains what the route means.
- All tables/figures are called out in the text and interpreted. Table values match the retained current run files.
- All citation keys resolve to bibliography entries. The existing Dahlander/McFarland title was corrected to “Ties That Last: Tie Formation and Persistence in Research Collaborations over Time.”
- Two clean PDF build passes; no undefined references/citations, overfull boxes, or LaTeX warnings. Extracted text and rendered pages reviewed. `git diff --check` passed.
- Application logic, datasets, and test results were not changed to obtain a more favorable report score.

## Engineering evidence retained from the implementation review

The following sections document the earlier implementation validation. They support factual accuracy; they do not independently earn writing or feedback points. The submission itself no longer reads as this engineering checklist.

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
