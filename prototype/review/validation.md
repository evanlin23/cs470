# Proposal-aligned prototype validation

Current model: `proposal-path-v2`. The user's design direction restored joint-paper-count edges, reachable cross-community non-coauthors at shortest distance >=3, and training-topic similarity plus a saturated three-edge-path bonus. The proposal's three-screen happy path and restrained research-directory styling remain. Historical shared-model-v1 source/results are archived separately.

## Verified

`python -m unittest discover -s prototype/tests -v`: **19 tests passed**. Checks cover canonical result/report copies and provenance, all published prediction values and the supporting citation-analysis note, all 500 displayed rankings and shortest observed paths, hand-calculated score/eligibility (including four-hop and disconnected candidates), training-only features, native baseline study attribution and participant-level analysis.

`python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-checks`: **11 Chromium tests passed**. The suite starts an isolated supported server and checks:

1. Search and community/topic filtering.
2. All 50 researchers' maps, suggestion lists and ordered cards.
3. Real map-link clicks and keyboard activation, zoom and fit.
4. Reload, browser history and shareable researcher/candidate selections.
5. Editable outreach with exact-text copying/download and keyboard focus.
6. Layout at 360, 390, 768 and 1440px without horizontal overflow.
7. Keyboard researcher selection and card ratings.
8. All five study contexts with correct unique-card counts and hidden method labels.
9. Same-tab recovery of card order, identity, answers and SUS progress.
10. Actual downloaded response JSON analyzed with its matching private key.
11. Desktop/mobile screenshot capture and optional ranking explanation.

The first run found that a node label intercepted the click on a suggested edge. Labels now have `pointer-events:none`; the full rerun passed. Clipboard permission UI itself is not automated; the test verifies the clipboard API contract and downloaded edited text.

## Model and evidence limits

All 500 bundled suggestions have three-edge routes and no shared co-author. Native Adamic–Adar uses two-hop candidates, while BridgeFinder and Topic-Only share the >=3-hop pool. Zero overlap between these pools is structural, not evidence of recommendation quality. Fresh backtests are weaker than Adamic–Adar; the report states that outcome.

The study has 63 unique cards across five community contexts. Each method contributes its true top five, with shared candidates rated once and attributed to every selecting method. Export revision IDs bind cards to their matching private key. The supported public-asset server serves both app/study and excludes private keys/raw datasets.

All automated answers are synthetic fixtures, discarded after checks. They are not participant responses or evidence of human comprehension. Publication paths do not prove acquaintance, mentoring availability or willingness to introduce someone. Inferred topic labels are not departments.

## Reproduce

From the repository root, install `prototype/requirements.txt` and `prototype/tests/requirements.txt`; browser tests use `/usr/bin/chromium`.

```bash
python prototype/refresh_results.py
python prototype/web/prepare_web_data.py
python prototype/study/generate_cards.py
python prototype/audit_recommendations.py
python -m unittest discover -s prototype/tests -v
python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-checks
python prototype/serve.py
```

The app is `/web/` and study `/study/` on default port 8765. `refresh_results.py` replaces canonical result files, report copies and provenance manifests only after all three analyses succeed. Screenshots and the browser summary retained here document the final browser run; the paper's own 3× captures are in `midterm/review/screenshots/`.

## Author-feedback guidance update

The landing page now explains why a starting researcher must be selected and gives three steps: choose that person, open a suggestion, then review the researcher card and route. A card is explicitly defined as a profile containing topics, papers and a possible introduction. The map explains its reduced scope and community colors. These changes follow the author's reported confusion; they are software-verified, not human-retested. The report also records the existing visual overhaul, corrected tags and focused map as responses to the author's additional feedback. Ranking, generated data and empirical results are unchanged.
