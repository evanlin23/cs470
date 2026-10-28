# Supporting analysis omitted from the short paper

The submission now focuses on the proposal's core question: do topic-and-path suggestions help a student discover a useful contact? The detailed citation analysis, extra popularity/centrality baselines, inferential-test names and implementation audit are retained here and in repository records. They are not necessary to explain the app or satisfy a rubric criterion. The short paper still reports the less favorable prediction results and its actual scope.

## Historical results and extra metrics

The current single-dataset result is `prototype/results/backtest_results_scaled.json`. The paper shows P@10 for Topic-Only, simple common-neighbor Triadic Closure and BridgeFinder. P@5, R@10 and NDCG@10 remain in the supporting result JSON but are not required to explain the proposal's top-ten evaluation.

The 5,000-work pilot is historical under `prototype/legacy/pilot-development/`. The former Adamic–Adar comparison is historical under `prototype/legacy/adamic-adar-v2/`; its output also includes extra popularity/centrality baselines. These were not the simple shared-contact comparison selected by the user. Current code, paper and study attribution use common-neighbor counts and one dataset. Numerical values must come from the fresh run of that version.

The complete harvest of OpenAlex works (2015–2024) matching our query is finished, collecting 102,947 works and retaining 49,651 multi-authored UIUC papers. OpenAlex is mutable and not every real-world paper is indexed.

## Ancillary citation comparison

The separate citation pipeline excludes papers with more than 25 retained UIUC authors and builds its own training-community partition. It is an exploratory association, not a causal estimate of the value of recommendations.

Of 26,228 later papers, 4,802 were cross-community, 17,866 were within-community, and 3,560 could not be classified because none of their authors appeared in the training graph. Mean citations were 21.77 and 19.14, respectively, a ratio of 1.137. The medians were 7.0 and 7.0. A two-sided Mann–Whitney test gave $p=0.7740$.

The mean-ratio target (>1.10) was met, but the distributional-test target (p<.05) was not. Field, paper age, repeated teams and heavy citation skew limit interpretation. The canonical output is `prototype/results/citation_impact.json`, with a matching report-review copy and provenance sidecar. Removing this secondary question from the short paper does not turn it into a positive finding.

## Planned study details

`prototype/study/README.md` retains the method-blinded protocol and participant-level analysis details. The primary planned outcome is the within-participant difference in the proportion of jointly relevant-and-new cards, BridgeFinder versus simple Triadic Closure. The implementation uses a paired Wilcoxon comparison; other rating comparisons are exploratory with Holm correction, and paired t intervals are exploratory small-sample intervals. N=15 is not a powered confirmatory study.

Card relevance asks about the starting researcher's work, while novelty concerns the participant's own familiarity. The routes and candidates both differ across methods, so actionability comparisons do not isolate a route-display treatment. SUS concerns the interactive BridgeFinder app, not the static baselines. The main paper keeps these measurement distinctions and the success thresholds while omitting the test names.

The clarified usability task in the paper is a future protocol: choose a starting researcher, open a suggestion and draft, then explain the route and line types without coaching. Record task completion and explanation outcomes in a facilitator log. This description must not be retroactively reported as the script used in the four formative sessions.

No human comparative-study results are present. Test fixtures are not evidence of student ratings or comprehension.
