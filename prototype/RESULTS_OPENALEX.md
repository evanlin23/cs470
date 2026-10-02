# MethodBridge pilot on OpenAlex: backtest results

Data: OpenAlex (with API key), fetched by `fetch_openalex.py`. It writes the same JSON schema as `fetch.py`,
so `analyze.py` runs **unchanged**. Per-case outputs are in `results/openalex/<case>.json`, and case
definitions with their seed rules are in `case_*.json`. The walk settings are the same in every case: sample 1200
seed-citers, take the top 600 candidates cited by ≥2 sampled citers, and cap at 1500 citers per work.

**Bottom line:** in this pilot MethodBridge did not beat a baseline on any case. In 3 of the 4 cases
the weak-tie walk never reached the target, so no ranking could find it. In the one case where the target
was reached (PageRank → bibliometrics), plain **in-degree ranked it best**.

## Target ranks (lower is better; "—" = target not reached by the walk)

| Case (freeze year) | Target | in graph | MethodBridge | Co-citation (triadic) | In-degree | Global HITS |
|---|---|---|---|---|---|---|
| GeneRank: PageRank → microarray genes (2004) | Brin & Page 1998 | no | — | — | — | — |
| | Kleinberg 1999 (HITS) | no | — | — | — | — |
| | Langville & Meyer 2004 | no | — | — | — | — |
| Chen et al.: PageRank → citation analysis (2005) | Brin & Page 1998 | yes | 465 / 542 | 496 | **18** | 51 |
| | Kleinberg 1999 (HITS) | yes | 470 / 542 | 452 | **23** | 99 |
| Item2Vec: word2vec → recommender systems (2015) | Mikolov et al. 2013 | no | — | — | — | — |
| Sohl-Dickstein et al.: non-eq. thermodynamics → diffusion models (2014) | Jarzynski 1997 | no | — | — | — | — |
| | Jarzynski 2011 review | no | — | — | — | — |
| | Langevin 1908 | no | — | — | — | — |

Across the 4 cases (best-ranked target per case; unreached counts as 0):

| Ranking | Hit@10 | MRR |
|---|---|---|
| MethodBridge | 0/4 | 0.0005 |
| Co-citation with seeds | 0/4 | 0.0006 |
| In-degree | 0/4 | **0.014** |
| Global HITS | 0/4 | 0.005 |

There are only 4 cases, and 3 of them had no reachable target, so these numbers mostly measure the walk, not the ranking.

## Why it failed

1. **The walk is a triadic-closure filter.** Candidates are works cited by ≥2 *sampled* citers of the seeds,
   and only the top 600 by that count are kept. In practice the cutoff was 6–8 co-citing citers. An imported method is, by definition,
   rarely cited by the home field before the transfer. I checked the cache (no extra requests) to count how many seed-citers cited each target before the freeze:
   - GeneRank: **0 of 3111** cited PageRank or HITS before 2005. No two-hop walk from the seeds can reach them.
   - Item2Vec: 11 of 6249 cited word2vec. The 1200-citer sample would expect about 2, which is far below the cutoff of 6.
   - Diffusion: 20 of 5978 cited Jarzynski 1997, 2 cited the 2011 review, and 1 cited Langevin. All are below the cutoff.

   The walk needs an outward hop that does not require home-field citations, for example the references of
   the *candidates'* citers, or field-level sampling. That is the most important fix.
2. **The minimum community size hid the one reachable target.** In the PageRank → bibliometrics case, Louvain put
   PageRank, HITS and *Modern Information Retrieval* in a 3-work community. PageRank is that community's top
   authority (hole = 0.56), but `analyze.py` zeroes out communities smaller than 5. With that filter removed, the
   ranks become PageRank 48 and HITS 220. That is still worse than in-degree (18 and 23), so this is not a hidden win. I did not change `analyze.py`.
3. **Within-community HITS is normalized to 1 in each community.** So every small, off-topic community's top
   paper scores about 1 × hole. MethodBridge's top 10 is full of high-hole generic classics: psychology-of-creativity
   books in the bibliometrics case, CART and SVMs in the diffusion case, and Bradford protein assay
   duplicates in GeneRank. It needs a relevance or size prior.

## Communities: Louvain vs CNM vs Girvan–Newman

| Case | works / edges / citing papers | Louvain k, Q, time | CNM k, Q, time | GN best Q (top-150 subgraph, ~2 min) vs Louvain Q on the same subgraph |
|---|---|---|---|---|
| GeneRank | 599 / 86,666 / 116,377 | 7, 0.487, 0.7s | 8, 0.488, 2.6s | 0.029 vs 0.560 (121s) |
| PageRank → bibliometrics | 545 / 70,199 / 55,780 | 7, 0.570, 0.3s | 6, 0.567, 1.7s | 0.012 vs 0.557 (126s) |
| Item2Vec | 563 / 89,240 / 162,880 | 8, 0.477, 0.5s | 8, 0.476, 2.1s | 0.008 vs 0.574 (138s) |
| Diffusion | 597 / 90,093 / 295,476 | 9, 0.505, 0.6s | 9, 0.503, 2.2s | 0.000 vs 0.561 (132s) |

Louvain and CNM agree closely, and Louvain is 3–5× faster. Girvan–Newman barely gets past the first splits of these
dense co-citation graphs within its 2-minute budget, so its modularity stays near 0. That is a clean "why Louvain over GN" argument.

## API spend and coverage

- **Pricing observed** (`x-ratelimit-*` headers): a single-work GET costs $0, a list or filter page costs $0.0001, and a search costs $0.001.
  The daily budget is $1.00 (`X-RateLimit-Limit-USD`), and requests also count against a 10,000-per-day limit.
- **Spend:** 7,729 requests, about **$0.774** in total (GeneRank $0.162, PageRank → bibliometrics $0.097, Item2Vec $0.199,
  diffusion $0.314, and about $0.002 to inspect candidate cases). That left $0.226 of today's budget.
  Every response is cached under `prototype/cache/` (gitignored), and a re-run makes 0 requests.
- **Citer cap:** the 1500-citer cap was hit for 52, 19, 118 and 235 works in the four cases (recorded in `fetch.capped` in each graph file).
- **Dangling references:** 6 of Item2Vec's 18 `referenced_works` return 404 (merged or deleted W-ids), probably including
  Mikolov et al. NIPS 2013. 8 of Gruhl et al. 2004's 34 and 5 of Sohl-Dickstein's 45 are dangling too.
- **Field labels are unreliable for the seed rule:** `primary_topic.field` puts Kleinberg's HITS paper, Kempe et al. 2003
  and Gruhl et al. 2004 in "Physics and Astronomy". It puts the transfer paper itself on the *method* side for the diffusion case (Physics)
  and Gruhl (Physics), and on a wrong topic for Item2Vec (Topic Modeling) and Chen et al. (Text Analysis). For each case
  the `seed_rule` field says which label level and home label were used, and why. Item2Vec and Chen et al. have only 3 seeds each.
- **Dropped cases:**
  - Gruhl et al. 2004 (epidemics → blogs) and Kempe et al. 2003 (threshold models → viral marketing): OpenAlex puts the
    home-side and method-side references under the same label (Statistical and Nonlinear Physics / Complex Network Analysis),
    so the label rule cannot separate seeds from the method without hand-picking.
  - Gleich 2015: a survey rather than a single transfer; not attempted.

## Fragile or known bugs

- **Bug, fixed in code but the case was not re-run:** `fetch_openalex.py` looked up seeds given as W-ids through the DOI filter,
  so 3 of the 24 diffusion-case seeds (NADE and two others without DOIs) were silently dropped. The fetch ran with
  21 seeds. Re-fetching would cost about $0.3, which is more than today's remaining budget.
- Duplicate records (e.g. two *Bradford 1976* and three *SWISS-PROT* entries in GeneRank) split citations between W-ids.
  Merging by DOI only helps when the duplicates share a DOI.
- No comparison was made with the OpenCitations version: `results/generank_opencitations.json` was not on the branch.
- The broker-author step (optional) was not done: the project may pivot, and the budget is nearly spent.
