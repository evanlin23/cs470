# Prototype happy-path validation

Scope follows the user's clarification: make the normal research-discovery and study flows work. No new recommendation algorithm or empirical performance claim was introduced.

## Fixes

- Replaced technical screen labels with Researchers → Network → Suggestions navigation.
- Replaced the generic dashboard treatment with restrained research-directory typography, flat rows, thin separators and a quieter palette. Research topics are plain text, and technical scores live in an expandable explanation instead of decorative badges.
- Fixed confirmed horizontal overflow at 390px. Desktop, tablet and mobile layouts now fit their viewports.
- Made researcher selection, suggestion lists, map links, rating choices and navigation keyboard-operable.
- Built focused maps from the selected researcher's actual candidate/path nodes. Zoom and fit keep that map in view; navigating or dragging no longer restarts an unrelated global simulation.
- Added research-area filtering using the teammate's preserved topic keyword rules. These labels are explicitly inferred topics rather than departments and do not change evaluated rankings or community IDs.
- Kept raw dataset text intact and used DOM text rendering. Names, searches and outreach messages no longer get HTML entity artifacts.
- Made the outreach draft genuinely editable, with text download and copying of the edited message. Nothing sends email.
- Preserved chosen researcher/candidate in the URL, including reload and browser back/forward.
- Added study progress restoration in the same browser tab, review of earlier ratings, preserved SUS answers and an actual export download.
- Bound study exports and private method keys to a dataset revision. The analyzer accepts the new export format and checks its attribution before computing participant-level outcomes.
- Added a simple public-asset server so normal study deployment does not serve the private method key or raw repository files.

## Verified happy paths

Command: `python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-checks`

**11 browser tests passed, 0 failures, 0 errors**, using system Chromium through Playwright. The suite starts and stops an isolated instance of the supported public-asset server.

1. Search for every starting researcher; select each community and inferred research-area filter.
2. Choose each of the **50** researchers; verify matching map links, suggestion lists and ordered cards.
3. Click an actual map link, use its keyboard equivalent, zoom, fit and show all cards again.
4. Reload a shared candidate selection and navigate back/forward without changing the selected person.
5. Edit an outreach message, copy its edited contents through the clipboard API contract, download the exact edited text, and open the draft with keyboard focus. Native clipboard permission UI itself is not automated.
6. Use the main views at **360px, 390px, 768px and 1440px** without horizontal document overflow.
7. Choose a researcher and a rating using only keyboard activation.
8. Start each of the five study contexts with the correct unique-card count and hidden method labels.
9. Reload study progress and recover card order, participant identity and earlier ratings.
10. Complete the cards and SUS, review a previous card, download the actual JSON file, and analyze that export using its matching private key. The first context has 11 unique cards representing five outcomes per method.
11. Capture desktop and mobile views for visual inspection.

Screenshots are retained in `screenshots/`. The final visual pass was inspected at desktop and mobile widths and rerun through the same happy-path suite; the ranking explanation was also opened and closed during that run. `browser-summary.json` records the completed final browser run.

## Supporting model and measurement checks

`python -m unittest discover -s prototype/tests -v`: **13 tests passed**. These include all 500 displayed rankings, real shortest-path edges, independent NetworkX verification of autonomy, hand-calculated path bonuses, study overlap attribution, training-only topic features, topic classification and participant-level analysis. The analyzer contract checks also cover malformed data; no further UI edge-case expansion was pursued after the user narrowed the scope.

The 500 recommendations still match the shared temporal model: **483 two-hop routes and 17 three-hop routes**. The topic labels and interface do not alter scoring weights, candidate eligibility, rank order or backtest results.

All automated ratings are synthetic fixtures. Browser-generated answer files and calculated study statistics remain temporary and are discarded after the test; they are not participant findings. The screenshots show the software, not evidence of a completed human evaluation.

## Reproduce the demo

```bash
python -m pip install -r prototype/requirements.txt
python prototype/serve.py
```

The app is served at `/web/`, and the study at `/study/`, on port 8765 by default. For browser checks install `prototype/tests/requirements.txt` and system Chromium. Existing report screenshots were left unchanged; these new UI captures document this prototype revision.
