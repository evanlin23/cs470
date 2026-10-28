# Supporting analysis omitted from the short paper

The submission now focuses on the proposal's core question: do topic-and-path suggestions help a student discover a useful contact? The detailed citation analysis, extra popularity/centrality baselines, inferential-test names and implementation audit are retained here and in repository records. They are not necessary to explain the app or satisfy a rubric criterion. The short paper still reports the less favorable prediction results and its actual scope.

## Extra baselines

`prototype/results/backtest_results.json` and `backtest_results_scaled.json` retain all five computed methods. The paper shows only Topic-Only, Adamic–Adar and BridgeFinder, the proposal's central comparisons. No results were altered or rerun for this simplification. Popularity and betweenness use all cross-community non-coauthors; their wider pools differ from the proposal pool. The manifests record source/data hashes and runtime settings.

## Ancillary citation comparison

The separate citation pipeline excludes papers with more than 25 retained UIUC authors and builds its own training-community partition. It is an exploratory association, not a causal estimate of the value of recommendations.

Of 6,231 later papers, 1,051 were cross-community, 4,203 were within-community, and 977 could not be classified because none of their authors appeared in the training graph. Mean citations were 65.13 and 61.55, respectively, a ratio of 1.058. The medians were 36 and 37. A two-sided Mann–Whitney test gave $p=0.1132$.

The former impact targets (ratio >1.10 and p<.05) were not met. Field, paper age, repeated teams and heavy citation skew limit interpretation. The canonical output is `prototype/results/citation_impact.json`, with a matching report-review copy and provenance sidecar. Removing this secondary question from the short paper does not turn it into a positive finding.

## Planned study details

`prototype/study/README.md` retains the method-blinded protocol and participant-level analysis details. The primary planned outcome is the within-participant difference in the proportion of jointly relevant-and-new cards, BridgeFinder versus Adamic–Adar. The implementation uses a paired Wilcoxon comparison; other rating comparisons are exploratory with Holm correction, and paired t intervals are exploratory small-sample intervals. N=15 is not a powered confirmatory study.

Card relevance asks about the starting researcher's work, while novelty concerns the participant's own familiarity. The routes and candidates both differ across methods, so actionability comparisons do not isolate a route-display treatment. SUS concerns the interactive BridgeFinder app, not the static baselines. The main paper keeps these measurement distinctions and the success thresholds while omitting the test names.

The clarified usability task in the paper is a future protocol: choose a starting researcher, open a suggestion and draft, then explain the route and line types without coaching. Record task completion and explanation outcomes in a facilitator log. This description must not be retroactively reported as the script used in the five formative sessions.

No human comparative-study results are present. Test fixtures are not evidence of student ratings or comprehension.
