# Strict rubric review after the external review

Scores use the uploaded rubric's integer 0–4 scale and `(score / 4) × weight`. The external review's 92.5/100 was a reasonable strict estimate. The earlier 100/100 self-assessment was too generous and is superseded here. No editorial estimate guarantees an instructor grade.

## Current editorial assessment

| Criterion | Weight | Score | Points | Basis and limits |
|---|---:|---:|---:|---|
| Objective | 10 | 4 | 10 | The abstract and §1 identify the student problem, significance, challenge and completed progress. Both baseline comparisons are accurate. |
| Related work | 10 | 4 | 10 | §2 gives relevant contributions, strengths, task-specific limits and explicit contrasts. The uploaded Tang paper now supports a concrete account of learned cross-field topics and random-walk ranking, its publication-history requirement, our student interest proxy and our fixed score's inability to learn cross-field topic relationships. |
| Course concepts and network analysis | 15 | 4 | 15 | §3 defines the graph, weights, brokerage, communities and ranking, justifies Louvain against Girvan–Newman, and interprets real results. Harvest identity/date, per-paper affiliation, unweighted path counts and empty-topic handling are explicit. |
| Design and implementation | 25 | 4 | 25 | §4 explains the complete three-view flow and its rationale. One large actual card image makes the route legible. Route-first ordering is a design choice, not an unsupported feedback attribution. |
| Users and feedback | 20 | 4 | 20 | §5 identifies and justifies the four students, reports the author-confirmed minimal-context individual exploration with active feedback, and connects observations to four revisions. Recruitment and note-taking/recording were not specified and are not invented. No retest is claimed. |
| Evaluation | 15 | 4 | 15 | §6 states candidate pools, frozen communities, seed inclusion and the fixed P@10 denominator. Planned measures have reasons, procedures, comparisons and targets. Personal-interest relevance and identical card/route presentation are described and implemented. |
| Writing | 5 | 4 | 5 | The rubric-aligned argument, explained figure and conclusions agree with the evidence. Four rendered pages and the extracted Overleaf build are checked. |
| **Total** | **100** | | **100** | No remaining specific rubric omission identified in this pass. This is an editorial assessment, not a guaranteed instructor grade. |

The feedback score assesses an initial qualitative round, not representative usability evidence. The rubric does not require a particular participant minimum, recordings, quotations, session duration or a post-change retest. An instructor may judge the available evidence more strictly.

## Targeted corrections

- All methods rank training authors in another training-period community and exclude existing collaborators. Frozen training labels identify future cross-community ties.
- A seed needs any new cross-community future tie, even one outside BridgeFinder's candidate pool. P@10 always divides by ten, including short lists.
- The paper records OpenAlex institution `I157725225`, years 2015–2024, completion on October 28, 2026 UTC, 515 exhausted pages, 102,947 collected works and 49,651 retained papers. Affiliation comes from each paper's authorship records. Table 1 is training only.
- The author confirmed that students received minimal context, worked through the app and gave feedback when problems arose. No recruitment source, notes, recordings, frequencies or quotations were inferred.
- Route-first placement is a design decision. The supplied feedback does not specifically establish that ordering as a participant request.
- Participants state an interest before app use. The form displays it and asks about relevance to it. Exports identify `student-interest-v1`; analysis rejects old/missing protocols and missing interests. This changes one planned relevance measure, without adding a historical metric.
- All comparison cards use identical fields and the same unweighted shortest-path procedure. Closure routes have two edges; BridgeFinder and Topic-Only routes have at least three. Unreachable candidates are excluded. Different candidates still prevent a causal test of route display.
- Three-edge paths have four distinct vertices and ignore weights. Topic similarity is zero if either topic set is empty.
- The paper uses one enlarged actual card detail instead of the small overview map. Full map captures remain in the repository. Web references show exact URLs without invented access dates.

## Resolved primary-source check

The previous 97.5 estimate withheld 2.5 points for the high-level Tang comparison. The author supplied the original PDF after external retrieval was blocked. Its title, authors and printed pages match the citation. Sections 2, 3.3 and 4.1–4.2 support the revised comparison. `tang-source-check.md` records the PDF hash and exact source locations.

Tang learns collaboration topics and uses random walk with restart on a graph containing authors and topics. Publication histories support its author representations. Our fixed score instead uses a chosen researcher as the student's interest proxy and displays a route, while lacking learned relationships between topics in different fields. The paragraph now gives a source-supported contribution, strength, task-specific limitation and explicit methodological contrast. This evidence, rather than added length or a better experimental result, resolves the identified Related Work deduction.

An instructor can still judge the formative sample, related-work depth or study plan more strictly. A rubric assessment does not establish human usability, validate reported sessions independently or guarantee a score. The authors should verify their final rewrite and contribution disclosure before submission.

## Verification

- Current dataset/results/provenance match. P@10 remains .0079 for Topic-Only, .0287 for closure and .0131 for BridgeFinder.
- This prose-only source-check pass reruns the five publication-consistency checks, the PDF build and clean Overleaf extraction/compilation. Ranking, UI and study behavior are unchanged.
- The preceding implementation revision passed five full-data workflow tests, twelve validation/analysis tests and twelve Chromium happy-path tests. These cover all 500 displayed rankings/routes, genuine study top-five attribution, personal-interest entry, saved context, export/analysis, keyboard interaction and mobile layout. Automated answers are synthetic fixtures, not human evidence.
- Four pages at the original 10pt size. Two pdfLaTeX passes without warnings, rendered-page inspection, and a cleanly extracted/compiled Overleaf project matching the report text.
- Original proposal, dataset, ranking and historical results unchanged.

## Reproduce

```bash
python midterm/capture_screenshots.py
python -m unittest discover -s prototype/tests -p test_publication_consistency.py -v
python -m unittest discover -s prototype/tests -p test_workflow.py -v
python -m unittest discover -s prototype/tests -p test_validation.py -v
python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-review
mkdir -p .build/midterm
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
cp .build/midterm/main.pdf midterm/midterm.pdf
python midterm/package_overleaf.py --verify
```
