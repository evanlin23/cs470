# Midterm submission review — proposal-path-v2

The uploaded midterm rubric uses integer ratings 0–4 with weights: Objective 10, Related Work 10, Network Analysis 15, Design/Implementation 25, Users/Feedback 20, Evaluation 15, Writing 5. The earlier blanket 100/100 self-assessment was too confident. This document records evidence and limits; only the instructor can award the grade.

## Criterion review

| Criterion | Submission evidence | Remaining judgment or evidence limit |
|---|---|---|
| Objective | Abstract and §1 explain the student's problem, intended population, familiar-researcher entry point, discovery/relevance tradeoff and current progress. | Whether this framing is sufficiently compelling is an instructor judgment. |
| Related work | §2 compares researcher search, literature maps, link prediction, cross-domain recommendation, brokerage theory and longitudinal collaboration research. §4 links these ideas to interface choices. | Product comparisons are task-specific, not a systematic usability study. Live Illinois Experts access was blocked by the environment proxy; no unsupported claim that it lacks network tools was added. |
| Network analysis | §3 defines joint-paper edge weights, training-only topics, seeded Louvain, graph sizes/modularity, cross-community >=3-hop eligibility and the topic/path equation. It explains why network structure matters and why disconnected components complicate interpretation. | Capped historical data omits external and informal ties. Communities are not verified departments. |
| Design and implementation | §4 walks through Researchers → Network → Suggestions, actual introduction paths and editable outreach. Native browser images show the current map and researcher-card detail. The app, study and backtest import one ranking model. | Co-authorship routes are possible introductions, not verified acquaintance or availability. |
| Users and feedback | §5 describes the author-confirmed five 30-minute think-aloud sessions, participant backgrounds, sample rationale and three observation-to-design changes. It separates historical revisions from the present interface. | No raw notes, issue frequencies, quotes or measured post-revision improvement were supplied. The qualitative accounts are author-confirmed rather than independently verified. |
| Evaluation | §6 reports freshly rerun prediction/citation results and missed targets, defines metrics and baseline pools, and specifies a 15-student plan with relevance/novelty, actionability, comprehension, SUS and participant-level analysis. | Native Adamic–Adar uses two-hop candidates while BridgeFinder uses >=3; this compares strategies, not isolated scores. Prediction uncertainty and comparative human outcomes remain future work. |
| Writing | Five letter-size pages, 10-point body text, clear sections, explained terms, grouped numeric tables, current figure caption and resolved citations. The method now follows the proposal and uses one short equation. | Final writing quality is a human judgment; compilation and software tests alone cannot establish it. |

## Proposal correction

The previous shared hybrid favored two-hop suggestions and differed from the submitted proposal. The user explicitly asked to follow the proposal. The current model uses joint-paper weights and `S + 0.5*c3/(1+c3)` on reachable cross-community non-coauthors at distance >=3. All 500 displayed suggestions now have three-edge routes and no shared co-author. Historical source, bundles and results are preserved under `prototype/legacy/shared-model-v1/`; the original proposal is unchanged.

The new result is weaker than shared-contact prediction. Larger-sample BridgeFinder P@5/NDCG@10 are .0102/.0225 versus Adamic–Adar's .0282/.0472. Pilot/larger eligible seed counts are 184/1,369. Citation means are 65.13/61.55, ratio 1.058, p=.1132. The paper reports these negative findings directly, rather than carrying over the old model's favorable results.

The original approximate 110,000-work collection goal is not complete: the larger dataset has 25,000 harvested works. That scope gap is explicit in the limitations. The 15-person comparison still requires real participants. No software test responses are used as human evidence.

## Verification

- All 19 supporting tests passed, including 20 published prediction-table cells, citation statistics, report/result copies, dataset/code hashes, hand-calculated ranking/eligibility, all 500 displayed rankings and shortest paths, training-only topics, native baseline attribution and participant-level analysis.
- All 11 Chromium happy-path tests passed: all 50 starting researchers, actual map clicks and keyboard activation, zoom/fit, mobile/tablet layout, search/filtering, URL navigation, edited outreach, study progress and actual export-to-analysis round trip.
- The first browser run exposed a map label intercepting an edge click. Labels now let pointer events through; the entire browser suite then passed.
- Current report screenshots were captured at native 3× device resolution. They are lossless PNGs, not enlarged old captures. The card image is explicitly an introduction detail, not a full-card claim.
- The report was built twice from the repository root. Five pages, no LaTeX warnings, unresolved references or overflowing boxes; rendered pages inspected. The result interpretation paragraph is kept together across the full-width figure.

See `HANDOFF.md` for reproduction and `docs/teammate-review-assessment.md` for the attachment claim check. These checks support accuracy and reviewability, not a guaranteed rubric score.
