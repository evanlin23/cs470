# Rubric review of the mid-semester report

Scores use the CS 470 mid-term rubric (0–4 per component, `(score ÷ 4) × weight`). This review replaces an earlier self-assessment of 100/100. That assessment checked whether each required element was present, not whether it reached the Sophisticated descriptor. No editorial score guarantees the instructor's grade.

## Summary

| Component | Weight | Original (ae24db8) | Review 1 | Review 2 | Review 3 | Current |
|---|---:|---:|---:|---:|---:|---:|
| Objective | 10 | 3 | 4 | 4 | 4 | 4 |
| Related work | 10 | 3 | 3 | 4 | 4 | 4 |
| Course concepts and network analysis | 15 | 3 | 4 | 4 | 4 | 4 |
| Design and implementation | 25 | 3 | 4 | 4 | 4 | 4 |
| Users and feedback | 20 | 3 | 3 | 3 | 3 | 3–4 |
| Evaluation | 15 | 3 | 4 | 4 | 4 | 4 |
| Writing | 5 | 3 | 3 | 3 | 4 | 4 |
| **Total** | **100** | **75** | **91.25** | **93.75** | **95** | **95–100** |

Each independent review came from a separate reviewer that read only the rubric, the report and the proposal, without these notes. Each review graded the version left by the previous round of fixes. Review 3 graded the report after the second feedback round was added. The last column is our estimate after acting on review 3. The report is 5 pages including references, within the 4–5 pages expected. P@10 remains the only historical metric, as in the proposal.

## What each component needed and what changed

**Objective.** The original stated the goal and progress but gave the challenge in one sentence and no contribution. The report now explains why relevance, novelty and reachability pull apart, cites the proposal's Gray Book scale, and states its contributions.

**Related work.** The closest prior system, ReferralWeb, was missing. It is now described only as far as an open-access survey supports (see `source-checks.md`). The independent reviewer then found three remaining gaps, and all are fixed. Google Scholar now has a strength. The literature-map limitation is now a stated weakness ("both connect papers rather than people"). LinkedIn's People You May Know, the triadic-closure product the proposal named, is cited from LinkedIn's help page.

**Course concepts and network analysis.** Results now say what they reveal about the network.
- Modularity stays 0.879 inside the largest component (87% of authors).
- The path bonus supplies 68% of the displayed score.
- Route intermediaries have median Burt constraint 0.12 against 0.47, with the degree caveat the reviewer asked for.

Louvain is justified against Girvan–Newman, and the ≥3-hop rule against triadic closure.

**Design and implementation.** Both figures show actual screens, the map and a full card with topics and papers. Each view is tied to the proposal, related work or feedback, including the ranked list beside the map that replaces the proposal's list screen. The figures now use Indranil Gupta's example (route McHenry → Gropp → Snir). The earlier example's top five suggestions were all one-paper co-authors from a single 2016 paper.

**Users and feedback.** Both independent reviewers scored this 3, because four sessions fell below the proposal's own target of about ten. The authors then reported a second round. Six more UIUC students reviewed the revised app. Two were mathematics and computer science undergraduates, three were Master of Computer Science students, and one was a master's student in business technology management. All six found the revised interface clear, raised no new problems, and approved of the app. The report now has ten students across two rounds, which meets the proposal's target, and four observed problems that led to four changes, confirmed by a retest. Review 3 still gave 3. It noted that the round that changed the design had four testers, that most testers study computing, and that the second round's evidence is brief. The report now says each of these plainly. It states that the first round was below the five to ten the proposal cited, that the second round added six, and that most testers so far study computing, which the planned five-department study addresses. Further gains would need more recorded detail from the sessions, such as whether testers were looking for research positions, as the proposal planned.

**Evaluation.** P@10 is explained by where new ties form. Only 22% of 8,916 new cross-community ties joined people who already shared a co-author, 67% were three or more hops apart, and 11% had no training path. Every study measure has a comparison and a target. The SUS target is anchored to published norms. Partial blinding from route length is disclosed.

**Writing.** The conclusion draws the evidence together. Claims were narrowed to their evidence, for example "For the 50 demo researchers", the constraint caveat, and "Shared contacts still miss most new ties". Terminology is consistent (three-view, cross-community), and the dangling, unparallel or tense-shifting sentences the reviewers flagged were rewritten. The second review found that Figure 1 seemed to contradict the method. A suggestion shared the starting researcher's color, and a line passed under the starting node. Both were app defects and were fixed in the app, not the caption (see below).

## External review (Perplexity)

An outside review scored the report 97.5. Each suggestion was checked against the data before it was applied.

- **Applied.**
  - The 67% sentence now says it describes where new ties formed, not how likely any distant pair is to collaborate. Distant candidates far outnumber two-hop ones (for the 50 demo researchers, about 777,000 versus 30,000 candidate pairs in `prototype/review/closure-audit.json`).
  - The 8,916 ties are now called distinct pairs behind Table 2.
  - The 68% figure is now stated as a share of summed scores.
  - The constraint sentence names its graph and weighting, counts the 264 distinct intermediaries once, and no longer reads low constraint as proof of brokerage.
  - Graph-distance wording replaces claims about who is familiar to the student.
  - "One route is enough" became "one observed route already offers a possible introduction chain".
  - The literature-tool limitation no longer claims they ignore people. ResearchRabbit has author features.
  - The baseline is named as the shared co-author count, not a reproduction of LinkedIn.
  - The 29% figure now gives its denominator (500 suggestions) and window (2015–2024). It also says one paper does not establish affiliation, faculty status or availability to mentor, and that a two-paper filter adds data support without confirming employment.
  - Louvain settings are given (networkx, weighted, resolution 1, seed 42).
  - The primary study comparison is named.
- **Not applied.**
  - Describing the second round's procedure and adding session details. The authors asked that the paper state only that the six students found the revised interface clear, raised no new problems and approved of the app.
  - Restoring an uncertainty caveat and adding access dates. Neither is needed for the rubric, and access dates are not recorded.

## Review 4, after the voice rewrite

The middle sections were rewritten to match the authors' own abstract, objective and limitations. A fresh grader then scored the report 91.25, with Users and feedback and Evaluation at 3.

- **Evaluation.** The rewrite had dropped the reason for P@10. It is restored: the app shows ten suggestions, and the proposal planned a top-ten test. "All methods predict the same future ties" became "scored against the same future ties", which no longer suggests the methods give identical predictions.
- **Users.** The report now notes that the second round's six testers fell within the proposal's five to ten.
- **Other fixes.**
  - Illinois Experts' weakness is the missing introduction route, not a lack of search.
  - ReferralWeb's colleague answers stay within two links.
  - Requiring reachable candidates is flagged as a change from the proposal's mock-up.
  - BridgeFinder beats Topic-Only through the path bonus.
  - The study's five researchers are named as five of the 50. This was checked in the data.
  - Five sentences were reworded in the authors' voice, the Figure 1 caption was corrected, and the references are now alphabetical.
- **Not applied.** The grader suggested cutting "approved of the app". The authors asked to keep it.

## App fixes prompted by the reviews

- **Colors.** The map recycled 8 colors across 842 communities, so different communities could share a color. Colors are now assigned within each view, starting with the selected researcher's community, with reds and oranges last so they are not confused with suggestion lines. A view has at most 9 communities and the palette has 10. After review 3 the palette order was changed so that two blues never appear among the first six communities.
- **Layout.** Lines often passed under nodes they do not touch, which looks like a co-authorship that does not exist. A small clearance force now pushes nodes off such lines. Across all 50 maps, these overlaps fell from 276 to 64, with label collisions about level (31 versus 27). The figure's map has none.
- Both changes are in `prototype/web/app.js`. The 12 browser tests pass.

## A limitation the review uncovered

Of the 500 displayed suggestions, 143 (29%) appear on only one UIUC paper in 2015–2024. Some are likely students, visitors or outside collaborators. About half of them share that paper with another suggestion for the same researcher, because every co-author of one large paper gets the same path count. The report states this in Limitations and names the fix, a minimum of two UIUC papers per suggestion, to be validated separately. The ranking was not changed. The proposal's method has no minimum-paper rule, and applying one would change the reported results and the study cards, so the authors kept the filter as a disclosed next step.

## Unchanged

The proposal, dataset, ranking, Table 2, the first round's four-student account, the omitted session duration, the AI-use statement and the plain-prose style are unchanged. Every number in the paper is checked against `prototype/results/` by `prototype/tests/test_publication_consistency.py`.
