# Supporting analysis not shown in full in the paper

All numbers come from `prototype/results/`, which `python prototype/refresh_results.py` regenerates with dataset and code hashes.

## Historical prediction

`backtest_results_scaled.json` holds P@5, P@10, R@10 and NDCG@10 for Topic-Only, triadic closure and BridgeFinder. The paper reports only P@10, as the proposal specified. The file also records the training-graph distance of every new 2020–2024 cross-community tie, which the paper uses to explain the P@10 result. Triadic closure ranks two-hop candidates, while BridgeFinder and Topic-Only rank the reachable pool at three or more hops. The comparison is between discovery strategies, not scores on one pool.

## Network structure

`network_stats.json` describes the 2015–2019 training graph. It reports modularity of the Louvain partition restricted to the largest component and Burt's constraint (networkx, weighted) for every author in the largest component and for the intermediaries on the 500 displayed routes. Low constraint partly reflects high degree, which the paper notes. It also counts displayed suggestions who appear on only one retained UIUC paper (143 of 500). Of these, 76 share that paper with another suggestion for the same starting researcher, because every co-author of one large paper gets the same three-path count. A minimum of two UIUC papers per suggestion is the planned fix, to be validated separately before the study.

## Ancillary citation comparison

The separate citation pipeline excludes papers with more than 25 retained UIUC authors and builds its own training-community partition. It is an exploratory association, not a causal estimate of the value of recommendations.

Of 26,228 later papers, 4,802 were cross-community, 17,866 were within-community, and 3,560 could not be classified because none of their authors appeared in the training graph. Mean citations were 21.77 and 19.14, respectively, a ratio of 1.137. The medians were 7.0 and 7.0. A two-sided Mann–Whitney test gave $p=0.7740$.

The mean-ratio target (>1.10) was met, but the distributional-test target (p<.05) was not. Field, paper age, repeated teams and heavy citation skew limit interpretation. This question is not in the short paper.

## Planned study details

`prototype/study/README.md` holds the method-blinded protocol and participant-level analysis. The primary outcome is the within-participant difference in the share of cards rated both relevant and new, BridgeFinder versus triadic closure, tested with a paired Wilcoxon test. Other comparisons are exploratory with Holm correction. N=15 is not a powered confirmatory study. Relevance is rated against the participant's own stated interest, recorded before app use. The analyzer requires protocol `student-interest-v1` and a nonempty interest. No human comparative-study results exist yet. Test fixtures are not evidence of student ratings.
