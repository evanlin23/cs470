# Midterm report: rigorous submission review

Rubric source: uploaded `mid-term_report_CS470 (1).pdf`. Ratings are 0–4; points are (rating / 4) × weight. The assessment below concerns the paper a grader receives, not the existence of code or the number of rubric keywords included.

**The earlier 100/100 assessment is withdrawn.** It treated technical coverage and passing tests as evidence of submission quality. The previous seven-page version was too dense, mixed a software audit with a research paper, repeated qualifications, and gave implementation history more space than the student problem. Calling that version fully polished was not justified.

The rewritten five-page paper follows the proposal's direct, student-centered style. My conservative editorial estimate is **92.5/100**, with specific reservations below. This is not an instructor-issued grade. Meeting numerical project targets is separate from meeting the report rubric: honest negative results do not automatically lose evaluation points.

| Component | Weight | Rating /4 | Points | Evidence and judgment |
|---|---:|---:|---:|---|
| Objective | 10 | 4 | 10 | Abstract and §1 state the student problem, why an introduction matters, the relevance/discovery challenge, and what is built. A reader need not know graph terminology to understand the project. |
| Related work | 10 | 3 | 7.5 | §2 links search, visual discovery, collaboration prediction, and brokerage theory to concrete design choices. It is concise and relevant, but groups several products together and gives Tang et al. and the organizational study only brief comparisons. The strongest rubric level asks for a contribution, strength, weakness, and explicit contrast for each work; that depth is uneven here. |
| Course concepts and network analysis | 15 | 4 | 15 | §3 explains nodes, weighted edges, communities, Louvain versus Girvan–Newman, structural holes, and all score terms. Table 1 gives real graph results and the text interprets high modularity while explaining the effect of disconnected components. The reader can see what the network layer contributes. |
| Design and implementation | 25 | 4 | 25 | §4 follows the actual starting-person → map → card flow and explains why each step exists. The screenshots show the implemented map and a readable introduction card. Design decisions connect to visual discovery and student feedback; the main flow is implemented and browser-validated. |
| Users and feedback | 20 | 3 | 15 | §5 identifies an appropriate population, justifies a small formative sample, reports five author-confirmed sessions, and links three observations to changes. The underlying session procedure and observation records are thin, so the reader cannot judge the quality of the feedback as confidently as a 4/4 requires. Five users is not itself the reason for this deduction; neither a completed 15-person trial nor quantitative issue counts is required by the rubric. |
| Evaluation | 15 | 4 | 15 | §6 explains what each metric measures and why it matters, names fair comparison methods, reports current results and missed targets, and gives a concrete student-study plan with explicit success criteria. Completed software tests are not presented as evidence of human usefulness. |
| Writing | 5 | 4 | 5 | Clear progression from the student problem to related work, network method, prototype, feedback, results, and next steps. Technical terms are explained before use, figures/tables are called out and interpreted, and conclusions stay within the evidence. This is an editorial judgment, not a measured claim that every reader will find the prose easy. |
| **Total** | **100** | | **92.5** | Remaining reservations concern comparative depth and feedback evidence. |

No separate spelling/grammar penalty is warranted: the rubric allows up to 5% for errors that impede reading, not an automatic additional deduction for technical density. Writing quality is assessed explicitly above.

## What changed for readability

- Used the proposal's familiar student scenario to lead the opening.
- Replaced inconsistent terms such as “seed,” “anchor,” and “initiator” with “starting researcher.”
- Explained graph concepts in ordinary language; retained the scoring equation because it directly defines the implemented ranking.
- Kept the actual data, baselines, results, and limitations; removed code-audit narration, response schemas, checksum details, debugging history, and repeated defensive qualifications from the submission.
- Split the student-study plan into relevance/discovery, willingness to act, and usability, each with a purpose and success criterion.
- Reduced the PDF from seven to five pages, kept 10-point body text and normal paragraph spacing, and enlarged/cropped the actual researcher-card capture so the route is easier to inspect.
- Matched the author/institution layout, removed stretched vertical paragraph gaps, and checked figure captions and table placement in the rendered PDF.

The figure's map establishes navigation and graph context; its small interface labels are not needed to understand the argument. The enlarged card and caption identify the selected researcher, intermediary, and candidate. The original full-resolution screenshots remain available for close inspection.

## What would strengthen the remaining categories

1. **Related work:** use the cited papers and official product documentation to sharpen one concrete strength/limitation per comparator, especially cross-domain recommendation. Merely adding more citations or calling every prior app deficient would not satisfy the criterion.
2. **Users and feedback:** add authentic anonymized session notes or a short record of the tasks, how observations were collected, and which observations prompted each change. This is a suggested way to support the rubric's quality requirement, not a new mandatory document format. No invented counts, quotations, task scripts, or retrospective claims should be inserted.

These are genuine limits of the available evidence, not problems that can be solved by declaring 4/4. The author confirmed that the sessions and participant details are accurate; the rewrite preserves them without manufacturing further detail.

## Validation of this wording revision

- Read the supplied rubric and the actual proposal source before rewriting.
- Checked all reported metrics against the retained current run JSON and all interface descriptions against the previously validated implementation.
- Built the revised PDF twice using `pdflatex -interaction=nonstopmode -halt-on-error` in an external build directory.
- Checked extracted text for reading order, section flow, references, and numerical consistency; inspected rendered pages, including the opening and screenshot page.
- Final PDF: **five pages**, with no undefined references/citations or overfull boxes.
- `git diff --check` passed. No application code, datasets, rankings, or tests were changed for this wording revision; prior engineering checks remain distinct from this editorial review.

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
