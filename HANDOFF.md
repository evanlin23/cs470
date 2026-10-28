# BridgeFinder: Contributor Handoff

BridgeFinder is a CS 470 project by **Evan Lin** and **Eric Liu** that helps UIUC students discover research collaborators outside a familiar professor's collaboration circle and inspect viable introduction paths.

---

## 1. Quickstart

Run the web prototype locally using Python 3.12+:

```bash
python -m pip install -r prototype/requirements.txt
python prototype/serve.py
```

Open `http://localhost:8765`:
- `/web/` — Public researcher discovery interface (search, graph, cards, editable outreach draft).
- `/study/` — Blinded study interface for rating recommendation cards.

---

## 2. Recommendation Model & Baselines

Implementation: `prototype/model.py` (`proposal-path-v3-common-neighbors`).
- **Graph**: Multi-authored UIUC papers (2015–2019), edge weights = joint paper count, communities found via Louvain.
- **BridgeFinder**: Candidates must be in another community at shortest distance $\ge 3$. Ranked by:
  $$\text{Score} = \text{Topic Jaccard} + 0.5 \cdot \frac{c_3}{1 + c_3}$$
  where $c_3$ is the count of simple 3-hop introduction paths.
- **Baselines**:
  - *Triadic Closure*: 2-hop candidates ranked by number of shared co-authors.
  - *Topic-Only*: Candidates at distance $\ge 3$ ranked purely by topic similarity.

---

## 3. Dataset & Evaluation Results

- **Dataset (`prototype/uiuc_data_scaled.json`)**:
  - Full uncapped OpenAlex harvest (2015–2024): 102,947 works collected $\to$ 49,651 multi-authored UIUC papers across 35,593 authors.
  - Training graph ($\le 2019$): 19,389 authors, 78,281 edges, 842 communities (modularity $Q = 0.884$).
  - Evaluation graph ($> 2019$): 22,758 authors, 93,220 edges.
- **Historical Link Prediction (P@10 across 3,492 eligible seeds)**:
  - **Triadic Closure**: **0.0287**
  - **BridgeFinder**: **0.0131**
  - **Topic-Only**: **0.0079**
  *(Triadic closure predicts more future ties, but BridgeFinder discovers non-obvious connections across communities beyond shared co-authors).*

---

## 4. Formative User Feedback

We gathered feedback from four individuals in individual 30-minute sessions who talked through their use of the prototype:
- **Participants**:
  - 2 graduate students: one in Computer Science, one Master of Computer Science in Computational Biology.
  - 2 undergraduates: one in Electrical and Computer Engineering (ECE), one in Food Systems.
- **Design Changes Implemented**:
  1. *Getting Started*: Added landing page instructions clarifying that selecting a starting researcher anchors the search.
  2. *Interface & Cards*: Overhauled layouts and added clear definitions for researcher cards and introduction routes.
  3. *Readable Map*: Focused graph view on the selected researcher, top suggestions, and route intermediaries with community coloring.
  4. *Profile Labels*: Clarified inferred research keywords vs. collaboration communities (no unverified departmental claims).

---

## 5. Key Files & Useful Commands

| Path | Purpose |
| :--- | :--- |
| `prototype/model.py` | Core ranking algorithm and baselines |
| `prototype/web/` | Web application assets and data |
| `prototype/study/` | Blinded user study interface and card generator |
| `midterm/latex/main.tex` | 4-page midterm research paper |
| `midterm/midterm.pdf` | Compiled midterm report PDF |
| `midterm/bridgefinder-midterm-overleaf.zip` | Standalone bundle ready for Overleaf |

### Useful Commands

```bash
# Run unit tests (all 27 tests pass)
python -m unittest discover -s prototype/tests -v

# Refresh canonical results, web data, and study cards
python prototype/refresh_results.py
python prototype/web/prepare_web_data.py
python prototype/study/generate_cards.py

# Recompile paper PDF
tectonic -Z search-path=. midterm/latex/main.tex && cp midterm/latex/main.pdf midterm/midterm.pdf

# Package and verify Overleaf ZIP
python midterm/package_overleaf.py --verify
```
