# BridgeFinder prototype

Choose a UIUC researcher whose work you know, explore suggested connections outside their collaboration community, and open a card to see research topics, example papers, and a possible introduction route. You can edit and copy or download an outreach draft.

## Run

From the repository root, with Python 3.12:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r prototype/requirements.txt
python prototype/serve.py
```

The server defaults to port 8765. The researcher interface is at `/web/` and the study is at `/study/`. It serves the public assets only, keeping the private method key and raw datasets out of the study interface. D3 is included locally; no API keys, frontend build, or external CDN are needed.

## Main flow

1. Search by name or topic, or narrow the starting researchers by community or research area.
2. Choose someone to open the map. Solid lines show published collaborations; orange dashed lines show suggestions. Click a dashed line or a name in the adjacent list.
3. Read the suggested researcher's card and observed co-authorship route. Edit the outreach draft to reflect your actual background, then copy or download it. No email is sent.

The interface works on desktop and mobile, supports keyboard navigation, and keeps researcher selections in the URL. Research areas are keyword-based hints adapted from the teammate's labeling work; they are not verified departments. They do not alter rankings or community identities. Numbered communities come from collaboration patterns.

The precomputed data describes UIUC-affiliated publications from 2015–2019. Current employment, mentoring availability, personal acquaintance, and willingness to introduce someone need to be checked separately.

## Study

After using the research interface, a participant selects a starting researcher and rates the shuffled, method-hidden cards, then answers the ten SUS questions. Answers and card order survive a reload in the same browser tab. Participants can review earlier ratings and choose whether to download their responses. Nothing is uploaded automatically.

See [the study protocol](study/README.md) for recruitment, interpretation, and analysis. The interface and analyzer use the same dataset revision ID so exports cannot accidentally be analyzed with another method key.

## Check the happy path

```bash
python -m pip install -r prototype/tests/requirements.txt
python -m unittest discover -s prototype/tests -v
# Requires Chromium at /usr/bin/chromium. Starts and stops its own test server:
python prototype/tests/browser_workflow.py --artifacts /tmp/bridgefinder-checks
```

The browser suite covers normal desktop/mobile navigation, search and filters, all 50 researchers, actual map clicks, zoom/fit, shareable selection, an edited outreach message, study progress, and a downloaded study export analyzed with its matching method key. Test answers are synthetic and discarded; they are not user-study findings. Screenshots and the browser summary go to the chosen artifacts directory, not the report.

## Regenerate the bundled data

These commands use committed datasets and the shared temporal model. Run from the repository root:

```bash
python prototype/web/prepare_web_data.py
python prototype/study/generate_cards.py
python prototype/backtest.py --data prototype/uiuc_data.json --out /tmp/pilot-backtest.json
```

`model.py` supplies the same pre-2020 graph, training-only topic profiles, seeded partition, candidate population, and ranking weights to the demo, study, and backtest. Candidate ties resolve by author ID. The topic filter changes only the starting-person list, not those predictions.

## Earlier MethodBridge experiment

The earlier paper-transfer pilot remains in `fetch.py`, `analyze.py`, and `case_generank.json`. It uses OpenCitations/Crossref and requires network access; it is separate from the bundled-data BridgeFinder demo. Its original setup is:

```bash
MB_MAILTO=you@illinois.edu python prototype/fetch.py prototype/case_generank.json /tmp/graph.json
python prototype/analyze.py /tmp/graph.json /tmp/methodbridge-results.json
```
