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

## OpenAlex version

`fetch_openalex.py CASE.json OUT.json` is a drop-in replacement for `fetch.py` that uses OpenAlex. It needs
`OPENALEX_API_KEY` set, caches every response under `cache/`, and writes the same schema. `case_inspect.py DOI`
lists a transfer paper's references with their OpenAlex labels, for writing new cases. The results are in
`RESULTS_OPENALEX.md` and `results/openalex/`.
