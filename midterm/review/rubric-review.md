# Repeated rubric review — current midterm draft

Source: uploaded `mid-term_report_CS470 (1).pdf`, checked against its extracted text. The rubric assigns integer scores 0–4 and weights each by `(score / 4) × weight`; 3 means between Sophisticated and Competent. Grammar can cost up to five percentage points when it impedes reading. The report should read as a short research paper.

**Current rubric-based editorial assessment: 100/100 (4/4 in each criterion).** The author supplied the specific feedback context behind the previous 95/100 estimate, and the proposed landing-page instructions are now implemented and described accurately. This resolves that review's five-point reservation. It is an assessment against the rubric descriptors, not a guaranteed instructor grade. The earlier unconditional promise of 100 remains withdrawn.

## Final scoring

| Criterion | Weight | Score /4 | Weighted points | Evidence and rationale |
|---|---:|---:|---:|---|
| Objective | 10 | 4 | 10 | Abstract/§1 establish the student problem, relevance-versus-discovery challenge and concise progress. The reader learns what the system contributes and what is still unproven. |
| Related work | 10 | 4 | 10 | §2 describes researcher search, two literature tools, link prediction, cross-domain recommendation, weak-tie/brokerage theory and longitudinal collaboration research. Contributions, useful features and limits for this task are explicit. §4 connects these comparisons to design decisions. Supporting data/method sources are explained in §3. |
| Course concepts and network analysis | 15 | 4 | 15 | §3 explains the graph, joint-paper weights, training-only topics, Louvain versus Girvan–Newman, community boundaries, distance and the path-based ranking. Table 1 reports actual graph sizes and modularity, interpreted with a disconnected-component caveat. The text explains what removing the network layer would remove. |
| Design and implementation | 25 | 4 | 25 | §4 gives reasons for the starting-person → map → card flow, ties them to the problem and related work, and includes actual current screenshots. The demonstrated core flow includes observed routes and editable outreach. The 50-person list and use of researcher topics as an interest proxy are explicit limitations. |
| Users and feedback | 20 | 4 | 20 | §5 identifies and justifies the formative sample and traces observations to implemented changes. The new author-provided example explains a student's goal (find a relevant professor), obstacle (not understanding the first-screen selection), and response (explicit steps and an explanation of the interest proxy). It also connects UI confusion to the design overhaul, mismatched tags to corrected labeling, and card terminology to a new definition. The paper states that the new explanations have not been retested. This supports the rubric's collected-feedback-to-design requirement without inventing outcomes. |
| Evaluation | 15 | 4 | 15 | §6 gives justified metrics, baselines/thresholds, completed prediction results and a concrete future study. It now defines the usability task and facilitator checks, respects the actual relevance question, and distinguishes comparisons with different candidate pools from causal isolation. Participant-level analysis, exploratory comparisons and missed targets are clear. |
| Writing | 5 | 4 | 5 | The argument proceeds from student need to prior work, network method, interface, feedback, evidence and next steps. Tables/figure are referenced and interpreted. Unsupported claims of causal benefit were removed. The four-page rendered draft has readable body text and no overflowing boxes or unresolved references. |
| **Total** | **100** | | **100** | No additional reading-impeding grammar deduction identified. |

## Review loop and stopping rule

The loop stops when all identified changes supported by the available facts have been addressed. The author has now provided the previously missing interaction context, plus feedback about the interface, mismatched tags, unclear card terminology, and an overcrowded graph. It does not stop when a target number can be manufactured. No new sessions, quotations, counts, favorable results or source claims were invented.

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

Read the revised argument from the perspective of a reader unfamiliar with the code. Rechecked the rubric descriptors, claim-to-evidence links, section order, figures, tables and rendered pages. Remaining actionable writing and attribution issues were resolved. Those ratings were superseded after the author supplied the concrete example described in Pass 5.

`rewrite-guide.md` identifies what Evan and Eric should rewrite or verify, especially concrete formative-session context. Their final source interpretation and contribution/AI disclosure also need author ownership. This is a handoff for their rewrite, not a request to fabricate missing evidence.

### Pass 4: simplest sufficient paper

The user asked for substantially less complexity. The submission was rewritten as four pages with one short equation, two compact tables, one combined figure, three feedback-driven changes and three student-evaluation outcomes at that stage (the subsequent author feedback is documented in Pass 5). The main prediction table now shows only the three methods named in the proposal. The separate citation subsection, extra baseline descriptions, detailed inferential-test names and historical autonomy discussion were removed from the main paper and retained where relevant in `analysis-notes.md` and the repository. No unfavorable primary result was hidden.

Rechecked every rubric criterion after these cuts. The objective, individual related-work contrasts, method-versus-alternative justification, real-data interpretation, full prototype flow, feedback traceability, metric reasons/thresholds/comparisons and honest conclusion remain. At this stage the estimate remained 95/100; added technical detail would not address the remaining feedback concern.

### Pass 5: author-provided interaction context and implemented guidance

The author explained that a student trying to find a relevant professor did not realize they had to select a researcher on the first screen as the entry into the graph. The author proposed clearer landing-page descriptions and steps; they did not claim those instructions had already been added or tested. We implemented a plain three-step guide on the first screen and explained that the selected researcher's publications determine the suggestions. §4 describes the guidance and §5 ties it to the observed confusion, with an explicit statement that the revision has not been retested with students.

The author additionally reported that the UI was unintuitive (leading to the completed design overhaul), that tags did not match professors (a completed mechanical correction), and that the meaning of a card was unclear (leading to a newly implemented profile definition). The author also identified excessive graph nodes as a usability problem; the current map reduces the display to the selected researcher, suggestions and route intermediaries while retaining community colors. The paper separates these existing fixes from the newly added explanations and does not claim the latter have been retested. Labels remain inferred research areas and collaboration groups, not verified departments.

Reassessed Users and Feedback against its actual descriptor: a matched and justified formative population, a collected feedback round, and a concrete effect on design are now clearly supported. It receives 4/4 in this editorial review, taking the weighted estimate from 95 to 100. This does not certify the user sessions independently or establish post-revision usability. It also does not override the instructor's judgment.

### Pass 6: fresh review after all author feedback

Reread the actual rubric and current source without treating the previous score as evidence. Checked the graph/ranking definitions against `model.py`, baseline pools and ground truth against `backtest.py`, the student rating questions against the study interface, and current labels/papers against the web exporter. Publication checks verify all published values and provenance.

Three small ambiguities were corrected: the historical improvement targets now explicitly name Adamic–Adar as their comparison; relevance/novelty and willingness-to-contact thresholds explicitly apply to BridgeFinder; and Adamic–Adar is described as ranking candidates with shared co-authors. These edits change no method or outcome. The visual pass also caught the first evaluation bullet splitting across pages; space is now reserved so it stays together.

The criterion assessment remains 4/4 in each category under the supplied descriptors. The objective and progress are clear; related work has task-specific contrasts; the network method is justified against an alternative and interpreted on real data; the prototype demonstrates its full flow; author-confirmed feedback now has concrete observation-to-change links; and evaluation names measures, comparisons, thresholds and collection plans. The argument and figures are explained. The grade remains an editorial judgment, not an instructor commitment. No deduction was added for unfavorable results or for not yet running a study explicitly described as future work.

The paper remains deliberately short. Remaining limits are empirical rather than missing prose: no student retest of the new explanations, no completed comparative study, and no confirmation that publication paths imply acquaintance or mentoring availability. These are stated in the submission. Inspecting the PDF does not validate the author-reported sessions independently.

### Pass 7: structure and paragraph-level rewriting support

Compared the section order directly with every rubric component. Sections 1–6 follow the rubric order; §3 now explicitly names Course Concepts as well as Network Analysis and states the brokerage idea before defining the graph. Writing applies across the whole paper, so it is not a standalone content section. The abstract and short closing section support the required short-paper form.

Added source-only paragraph-purpose comments in `main.tex` and a section-to-criterion map in `rewrite-guide.md`. These make it possible for the authors to keep the structure while rewording each paragraph. They do not add visible audit material to the submission. The method alternative, real-data interpretation, design rationales, formative-sample justification, feedback-to-change links, and evaluation comparisons/thresholds remain; none was removed for brevity. Extra statistics remain in the supporting notes. Numerical results, methods, and study status are unchanged.

## What is not a rubric deduction by itself

The rubric does not demand that predictions beat Adamic–Adar, that citation comparisons be significant, that the planned 15-person trial already be complete, that 110,000 papers already be harvested, or that a particular notes artifact be attached. Negative findings, a justified formative sample and candid scope limitations can still support excellent midterm work. These are limitations to discuss accurately, not automatic percentage penalties.

The former feedback reservation concerned the reader's ability to assess the reported round, not a demand for a new study. Five formative sessions can be sufficient. Software tests support the implementation claims but cannot establish human usability or feedback quality.

## Verification and reproducibility

Most changes in this loop are editorial and prospective protocol clarification. Pass 5 additionally adds first-screen instructions and reruns browser checks. Publication checks were updated to reflect the three-row table and the relocation of the ancillary citation text, while retaining numerical verification. No algorithm, dataset, study responses or numerical results were changed. Publication-consistency checks compare all 12 displayed prediction cells, seed counts, the ancillary citation note and provenance hashes. Model verification remains applicable because the ranking is unchanged. Browser verification is rerun for the landing-page change.

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
