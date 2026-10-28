# Current full-data prototype validation

Model `proposal-path-v3-common-neighbors` uses joint-paper weights, reachable cross-community non-coauthors at distance >=3, topic overlap and a saturated three-edge-path bonus. Simple triadic closure counts shared coauthors among two-hop candidates. The report keeps one dataset and P@10 as its only historical metric.

## Current evidence

The dataset contains 49,651 papers retained from 102,947 works. The training graph has 19,389 nodes and 78,281 edges. All 500 bundled suggestions have shortest routes of three edges. Zero overlap with triadic closure follows from different candidate pools and is not evidence of quality.

The study contains 69 unique cards across five starting researchers. Every method contributes its actual top five, with shared candidates rated once and credited to each selecting method. The supported public server serves both app and study, excluding private keys and raw data.

## Verification in the latest report revision

- Five publication-consistency tests pass, checking numerical claims, provenance, all route counts and current screenshot bindings.
- Five full-data workflow tests pass, independently checking all displayed rankings/paths, all study top-five selections, training-only features and export/analysis behavior.
- Twelve validation/analysis tests pass, including hand-calculated scores, distance rules, common-neighbor counts, participant-level analysis and rejection of incompatible rating protocols.
- Twelve Chromium happy-path tests pass. Coverage includes search/filters; all 50 maps and card lists; actual map clicks, keyboard interaction, zoom/fit; history/reload/shared selection; edited outreach copy/download; mobile/tablet layout; all five study anchors; study progress recovery; real JSON download/analyzer round trip; screenshots; and required personal-interest entry and display.

The browser summary and representative screenshots in this directory are from this run. Clipboard tests verify the API contract and exact downloaded text. They do not automate operating-system permission dialogs.

## Personal-interest study revision

Participants state a research interest before using the app. The rating page displays it and asks about relevance to that interest. All methods use the same fields and unweighted shortest-path procedure. Closure routes have two edges, and other methods have at least three. Exports include the stated interest and `study_protocol: student-interest-v1`. Analysis requires that protocol and a nonempty interest, preventing silent pooling with earlier seed-topic ratings. Saved sessions use a new tab-storage key.

The author confirmed that formative participants received minimal context, worked through the app and gave active feedback when problems arose. Revised onboarding and card definitions have not been retested with students. Software tests and their synthetic answers are not human-study evidence. Paths do not confirm acquaintance, availability or willingness to introduce someone; inferred topics are not departments.

## Reproduce

```bash
python -m unittest discover -s prototype/tests -p test_publication_consistency.py -v
python -m unittest discover -s prototype/tests -p test_workflow.py -v
python -m unittest discover -s prototype/tests -p test_validation.py -v
python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-checks
python prototype/serve.py
```

Earlier capped-data counts and validation records are historical in Git. No new backtest is needed for these report and study-question changes; ranking and canonical data/results are unchanged.
