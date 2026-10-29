# Prototype validation

Model `proposal-path-v3-common-neighbors`. The cleanup removed the unused Burt-constraint computation from the model and the unused fields from `web/data.json`. Rankings, routes, study cards and keys, and every P@k value are unchanged. The study files are byte-identical, and the backtest point estimates match the previous results.

## Evidence in this directory

- `closure-audit.json` (from `audit_recommendations.py`). All 500 displayed suggestions are exactly three hops away and share no co-author with the starting researcher. Zero overlap with triadic closure follows from the disjoint candidate pools and says nothing about quality.
- `browser-summary.json` and `screenshots/` come from the latest browser run, which passed 12 of 12 Chromium tests. They cover search and filters, all 50 maps and card lists, map clicks, keyboard use, zoom and fit, history and shareable selection, the edited outreach text, mobile and tablet layout, the five study researchers, required personal interest, reload recovery, and a downloaded study export analyzed with its key.

## Unit tests

`python -m unittest discover -s prototype/tests -v` covers the following.

- Model invariants against hand calculations and independent oracles (`networkx.common_neighbors`), training-only topics, joint-paper weights, and the ≥3-hop rule.
- Displayed rankings and routes for all 50 starting researchers, and each method's true top five in the study cards.
- Study export validation and participant-level analysis.
- The OpenAlex collector (pagination, resume, deduplication, no publication before completion).
- Agreement between the paper, `results/`, the manifests, the demo data and the paper screenshots.

Test answers are synthetic. They are not evidence about students. Routes do not confirm acquaintance, availability or willingness to introduce someone, and inferred topics are not departments.

## Reproduce

```bash
python -m unittest discover -s prototype/tests -v
python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-checks
```
