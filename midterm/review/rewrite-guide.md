# Rewrite guide for Evan and Eric

The revised paper is an editable working draft. Keep the factual results and the distinction between completed work and planned studies while rewriting in your own voice.

## Keep this rubric-aligned structure

| Paper section | Rubric criterion | Content to preserve while rewording |
|---|---|---|
| Abstract + 1. Objective | Objective (10%) | Why the student problem matters, what makes it challenging, the contribution, and completed progress. |
| 2. Related Work | Related work (10%) | For each comparison: what it contributes, what is useful, its limit for our task, and how BridgeFinder differs. |
| 3. Course Concepts and Network Analysis | Course concepts and network analysis (15%) | Brokerage, graph definitions, method versus an alternative, actual results, their interpretation, and why the network is essential. |
| 4. Design and Implementation | Design and implementation (25%) | The full entry → map → card/outreach flow, reasons for the choices, links to related work, actual screenshots, and what is implemented. |
| 5. Users and Feedback | Users and feedback (20%) | Target users, the actual formative sample and why it fits, concrete observed problems, and changes made in response. |
| 6. Evaluation | Evaluation (15%) | Metrics and reasons, actual results, baseline differences, future collection plan, and explicit success thresholds. |
| 7. Limitations and Next Steps | Supports the argument and Writing (5%) | Conclusions proportional to the evidence, important limitations, and the next step. |

Writing is assessed across every section, rather than in a section called “Writing.” Contributions/AI Use and References remain short supporting material. The abstract is a compact overview, so its limited repetition of the body is deliberate.

Each prose paragraph and metric item in `main.tex` now has a `% Rewrite purpose:` comment above it. These comments appear in the source only. Use them as a paragraph-by-paragraph guide while replacing the wording with your own. Keep the problem → method → design → feedback → evaluation → conclusion sequence, rather than adding implementation history to the submission.

Simplicity means each paragraph has a clear job. Do not remove the method alternative, interpretation of results, reasons behind design choices, sample justification, or metric comparisons: these earn rubric credit. Keep extra baseline runs, ancillary citation statistics, detailed statistical procedures and engineering checks in the repository notes unless you need them to support a specific claim.

## Author verification: feedback

The author supplied a concrete example: a student wanted to find a relevant professor but did not realize they needed to select a researcher on the first screen to enter the graph. The author proposed clear landing-page descriptors and steps. Those instructions have now been implemented, and §5 links this observed problem to the revision. The author also confirmed that an unintuitive UI prompted the existing design overhaul, that mismatched professor tags were corrected, and that a graph with too many nodes led to a focused display with community grouping. A further report of confusion about what a card means led to the new plain-language definition on the landing page.

Keep the sequence accurate: the confusion was observed; explicit instructions and the card definition were proposed in follow-up and then added; the interface overhaul and tag corrections were reported as completed changes. No student retest of the new explanations has been reported. Do not write that the change solved the problem or improved completion rates. The new account addresses the prior editorial reservation about feedback specificity.

Confirm the five sessions, 30-minute format, three CS/CE undergraduates and two Bioengineering/Information Sciences graduate students, and other reported observations. These were author-confirmed in conversation, not independently observed by this review. Add issue frequencies or quotations only if authentic and useful. No new session, quote, participant identity or count was inferred from the example.

## Keep the central argument

A student knows an instructor but wants research opportunities outside that instructor's usual collaboration group. BridgeFinder uses the instructor's research as an interest proxy, finds related researchers at least three hops away in another community, and shows an observed co-authorship route. Historical prediction is weak; the planned student study tests perceived relevance, discovery and willingness to contact.

Graph distance and community boundaries operationalize discovery. They do not prove a structural hole in a social network, a weak personal tie, an available introduction, or willingness to mentor. Explain these choices in your own words without overstating them.

## Facts that must stay synchronized

- Current model: `proposal-path-v3-common-neighbors`. Edges count joint papers; candidates are reachable cross-community non-coauthors at shortest distance >=3.
- Score: `S + 0.5*c3/(1+c3)`, where S is training-topic Jaccard similarity and c3 counts simple three-edge paths. The proposal specified the general topic/path idea; the coefficient and saturation are implementation choices.
- Topic-Only shares BridgeFinder's candidate pool. Simple triadic closure uses two-hop candidates ranked by the number of shared co-authors. All predict the same future ties. The comparison does not isolate distance or the route display.
- One current dataset contains 13,229 multi-UIUC papers from a capped collection of 25,000 works. Training nodes: 9,042. Training edges: 36,748. Communities: 455. Eligible prediction seeds: 1,369. This is not a complete campus collection. The pilot is historical.
- Current P@10 is .0099 for Topic-Only, .0223 for simple triadic closure and .0094 for BridgeFinder. The main historical measure is P@10, the fraction of the first ten suggestions that became later collaborators, averaged across starting researchers. Use the current common-neighbor result JSON. Older Adamic–Adar values are historical. The proposal named triadic closure and top-ten hit counting; it did not name P@5 or NDCG@10.
- Citation means: 65.13/61.55; ratio 1.058; p=.1132. Counts: 1,051 cross-community, 4,203 within-community, 977 unclassified. Neither impact target is met. This ancillary citation analysis is in review/analysis-notes.md, not the short paper.
- All 500 displayed suggestions currently use three-edge routes. That audit describes the bundled demo, not all possible candidates.
- The app has 50 starting researchers; the comparison study offers five starting-researcher contexts and 63 unique cards across them. Contexts are collaboration communities, not verified departments.
- Card relevance asks about the starting researcher's work; novelty asks about the participant's familiarity. This does not directly establish personal-interest fit. SUS concerns the interactive app.
- The comparative 15-person study is planned, not completed. Software tests are not participant findings. Current affiliations and availability have not been verified.

## Source and contribution check

Read the cited work you rely on, confirm that each comparison accurately reflects it, and adjust the prose to your own interpretation. Verify author contributions and AI-use disclosure before submission. Product links are not a substitute for checking the described workflow. Do not add invented access dates.

## Manual editing and final check

Edit `main.tex` in the Overleaf ZIP using pdfLaTeX. The bibliography is embedded in that file. Keep the two figure paths and their directory structure unless you update the source references. Recompile after changing text, check every page, and make sure figures remain readable and references resolve. The current draft is four pages; that is an editorial target, not a page limit stated in the supplied rubric. Prioritize readable text over squeezing content into a page target.

If your rewrite changes a method, numerical claim or study protocol, synchronize the corresponding prototype or clearly label it as planned work. Rewording alone cannot establish a completed study or guarantee a grade.

## Prose style

The draft now uses periods or commas in place of colons and semicolons in its authored prose. Metric items use full sentences, and the closing paragraph states what the study findings will be used for. Preserve accurate names, reference titles, numerical ranges and the AI-use disclosure. There is no reliable punctuation-based test of authorship. Use your own explanation of the project rather than trying to imitate a supposed human-writing checklist. `style-review.md` records the source check and scope of these edits.

## Match the proposal's style

The proposal is clearest when it explains the student's action before the technical method. Keep that approach in the midterm. Say what a student chooses, sees and can do, then explain the graph that supports it. Use “five starting researchers for the card comparison” rather than “five study contexts.” Explain brokerage in terms of connections across groups. Describe think-aloud feedback as students talking through their use of the prototype.

The midterm needs more evidence than the proposal. Keep its actual graph/results tables, the method alternative, observations linked to revisions, and concrete study thresholds. Avoid copying the proposal's stronger claims about structural holes, existing products or successful prediction unless the current evidence supports them. The current relevance question concerns the starting researcher's work, not directly the student's own interests; preserve that distinction and the interest-proxy limitation.
