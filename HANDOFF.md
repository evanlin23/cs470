# BridgeFinder: contributor handoff

BridgeFinder is a CS 470 project by **Evan Lin** and **Eric Liu**. It helps UIUC students find researchers outside a familiar professor's collaboration circle and see an observed co-authorship route to them.

## Layout

| Path | Contents |
|---|---|
| `proposal/` | Submitted proposal (unchanged) |
| `midterm/latex/main.tex` | Mid-semester report source. `midterm/midterm.pdf` is the build |
| `midterm/review/` | Rubric review, rewrite guide, supporting analysis notes, Tang source check, paper screenshots |
| `prototype/` | Model, app, study, analyses, tests. See `prototype/README.md` |
| `docs/` | Early planning: project ideas, the brokerage spec |

## Quickstart

```bash
python -m pip install -r prototype/requirements.txt
python prototype/serve.py            # http://localhost:8765/web/ and /study/
python -m unittest discover -s prototype/tests -v
```

## Current state

- **Model** `proposal-path-v3-common-neighbors`: reachable cross-community candidates at least three hops away, ranked by topic Jaccard plus `0.5*c3/(1+c3)`. Baselines are triadic closure (two-hop, shared co-author count) and Topic-Only (same pool as BridgeFinder).
- **Data**: complete OpenAlex harvest for UIUC 2015–2024, 102,947 works collected and 49,651 multi-author UIUC papers retained. The training graph (≤2019) has 19,389 authors and 78,281 edges.
- **Historical test**: 3,492 starting researchers. P@10, the proposal's only historical metric, is 0.0287 for triadic closure, 0.0131 for BridgeFinder and 0.0079 for Topic-Only. Of 8,916 new cross-community ties, 22% joined authors who already shared a co-author and 67% were three or more hops apart.
- **Feedback**: round one (four students) led to four design changes. Round two (six students) reviewed the revised app, found it clear, raised no new problems and approved of it.
- **Study**: the 15-student blinded card study is implemented but not yet run.

## Rebuild the report

```bash
python prototype/refresh_results.py          # only if data or model changed
python midterm/capture_screenshots.py        # only if the app or its data changed
mkdir -p .build/midterm
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
cp .build/midterm/main.pdf midterm/midterm.pdf
python midterm/package_overleaf.py --verify
```

Run `pdflatex` from the repository root, because figure paths are relative to it. `test_publication_consistency.py` fails if the paper's numbers, results, manifests or screenshots drift apart.

## Before submitting

Read `midterm/review/rubric-review.md`. If you reword the report, keep the facts listed in `midterm/review/rewrite-guide.md` synchronized, rebuild, and rerun the tests.
