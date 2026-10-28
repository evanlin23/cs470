# Historical Capped 25,000-Work Capture

This archive preserves the historical capped 25,000-work collection and its results before the complete uncapped OpenAlex collection.

- Source collection: Capped harvest of 25,000 OpenAlex works (2015–2024).
- Retained multi-UIUC-author papers: 13,229 papers.
- Unique UIUC authors: 16,604 authors.
- Model: proposal-path-v3-common-neighbors (joint-paper weights, Louvain communities on <=2019, >=3 hops, simple common-neighbor triadic closure).
- Backtest seeds: 1,369 eligible seeds with new cross-community ties in 2020–2024.
- Metrics on capped dataset:
  * Topic-Only: P@5 = 0.0108, P@10 = 0.0108, R@10 = 0.0355, NDCG@10 = 0.0205
  * Triadic Closure: P@5 = 0.0282, P@10 = 0.0253, R@10 = 0.0638, NDCG@10 = 0.0472
  * BridgeFinder: P@5 = 0.0102, P@10 = 0.0109, R@10 = 0.0315, NDCG@10 = 0.0225
- Citation impact: 1,051 cross-community, 4,203 within-community, 977 unclassified (mean ratio 1.058, Mann–Whitney p = 0.1132).
