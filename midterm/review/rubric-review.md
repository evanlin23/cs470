# Strict rubric review of the full-data midterm

Source is the uploaded CS 470 midterm rubric. Scores are integers from 0 to 4. Each contributes `(score / 4) × weight`. The rubric separately permits up to a five-point deduction for spelling/grammar that impedes reading. This is an editorial judgment, not an instructor-issued grade or a guarantee.

## Starting grade and actual deductions

**Starting estimate in this pass: 90/100.** The previous blanket 100 assessment missed a stale figure. The full-data report still illustrated the older capped-data shortlist. Pilgyu Kang was not in the current displayed shortlist for John A. Rogers. That made the previous claim that the screenshots were current inaccurate.

| Criterion | Weight | Starting score | Revised score | Revised points | Evidence for revised score |
|---|---:|---:|---:|---:|---|
| Objective | 10 | 4 | 4 | 10 | Abstract and §1 state the student problem, contribution, relevance/discovery challenge, implemented progress and next evaluation. The abstract now reports both comparisons correctly: above topic-only, below triadic closure. |
| Related work | 10 | 3 | 4 | 10 | §2 now gives explicit contributions and task-specific limits for the researcher-search tools, literature maps, link-prediction work, cross-domain recommendation and network theory. The contrasts motivate the entry point, map, missing-link suggestions and human evaluation. Method/data sources are explained in §3. |
| Course concepts and network analysis | 15 | 4 | 4 | 15 | §3 defines brokerage, nodes, joint-paper weights, communities and the actual score. Louvain is justified against Girvan–Newman, as the rubric requires a method alternative. Table 1 reports actual full-data graph results, interpreted with the disconnected-component caveat. The text explains what removing the graph would remove. |
| Design and implementation | 25 | 3 | 4 | 25 | §4 explains the full entry → map → card/outreach flow and relates decisions to the problem, related work and feedback. Figure 1 now comes from the actual current full-data prototype, with its candidate/route verified against the exported bundle. All 11 happy-path browser tests pass on that bundle. |
| Users and feedback | 20 | 4 | 4 | 20 | §5 reports the author's corrected four-student sample and its composition, explains why undergraduates and graduate/application perspectives fit an initial round, describes talk-through feedback, and traces four observed issues to concrete revisions. New explanations are not claimed to have been human-retested. |
| Evaluation | 15 | 4 | 4 | 15 | §6 uses one historical measure, P@10, with explicit baselines and the actual full-data results. The future study gives recruitment, tasks, blinded cards, overlap handling, participant-level analysis and comparisons/thresholds for discovery, willingness to contact and usability. Brief explanations now make each measure's purpose clearer. |
| Writing | 5 | 3 | 4 | 5 | The argument proceeds from student need through prior work, method, interface, feedback and evidence to next steps. Tables and the current figure are referenced and explained. The prose removes unnecessary audit narration and accurately summarizes the mixed result. Rendered-page review checks the layout. |
| **Total** | **100** | **90/100 weighted** | | **100** | No reading-impeding grammar deduction identified after revision. |

The starting deductions were 2.5 points for Related Work, 6.25 for Design/Implementation and 1.25 for Writing. The revisions address those specific weaknesses; the score was not raised by changing empirical results.

## Iteration 1 — evidence and rubric gaps

Checked the rubric independently of the existing self-score. The related-work descriptions did not always make each comparison's contribution and task-specific limit explicit. The full-data prototype changed its ranked researchers, but Figure 1 still showed the earlier example. The abstract mentioned only the disadvantage against shared-contact ranking, without stating the advantage over topic-only. These were concrete report defects.

The corrected four-student account was retained. No minimum participant number, required quotation, issue frequency or post-revision retest was invented as an additional rubric requirement.

## Iteration 2 — repair while keeping the paper simple

- Rewrote the related-work comparisons with direct explanations of their useful contribution, task-specific limitation and connection to BridgeFinder.
- Captured the current prototype at native 3× resolution. The example is Naiman A. Khan → Ruopeng An → Kelly Scott Swanson → Victoria J. Vieira-Potter. The caption and visible researcher card now match the current bundle.
- Added `midterm/capture_screenshots.py` and capture metadata recording the dataset, current UI/bundle hashes, exact selected route and screenshot hashes. A publication check catches stale figure assets when those inputs change.
- Clarified why the existing planned ratings matter without adding another historical prediction metric. One dataset and one historical measure, P@10, remain.
- Applied the author's wording requests. The abstract states the advantage over topic-only and disadvantage against triadic closure before motivating the user study. Session duration and the generated-response sentence are omitted from the submitted prose. The short method-alternative justification remains because it is explicitly required by the rubric.

The original proposal, data, ranking, P@10 values, participant composition and supplied observations are unchanged.

## Iteration 3 — regrade and verify

Reread the revised paper against every top-level descriptor. The revised table above reflects this pass. The report supports the strongest descriptors while retaining its short-paper structure. The source-only paragraph-purpose comments remain for the authors' manual rewrite.

The remaining limitations are reported rather than disguised. Co-authorship does not establish acquaintance or mentoring availability. Interest matching uses the starting researcher's topics as a proxy. The formative feedback is author-reported. The 15-person comparison is planned, not completed. Historical P@10 is lower than triadic closure. These do not by themselves prevent full rubric credit for a midterm with real analysis, a demonstrable prototype, feedback-driven design and a concrete evaluation plan.

## What is still needed for a guaranteed 100

No reviewer can guarantee the instructor's judgment. This pass found no remaining specific rubric omission that can responsibly be repaired with the available evidence. The authors should own and verify the final wording, citations, participant account and contribution disclosure before submission. New participant evidence must come from actual participants. More formulas, additional prediction metrics, invented quotes or a favorable outcome are not required to fill a missing rubric category.

## Current evidence

- One completed API-query harvest records 102,947 unique works and 49,651 retained papers. Its dataset hash, actual counts and analysis provenance match the checkout. That verifies the provided artifacts, not an independent replay of the remote harvest.
- P@10 is .0079 for Topic-Only, .0287 for simple triadic closure and .0131 for BridgeFinder across 3,492 evaluated starting researchers.
- Four formative participants were two undergraduates (ECE and Food Systems) and two graduate students (one CS student and one MCS student researching computational biology). Session duration remains available in the author record but is not necessary in the paper.
- All 11 browser happy-path checks pass on the full-data demo/study bundle. Software fixtures are not human-study evidence.
- Publication checks verify the numerical table, matching report copies and provenance, the ancillary citation note, all displayed route counts, and the current figure's dataset/UI/image bindings.
- Build the report twice from the repository root, inspect the rendered pages and verify the cleanly extracted Overleaf project. The report uses one dataset and P@10 only for historical prediction; the separate planned app-evaluation measures satisfy the rubric's several-metrics requirement.

## Reproduce

```bash
python midterm/capture_screenshots.py
python -m unittest discover -s prototype/tests -p test_publication_consistency.py -v
python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-review
mkdir -p .build/midterm
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
cp .build/midterm/main.pdf midterm/midterm.pdf
python midterm/package_overleaf.py --verify
```

Earlier editorial passes are recoverable from Git history. This file supersedes their scores and current-status claims.
