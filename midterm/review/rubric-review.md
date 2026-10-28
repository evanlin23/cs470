# Repeated rubric review — current midterm draft

Source: uploaded `mid-term_report_CS470 (1).pdf`, checked against its extracted text. The rubric assigns integer scores 0–4 and weights each by `(score / 4) × weight`; 3 means between Sophisticated and Competent. Grammar can cost up to five percentage points when it impedes reading. The report should read as a short research paper.

**Final conservative editorial estimate: 95/100, before any instructor judgment.** This is a criterion-based estimate, not a promised grade or a statistical confidence interval. The remaining five-point reservation concerns the specificity of the feedback account. A reader who finds that account sufficient could reasonably score it 4/4; this review does not presume that outcome. Conversely, an instructor may judge other criteria more harshly. The earlier unconditional 100 claim remains withdrawn.

## Final scoring

| Criterion | Weight | Score /4 | Weighted points | Evidence and rationale |
|---|---:|---:|---:|---|
| Objective | 10 | 4 | 10 | Abstract/§1 establish the student problem, relevance-versus-discovery challenge and concise progress. The reader learns what the system contributes and what is still unproven. |
| Related work | 10 | 4 | 10 | §2 describes researcher search, two literature tools, link prediction, cross-domain recommendation, weak-tie/brokerage theory and longitudinal collaboration research. Contributions, useful features and limits for this task are explicit. §4 connects these comparisons to design decisions. Supporting data/method sources are explained in §3. |
| Course concepts and network analysis | 15 | 4 | 15 | §3 explains the graph, joint-paper weights, training-only topics, Louvain versus Girvan–Newman, community boundaries, distance and the path-based ranking. Table 1 reports actual graph sizes and modularity, interpreted with a disconnected-component caveat. The text explains what removing the network layer would remove. |
| Design and implementation | 25 | 4 | 25 | §4 gives reasons for the starting-person → map → card flow, ties them to the problem and related work, and includes actual current screenshots. The demonstrated core flow includes observed routes and editable outreach. The 50-person list and use of researcher topics as an interest proxy are explicit limitations. |
| Users and feedback | 20 | 3 | 15 | §5 identifies and justifies a relevant formative sample, reports an author-confirmed round and traces three observations to changes. However, the account remains broad: it does not describe the actual activity surrounding a specific observed problem, making feedback quality harder to assess. This is a conservative reservation about persuasiveness under “sufficient size and quality,” not an invented requirement for transcripts, quotations or a minimum sample larger than five. Authentic interaction context from the authors could strengthen it. |
| Evaluation | 15 | 4 | 15 | §6 gives justified metrics, baselines/thresholds, completed prediction results and a concrete future study. It now defines the usability task and facilitator checks, respects the actual relevance question, and distinguishes comparisons with different candidate pools from causal isolation. Participant-level analysis, exploratory comparisons and missed targets are clear. |
| Writing | 5 | 4 | 5 | The argument proceeds from student need to prior work, network method, interface, feedback, evidence and next steps. Tables/figure are referenced and interpreted. Unsupported claims of causal benefit were removed. The four-page rendered draft has readable body text and no overflowing boxes or unresolved references. |
| **Total** | **100** | | **95** | No additional reading-impeding grammar deduction identified. |

## Review loop and stopping rule

The loop stops when all identified changes supported by the existing facts have been addressed and the remaining issue requires the authors' authentic session context. It does not stop when a target number can be manufactured. No new sessions, quotations, counts, favorable results or source claims were invented.

### Pass 1: strict rubric and claim review

Conservative starting ratings were Objective 4, Related Work 3, Network Analysis 4, Design 4, Users 3, Evaluation 3, Writing 3: **87.5/100**. These are retrospective editorial ratings of the starting draft, not an instructor assessment.

Identified issues:

- The formula was called “the proposal's score,” although the proposal specified the general topic/path approach rather than that exact saturation and coefficient.
- Some related-work contrasts were grouped too broadly; Burt's two sources were not distinguished clearly.
- The source of the student's interest profile was implicit: ranking uses the selected researcher's topics.
- “Eligible” future ties could be misread as satisfying the >=3-hop rule. Ground truth also includes two-hop ties.
- The result interpretation could imply that distance alone caused poorer prediction.
- The proposed usability task did not give a sufficiently concrete completion/comprehension rule.
- The willingness-to-contact comparison suggested it isolated the route's effect, even though methods choose different candidates.

These were corrected in the paper without changing the algorithm or empirical results.

### Pass 2: check the measurement against the actual implementation

Checked `prototype/model.py`, `backtest.py`, the web exporter, study questions and participant-level analyzer against the prose.

The paper now correctly states that card relevance is to the starting researcher's work, while novelty is personal familiarity. A separate student topic profile is not implemented. The limited 50 starting researchers and five study contexts are acknowledged. The study assesses full suggestions, not an isolated path intervention. The selected researcher remains an interest proxy; the task plan does not pretend to have been run.

This pass also removed repeated wording and simplified explanation of previous UI revisions. All result values remain unchanged. The short paper keeps the three proposal baselines; the ancillary citation analysis and extra baselines are retained in analysis-notes.md and the canonical outputs.

### Pass 3: submission/readability and handoff review

Read the revised argument from the perspective of a reader unfamiliar with the code. Rechecked the rubric descriptors, claim-to-evidence links, section order, figures, tables and rendered pages. Remaining actionable writing and attribution issues were resolved. The conservative final ratings are those above.

`rewrite-guide.md` identifies what Evan and Eric should rewrite or verify, especially concrete formative-session context. Their final source interpretation and contribution/AI disclosure also need author ownership. This is a handoff for their rewrite, not a request to fabricate missing evidence.

### Pass 4: simplest sufficient paper

The user asked for substantially less complexity. The submission was rewritten as four pages with one short equation, two compact tables, one combined figure, three feedback-driven changes and three student-evaluation outcomes. The main prediction table now shows only the three methods named in the proposal. The separate citation subsection, extra baseline descriptions, detailed inferential-test names and historical autonomy discussion were removed from the main paper and retained where relevant in `analysis-notes.md` and the repository. No unfavorable primary result was hidden.

Rechecked every rubric criterion after these cuts. The objective, individual related-work contrasts, method-versus-alternative justification, real-data interpretation, full prototype flow, feedback traceability, metric reasons/thresholds/comparisons and honest conclusion remain. The shortened version retains the same conservative 95/100 estimate; added technical detail would not automatically earn the remaining feedback points.

## What is not a rubric deduction by itself

The rubric does not demand that predictions beat Adamic–Adar, that citation comparisons be significant, that the planned 15-person trial already be complete, that 110,000 papers already be harvested, or that a particular notes artifact be attached. Negative findings, a justified formative sample and candid scope limitations can still support excellent midterm work. These are limitations to discuss accurately, not automatic percentage penalties.

The feedback reservation above is about the reader's ability to assess the reported round, not a demand for a new study. Five formative sessions can be sufficient. Software tests support the implementation claims but cannot establish human usability or feedback quality.

## Verification and reproducibility

The source changes in this loop are editorial and prospective protocol clarification. Publication checks were updated to reflect the three-row table and the relocation of the ancillary citation text, while retaining numerical verification. No algorithm, dataset, study responses or numerical results were changed. Publication-consistency checks compare all 12 displayed prediction cells, seed counts, the ancillary citation note and provenance hashes. Previous model/browser verification remains applicable because implementation is unchanged.

The paper is built twice with pdfLaTeX from the repository root and checked for warnings, unresolved references and overflows. The Overleaf ZIP is separately compiled after clean extraction, with the root file named `main.tex` and matching figures. It contains no prototype datasets or private study key.

Reproduce the paper from the repository root:

```bash
mkdir -p .build/midterm
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=.build/midterm midterm/latex/main.tex
cp .build/midterm/main.pdf midterm/midterm.pdf
python -m unittest discover -s prototype/tests -p test_publication_consistency.py -v
python midterm/package_overleaf.py --verify
```
