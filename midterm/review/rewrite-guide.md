# Rewrite guide for Evan and Eric

The revised paper is an editable working draft. Keep the factual results and the distinction between completed work and planned studies while rewriting in your own voice.

## Highest-value author revision: feedback

Section 5 currently supports three changes with general qualitative observations. Strengthen it with one or two concrete, authentic examples from your sessions. This is the main reason the strict editorial review holds Users and Feedback at 3/4 rather than assuming 4/4.

For each example, explain what the participant was trying to do, what happened, what it revealed, and what you changed. For example, an account of a participant's actual interpretation of a dashed link would show why the legend mattered. The paper already reports that general observation; the missing part is a specific, accurate interaction context. Use this structure only with facts you remember reliably or can verify in notes. Do not turn this suggested example into a new claimed session event.

Confirm the five sessions, 30-minute format, three CS/CE undergraduates and two Bioengineering/Information Sciences graduate students, and the reported observations. The author confirmed these details in conversation; this review did not independently observe the sessions. Raw notes, quotations and issue counts are not mandatory rubric artifacts. Add them only if authentic and useful. Do not invent “4 of 5,” a participant quote, task timings, recruitment methods, or post-revision success.

## Keep the central argument

A student knows an instructor but wants research opportunities outside that instructor's usual collaboration group. BridgeFinder uses the instructor's research as an interest proxy, finds related researchers at least three hops away in another community, and shows an observed co-authorship route. Historical prediction is weak; the planned student study tests perceived relevance, discovery and willingness to contact.

Graph distance and community boundaries operationalize discovery. They do not prove a structural hole in a social network, a weak personal tie, an available introduction, or willingness to mentor. Explain these choices in your own words without overstating them.

## Facts that must stay synchronized

- Current model: `proposal-path-v2`. Edges count joint papers; candidates are reachable cross-community non-coauthors at shortest distance >=3.
- Score: `S + 0.5*c3/(1+c3)`, where S is training-topic Jaccard similarity and c3 counts simple three-edge paths. The proposal specified the general topic/path idea; the coefficient and saturation are implementation choices.
- Topic-Only shares BridgeFinder's candidate pool. Adamic–Adar uses native two-hop candidates. Popularity/betweenness use all cross-community non-coauthors. All predict the same future ties. The comparison does not isolate distance or the route display.
- Pilot/larger harvested works: 5,000/25,000. Retained multi-UIUC papers: 2,493/13,229. Training nodes: 3,642/9,042. Training edges: 16,408/36,748. Communities: 344/455. Eligible prediction seeds: 184/1,369.
- Larger-sample BridgeFinder P@5/NDCG@10: .0102/.0225. Adamic–Adar: .0282/.0472. The prediction targets are not met. The short paper compares only the three methods in the proposal; additional baseline runs remain in the canonical JSON. Copy table cells from those current files, not historical review files.
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
