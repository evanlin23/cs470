# Proposal-stage handoff: BridgeFinder (CS 470, Fall 2026)

Written 2026-11-19 by session `session_015pLTPGXGuzNB2XWkYefWEY` (the brainstorming/proposal session, active Oct 1–2, 2026) for the session writing the **final report**. Team: **Evan Lin** and **Eric Liu**.

Sources:
- this session's conversation with Evan;
- the repo;
- the course page and rubric PDFs, **re-fetched 2026-11-19**.

Anything not verified is marked as such. For midterm-stage context (the model, dataset, results and the four-person study), see `HANDOFF.md`, which another session wrote.

---

## 0. The short version

- **Due:** final report **and** a 10-minute video, Wed **Dec 9, 2026, 5:00pm**.
- **Report format:** 10–12 pages plus unlimited references, "standard ACM conference style format", and it should "read like a research paper ready for submission".
- **Weights within the project grade:** proposal 5%, mid-semester 25%, **final report 35%, presentation 35%**.
- **Partners (new on the course page since Oct 2):** groups of at most two, with identical deliverables and both names. **From the mid-semester report on, each deliverable ends with a short statement of who did what.** Group size is taken into account when grading the prototype and the evaluation.
- **The submitted proposal** is commit `6c5cb92` (2026-10-27, by evanlin23): `proposal/latex/main.tex` and `proposal/proposal.pdf`. Its commitments are quoted verbatim in §5.
- **Main tension the final must handle candidly.** The proposal's falsifiable claim says BridgeFinder beats triadic closure *and* topic-only on new cross-community collaborations. The midterm numbers in `HANDOFF.md` show triadic closure ahead on P@10 (0.0287 vs 0.0131). The final report rubric rewards being "candid about where the network analysis performed poorly, and why". Check exactly which set of ties the midterm evaluated (all new ties, or cross-community ones as the proposal specified) before writing the claim's verdict.
- **Proposal grade or instructor feedback:** **none was ever shared with this session.** Ask Evan.

---

## 1. Course requirements (verbatim from the course page, fetched 2026-11-19)

Source: https://sundaram.cs.illinois.edu/CS470.html

**4-credit project:**
> Four credits students have the opportunity to dive deeper into the topics discussed in class through developing a functional app related to any topic relevant to the class. For example, build a new social media app focused on say privacy concerns, develop an agentic moderation system, or develop a better social media feed construction algorithm that supports greater user engagement while reducing the spread of AI slop. The expectation is that the prototype is mature and ready to be put into development. Here are two examples of app development projects [App 1], [App 2].

> Four-credit students may do the project individually or in a group of at most two. Partners submit identical deliverables with both names on each, and from the mid-semester report on, each deliverable ends with a short statement of who did what. Both partners receive the same project grade, and when we grade the prototype and the evaluation, we take the size of the group into account. Within the project grade, the proposal counts for 5%, the mid-semester report 25%, the final report 35% and the presentation 35%.

On Oct 2 the page said nothing about partners; this session checked at Evan's request. That paragraph is new. The two example reports are https://sundaram.cs.illinois.edu/Example_reports/App_do_dates.pdf and https://sundaram.cs.illinois.edu/Example_reports/App_route_sharing.pdf. Both are CS 514 reports, strong on user research but weak on network analysis.

**Deliverables:**
> Project proposal (4-credit only): 1 page, with additional space for unlimited references. The project proposal should discuss the problem that you wish to tackle in the project. It should read like an extended abstract, explaining what problem you want to tackle and why it is important/urgent to address. Discuss past approaches to tackling the problem, and provide a sketch of what you plan to do and how you plan to evaluate your solution. In particular, discuss your plan to evaluate your design with users.

> Mid-semester report (4-credit only): 4-5 pages, with additional space for unlimited references. The mid-semester report should contain details of the work done, including completed related work, the preliminary idea for the solution, and a detailed assessment methodology, including baselines to evaluate the proposed idea.

> Final project report (4-credit only): 10-12 pages, with additional space for unlimited references. This final report should be written in a standard ACM conference style format and read like a research paper ready for submission. If you are developing a system, a demonstration of the final working system (i.e. a functional design prototype on Figma) is expected during the final presentation.

> Final presentation (4-credit only): A 10 minute video recording that motivates the problem, walks through the working prototype end to end, reports what user feedback changed and what the evaluation showed.

**Dates:**
> Final project (4-credit): Project proposal due Friday, Oct. 2nd at 5:00pm; mid-semester report due Friday, Oct. 30th at 5:00pm; final project report and presentation (as a 10 minute video recording) due Wednesday, Dec. 9th, 2026 at 5:00pm, the last day of class.

Also on the calendar: Long Homework Part B is due Fri Nov 20 at 5:00pm, Short Exam #6 runs Tue Dec 1 – Thu Dec 3, Thanksgiving break is Nov 21–29, and the final exam window is Dec 10–16.

**Grading:** the final project is 25% of the course grade for 4-credit students, submitted on Gradescope, split as above (5/25/35/35).

**Late policy (applies to the project):**
> All assignments are due at the date and time marked for the Assignments. Late submissions will not be accepted except in the case of documented emergencies or religious absences approved in advance.

**Generative AI policy (verbatim):**
> Use of generative AI technologies is allowed and encouraged in this class, provided you engage with them critically and transparently. […] When you use AI tools for course assessments (homework, projects), you must demonstrate that you understand the underlying concepts and can critically evaluate AI-generated content.
>
> Your Obligation: clearly documenting when and how you used AI, verifying any claims or code the AI produces, and being able to explain your reasoning independent of the tool. […]

The submitted proposal's statement was: *"AI Use: We used Claude as a collaborator to brainstorm ideas, and create an initial draft. Everything was reviewed and verified."*

**Rubrics:** all four are reproduced verbatim in **Appendix A**. The PDFs fetched on 2026-11-19 are the same byte sizes as on Oct 2 (proposal 49,535; mid-term 50,515; final 50,536; presentation 53,765), so they are very likely unchanged.

Key points of the **final report** rubric (scored 4/3/2/1/0; component weight × score ÷ 4):

| Component | Weight |
|---|---|
| Objective | 10% |
| Related work | 10% |
| **Course concepts & network analysis** | **20%** |
| Design & implementation | 20% |
| Users & feedback | 15% |
| **Evaluation** | **20%** |
| Writing | 5% |

Up to 5% is deducted for spelling or grammar errors that impede reading.

Phrases that decide a 4 on that rubric:
- **Course concepts:** "justified against at least one alternative covered in class, with evidence rather than assertion"; "candid about where the network analysis performed poorly, and why". The 1-level description is "removing the network analysis would not change what the app does".
- **Users & feedback:** "Several rounds of feedback are reported, including what users actually did with the prototype, and the report shows how the design changed across rounds."
- **Evaluation:** "Results are reported against those metrics and against a named baseline … and the authors are candid about what did not work". The gaps it penalizes include "the metrics reported are not the ones proposed".
- **Form:** "Write it as a short paper … Imagine submitting it to a venue such as CHI."

The **presentation** rubric weights are:

| Component | Weight |
|---|---|
| Organization | 10% |
| Content | 25% |
| Course concepts | 15% |
| **Demonstration** | **30%** |
| Slide & visual design | 10% |
| Delivery | 10% |

For the demonstration, a 4 needs the "core user flow shown end to end … tied back to the design decisions".

---

## 2. Template, LaTeX and Overleaf notes

- **Class:** `\documentclass[sigconf,nonacm]{acmart}` with `\settopmatter{printacmref=false, printfolios=false}`. The bibliography uses `ACM-Reference-Format`. The figure is TikZ (`\usepackage{tikz}`, `\usetikzlibrary{positioning,arrows.meta,calc}`), drawn as grayscale wireframes in `proposal/latex/figure/flow.tex`.
- **Overleaf:** Evan and Eric compile on Overleaf. On Oct 2, Overleaf's log showed TeX Live 2026 and **acmart v2.18**. This session also tested against acmart **v2.20**, built from CTAN source. Things that bit us:
  - **acmart ≥ 2.18 raises an error** at `\end{document}` if `\section`, `\subsection`, `\subsubsection`, `\paragraph` or `\baselinestretch` (including `\linespread`) is redefined. Don't tighten headings or line spacing.
  - v2.20 also warns whenever `\vspace` is used for layout.
  - It warns if a figure lacks `\Description{...}`, which is accessibility text and invisible on the page. Add one to every figure.
  - It warns "Do not put several addresses in the same \email macro". The proposal avoided this with a single `\author{Evan Lin (…) \quad Eric Liu (…)}` line and one shared `\affiliation`.
  - The braces in `\email{{a, b}@…}` render differently across acmart versions; avoid that form.
  - "No city present for an affiliation" is harmless. Adding `\city{}` costs a full line.
- **Margins:** to fit one page, the proposal shrank them with `\geometry{top=20pt, bottom=20pt, inner=34pt, outer=34pt, columnsep=1pc}` and scaled the figure to 74%. **Drop that for the final.** Use the stock sigconf geometry, since the final is supposed to be "standard ACM conference style".
- **Midterm bundle:** the midterm session made an Overleaf bundle, `midterm/bridgefinder-midterm-overleaf.zip`, built by `midterm/package_overleaf.py`. Reusing that flow for the final is probably easiest.
- **Bibliography:** in the submitted proposal, Evan replaced the `nielsen1993` entry with Nielsen's 1993 book *Usability Engineering* (Morgan Kaufmann), cited for "five to ten testers are enough to surface most usability problems". Check that the claim matches whichever Nielsen source the final cites.

---

## 3. How the project got here (proposal stage)

1. **Brainstorm (`project-ideas.md`).** Eight ideas ranked against the rubrics. Evan chose an earlier idea of his own: finding methods from other departments that could be used in a research area. That became **MethodBridge**: method papers across structural holes in the citation graph.
2. **MethodBridge pilot. It failed, and that drove the pivot.**
   - **OpenCitations, GeneRank case, graph frozen at 2004** (`prototype/results/generank_opencitations.json`):
     - 0 of 600 walk candidates were the PageRank/HITS targets.
     - Louvain found Q = 0.51 in 1.5 s on 610 nodes. Girvan–Newman found no useful split of a 150-node subgraph in 148 s (Louvain Q = 0.43 on the same subgraph).
     - MethodBridge's "methods across the hole" were just other biology subfields: lab protocols, BLAST, CLUSTAL.
   - **OpenAlex, 4 cases** (branch `claude/methodbridge-openalex-pilot`, `prototype/RESULTS_OPENALEX.md`):
     - MethodBridge beat no baseline.
     - In 3 of 4 cases the walk never reached the target. For GeneRank, 0 of 3,111 pre-2005 citers of the seeds cited PageRank/HITS.
     - In the 4th case (PageRank into bibliometrics), in-degree ranked the targets 18 and 23; MethodBridge ranked them 465 and 470.
   - **Lesson:** a true structural hole has no citation path across it, so walking citations can't cross it.
3. **The pivot, in Evan's words (paraphrased):** instead of finding a hole from a prompt, find the professors or people who do similar research but have no connections within your space, so you can act as a broker. Also, ideally, a place to just look at a graph and find your structural holes. The spec is in `docs/idea-brokerage.md`.
4. **Independent review** (branch `claude/brokerage-review`, `review/REVIEW.md`; review session `session_01UXUUTupULeCVBBZtytfdpK`). Verdict: **GO-WITH-CHANGES**.
   - **Data:**
     - The full UIUC OpenAlex corpus for 2015–2024 (109,471 works) cost $0.0575 to download.
     - The graph has 41,295 authors and 139,010 edges (papers with ≤ 25 authors).
     - Louvain on the core found Q = 0.83 and 52 communities.
   - **Defects found:**
     1. The planned "brokerage gain" (Δ Burt constraint) is constant for every candidate at distance ≥ 3, so it does nothing.
     2. The original claim, that far pairs collaborate more than friend-of-friend pairs, was already false. Friend-of-friend pairs form new ties 3–8× more often, and triadic closure's P@10 was 0.076 vs 0.023.
     3. Undergraduates with no papers and no advisor give the network nothing to work with.
   - **Suggestions:**
     - Use warm-intro path counts as the network feature.
     - Compare against topic-only on the distance ≥ 3 pool, with a held-out split.
     - Reuse the same 8–12 people across rounds.
     - Drop the "follow-up on emails sent" idea.
     - Never show other people's constraint scores.
     - Show ORCID and the most recent paper on cards, because of disambiguation.
     - Filter recommendations to people with UIUC work in the last two years, since 47% of 2015–19 regulars had left.
   - **Citation impact:** papers from new distance-≥3 ties were cited *less* than papers from new friend-of-friend ties (median 0.59 vs 0.72, p = 1e-11). So the proposal **dropped** the "cross-community papers are cited more" half of the claim.
   - ⚠ The review cites "DeepConnect (Feng et al., arXiv 2608.05134, 2026)" and "Noor et al., arXiv 2607.04529". **This session never verified these.** Check them before citing.
5. **User-group decisions (Oct 2, with Evan):**
   - **Who:** UIUC students who liked a class and want to do research in that area.
   - **Entry point:** students attach to the graph through the **professors whose classes they enjoyed**, which act as weak ties. Recommendations are researchers with similar topics *outside those professors' circles* (distance ≥ 3), plus *who could introduce them*: shared co-authors on a length-3 path (You → Prof → co-author → target).
   - **Testers:** friends and classmates, about 10, reused across rounds, with **blind** ratings.
   - **No real outreach:** nobody actually emails anyone. "Usefulness" is a stated-intent survey question.
6. **Scope edits Evan asked for before submitting:**
   - The proposal does *not* name Louvain or Lesson 10, because community detection hadn't been taught yet (Lesson 10 was Nov 4). It says "Researchers who co-author densely with each other form research communities." The final can name the method.
   - The Objective was the partner's section. The Gray Book figure ("2,574 professor-titled faculty across 110 departments") came from the partner; this session confirmed the Gray Book exists but **not the number**.

---

## 4. Proposal feedback

**None received in this session.** No grade, rubric scores or TA/instructor comments were ever shared here. If they exist, they're on Gradescope; ask Evan. The midterm session may know more.

---

## 5. What the submitted proposal committed to (verbatim from commit `6c5cb92`)

**Core concept and claim (Course Concepts):**
> Our project centers on the core concept of **brokerage**, which emphasizes the importance of weak ties that act like local bridges, passing information between two disconnected groups. We will build a graph where the nodes are UIUC researchers in OpenAlex, and the edges are co-authorships, weighted by the number of joint papers. In addition, each node will be tagged with the OpenAlex topics that the researcher works on. Researchers who co-author densely with each other form research communities. For a student, we rank researchers at least three steps away by topic similarity, boosted by the number of introduction paths to them. An alternative we considered was triadic closure, but it only finds people already within your network, so it cannot surface new research topics. Our falsifiable claim is that, using only papers from 2015 to 2019, BridgeFinder ranks the actual partners of new cross-community collaborations in 2020 to 2024 higher than triadic closure or topic-only ranking.

**Proposed work:**
> We will create a web app with at least the three screens shown in Figure 1; the core flow is described in Section 5. To create the campus map, we will write a Python program to preprocess the UIUC co-authorship graph from OpenAlex (around 110,000 papers from 2015 to 2024).
> **By Oct 30:** We will have the preprocessed graph and communities, version 1 of the app, and feedback from round 1. **By mid-Nov:** We will have the researcher cards, introduction paths, and the round 2 feedback. **By Dec 9:** We will polish the app, and record the final evaluation and video.

> **Assumptions:** the co-authors of papers know each other; OpenAlex correctly identifies people; the OpenAlex topics correctly capture what a researcher worked on; professors who teach a class do research in the corresponding area. The app can't actually tell if a professor is taking students, so it should just be used as a suggestion about people to talk to.

**Preliminary design** (Figure 1 has three screens: campus hole map, people across the hole, researcher card):
> The core flow of the app follows Figure 1. The student first picks the professors from classes they enjoyed. Then, the map will show their research communities and holes between them. Alongside this, the app will also display a ranked list of researchers across those holes, and each of the researchers can be clicked to open a researcher card that shows their matching papers and the introduction path. Unlike previous work such as Illinois Experts or Google Scholar, which all start with a search box, we collect the user's interests, then show the map first so users can see where the gaps are as well as the overall research landscape. Additionally, we provide reasoning for each suggestion.

**Users:**
> Our target user group is UIUC students who liked a class and want to do research in the topic the class covered. A student will be attached to the graph through the professors whose class they enjoyed, and the app will be able to find researchers with similar work (but outside of the professors' circles) along with who could introduce them. We will try to recruit around 10 people (friends and classmates looking for a research position) to test the app through each of the rounds; five to ten testers are enough to surface most usability problems, and our larger-scale claims rest on the backtest.

**Evaluation:**
> (1) **Backtest:** Looking at the data from 2015 to 2019, we will predict the top 10 relevant people for each researcher using different methods (our method, triadic closure, topic only). We then count how often those people include someone in a different community who they actually started working with in 2020 to 2024.
> (2) **Blind rating:** We will give each participant around 15 researcher cards (name, department, recent papers), five from each method. These will be shuffled so they don't know which method produced them. They then rate each researcher based on relevance of their work to their interests, and whether they knew the person already. Our method succeeds if more of its cards are both relevant and new to the participant.
> (3) **Usefulness:** We will also survey if our users would feel comfortable enough to contact the suggested people, compared across the three methods.

**Related work cited:**
- Illinois Experts, Google Scholar;
- Barley et al. 2025 (*PLOS ONE*, doi 10.1371/journal.pone.0322943; verified);
- Dahlander & McFarland 2013 (*ASQ* 58(1)); Tang et al. 2012 (KDD, cross-domain collaboration recommendation via topic model; verified);
- Liben-Nowell & Kleinberg 2007 (link prediction); LinkedIn "People You May Know";
- Granovetter 1973; Burt 2004; OpenAlex (Priem et al. 2022); the Gray Book.

**Promises to check against the final:**

| Promise | Where it stands, per `HANDOFF.md` (verify) |
|---|---|
| Backtest P@10, with all three baselines, on cross-community ties | Reported P@10 is TC 0.0287 > BF 0.0131 > topic 0.0079 |
| Blind-card study, ~15 cards, 5 per method | `prototype/study/` exists |
| Usefulness question, compared across methods | — |
| ~10 testers × 3 rounds | Midterm reports 4 participants, one round |
| Researcher cards with matching papers and introduction paths | — |
| Map-first flow | — |
| "Reasoning for each suggestion" | — |
| AI-use statement | — |
| Who-did-what statement (now required by the course page) | — |

If any promise can't be met, the rubric's "metrics reported are not the ones proposed" penalty applies, so say so explicitly and explain why.

---

## 6. Evan's style rules and preferences (stated in this session)

- **LaTeX, not HTML/Markdown, for papers** ("can we use latex instead? PLEASE"). Use the ACM `acmart` class.
- **Figures in LaTeX/TikZ**: concise, **no colors** (grayscale), readable at print size. He disliked the HTML-rendered figures and found an early dense draft "unreadable".
- **Content first, length second.** He explicitly said not to over-index on the page limit until the content was right.
- **His own words.** He and Eric write sections in their own words. Edit minimally, keep their voice, and don't rewrite a partner's section without asking. On the proposal, the partner owned Objective (and drafted Course Concepts and Related Work); Evan owned Proposed Work, Preliminary Design, Users and Evaluation.
- **Plain explanations, one part at a time.** He asks "is this good enough?" often; answer directly against the rubric, briefly.
- **Show a diff after making changes.**
- **Commits:** every commit ends with both co-author trailers:
  ```
  Co-authored-by: Evan Lin <113861384+evanlin23@users.noreply.github.com>
  Co-authored-by: Eric Liu <143140470+e-liuu@users.noreply.github.com>
  ```
  He asked for this mid-session, so this session's first two commits (`175ce54`, `51f907d`) lack them; rewriting them was blocked.
- **Git:** don't push to `main`, don't open PRs.
- **Only cover what's been taught.** Don't name course material that hasn't been covered yet (this is why Louvain was cut from the proposal).
- **User study ethics:** no real outreach emails; testers are friends; never show other people's network scores.

---

## 7. Things not in git

| Item | Status |
|---|---|
| OpenCitations response cache (~437 MB) and graph for the GeneRank pilot | Lost when the container was rebuilt; re-creatable with `prototype/fetch.py` (keyless, slow). The analysed result is in git. |
| Course page and rubric PDFs | Not committed; re-fetchable (URLs below); text verbatim in Appendix A. |
| acmart v2.20 test build | Lost; rebuild from https://mirrors.ctan.org/macros/latex/contrib/acmart.zip with `latex acmart.ins`. |
| OpenAlex API key | Stored as the environment variable **`OPENALEX_API_KEY`** in the cloud environment (value never seen or logged). Free tier is $1/day, resetting at midnight UTC; list requests cost about $0.0001, searches about $0.001. |
| Other sessions from the proposal stage | `session_01BLt9ic4UosE8Qdk1cN3MWJ`: MethodBridge OpenAlex pilot, branch `claude/methodbridge-openalex-pilot`. `session_01UXUUTupULeCVBBZtytfdpK`: independent review, branch `claude/brokerage-review`. |
| Other remote branches I know nothing about | `claude/admiring-fermi-fxjd1r`, `claude/stoic-dijkstra-ruvpga` |

**Links:**
- Course page: https://sundaram.cs.illinois.edu/CS470.html
- Rubrics: https://sundaram.cs.illinois.edu/Rubrics/proposal_CS470.pdf, https://sundaram.cs.illinois.edu/Rubrics/mid-term_report_CS470.pdf, https://sundaram.cs.illinois.edu/Rubrics/final_report_CS470.pdf, https://sundaram.cs.illinois.edu/Rubrics/presentation_CS470.pdf
- Readings: https://sundaram.cs.illinois.edu/CS470_readings.html
- Gray Book: https://bot.uillinois.edu/resources/gray_book/

---

## Appendix A: Rubrics, verbatim (`pdftotext -layout` of the PDFs, fetched 2026-11-19)

The table layout is preserved as the PDF text extraction gives it.

### Proposal rubric

Source: https://sundaram.cs.illinois.edu/Rubrics/proposal_CS470.pdf

```text
Scoring. Each component is scored 4, 3, 2, 1, or 0. Award 3 when the work sits between Sophisticated and Competent, and 0
when the component is absent altogether. A component contributes (score ÷ 4) × weight to the grade.
Spelling and grammar are not a component. Up to 5% is deducted from the total for errors that impede reading.


 Components            Weight Sophisticated (4)                        Competent (2)                          Not Yet
                                                                                                              Competent (1)


 Objective             10%         The problem the app addresses       The problem is clearly stated,         The problem has to be
                                   is clearly stated, and the reader   but the reader is left to supply       inferred from the text,
                                   understands who has this            the motivation: who has the            and no motivation is
                                   problem and why it matters.         problem, or why it matters, is         offered.
                                                                       asserted rather than
                                                                       established.


 Related work          10%         Sources are chosen carefully        Related work is present but            Little or no related work
                                   and are thematically related to     uneven: sources are listed             is cited, or citations
                                   the app. Each existing app or       without summary, or an obvious         appear without any
                                   paper is summarized concisely,      comparable app or a central            discussion.
                                   and the proposal says what this     paper is missing, or the contrast
                                   project would do differently.       with this project is left implicit.


 Course concepts 15%               The app's core function rests on    A course concept is named and          The app has a social or
                                   a specific concept from the         plausibly connected to the app,        networked theme, but
 and network
                                   course, and the proposal names      but one of the three supporting        no course concept is
 analysis                          it.                                 elements is missing: no                identified, and nothing
                                    • The choice of method is          alternative is considered, or the      in the proposal would
                                      argued against at least one      data source is unspecified, or         require network
                                      alternative covered in class     the expected finding is stated         analysis to build.
                                                                       so loosely that any result would
                                    • The data the analysis will run
                                                                       confirm it.
                                      on, and where it comes from,
                                      are stated
                                    • What the analysis is expected
                                      to reveal is stated as a claim
                                      that could turn out to be
                                      false


 Proposed work         20%         There is clarity on what will be    The final deliverable is               There is little clarity on
                                   built and what the finished         identifiable, but one element is       what is being
                                   prototype will do.                  missing: the scope is optimistic       proposed. The
                                    • The scope of the work is         for a single semester, or              deliverable is unclear,
                                      realistic for one semester       assumptions are left implicit.         the scope is unrealistic
                                                                                                              or undefined, and no
                                    • Assumptions made in
                                                                                                              assumptions are made
                                      pursuing the work are stated
                                                                                                              explicit.
                                      explicitly


 Preliminary           15%         An initial design for the app is    An initial design is proposed,         No design is proposed.
                                   proposed and justified in the       but it is justified thinly, or it is
 design
                                   context of prior work. Key          described in prose without
                                   screens or interactions are         enough detail for the reader to
Components   Weight Sophisticated (4)                     Competent (2)                         Not Yet
                                                                                                Competent (1)

                     sketched, and the core user          picture the app.
                     flow can be followed end to
                     end.


Users        15%     The population to evaluate the       A population is identified, but       Potential users have not
                     app is identified, well matched      one element is missing: the           been identified.
                     to the problem, and of sufficient    choice is not justified, or it is
                     size and quality; the authors        unclear whether it is of sufficient
                     justify the choice and describe      size or quality, or there is no
                     how they will reach these users.     plan for reaching them.


Evaluation   10%     Several metrics are proposed;        Metrics are proposed but not          No metric is provided.
                     each is justified, and it is clear   justified, or no point of
                     how each would be measured           comparison is named, so it is
                     with real users. A point of          unclear what would count as
                     comparison — a baseline              success.
                     method or a prior iteration — is
                     named.


Writing      5%      The report carries a clear           The argument is mostly                There is no
                     argumentative line from the          followable, but the reader has        argumentative line; the
                     problem to the conclusion.           to reconstruct parts of it: some      report reads as a
                     Every figure, screenshot, or         figures are presented without         sequence of
                     interface mockup is referred to      explanation, or a few claims are      disconnected sections.
                     in the text and explained, and       asserted without supporting           Figures are
                     the conclusions are supported        evidence.                             unexplained, or the
                     by the evidence presented.                                                 conclusions do not
                                                                                                follow from the
                                                                                                evidence presented.
```

### Mid-semester report rubric

Source: https://sundaram.cs.illinois.edu/Rubrics/mid-term_report_CS470.pdf

```text
Scoring. Each component is scored 4, 3, 2, 1, or 0. Award 3 when the work sits between Sophisticated and Competent, and 0
when the component is absent altogether. A component contributes (score ÷ 4) × weight to the grade.
Spelling and grammar are not a component. Up to 5% is deducted from the total for errors that impede reading.
Form of the report. Write it as a short paper: an opening that states the problem and what you contribute, related work, a
description of the system, and an evaluation. Imagine submitting it to a venue such as CHI.


 Components             Weight Sophisticated (4)                         Competent (2)                        Not Yet
                                                                                                              Competent (1)


 Objective              10%         The goal of the project is clearly   The goal is stated, but one of       The goal has to be
                                    stated; the reader grasps both       the three supporting elements        inferred from the text.
                                    why the work matters and why         is thin or missing: why it           Neither the importance
                                    the problem is challenging; and      matters, why it is challenging, or   nor the challenge is
                                    the report opens with a concise      the summary of progress.             established, and there
                                    summary of what has been built                                            is no summary of
                                    so far.                                                                   progress.


 Related work           10%         Sources are chosen carefully         Related work is present but          Little or no related work
                                    and are thematically related to      uneven: sources are                  is cited, or citations
                                    the app being built. For each        summarized without assessing         appear without any
                                    paper or existing app there is a     strengths and weaknesses, or         discussion.
                                    concise summary of its               an obvious comparable app or
                                    contribution, its strengths and      a central paper is missing, or
                                    weaknesses are identified, and       the contrast with this project is
                                    the contrast with this project is    left implicit.
                                    explicit.


 Course concepts 15%                The app's core function              The course concept is present        No course concept is
                                    demonstrably rests on a              in the implementation, but one       meaningfully present.
 and network
                                    concept from the course,             of the three supporting              The app could be built,
 analysis                           described in enough detail to        elements is missing: the             and would behave the
                                    see how.                             method is used as a black box        same way, with the
                                     • The method is justified           without justification, or the        network analysis
                                       against an alternative            analysis has been run only on        removed.
                                       covered in class                  toy data, or results are reported
                                                                         without interpretation.
                                     • The analysis has been run on
                                       real or realistic data, and
                                       preliminary results are
                                       reported
                                     • The report says what those
                                       results reveal about the
                                       network, not only that the
                                       code runs


 Design and             25%         There is a careful discussion of     The goals and functionality are      While there are ideas
                                    the goals and functionality of       described and the design             for the app, little has
 implementation
                                    the app, and the design              seems sound, but the reasoning       been built, and the
                                    decisions are traced back to the     behind the decisions is thin, or     design cannot be
                                    problem and to related work.         the prototype covers only            evaluated from what is
                                    The prototype is far enough          fragments of the intended flow.      presented.
Components   Weight Sophisticated (4)                      Competent (2)                         Not Yet
                                                                                                 Competent (1)

                     along that its core flow can be
                     demonstrated.


Users and    20%     The population to test the app        A user population is identified,      Users are not yet
                     is identified, well matched to        but the choice is not justified, or   identified and no
feedback
                     the problem, and of sufficient        feedback was gathered — from          attempt was made to
                     size and quality, and the choice      peers or a survey — without the       solicit human feedback,
                     is justified. At least one round of   report showing how it changed         casting doubt on the
                     feedback has been collected,          the design.                           app's ecological
                     and the report shows what it                                                validity.
                     changed in the design.


Evaluation   15%     Several metrics to evaluate the       Metrics are presented, but the        No effort to evaluate
                     app are presented; each is            plan is incomplete: it is unclear     the quality of the
                     justified, and there is a concrete    what would count as success, or       proposed app.
                     plan for measuring them,              no baseline is named.
                     naming the baseline or point of
                     comparison each will be
                     measured against.


Writing      5%      The report carries a clear            The argument is mostly                There is no
                     argumentative line from the           followable, but the reader has        argumentative line; the
                     problem to the conclusion.            to reconstruct parts of it: some      report reads as a
                     Every figure, screenshot, or          figures are presented without         sequence of
                     interface mockup is referred to       explanation, or a few claims are      disconnected sections.
                     in the text and explained, and        asserted without supporting           Figures are
                     the conclusions are supported         evidence.                             unexplained, or the
                     by the evidence presented.                                                  conclusions do not
                                                                                                 follow from the
                                                                                                 evidence presented.
```

### Final report rubric

Source: https://sundaram.cs.illinois.edu/Rubrics/final_report_CS470.pdf

```text
Scoring. Each component is scored 4, 3, 2, 1, or 0. Award 3 when the work sits between Sophisticated and Competent, and 0
when the component is absent altogether. A component contributes (score ÷ 4) × weight to the grade.
Spelling and grammar are not a component. Up to 5% is deducted from the total for errors that impede reading.
Form of the report. Write it as a short paper: an opening that states the problem and what you contribute, related work, a
description of the system, and an evaluation. Imagine submitting it to a venue such as CHI.


 Components             Weight Sophisticated (4)                         Competent (2)                        Not Yet
                                                                                                              Competent (1)


 Objective              10%         The goal of the project is clearly   The goal is stated, but one of       The goal has to be
                                    stated; the reader grasps both       the three supporting elements        inferred from the text.
                                    why the work matters and why         is thin or missing: why it           Neither the importance
                                    the problem is challenging; and      matters, why it is challenging, or   nor the challenge is
                                    the report opens with a concise      the summary of what was built.       established, and there
                                    summary of what was built.                                                is no summary of what
                                                                                                              was built.


 Related work           10%         Sources are chosen carefully         Related work is present but          Little or no related work
                                    and are thematically related to      uneven: sources are                  is cited, or citations
                                    the app that was built. For each     summarized without assessing         appear without any
                                    paper or existing app there is a     strengths and weaknesses, or         discussion.
                                    concise summary of its               an obvious comparable app or
                                    contribution, its strengths and      a central paper is missing, or
                                    weaknesses are identified, and       the contrast with this project is
                                    the contrast with this project is    left implicit.
                                    explicit.


 Course concepts 20%                The app's core function rests on     The course concept is present        No course concept is
                                    a concept from the course, and       and functioning, but one of the      meaningfully present;
 and network
                                    the report shows exactly how.        three supporting elements is         removing the network
 analysis                                                                missing: it is used as a black       analysis would not
                                     • The method is justified
                                       against at least one              box, or its results are reported     change what the app
                                       alternative covered in class,     without interpretation, or no        does.
                                       with evidence rather than         alternative was considered.
                                       assertion
                                     • Results of the analysis on real
                                       data are reported and
                                       interpreted
                                     • The report is candid about
                                       where the network analysis
                                       performed poorly, and why


 Design and             20%         There is a careful discussion of     The goals and functionality are      The app is not well
                                    the goals and functionality of       described and the app seems          motivated or well
 implementation
                                    the app; design decisions are        well designed, but the               designed, and what
                                    traced back to the problem, to       reasoning behind the decisions       was actually built
                                    related work, and to what was        is thin, or the final prototype is   cannot be determined
                                    learned during development.          described only at a high level.      from the report.
                                    The final prototype is described
                                    in enough detail that a reader
Components   Weight Sophisticated (4)                   Competent (2)                      Not Yet
                                                                                           Competent (1)

                     could reproduce the core flow.


Users and    15%     The users who tested the app       Users tested the app, but one    Users were not
                     are well matched to the            element is missing: the          involved in testing the
feedback
                     problem and of sufficient size     population is not justified, or  app.
                     and quality, and the choice is     only a single round is reported,
                     justified. Several rounds of       or what changed as a result is
                     feedback are reported,             described only in general terms.
                     including what users actually
                     did with the prototype, and the
                     report shows how the design
                     changed across rounds.


Evaluation   20%     Several metrics to evaluate the    Results are reported, but with a   No effort to evaluate
                     app are presented and justified.   gap: no baseline is used, or the   the quality of the app.
                     Results are reported against       metrics reported are not the
                     those metrics and against a        ones proposed, or failures are
                     named baseline — an alternative    not discussed.
                     method, or a documented
                     earlier iteration — and the
                     authors are candid about what
                     did not work.


Writing      5%      The report carries a clear         The argument is mostly             There is no
                     argumentative line from the        followable, but the reader has     argumentative line; the
                     problem to the conclusion.         to reconstruct parts of it: some   report reads as a
                     Every figure, screenshot, or       figures are presented without      sequence of
                     interface mockup is referred to    explanation, or a few claims are   disconnected sections.
                     in the text and explained, and     asserted without supporting        Figures are
                     the conclusions are supported      evidence.                          unexplained, or the
                     by the evidence presented.                                            conclusions do not
                                                                                           follow from the
                                                                                           evidence presented.
```

### Final presentation rubric

Source: https://sundaram.cs.illinois.edu/Rubrics/presentation_CS470.pdf

```text
Scoring. Each component is scored 4, 3, 2, 1, or 0. Award 3 when the work sits between Sophisticated and Competent, and 0
when the component is absent altogether. A component contributes (score ÷ 4) × weight to the grade.


 Components            Weight Sophisticated (4)                        Competent (2)                       Not Yet
                                                                                                           Competent (1)


 Organization          10%         The presentation is clear,          The presentation is generally       Organization is
                                   logical, and organized; the         clear and well organized, but a     haphazard; the viewer
                                   viewer can follow the line of       few points are confusing, or the    can follow the
                                   reasoning. It fits the ten-minute   pacing leaves too little time for   presentation only with
                                   limit without rushing the           some sections.                      effort. Arguments are
                                   demonstration.                                                          not clear, or the
                                                                                                           recording runs well
                                                                                                           over or under time.


 Content               25%         The speakers give an accurate       The account is broadly accurate,    The account of the
                                   and complete account of the         but uneven: the users are           project is inaccurate or
                                   project.                            vague, or related work is           incomplete. Related
                                    • The problem and the users        presented without connecting it     work is absent, the
                                      are established early, and       to this project, or feedback and    design rationale is not
                                      why the problem matters is       results are mentioned without       explained, and
                                                                       specifics.                          feedback and results
                                      clear
                                                                                                           are not discussed.
                                    • Related apps and research
                                      are covered, and the contrast
                                      with this project is explicit
                                    • The design rationale is
                                      communicated with
                                      examples or analogies
                                    • What user feedback changed
                                      is described concretely, and
                                      results are reported honestly,
                                      including what did not work


 Course concepts 15%               The talk makes clear which          The course concept is named,        No course concept is
                                   course concept the app rests on     but the talk does not explain       identified; a viewer
 and network
                                   and why that method was             why it was chosen, or its           could not say what this
 analysis                          chosen over the alternatives,       connection to what is               project has to do with
                                   and the demonstration shows         demonstrated is left for the        social and information
                                   the concept doing real work in      viewer to infer.                    networks.
                                   the app.


 Demonstration         30%         The working prototype is            The prototype is shown, but         The prototype is not
                                   demonstrated on screen. The         only in fragments, or the           demonstrated; the app
                                   core user flow is shown end to      demonstration moves too             is described only in
                                   end at a pace the viewer can        quickly to follow, or it is         words or slides.
                                   follow, and the demonstration is    presented as static screenshots
                                   tied back to the design             where a live walkthrough was
                                   decisions that produced it.         possible.
 Components             Weight Sophisticated (4)                         Competent (2)                      Not Yet
                                                                                                            Competent (1)


 Slide and visual       10%          Visuals enhance the                 Visuals contribute to the          Visuals are poorly
                                     presentation.                       presentation, but one element      prepared or used
 design
                                      • Text on the slides is readable   is weak.                           inappropriately.
                                        at video resolution              • Text is mostly readable          • Text is too small to
                                      • Information is organized to      • Appropriate information is         read
                                         maximize comprehension            included                         • Too much
                                      • Detail is minimized so that      • Some material is not               information is
                                        main points stand out              supported by visuals                included
                                                                                                            • Unimportant detail is
                                                                                                              highlighted and may
                                                                                                              confuse the viewer


 Delivery and           10%          The presentation is a planned       The level is generally             Aspects of the
                                     conversation pitched at the         appropriate, but the pacing is     presentation are too
 language
                                     right level for the class, not a    sometimes too fast or too slow,    elementary or too
                                     reading of the report. Audio is     or audio quality varies, or word   sophisticated for the
                                     clear throughout, sentences are     choice is imprecise in places.     audience. Much of the
                                     complete and grammatical, and                                          content is read aloud,
                                     words are well chosen.                                                 audio is hard to follow,
                                                                                                            or grammatical errors
                                                                                                            distract from the
                                                                                                            content.



Adapted from the “Oral Communication Rubric”, Eberly Center for Teaching Excellence, Carnegie Mellon University.
```

