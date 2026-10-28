# BridgeFinder contributor handoff

**Full-dataset collection is pending. Existing results are provisional capped-data results, not completion of the user's full-collection request.**

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

`prototype/model.py` implements `proposal-path-v3-common-neighbors`, shared by the app, backtest and study. Edges count joint papers. Candidates must be reachable non-coauthors in a different Louvain community, at shortest distance >=3. Score = `S + 0.5*c3/(1+c3)`, where S is training-topic Jaccard similarity and c3 counts simple three-edge introduction paths. More distant reachable candidates remain eligible without a three-step bonus. The card shows an actual shortest path. Autonomy and boundary-spanning values are descriptive, not ranking terms.

Numbered communities are not departments. Inferred research-area keyword labels are separate and do not alter rankings. Publication paths do not confirm personal introductions or mentoring availability.

## Proposal alignment and triadic closure

The user's design direction restored the proposal's three-or-more-hop requirement and raw joint-paper weights. All 500 displayed top-ten suggestions now use three-edge paths, with no shared co-author. Simple triadic closure ranks its two-hop shared-contact candidates by the number of common co-authors; Topic-Only uses the same >=3-hop pool as BridgeFinder. Popularity and betweenness use all cross-community non-coauthors. All predict the same future new cross-community ties. These are comparisons of discovery strategies with different pools; zero overlap with triadic closure follows from eligibility and is not evidence of higher quality.

Run `python prototype/audit_recommendations.py` to reproduce `prototype/review/closure-audit.json`. The previous hybrid, which displayed 483 two-hop suggestions, is archived under `prototype/legacy/shared-model-v1/`. Its results are historical and must not be mixed with this experiment. The submitted proposal remains unchanged.

## One current dataset

The app, study and current report use `prototype/uiuc_data_scaled.json`. Its historical filename is retained for provenance. It contains 13,229 multi-UIUC-author papers retained from a capped collection of 25,000 OpenAlex works. There are 16,604 author records; the 2015–2019 training graph has 9,042 authors, 36,748 edges and 455 communities (modularity .905). The temporal evaluation has 1,369 starting researchers with later new cross-community ties.

The 5,000-work pilot and its outputs are development history under `prototype/legacy/pilot-development/`. They are not a second current dataset. The report presents one prediction measure, top-ten precision (P@10), directly corresponding to the proposal's top-ten hit counting. Current P@10 values are Topic-Only .0099, simple triadic closure .0223 and BridgeFinder .0094, also recorded in `prototype/results/backtest_results_scaled.json` and the matching paper copy. Other metrics remain in that supporting JSON.

The current triadic-closure baseline simply counts shared co-authors, without inverse-degree weighting. Older Adamic–Adar source, results and study attribution are archived in `prototype/legacy/adamic-adar-v2/`. They must not be mixed with the new study dataset revision.

This is **not** an exhaustive set of all relevant UIUC papers. A full collection attempt was blocked by the environment's OpenAlex proxy policy (HTTP CONNECT 403). Exhaustiveness requires completing the collection, checking pagination/coverage, and rerunning the pipeline. Nothing in the paper claims that has happened.

The separate citation analysis remains ancillary and is not part of the short paper. Its files and provenance remain under `prototype/results/` and `midterm/review/`.

## Refresh results and generated data

```bash
python prototype/refresh_results.py
python prototype/web/prepare_web_data.py
python prototype/study/generate_cards.py
```

The first command runs the single-dataset prediction analysis and ancillary citation analysis in a temporary directory, then publishes all results and manifests only after every command succeeds. Current metrics live in `prototype/results/`, and matching report copies live in `midterm/review/`. `scaled-run.json` and `citation-run.json` record dataset/code hashes, runtime versions, algorithm settings, and actual counts. Original historical outputs remain in the legacy directory.

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

## Complete local collection

Paste the prompt in `docs/local-complete-dataset-prompt.md` into a local coding agent with OpenAlex access. It requires uncapped/resumable collection and completeness checks before publishing a new dataset, then regeneration of the report, app, study, provenance and Overleaf ZIP.

## Exhaustive collector

`prototype/fetch_openalex.py` is now uncapped by default. It resumes query-specific page checkpoints under `.build/openalex-full`, deduplicates work IDs, validates exact UIUC affiliation and distinct author IDs, verifies cursor exhaustion and a stable matching API total, and publishes the processed dataset plus a `.collection.json` manifest only after those checks. Failed, capped or unreconciled runs do not overwrite the existing corpus. Legacy raw cache lists are not treated as complete. It retains full API work objects so truncation flags are not dropped by field selection; live API behavior still needs verification once access is enabled.

Run from the repository root after enabling OpenAlex network access:

```bash
python prototype/fetch_openalex.py --cache-dir .build/openalex-full --out prototype/uiuc_data_scaled.json
```

If OpenAlex requires authentication, supply it securely through the `OPENALEX_API_KEY` environment binding. No key is currently configured, and API authentication requirements cannot yet be tested because the proxy denies the destination. Do not place keys in command text or Git.

The network draft adds `api.openalex.org`, `docs.openalex.org` and `developers.openalex.org` while preserving the existing custom domain and preset policy. Saving that draft does not apply it. Review/save in environment settings and publish, then retry collection. Only after successful collection should the backtest, app/study data, screenshots, report and Overleaf ZIP be regenerated. Seven collector fixtures validate failure/resume/completeness behavior; they are not evidence that the real corpus was harvested.
