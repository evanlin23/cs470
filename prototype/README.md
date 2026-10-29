# BridgeFinder prototype

Choose a UIUC researcher whose work you know, explore suggested researchers outside their collaboration community, and open a card with their topics, example papers, and an observed co-authorship route. The outreach draft can be edited, copied, or downloaded. No email is sent.

## Run

From the repository root, with Python 3.12 or newer:

```bash
python -m pip install -r prototype/requirements.txt
python prototype/serve.py
```

Open `http://localhost:8765/web/` for the app and `/study/` for the blinded card study. The server only exposes the public app and study assets. It never serves the private method key or the raw dataset. D3 is bundled, so no build step or CDN is needed.

## Model

`model.py` (`proposal-path-v3-common-neighbors`) is shared by the app, the study cards, and the backtest.

- Graph: UIUC authors from 2015–2019 papers. Edge weight is the number of joint papers. Topic profiles use only these training papers.
- Communities: Louvain (seed 42).
- BridgeFinder: reachable non-coauthors in another community at shortest distance of at least three edges, ranked by topic Jaccard plus `0.5*c3/(1+c3)`, where `c3` counts simple three-edge paths.
- Triadic closure: cross-community two-hop candidates ranked by the number of shared co-authors.
- Topic-Only: BridgeFinder's candidate pool ranked by topic Jaccard alone.

Ties are broken by author ID. Routes are observed shortest co-authorship paths. They do not confirm acquaintance, availability, or willingness to introduce someone. Topic-group labels in the app are keyword hints, not departments, and do not affect rankings.

## Data

`uiuc_data_scaled.json` is the one dataset: 49,651 multi-author UIUC papers retained from all 102,947 OpenAlex works for institution `I157725225`, 2015–2024. `uiuc_data_scaled.collection.json` records the query and completeness checks. To re-collect it (uncapped and resumable, writes only after the harvest completes):

```bash
python prototype/fetch_openalex.py
```

## Results

```bash
python prototype/refresh_results.py
```

This reruns three analyses and replaces `prototype/results/` only if all of them succeed. Each result has a manifest with dataset and code hashes.

| Script | Result | Contents |
|---|---|---|
| `backtest.py` | `backtest_results_scaled.json` | P@10 per method (the paper's metric), plus P@5, R@10 and NDCG@10, and the training-graph distance of the new ties |
| `network_stats.py` | `network_stats.json` | Modularity inside the largest component, Burt's constraint of route intermediaries |
| `citation_impact.py` | `citation_impact.json` | Exploratory citation comparison of cross- vs within-community papers (not in the paper) |

`audit_recommendations.py` writes `review/closure-audit.json`, which checks the hop distance of every displayed suggestion and its overlap with the baselines.

## Regenerate the app and study data

```bash
python prototype/web/prepare_web_data.py
python prototype/study/generate_cards.py
python prototype/audit_recommendations.py
```

See [study/README.md](study/README.md) for the study protocol and analysis.

## Tests

```bash
python -m pip install -r prototype/tests/requirements.txt
python -m unittest discover -s prototype/tests -v
python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-checks
```

The unit tests check the model against hand calculations and independent oracles, rankings and routes for all 50 starting researchers, study attribution and analysis, the collector, and agreement between the paper, results, and figure. The browser suite needs Chromium at `/usr/bin/chromium`. Its answers are synthetic and are not user-study evidence.
