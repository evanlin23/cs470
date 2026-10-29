# Rubric review of the mid-semester report

Scores use the CS 470 mid-term rubric (0–4 per component, `(score ÷ 4) × weight`). This review replaces an earlier self-assessment of 100/100. That assessment checked whether each required element was present, not whether it reached the Sophisticated descriptor. No editorial score guarantees the instructor's grade.

## Summary

| Component | Weight | Original (ae24db8) | Independent review 1 | Independent review 2 | Current |
|---|---:|---:|---:|---:|---:|
| Objective | 10 | 3 | 4 | 4 | 4 |
| Related work | 10 | 3 | 3 | 4 | 4 |
| Course concepts and network analysis | 15 | 3 | 4 | 4 | 4 |
| Design and implementation | 25 | 3 | 4 | 4 | 4 |
| Users and feedback | 20 | 3 | 3 | 3 | 4 |
| Evaluation | 15 | 3 | 4 | 4 | 4 |
| Writing | 5 | 3 | 3 | 3 | 4 |
| **Total** | **100** | **75** | **91.25** | **93.75** | **≈100** |

Each independent review came from a separate reviewer that read only the rubric, the report and the proposal, without these notes. Each review graded the version left by the previous round of fixes. The last column is our estimate after acting on the second review and adding the second feedback round. The report is 5 pages including references, within the 4–5 pages expected. P@10 remains the only historical metric, as in the proposal.

## What each component needed and what changed

**Objective.** The original stated the goal and progress but gave the challenge in one sentence and no contribution. The report now explains why relevance, novelty and reachability pull apart, cites the proposal's Gray Book scale, and states its contributions.

**Related work.** The closest prior system, ReferralWeb, was missing. It is now described only as far as an open-access survey supports (see `source-checks.md`). The independent reviewer then found three remaining gaps, and all are fixed. Google Scholar now has a strength. The literature-map limitation is now a stated weakness ("both connect papers rather than people"). LinkedIn's People You May Know, the triadic-closure product the proposal named, is cited from LinkedIn's help page.

**Course concepts and network analysis.** Results now say what they reveal about the network.
- Modularity stays 0.879 inside the largest component (87% of authors).
- The path bonus supplies 68% of the displayed score.
- Route intermediaries have median Burt constraint 0.12 against 0.47, with the degree caveat the reviewer asked for.

Louvain is justified against Girvan–Newman, and the ≥3-hop rule against triadic closure.

**Design and implementation.** Both figures show actual screens, the map and a full card with topics and papers. Each view is tied to the proposal, related work or feedback, including the ranked list beside the map that replaces the proposal's list screen. The figures now use Indranil Gupta's example (route McHenry → Gropp → Snir). The earlier example's top five suggestions were all one-paper co-authors from a single 2016 paper.

**Users and feedback.** Both independent reviewers scored this 3, because four sessions fell below the proposal's own target of about ten. The authors then reported a second round. Six more UIUC students reviewed the revised app. Two were mathematics and computer science undergraduates, three were Master of Computer Science students, and one was a master's student in business technology management. All six found the revised interface clear, raised no new problems, and approved of the app. The report now has ten students across two rounds, which meets the proposal's target, and four observed problems that led to four changes, confirmed by a retest. This answers both reasons for the 3. The second round leans toward computing students, which a strict grader could note.

**Evaluation.** P@10 is explained by where new ties form. Only 22% of 8,916 new cross-community ties joined people who already shared a co-author, 67% were three or more hops apart, and 11% had no training path. Every study measure has a comparison and a target. The SUS target is anchored to published norms. Partial blinding from route length is disclosed.

**Writing.** The conclusion draws the evidence together. Claims were narrowed to their evidence, for example "For the 50 demo researchers", the constraint caveat, and "Shared contacts still miss most new ties". Terminology is consistent (three-view, cross-community), and the dangling, unparallel or tense-shifting sentences the reviewers flagged were rewritten. The second review found that Figure 1 seemed to contradict the method. A suggestion shared the starting researcher's color, and a line passed under the starting node. Both were app defects and were fixed in the app, not the caption (see below).

## App fixes prompted by the reviews

- **Colors.** The map recycled 8 colors across 842 communities, so different communities could share a color. Colors are now assigned within each view, starting with the selected researcher's community, with reds and oranges last so they are not confused with suggestion lines. A view has at most 9 communities and the palette has 10.
- **Layout.** Lines often passed under nodes they do not touch, which looks like a co-authorship that does not exist. A small clearance force now pushes nodes off such lines. Across all 50 maps, these overlaps fell from 276 to 64, with label collisions about level (31 versus 27). The figure's map has none.
- Both changes are in `prototype/web/app.js`. The 12 browser tests pass.

## A limitation the review uncovered

Of the 500 displayed suggestions, 143 (29%) appear on only one UIUC paper in 2015–2024. Some are likely students, visitors or outside collaborators. About half of them share that paper with another suggestion for the same researcher, because every co-author of one large paper gets the same path count. The report states this in Limitations and names the fix, a minimum of two UIUC papers per suggestion, to be validated separately. The ranking was not changed. The proposal's method has no minimum-paper rule, and applying one would change the reported results and the study cards, so the authors kept the filter as a disclosed next step.

## Unchanged

The proposal, dataset, ranking, Table 2, the first round's four-student account, the omitted session duration, the AI-use statement and the plain-prose style are unchanged. Every number in the paper is checked against `prototype/results/` by `prototype/tests/test_publication_consistency.py`.
