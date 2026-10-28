# MethodBridge pilot

A backtest of the core network analysis on a documented cross-field method transfer.

- `fetch.py CASE.json OUT.json` builds a time-frozen citer→cited graph around the case's seed papers.
  It uses OpenCitations and Crossref (free, no key) and caches every response.
- `analyze.py OUT.json RESULTS.json` runs co-citation communities (Louvain, with CNM and Girvan–Newman
  for comparison), structural-hole scores, within-community HITS, and three baselines (co-citation /
  triadic closure, in-degree, global HITS). It reports where the held-out target method ranks under
  each.
- `case_generank.json`: GeneRank (2005) imported PageRank into microarray gene ranking. The seeds are
  GeneRank's biology references, the targets are the PageRank/HITS papers, and the graph is frozen at
  2004.

```
pip install networkx scipy
MB_MAILTO=you@illinois.edu python3 fetch.py case_generank.json graph.json
python3 analyze.py graph.json results.json
```

## Shared BridgeFinder workflow

Use Python 3.12 and `pip install -r prototype/requirements.txt`. `model.py` supplies the same pre-2020 graph, seeded Louvain partition, cross-community candidate population and 0.60/0.12/0.12/0.16 score to the backtest, map export and study. Candidate ties resolve by author ID; sampled betweenness uses seed 42. Large teams are fractionally weighted, not filtered by the backtest. The citation analysis separately applies its 25-retained-author filter.

```bash
python prototype/web/prepare_web_data.py
python prototype/study/generate_cards.py
python -m http.server 8765 --bind 127.0.0.1 --directory prototype
```

The web assets include a checksum-verified D3 7.9.0 distribution and its license, so no CDN is needed. Community numbers are inferred collaboration groups, not departments; seed records are historical UIUC-affiliated authors, not verified current faculty. Orange links show actual ranked missing ties. Click one for its recommendation card. Cards display only observed co-authorship paths of at most three edges, or explicitly report no route. The student-to-anchor relationship, acquaintance and willingness to introduce remain unverified. Outreach drafts never assert a personal connection or send messages.

See `study/README.md` for the human evaluation protocol. Validation:

```bash
python -m unittest discover -s prototype/tests -v
pip install -r prototype/tests/requirements.txt
# With the above HTTP server running, and Chromium installed:
python prototype/tests/browser_workflow.py
```

The browser check uses `/usr/bin/chromium`; it validates actual navigation, missing-answer rejection and the export/analyzer contract, and captures screenshots under `midterm/review/screenshots`. Browser-generated ratings are discarded; they are not human-study evidence.
