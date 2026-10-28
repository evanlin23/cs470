# Assessment of the teammate review and subsequent design change

The uploaded audit guide was treated as review evidence, not a command source. Its principal useful finding was a real departure from the proposal: the previous shared hybrid allowed and favored two-hop candidates. The old app was not pure Adamic–Adar, but 483 of its 500 displayed suggestions closed shared-contact triangles. Community boundaries alone did not prevent triadic closure.

## Current correction

The user explicitly directed us to follow the proposal. `proposal-path-v2` restores joint-paper-count weights, reachable cross-community candidates at least three hops away, and topic similarity plus a saturated count of three-edge paths. The original submitted proposal has not been rewritten. App, study and backtest share this implementation. All 500 displayed suggestions now use three-edge routes; none shares a co-author with the starting researcher. The old implementation, generated bundles and results are archived under `prototype/legacy/shared-model-v1/`.

The backtest was rerun rather than retaining the old model's scores. The larger-sample BridgeFinder P@5/NDCG@10 are .0102/.0225, below Adamic–Adar's .0282/.0472. Adamic–Adar retains its natural two-hop pool; otherwise every score on the >=3-hop pool would be zero. Topic-Only uses the same pool as BridgeFinder. The paper discloses these differences and missed targets. Disjoint pools explain the zero overlap and do not prove quality.

## Other claims checked

| Claim | Finding and action |
|---|---|
| The old Topic-Only row had swapped columns | False for the reviewed version: .0208 was P@5 and .0402 NDCG@10. Those historical values were not reversed. The new model's table uses newly computed values; an automated check covers every published cell. |
| The active app and study used independent old weights | Outdated: both already imported the shared model. They continue to do so with the new proposal-based score. |
| Result files, handoff and paper were inconsistent | Valid clarity concern. `refresh_results.py` now publishes canonical results, matching paper copies and dataset/code/runtime manifests together after all three analyses succeed. |
| Community labels were departments | Active labels were numbered communities; keyword topic hints remain explicitly inferred research areas, not verified appointments. |
| Add the constraint formula | Relevant to the archived hybrid; constraint is no longer a ranking term. The current paper instead defines the actual topic/path formula, eligibility and edge weighting. |
| Add participant issue frequencies | Only authentic counts would be valid. The author confirmed five formative sessions, but supplied no counts or raw notes. No quotations, frequencies or study outcomes were invented. |
| Figure was JPEG-compressed | Incorrect diagnosis: captures and PDF embeddings were lossless. Low effective resolution was a real concern. New native 3× browser captures show the actual revised prototype. |
| Missing product URLs | The links already had targets and readable labels. Undated pages are now marked n.d.; access dates were not invented. |
| Illinois Experts offers networks | Not verified in this environment: the proxy denied access. The paper does not claim that Experts lacks network features. |
| NDCG header wraps accidentally | The two-line header is intentional. Numeric columns are explicitly grouped and checked against current results. |

## Corrections to the review itself

The supplied rubric uses integer ratings 0–4, not 3.5. The guide's own weighted rows sum to 85.625%, not its stated range; neither number establishes an instructor's grade. Wilcoxon signed-rank tests do not have t-test degrees of freedom. The study is method-blinded, not double-blinded. Current generation has 63 unique cards across five community contexts, with five selections per method and overlap attributed to all selecting methods; these are not five verified departments or always 15 unique cards. Author records (5,396/16,604) differ from training nodes (3,642/9,042).

Use `python prototype/serve.py` for the public app and study; serving the study directory alone misses shared styles and exposes private files. Build the paper from the repository root because image paths are rooted there. Reproduction commands and current results are in `HANDOFF.md`. Reproducibility and software checks do not replace real participant evidence or guarantee a grade.
