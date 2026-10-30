# Rewrite guide for Evan and Eric

`midterm/latex/main.tex` is ready to submit. If you reword it, keep its facts and the line between finished and planned work. The table below says which rubric criterion each section serves.

## Structure and the rubric

| Paper section | Rubric criterion | What the section must keep |
|---|---|---|
| Abstract + 1. Objective | Objective (10%) | The student problem, why it matters (Gray Book scale), why it is hard (relevance, novelty and reachability pull apart), what we contribute, and what is built |
| 2. Related Work | Related work (10%) | For each source: contribution, strength, limit for our task, explicit contrast. ReferralWeb is the closest prior system. LinkedIn is the triadic-closure product the proposal named |
| 3. Course Concepts and Network Analysis | Course concepts (15%) | Brokerage, graph definition, Louvain versus Girvan–Newman, the ≥3-hop rule versus triadic closure, and what the data show (largest-component modularity, path-bonus dominance, low-constraint intermediaries) |
| 4. Design and Implementation | Design (25%) | The three views, each tied to the problem, related work, the proposal, or feedback. Figures 1 and 2 |
| 5. Users and Feedback | Users (20%) | Ten students in two rounds, why they fit, four observed problems and the change each caused, and the second round's retest of those changes |
| 6. Evaluation | Evaluation (15%) | P@10 only (as proposed), one sentence on where new ties form, and the planned study with a comparison and target for every measure |
| 7. Limitations and Next Steps | Writing (5%) | What the evidence shows, its limits, and the next step |

The midterm rubric expects 4–5 pages (`docs/project-ideas.md`). The current build is within that.

## Facts that must stay synchronized

`prototype/tests/test_publication_consistency.py` checks the numbers below against `prototype/results/`. If a number changes, rerun `python prototype/refresh_results.py` and update the paper. Never edit a result file by hand.

- Model `proposal-path-v3-common-neighbors`. Joint-paper edge weights, Louvain seed 42, candidates reachable, cross-community and at least three hops away. Score is topic Jaccard plus `0.5*c3/(1+c3)`.
- Data: 102,947 works collected, 49,651 retained. Training graph 19,389 authors, 78,281 edges, 842 communities, modularity 0.884 overall and 0.879 within the largest component (87% of authors).
- Demo: 50 starting researchers, 500 suggestions, all exactly three hops. Path bonus is 68% of their combined score. Route intermediaries have median constraint 0.12 versus 0.47 for the median largest-component author. 29% of suggestions (143) appear on only one UIUC paper.
- Figures: the example is Indranil Gupta, whose top suggestion Marc Snir is reached through Kenton G. McHenry and William Gropp. `midterm/capture_screenshots.py` fixes this example and checks that none of its ten suggestions is a one-paper author.
- Backtest: 3,492 starting researchers. P@10 is 0.0079 (Topic-Only), 0.0287 (triadic closure) and 0.0131 (BridgeFinder). Of 8,916 new cross-community ties, 22% were two hops apart and 67% three or more.
- Study: 15 students planned, five starting researchers, 69 unique cards, protocol `student-interest-v1`. Not yet run.

## Sources

`source-checks.md` records what each related-work comparison rests on. Tang et al. was checked against the paper itself. ReferralWeb is described only as far as an open-access survey supports. The Gray Book figure (2,574 faculty, 110 departments) is carried over from the proposal. The AI Use section is the authors' own statement.

## Style preferences already applied

Plain prose without colons, semicolons or em dashes in authored text. Accurate titles, names and numeric ranges keep their punctuation. The paper does not state session duration. The original proposal stays unchanged. The proposal's claim that Tang et al. ignore network structure is wrong and must not be copied into the midterm.
