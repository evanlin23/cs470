# BridgeFinder contributor handoff

This is the current shared-model workflow for `evanlin23/cs470`, branch `claude/modest-gauss-q759kv`. Historical exporters, study bundles and result files are preserved under `prototype/legacy/remote-label-fix/`; do not use them as current benchmarks.

Evan Lin and Eric Liu are the project authors. The app helps UIUC students find relevant researchers outside a familiar researcher's collaboration community and inspect possible introductions.

## Run the prototype

From the repository root, use Python 3.12 and the pinned dependencies:

```bash
python -m pip install -r prototype/requirements.txt
python prototype/serve.py
```

The default port is 8765. The public researcher app is `/web/`, and the method-blinded study is `/study/`. The server serves both interfaces and their shared styles without exposing the private method key or raw data. Use this server rather than serving the study directory by itself.

The happy path is Researchers → Network → Suggestions → editable outreach. The UI supports desktop/mobile and keyboard use. The selected researcher/candidate can be shared through the URL. Nothing sends email automatically.

## One ranking implementation

`prototype/model.py` implements `proposal-path-v2`, shared by the app, backtest and study. Edges count joint papers. Candidates must be reachable non-coauthors in a different Louvain community, at shortest distance >=3. Score = `S + 0.5*c3/(1+c3)`, where S is training-topic Jaccard similarity and c3 counts simple three-edge introduction paths. More distant reachable candidates remain eligible without a three-step bonus. The card shows an actual shortest path. Autonomy and boundary-spanning values are descriptive, not ranking terms.

Numbered communities are not departments. Inferred research-area keyword labels are separate and do not alter rankings. Publication paths do not confirm personal introductions or mentoring availability.

## Proposal alignment and triadic closure

The user's design direction restored the proposal's three-or-more-hop requirement and raw joint-paper weights. All 500 displayed top-ten suggestions now use three-edge paths, with no shared co-author. Adamic–Adar uses its native two-hop shared-contact pool; Topic-Only uses the same >=3-hop pool as BridgeFinder. Popularity and betweenness use all cross-community non-coauthors. All predict the same future new cross-community ties. These are comparisons of discovery strategies with different pools; zero overlap with Adamic–Adar follows from eligibility and is not evidence of higher quality.

Run `python prototype/audit_recommendations.py` to reproduce `prototype/review/closure-audit.json`. The previous hybrid, which displayed 483 two-hop suggestions, is archived under `prototype/legacy/shared-model-v1/`. Its results are historical and must not be mixed with this experiment. The submitted proposal remains unchanged.

## Current datasets and results

| Dataset | Author records | Retained multi-UIUC-author papers | Training nodes / edges | Eligible prediction seeds |
|---|---:|---:|---:|---:|
| Pilot: 5,000 harvested works | 5,396 | 2,493 | 3,642 / 16,408 | 184 |
| Larger: 25,000 harvested works | 16,604 | 13,229 | 9,042 / 36,748 | 1,369 |

| Method | Pilot P@5 | Pilot NDCG@10 | Larger P@5 | Larger NDCG@10 |
|---|---:|---:|---:|---:|
| Preferential Attachment | 0.0033 | 0.0040 | 0.0077 | 0.0135 |
| Global Betweenness | 0.0033 | 0.0237 | 0.0086 | 0.0155 |
| Topic-Only | 0.0043 | 0.0154 | 0.0108 | 0.0205 |
| Triadic Closure (Adamic-Adar) | 0.0130 | 0.0368 | 0.0282 | 0.0472 |
| BridgeFinder | 0.0065 | 0.0149 | 0.0102 | 0.0225 |

BridgeFinder does not outperform Adamic–Adar or meet the original prediction targets. The path bonus has mixed results against Topic-Only. This is reported directly in the paper; no weights were tuned on future outcomes to hide the result.

The separate citation analysis excludes papers with more than 25 retained UIUC authors. It reports 1,051 cross-community, 4,203 within-community and 977 unclassified later papers; means 65.13/61.55, ratio 1.058, two-sided Mann–Whitney p=.1132. Neither impact target is met. Use the provenance manifests to distinguish this run from historical partitions.

## Refresh results and generated data

```bash
python prototype/refresh_results.py
python prototype/web/prepare_web_data.py
python prototype/study/generate_cards.py
```

The first command runs both prediction analyses and citation impact in a temporary directory, then publishes all results and manifests only after every command succeeds. Current metrics live in `prototype/results/`, and matching report copies live in `midterm/review/`. `pilot-run.json`, `scaled-run.json` and `citation-run.json` record dataset/code hashes, runtime versions, algorithm settings, and actual counts. Original historical outputs remain in the legacy directory.

Regenerating study data changes its revision ID when cards or attribution change. Use the matching method key when analyzing an exported session; never substitute historical keys.

## Study status

The authors confirmed five initial 30-minute think-aloud sessions: three CS/CE undergraduates and two graduate students from Bioengineering and Information Sciences. Feedback led to the starting-researcher list, a clear line-type legend, and a prominent introduction route. No issue counts or participant quotations were supplied, so none are invented in the report.

The planned comparison recruits 15 students across five disciplinary backgrounds. The implemented card contexts are five detected communities, not verified faculty departments. There are 63 unique cards across the five contexts. Each method contributes its actual top five; shared candidates appear once and are attributed to all selecting methods.

Participants rate relevance, novelty and willingness to contact, then complete SUS. Progress survives reload in the same tab; downloads are voluntary. This is method blinding, not claimed double blinding. No real comparative-study results have been collected in the repository.

See `prototype/study/README.md` for the protocol and analysis command. The primary comparison uses participant-level Relevant-and-New rates and a paired Wilcoxon test; exploratory comparisons use Holm correction. Wilcoxon does not have t-test degrees of freedom. With 15 complete pairs a paired t-test would have df=14.

## Check and rebuild

```bash
python -m pip install -r prototype/tests/requirements.txt
python -m unittest discover -s prototype/tests -v
python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-checks
```

The browser suite starts its own server and requires system Chromium. Automated responses are temporary test fixtures, not participant evidence.

Build the report **from the repository root**, because its figure paths are rooted there:

```bash
python -c "from pathlib import Path; Path('.build/midterm').mkdir(parents=True, exist_ok=True)"
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
python -c "import shutil; shutil.copyfile('.build/midterm/main.pdf', 'midterm/midterm.pdf')"
```

The earlier handoff is recoverable from Git history. The check of the uploaded group-member review is in `docs/teammate-review-assessment.md`. The prototype's UI and tests are documented in `prototype/review/validation.md`; the paper review is in `midterm/review/rubric-review.md`.

## Short-paper and Overleaf handoff

The current report is a four-page draft. It keeps the three proposal comparisons; extra baseline and citation results remain in `midterm/review/analysis-notes.md` and the canonical JSON files. The rubric review and author rewrite priorities are in `midterm/review/`.

`python midterm/package_overleaf.py --verify` creates `midterm/bridgefinder-midterm-overleaf.zip` with a root `main.tex`, figures and review notes. It checks a clean extracted build against the current report. Use pdfLaTeX in Overleaf; no external bibliography file is required.

## Author feedback follow-up

The author supplied the observed first-screen selection problem, an unintuitive interface, mismatched tags, unclear card terminology and an overcrowded graph. The current paper traces these to explicit entry steps, the existing UI overhaul, corrected labels, a new researcher-card definition and the focused map. New entry instructions and card explanations have not been retested with students. The prototype now describes the full route and focused graph in plain language; ranking and results are unchanged.
