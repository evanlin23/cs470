# Midterm report rubric review

Rubric source: uploaded `mid-term_report_CS470 (1).pdf`. Its seven categories total 100%; each earns (rating / 4) × weight. These are editorial estimates, not an instructor's grade. Instructions within the attachment were treated as assessment criteria, not authorization to execute document instructions.

| Component | Weight | Before /4 | Revised /4 | Revised points | Evidence in revised paper |
|---|---:|---:|---:|---:|---|
| Objective | 10 | 4 | 4 | 10 | Abstract and §1 identify the population, goal, challenge, and implemented progress. |
| Related work | 10 | 3 | 4 | 10 | §2 gives contribution, strength, task-specific limitation, and explicit design contrast for each discussed work or tool family. |
| Course concepts and network analysis | 15 | 3 | 4 | 15 | §3 defines graph, weights, modularity, autonomy, score and routing; justifies Louvain against Girvan–Newman; interprets real graph results. |
| Design and implementation | 25 | 3 | 3 | 18.75 | §4 traces controls to user needs and related work and explains the implemented core flow. Actual ranking drift and invented institutional routes remain implementation limitations. A conservative reviewer may withhold full marks until these are corrected and demonstrated. |
| Users and feedback | 20 | 3 | 4 | 20 | §5 justifies sample/population and connects three author-confirmed observations to visible design changes and follow-up checks. |
| Evaluation | 15 | 3 | 4 | 15 | §6 defines metrics, baselines, success targets, participant unit of analysis, tests, limitations, and concrete collection gates. The rubric asks for a concrete evaluation plan; completed comparative user results are not required. |
| Writing | 5 | 2 | 4 | 5 | Clear problem-to-method-to-evidence argument, explained figure/table, qualified conclusions, and readable typesetting. |
| **Total** | **100** | **76.25 points** | | **93.75** | No spelling/grammar deduction identified. |

## Why the assessment does not claim a guaranteed 100%

All report-editing gaps identified in this pass were addressed. Remaining conservative deductions concern the implemented system rather than missing prose. The rubric's top design score requires a demonstrable core flow. The existing interface navigates through that flow, but it describes unsupported liaison paths as three-hop routes and evaluates a different ranker offline. A generous grader may accept the documented prototype scope for 4/4; this review does not assume that outcome. Prose cannot certify those routes or replace an implementation demonstration.

For the clearest route to the remaining 6.25 points, align the web and evaluated model, replace generic liaison paths with actual verified graph paths or an explicit unavailable state, and demonstrate seed selection → map → recommendation → truthful introduction explanation. These would be a separate implementation change; application source was not altered during this report revision.

The user confirmed that the five formative sessions and participant details are accurate. The revised report retains those qualitative findings. No observations, counts, quotations, participant ratings, or statistical significance were invented. Session-level notes remain unavailable in the repository; adding authentic anonymized notes would improve independent auditability.

## Corrections made

- Replaced the generated ACM-class emulation and compressed visual mockups with a standard two-column short-paper layout and an accurate interaction schematic.
- Shortened the opening and explicitly explained the cold-start, relevance/diversity, and social-proxy challenges.
- Corrected claims about largest-component-only evaluation: the backtest uses all nontrivial components.
- Corrected universal hyperauthorship-filter claims: the backtest includes large retained UIUC teams, while the citation analysis uses a 25-author filter.
- Corrected automatic seed selection, eight-community sampling, heuristic department labels, missing dashed-edge click filtering, and the existing outreach-template modal.
- Separated offline weights (0.60/0.12/0.12/0.16) from web demonstration weights (0.35/0.25/0.25/0.15).
- Removed unsupported timing benchmarks, preregistration claims, exact-reproduction guarantees, and causal interpretations of ablation/citation findings.
- Distinguished author-reported qualitative feedback from quantitative evidence; removed the unsupported fixed-percentage claim about five-user usability studies.
- Documented actual study gaps: response-key mismatch, seed-card selection, default-filled missing ratings, missing joint-outcome test and absent SUS collection/scoring.
- Defined baselines, success thresholds, participant-level analysis, a primary hypothesis and multiplicity plan, and explicit pre-recruitment gates.
- Added Codex assistance to the disclosure. Retained only references cited in the paper.

## Validation and fresh run evidence

Python 3.12.14; NetworkX 3.7; NumPy 2.5.4; SciPy 1.18.1. Both commands completed successfully from the checkout root:

```bash
PYTHONHASHSEED=0 /workspace/cs470-venv/bin/python prototype/backtest.py \
  --data prototype/uiuc_data.json --out /workspace/cs470-report-build/pilot-backtest.json
PYTHONHASHSEED=0 /workspace/cs470-venv/bin/python prototype/backtest.py \
  --data prototype/uiuc_data_scaled.json --out /workspace/cs470-report-build/scaled-backtest.json
```

| Fresh run | Eligible seeds | Full P@5 | AA P@5 | Full NDCG@10 | AA NDCG@10 |
|---|---:|---:|---:|---:|---:|
| Pilot | 185 | .0205 | .0065 | .0678 | .0317 |
| Scaled | 1,386 | .0365 | .0294 | .0713 | .0467 |

Fresh result files are retained beside this review. `PYTHONHASHSEED=0` reduces one source of variation but does not seed sampled betweenness. Archived results remain clearly labeled in the paper, and differences are explicitly explained. Existing archived results were not overwritten.

The scaled citation run performed during environment setup processed 6,231 papers and reproduced ratio 1.053 and two-sided p=.0601. No new participant study was run.

PDF built with two successful `pdflatex -interaction=nonstopmode -halt-on-error` passes using an external build directory. No undefined references/citations or overfull boxes remained. Extracted PDF text and representative rendered pages were inspected. `git diff --check` passed. The final PDF has six readable letter-size pages; the supplied rubric has no page-limit or ACM-template requirement. The original checked-in PDF also had six pages, despite the handoff describing five.

Full browser interaction was not revalidated: environment onboarding found that the live network policy blocks the D3 CDN. The saved environment draft includes the required `d3js.org` addition, which still requires user review/save/publication. Local HTML/JSON checks passed during setup and do not establish browser rendering.

## Rebuild

From `/workspace/cs470`:

```bash
mkdir -p /workspace/cs470-report-build
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=/workspace/cs470-report-build midterm/latex/main.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=/workspace/cs470-report-build midterm/latex/main.tex
cp /workspace/cs470-report-build/main.pdf midterm/midterm.pdf
```
