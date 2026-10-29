# Rubric review of the mid-semester report

This review scores the report against the uploaded CS 470 mid-term rubric (0–4 per component, `(score ÷ 4) × weight`). It replaces the earlier self-assessment of 100/100. That assessment checked that each required element was present and accurate. It did not ask whether each element met the Sophisticated descriptor. No editorial score guarantees the instructor's grade.

## Summary

| Component | Weight | Before (ae24db8) | After this revision | Main reason for the change |
|---|---:|---:|---:|---|
| Objective | 10 | 3 (7.5) | 4 (10) | Challenge now explained, contribution stated, scale of the problem given |
| Related work | 10 | 3 (7.5) | 4 (10) | Closest prior system (ReferralWeb) added with an explicit contrast |
| Course concepts and network analysis | 15 | 3 (11.25) | 4 (15) | Results now say what they reveal about the network, and brokerage is measured |
| Design and implementation | 25 | 3 (18.75) | 4 (25) | Map view shown, design choices traced to the proposal, feedback and score behavior |
| Users and feedback | 20 | 3 (15) | 3–4 (15–20) | Proposal shortfall acknowledged. Sample size and detail are limited by the data we have |
| Evaluation | 15 | 3 (11.25) | 4 (15) | P@10 result explained by where new ties form, and a reason for every study comparison and target |
| Writing | 5 | 3 (3.75) | 4 (5) | Conclusion now synthesizes the evidence instead of only listing next steps |
| **Total** | **100** | **75** | **95–100** | |

The midterm should be 4–5 pages (`docs/project-ideas.md`). The revision is 5 pages including references. Every change answers a specific rubric descriptor. Nothing was added only for length.

## Component review

### Objective (10%)

*Sophisticated:* clear goal, why it matters, why it is challenging, and an opening summary of what has been built.

**Before.** The goal and the progress summary in the abstract were clear. Importance rested on one example. The challenge was a single sentence ("suggest someone relevant who also extends the student's usual circle"). The CHI-style form asks for an opening that states the contribution, and none was stated.

**Changes.** Added the proposal's Gray Book figure (2,574 faculty, 110 departments) for why the problem matters. Rewrote the challenge as the tension between relevance, novelty and reachability, including the student cold start. Added a contribution paragraph listing the prototype, the historical test and the feedback round. Added the main network finding to the abstract.

### Related work (10%)

*Sophisticated:* carefully chosen sources, each with contribution, strengths, weaknesses, and an explicit contrast.

**Before.** Each source had a contribution and a contrast, and the Tang et al. paragraph was strong. The closest prior system was missing. ReferralWeb (Kautz, Selman and Shah, 1997) mined co-authorship and other co-occurrences to find experts and show the referral chain to them, which is BridgeFinder's core idea. The rubric's Competent descriptor names exactly this gap ("an obvious comparable app or a central paper is missing").

**Changes.** Added a ReferralWeb paragraph with its contribution, its strength (the chain makes an expert reachable), its limit (the searcher must be in the network, and results stay close to them), and the contrast (BridgeFinder starts from a familiar researcher and skips anyone within two hops). **Authors should check this description against the CACM article**, as they did for Tang.

### Course concepts and network analysis (15%)

*Sophisticated:* core function rests on a course concept, justified against an alternative from class, run on real data, and the report says what the results reveal about the network.

**Before.** The concept was present and the data were real. Two parts were weak. The Louvain justification was qualitative. Interpretation was mostly negative ("this is not evidence of disciplinary separation"). Brokerage was named, yet nothing measured it, and the score's actual behavior was not reported.

**Changes.** The new `prototype/network_stats.py` gives the report two short findings, and a third comes from the demo data.
- Modularity stays 0.879 within the largest component (87% of authors), so the high modularity reflects real clustering rather than disconnected pieces. Table 1 shows both values.
- On the 500 displayed suggestions the path bonus supplies 68% of the score, and every suggestion is exactly three hops away. The ranking therefore favors network position over topic match. This is a weakness, and the report now says so.
- Route intermediaries have median Burt constraint 0.12, against 0.47 for the median author in the largest component, so the routes do pass through brokers.

The Louvain justification is now concrete (Girvan–Newman recomputes betweenness for 78,281 edges, while Louvain runs in seconds). The ≥3-hop rule is now explicitly justified against triadic closure, the class alternative.

### Design and implementation (25%)

*Sophisticated:* careful discussion of goals and functionality, decisions traced to the problem and related work, and a prototype whose core flow can be demonstrated.

**Before.** The flow was complete and demonstrable, but only one of the three views was shown (a card detail), and the map that carries the network idea was not. Rationale was one clause per view. Departures from the proposal (several instructors replaced by one starting researcher, campus-wide map replaced by a focused map) were not explained.

**Changes.** Figure 1 now shows the actual network view, and Figure 2 shows the card. Each view now cites its reason: the proposal, related work, or the feedback that changed it. The score finding is carried into design. Topics and papers stay on the card so students can judge relevance, and the study's relevance ratings will decide whether the bonus should shrink. This is the highest-weight component, so it was the priority.

### Users and feedback (20%)

*Sophisticated:* population identified, well matched, of sufficient size and quality, justified, at least one round of feedback, and the report shows what it changed.

**Before and after.** The report identifies the target users, describes four real sessions, justifies the mix, and ties each of four observed problems to a change. That meets most of the descriptor. Two risks remain, and only the authors can reduce them.
- **Size and match.** Four students, two of them graduate students, against the proposal's "around 10 people". The report now states this openly instead of leaving a grader to find it.
- **Quality.** The observations are general ("students found the interface unintuitive"). Nothing reports what students thought of the suggestions themselves, which is the app's core value. If any student said whether a suggestion was relevant or whom they would contact, one sentence on it would help most. Do not add counts, quotes or recruitment details that were not recorded.

A strict grader may give 3 here (15/20). This is the component most likely to cost points.

### Evaluation (15%)

*Sophisticated:* several metrics, each justified, with a concrete plan and a named baseline or comparison point for each.

**Before.** The plan was strong, with blinded cards, five per method, participant-level analysis, and thresholds. The weaknesses were that the P@10 result had no interpretation beyond "fewer than triadic closure", the SUS target had no reference, and contact ratings were compared only with Topic-Only for no stated reason.

**Changes.** P@10 stays the only historical metric, as in the proposal, and Table 2 is unchanged.
- One sentence now reports where the 8,916 new cross-community ties formed. Only 22% joined authors who already shared a co-author, and 67% were three or more hops apart, inside BridgeFinder's pool. This supports the project's premise even though triadic closure has the higher P@10.
- The contact comparison is justified (Topic-Only shares BridgeFinder's pool, so the comparison tests the path bonus), and closure is reported for reference.
- The SUS target is anchored to published SUS norms (Bangor et al., 2008).

### Writing (5%)

*Sophisticated:* a clear argument from problem to conclusion, every figure referenced and explained, and conclusions supported by evidence.

**Before.** Sections were clear and the single figure was referenced. The conclusion was two sentences of next steps, and the argument stalled at the evaluation: if triadic closure predicts better, why BridgeFinder? Many defensive hedges diluted the line.

**Changes.** The conclusion now draws the evidence together. It says where new ties form, that triadic closure still predicts better, what the score leans on, and what the study must decide. Two redundant hedges were removed, and both figures are referenced and explained.

## What was not changed

The proposal, the dataset, the ranking method, P@10 as the only historical metric, Table 2, the four-student account, the omission of session duration, the AI-use statement and the plain-prose style (no colons, semicolons or em dashes in authored text) are unchanged. All new numbers come from `prototype/results/` and are checked by `prototype/tests/test_publication_consistency.py`.

## Before submitting

1. Verify the ReferralWeb description against the paper.
2. Add any real observation about how students judged the suggestions (Users and feedback).
3. Rewrite in your own voice using `rewrite-guide.md`, keeping every number synchronized.
4. Confirm the contributions and AI-use paragraph.
