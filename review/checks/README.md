# Viability checks for `docs/idea-brokerage.md`

All numbers in `../REVIEW.md` come from these scripts and their `results_*.json` outputs.
OpenAlex key is read from `OPENALEX_API_KEY` and is never printed or logged; `cost_log.jsonl`
records the `x-ratelimit-*` headers of every request made through `oa.py`.

| Script | What it checks | API cost |
|---|---|---|
| `01_counts.py` | UIUC institution ID, work/author counts 2015–2024, topic completeness | $0.0020 (incl. one $0.001 search) |
| `02_fetch_uiuc.py` | Streams **all** 109,471 UIUC works 2015–2024 (548 pages) into `data/uiuc_works.jsonl.gz` (not committed, 21 MB) | $0.0548 |
| `03_graph_stats.py` | Co-authorship graph, hyperauthorship, disambiguation flags, Louvain, Burt constraint/effective size | $0 (offline) |
| `04_backtest.py` | 2015–19 → 2020–24 backtest: confound table, precision@10 vs baselines, brokerage-gain check | $0 |
| `05_affiliation_coldstart.py` | Stale `last_known_institutions` (200 sampled authors), cold start | $0.0004 (plus $0.0003 for subfield names and a test page) |
| `06_value_of_far_ties.py` | Are papers from new far ties more cited than from new friend-of-friend ties? | $0 |

**Total spend: $0.0575** (566 requests). Daily remaining after the checks: $0.1688 of $1.

```
pip install networkx scipy scikit-learn
python3 01_counts.py && python3 02_fetch_uiuc.py && python3 03_graph_stats.py \
  && python3 04_backtest.py && python3 05_affiliation_coldstart.py && python3 06_value_of_far_ties.py
```
Runtime after the fetch (~8 min): under 5 minutes on a laptop.
