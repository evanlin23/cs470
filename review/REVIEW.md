# Review: "Finding people across the structural holes in UIUC research"

Independent review of `docs/idea-brokerage.md` for CS 470 (Fall 2026), 2 Oct 2026.
Evidence: the full UIUC OpenAlex corpus for 2015–2024 (109,471 works), pulled and analysed in
`review/checks/` for **$0.0575** in total.

## Verdict: GO-WITH-CHANGES

The data side is better than expected. The whole campus costs $0.06 to download, the graph and
Louvain run in seconds, the communities are meaningful, and a 2015–19 → 2020–24 backtest runs in
under 2 minutes. That makes for a feasible, demo-friendly project with a real course concept (Lesson 1
structural holes and weak ties, plus Lesson 10 communities). **The spec as written has three serious defects, though:**

1. **The "brokerage gain" term does nothing.** For every candidate at distance ≥ 3, the drop in
   Burt constraint from adding tie u–v is *exactly the same number* (verified for 1,500 of 1,500
   egos; the spread is 0.0). It only separates friends-of-friends from everyone else, which the distance
   term already does. As specified, the "network part" of the ranking is a distance filter on top of
   topic similarity. That is the rubric's "Not yet competent" description for course concepts.
2. **Falsifiable claim 1 is already false on real data.** At every level of topic similarity,
   friend-of-friend pairs form new collaborations **3–8× more often** than distant pairs (e.g.
   116 vs 20–36 per 1,000 at similarity ≥ 0.4). Triadic closure beats the spec's ranking at predicting
   new co-authors by 3.3× (precision@10 0.076 vs 0.023). A falsifiable claim is good, but one already
   known to be false is not.
3. **The primary users are the ones the network can't serve.** Undergrads looking for a first
   mentor have no papers and no advisor, so for them the app reduces to topic search with the network
   removed.

All three can be fixed by tomorrow's 5pm deadline (see [Required changes](#required-changes)). With the
fixes, I predict roughly **A-range** project scores; without them, roughly **70–75%**, and the
course-concepts component gets worse at each stage as the evaluation exposes defect 1.

Note: `proposal/proposal.md` is still the MethodBridge proposal, so the 1-page proposal has to be
rewritten in full today, with a new Figure 1.

---

## 1. Predicted rubric scores

Scores are 4/3/2/1/0. "As specified" means executed as in `docs/idea-brokerage.md`; "With changes"
means with the required changes below.

### Proposal (due Oct 2)
| Component (weight) | As spec'd | With changes | Why |
|---|---|---|---|
| Objective (10%) | 3 | 4 | 4 needs "the reader understands **who has this problem and why it matters**"; 2 is when who/why "is asserted rather than established". Burt motivates *why*, but nothing shows that students lack this. Add one fact: the topic-only list is 30% friends-of-friends, so it surfaces the circle you already have. |
| Related work (10%) | 2 | 4 | The spec cites only Burt. 2 = "an **obvious comparable app or a central paper is missing**". Here those are Illinois Experts "Similar Profiles", Liben-Nowell & Kleinberg's link prediction, and DeepConnect (2026). |
| Course concepts (15%) | 3–4 | 4 | Concept, alternatives, data and a falsifiable claim are all present, so it reads as a 4. But claim 1(b) is known false (§3.4), and the brokerage gain is a no-op that a careful grader will notice. |
| Proposed work (20%) | 3 | 3–4 | 2 = "the scope is **optimistic** … or assumptions are left **implicit**". Nightly recompute, three rounds, email follow-up and an optional Burt replication are a lot for one semester; the assumptions are listed as "risks". |
| Preliminary design (15%) | 2 | 4 | 4 = "key screens … **sketched**, core user flow can be followed end to end"; 2 = "described in prose". There is no sketch yet; the existing Figure 1 is MethodBridge. |
| Users (15%) | 3 | 4 | Population and reach are given, but the primary users don't fit the method (§4.1). |
| Evaluation (10%) | 3–4 | 4 | Several metrics and baselines are named. "Follow-up on emails sent" cannot be measured ethically or in time. |
| Writing (5%) | 3 | 4 | — |
| **Weighted** | **≈ 73%** | **≈ 95%** | |

### Mid-semester report (Oct 30)
| Component (weight) | As spec'd | With changes | Why |
|---|---|---|---|
| Objective (10%) | 3 | 4 | Needs a "summary of progress". |
| Related work (10%) | 3 | 4 | Now also needs "strengths and weaknesses" for each item. |
| Course concepts (15%) | 3 | 4 | 4 = run on real data, justified against an in-class alternative, and "says **what those results reveal about the network**". The backtest can give exactly that. If the gain term stays, it is a method "used as a black box without justification". |
| Design & implementation (25%) | 3 | 3–4 | 4 = "core flow **can be demonstrated**". Reachable if the prototype is clickable on the real graph by about Oct 19. |
| Users & feedback (20%) | 2 | 3–4 | 4 = "at least one round … **and the report shows what it changed**". The spec's "October round" must finish by about Oct 23, the same week Long Homework Part A is due and just before Short Exam #4 (Oct 27–29). As planned, this is the most likely place to lose points. |
| Evaluation (15%) | 3 | 4 | Name a baseline for each metric (§5). |
| Writing (5%) | 3 | 4 | — |
| **Weighted** | **≈ 70%** | **≈ 90%** | |

### Final report (Dec 9)
| Component (weight) | As spec'd | With changes | Why |
|---|---|---|---|
| Objective (10%) | 3 | 4 | — |
| Related work (10%) | 3 | 4 | — |
| Course concepts (20%) | **2–3** | 4 | 4 = justified against an alternative "**with evidence rather than assertion**", and "candid about where the network analysis performed poorly". 1 = "**removing the network analysis would not change what the app does**". The spec's own backtest will show its network term adds ≈0 over topic similarity (§3.4), so the authors would be documenting the 1/2 description themselves. |
| Design & implementation (20%) | 3 | 3–4 | 4 = "a reader could reproduce the core flow". |
| Users & feedback (15%) | 3 | 4 | 4 = "**several rounds** … what users actually did … how the design changed across rounds". Recruiting 10–15 new students per round is optimistic; reuse the same people. |
| Evaluation (20%) | 3 | 4 | 4 = results "against a named baseline … **candid about what did not work**". The data already supplies candid negatives (§3.4, §3.5). |
| Writing (5%) | 3 | 4 | — |
| **Weighted** | **≈ 70–75%** | **≈ 95%** | |

### Final presentation / video (Dec 9)
| Component (weight) | As spec'd | With changes | Why |
|---|---|---|---|
| Organization (10%) | 3 | 4 | — |
| Content (25%) | 3 | 4 | Feedback "described concretely", results "including what did not work". |
| Course concepts (15%) | 3 | 4 | 4 = "the demonstration shows **the concept doing real work**". The constraint drop is invisible on screen. Communities on the map and a highlighted intro path through a broker *are* visible. |
| **Demonstration (30%)** | 3 | 4 | 4 = "core user flow shown **end to end** … **tied back to the design decisions**". A precomputed campus graph makes a live demo low-risk. Demo with consenting participants' own profiles. |
| Slides & visuals (10%) | 3 | 3–4 | — |
| Delivery (10%) | 3 | 3–4 | — |
| **Weighted** | **≈ 75%** | **≈ 95%** | |

---

## 2. Is the network analysis load-bearing?

The test is the rubric's 1-level wording: "*The app could be built, and would behave the same way, with
the network analysis removed.*"

| Network element in the spec | Changes what the user sees? | Evidence |
|---|---|---|
| Louvain communities → campus map | **Yes**: this is the map. | Q = 0.83, 52 communities, NMI with dominant subfield 0.41 (shuffled: 0.08). Communities ≠ departments (median purity 0.25). |
| Network distance in the ranking | **Yes**, as a filter. | 30% of a topic-only top-10 are friends-of-friends; ranking with distance cuts that to 2–5%. |
| **Brokerage gain (Δ constraint)** | **No.** | For every candidate at distance ≥ 3, Δ constraint is identical (1,500 of 1,500 egos, spread 0.0). Adding it to topic × distance changed precision@10 by 0.0001. |
| Intro paths via weak ties or local bridges (L1, L13) | **Yes**, if built. | Only the network can produce them. A warm-intro path count is the one network feature that shows a (non-significant) lift (§3.4). |
| Constraint / effective size of the user | Descriptive only | Spearman with degree −0.89 (constraint) and +0.97 (effective size); see §3.3. |

**Why the gain is constant.** Burt's constraint of u is c_u = Σ_j (p_uj + Σ_q p_uq·p_qj)². If v is
at distance ≥ 3, no contact q of u is tied to v, so p_qv = 0 for every q. The new tie then adds the
term (p_uv)² and rescales u's other p_uj in the same way whoever v is. So Δc_u depends only on u. Only
friends-of-friends (distance 2) get a different, smaller gain. Use constraint to *describe* egos and
to *explain* the map, not to rank people.

---

## 3. Viability with real data

### 3.1 Scale and completeness (`01_counts.py`, `03_graph_stats.py`)
- UIUC = **`I157725225`** (ROR 047426m28).
- **109,471 works** from 2015–2024 (9.2k in 2015, 12.8k in 2024). 98,575 are research types: 67k
  articles, 14k conference papers, 12k preprints and others.
- **45,370** OpenAlex authors have UIUC as last-known institution; **127,487** have ever been affiliated.
- Topics are almost complete: 937 works (0.9%) lack a primary topic, and 94 research works have no topics.
- Field mix: Engineering 16.0k, CS 13.8k, Medicine 8.8k, Biochem/Genetics 8.7k, Physics 8.6k, Social
  Sciences 8.5k, and so on. A campus-wide map is realistic.
- The full download is 548 pages (about 8 min, **$0.055**). A nightly recompute is affordable within
  the $1/day cap but unnecessary: a one-off snapshot is enough.

### 3.2 Co-authorship graph, 2015–2024, UIUC-affiliated authors, papers with ≤ 25 authors
| | |
|---|---|
| Nodes / edges | **41,295 / 139,010** (density 1.6 × 10⁻⁴) |
| Components | 8,039; giant component **30,358 (73.5%)**; the next largest has 29 nodes; 6,839 isolates |
| Degree | mean 6.7, median 4, p90 15, p99 58, max 346. Heavy-tailed. |
| Clustering (giant, 2k sample) | 0.66: paper cliques make it very clustered |
| One-paper authors | 20,666 (50%): mostly students and visitors |
| "Core" (≥ 3 UIUC papers) | 14,563 nodes, 70,048 edges, giant component 13,071 |
| Build time | 1.5 s |

**Hyperauthorship is a real issue, and the ≤ 25 cut is right.** Only 3.3% of works have more than 25
authors, but keeping them would add **10.3M pairs against 1.5M** from all other papers, i.e. 87% of
all ties. Also, the list endpoint returns at most 100 authorships per work (max observed = 100),
so UIUC authors beyond position 100 are silently missing. This is harmless once those papers are dropped.

**Louvain is meaningful** (core giant component, 1.3 s): **52 communities, Q = 0.83**, 48 of them with
≥ 20 members (largest: 804). NMI against each author's dominant OpenAlex subfield is **0.41**, against
**0.08** for shuffled labels. Purity is low (median 0.25), so communities are cross-disciplinary
clusters rather than departments. Examples: Plant Science 28%; Public Health 10% (mixed); AI 25% and a
second AI cluster at 65%; Atomic/Molecular Physics & Optics 29%; Ecology 23%; Biomedical Eng. 22% +
Molecular Bio 19%; Mechanical Eng. 26% + Materials Chem 12%. This supports the "communities, not
department labels" pitch.

### 3.3 Burt constraint and effective size
- **Speed:** 500 nodes in 12.8 s (constraint) and 12.5 s (effective size). The whole core takes about 6 min,
  so precompute it.
- **Values are sensible:** median 0.40, range 0.04–1.22.
- **But they mostly measure degree:** Spearman(constraint, degree) = **−0.89**; Spearman(effective size,
  degree) = **+0.97**. Co-authorship graphs are unions of cliques, so a larger ego simply means less
  constraint. Some brokerage signal remains beyond degree: among nodes with degree 5–15 (n = 225),
  constraint vs. the number of distinct communities among one's neighbours has ρ = −0.51. **Recommended:**
  report "number of communities your co-authors span" next to constraint; it is easier to explain and
  not just degree.

### 3.4 The 2015–19 → 2020–24 backtest (`04_backtest.py`)
**Feasible:** the cohort (≥ 2 UIUC papers in 2015–19 and ≥ 1 in 2020–24) has **5,801** researchers
and **8,982 new pairs** (not tied before; co-authored in 2020–24). That is 53% of the 10,965
researchers with ≥ 2 papers in 2015–19 (the rest left or stopped publishing). **61% of new ties are
between pairs at distance ≥ 3**, so the app's target set is common, not an edge case. Among sampled
far new ties, 87% cross Louvain communities. A 1,500-ego evaluation runs in about 100 s.

**The confound is large.** New-tie rate per 1,000 candidate pairs (1,500 sampled egos):

| Topic cosine \ 2015–19 distance | 2 (friend of friend) | 3 | 4–5 | ≥ 6 / none |
|---|---|---|---|---|
| < 0.05 | 16.2 | 2.4 | 0.35 | 0.14 |
| 0.05–0.1 | 34.7 | 8.2 | 2.9 | 2.7 |
| 0.1–0.2 | 48.9 | 12.3 | 3.7 | 6.2 |
| 0.2–0.4 | 65.3 | 16.3 | 8.1 | 11.2 |
| ≥ 0.4 | **116.3** | 28.1 | 19.8 | 35.7 |

- Topic similarity raises the rate about 10× within every distance column. So "far and similar vs
  random" mostly measures similarity: **claim 1(a) is confounded**.
- Within every similarity row, distance 2 beats distance ≥ 3 by 3–8×. **Claim 1(b) ("far pairs collaborate
  more than friend-of-friend pairs of equal topic similarity") is false.**
- Interesting: at similarity ≥ 0.4, *disconnected* pairs (35.7) beat distance 4–5 (19.8). Similar
  researchers in separate components (often newer groups) do find each other. This is worth a sentence in
  the report.

**Ranking (precision@10; mean over egos; 95% CIs are paired bootstraps over egos):**

| Method | P@10, all new ties | P@10, new ties at distance ≥ 3 (1,165 egos) | Share of top-10 that are friends-of-friends |
|---|---|---|---|
| Random | 0.0005 | 0.0003 | 0.01 |
| Degree / "famous people" | 0.0079 | 0.0029 | 0.12 |
| **Adamic–Adar (triadic closure)** | **0.0755** | 0.0072 | **0.87** |
| Topic only | 0.0550 | 0.0250 | 0.30 |
| Topic × distance | 0.0278 | 0.0263 | 0.05 |
| **Spec: topic × distance × brokerage gain** | 0.0227 | 0.0264 | 0.02 |
| Topic, distance ≥ 3 candidates only | 0.0246 | 0.0317 | 0 |
| Topic × (1 + log warm-intro paths), distance ≥ 3 | 0.0261 | **0.0336** | 0 |

- At predicting *any* new tie, triadic closure wins by a wide margin (spec − AA = −0.053, CI
  [−0.058, −0.047]). That is expected: Liben-Nowell & Kleinberg (2007) found the same. Say so up front
  instead of claiming otherwise.
- At the app's actual job (finding *far* future collaborators), the spec ties topic-only (difference
  CI [−0.0005, +0.0035]). The gain term adds 0.0001 over topic × distance. Multiplying by raw distance
  hurts: it favours disconnected strangers over distance-3 people, so plain topic similarity on the
  distance ≥ 3 pool scores higher (0.0317).
- A network feature that does vary among far candidates, the **number of length-3 paths (warm-intro
  routes)**, gives +6% over the fair topic baseline (0.0336 vs 0.0317, CI [−0.0003, +0.0044]). That is
  suggestive but not significant. It is an honest, open question for the project to settle, which makes
  a good falsifiable claim.

**Fairer backtest design (use this):**
1. Make the candidate pool the app's output space: pairs at distance ≥ 3 in 2015–19.
2. Compare the network re-ranker against **topic-only on the same pool**. Report AA on all ties separately,
   as context.
3. Match or stratify on topic-similarity quartile and on ego degree, so the network feature must add
   signal *within* similarity strata.
4. Report P@10 and recall@50 with paired-bootstrap CIs over egos, and novelty (share of
   friends-of-friends in the top-10) as a second axis.
5. Use 2015–19 → 2020–22 as a development split and keep 2023–24 as a held-out test, so tuning cannot
   leak.

### 3.5 Optional "Burt replication": the data points the other way (`06_value_of_far_ties.py`)
Joint 2020–24 papers of **new distance ≥ 3 ties** have *lower* field- and year-normalised citations
than those of **new friend-of-friend ties**: median 0.59 vs 0.72, mean 1.27 vs 2.32 (Mann–Whitney
p = 1e-11; 5,491 vs 3,491 pairs). Caveats: pair-level, with larger teams and longer citation windows
for friend-of-friend papers. Don't make "brokerage gives better ideas" a selling point for *this*
data. Either drop claim 3, or keep it as a pre-registered test and report the negative candidly
(that suits the rubric's "candid about what did not work").

### 3.6 Disambiguation and staleness (`03`, `05`)
- 9,135 of 219,579 UIUC authorships (**4.2%**) have **no author ID** and silently drop out of the
  graph. Of all authorships, 5.7% have no ID and 3.3% have no institution.
- Split profiles: 139 of 26,432 ORCIDs map to more than one author ID (0.5%), which is modest. Common
  names are the bigger risk: **1,674 UIUC display names map to more than one ID** ("Bo Li": 44 IDs,
  "Yang Liu": 27, "Yu Zhang": 23). Many are different people, so a name search must show ORCID, the
  most recent paper and the department before the user picks "this is me".
- **Turnover:** of 7,675 researchers with ≥ 3 UIUC papers in 2015–19, **3,630 (47%) have no UIUC
  paper after 2020**. Of a sample of 100 of these, **26 still list UIUC as last-known institution**, so
  OpenAlex affiliation alone would recommend people who left years ago. Among 100 sampled researchers
  who still publish at UIUC in 2024, 24 do *not* list UIUC as last-known (multiple affiliations or lag).
  **Fix:** only recommend people with a UIUC-affiliated work in the last ~2 years (pull 2025–2026 for
  the live app; the backtest window stays 2015–2024).

### 3.7 Cold start
- Of 19,102 authors whose first UIUC paper is in 2020–24, 11,527 (60%) have only one paper. For
  9,268 (49%), the first paper has a co-author with ≥ 5 earlier UIUC papers (an "anchor", usually the
  advisor). Placing a newcomer through an anchor is workable for people with ≥ 1 paper.
- For a student with **no papers and no advisor**, the "advisor or chosen contacts" fix makes the
  student's ego the *advisor's* ego. The output is then "people far from your advisor", which is not
  what an undergrad looking for a first mentor needs; they need topic match plus availability. If they
  pick no contacts, the network does nothing and the app is a topic search. **So make students with
  ≥ 1 paper, or with a named advisor, the primary users.**

---

## 4. Product assessment

### 4.1 Real problem for these users?
- **Grad students (2nd year+), postdocs and faculty seeking collaborators, co-advisors or committee
  members outside their lab: plausible.** They have a network position, and the "friend-of-friend
  bias" is measurable: 30% of a topic-only list, and 87% of a triadic-closure list, are people they
  can already reach.
- **Undergrads looking for a first mentor: real problem, wrong tool.** Their bottlenecks are who takes
  undergrads, who has funding and who answers email; their network position is empty (§3.7).
- No user evidence exists yet. Run a 5-minute survey (n ≈ 20) next week: "How did you find your
  last collaborator, co-advisor or committee member? Did you look outside your department?" Use it
  in the mid-term Objective.

### 4.2 Existing tools, and whether the contrast holds
| Tool | What it does | Contrast |
|---|---|---|
| **Illinois Experts** (experts.illinois.edu, Elsevier Pure) | "Similar Profiles" from concept fingerprints **plus shared works and organisational affiliation**, and a co-author "Network" tab | **Closest incumbent, and the opposite bias:** shared work and affiliation *raise* similarity, so it surfaces your own circle. It is the ideal real-world baseline, and the contrast holds. |
| Google Scholar | Co-author list, "related articles" | No people recommendations. |
| ResearchGate | Suggested researchers to follow (topic and network) | Global, engagement-driven, opaque. |
| LinkedIn "People you may know" | Triadic closure | Exactly the Adamic–Adar baseline. |
| Semantic Scholar / Connected Papers | Paper similarity, author pages | Papers, not people. |
| **DeepConnect** (Feng et al., arXiv 2608.05134, 2026) | LLM-augmented visual analytics for finding interdisciplinary collaborators, with outreach rehearsal | Very close in purpose. It is driven by content and LLMs, has no structural-hole or network-distance ranking, and is not campus-specific. **Must be cited.** |
| Collaborator recommenders (CollabSeer, Chen et al. 2011; Noor et al., arXiv 2607.04529, 2026) | Network proximity or content similarity | The literature notes that proximity methods "reinforce existing structures". That is the gap this project addresses. |
| Link prediction (Liben-Nowell & Kleinberg 2007) | Adamic–Adar etc. on co-authorship | The central paper. It explains why triadic closure wins at *prediction*. |

### 4.3 Can they recruit three rounds?
Three rounds of 10–15 *new* students each is optimistic for two students with exams on Oct 27–29,
Nov 10–12 and Dec 1–3, Long Homework due Oct 23 and Nov 20, and Thanksgiving week Nov 21–29. Plan
for **8–12 people reused across rounds** (their research doesn't change, and returning users can say
what changed). Use 30-minute sessions on their own profile. Round 1: Oct 19–23. Round 2: Nov 9–13.
Round 3: Nov 30–Dec 3. Recruit through the team's own labs and grad cohorts first, then
ACM@UIUC/SIGs.

### 4.4 Ethics and privacy
- The data is public, but **ranking named faculty for cold outreach** concentrates email on whoever
  scores well. Cap how often one person appears across users, and show "this person gets many
  suggestions" instead of hiding it.
- **Never display others' constraint or brokerage scores.** They read as a judgement of a person's
  worth. Show them only for the logged-in user's own ego.
- Draft emails stay drafts: no sending from the app. **Drop "follow-up on emails sent"**: it measures
  third parties (faculty) who did not consent, and it can't finish by Dec 9. Stated intent is enough.
- In the video, demo the authors' own profiles or those of consenting participants, and blur the other
  names in lists.
- Feedback sessions are class evaluation. Ask the instructor whether IRB applies if results might be
  published, and keep notes anonymised.
- Disambiguation errors mean recommending the wrong person. Show the ORCID and most recent paper on
  every card.

---

## 5. Scope and feasibility

| By | Deliverable | Feasible? |
|---|---|---|
| Oct 2 | Rewritten 1-page proposal plus a new Figure 1 sketch | Tight but yes. The checks here provide the data facts. |
| Oct 9 | Pipeline: snapshot (2015–2026), graph, Louvain, topic vectors | **Mostly done**: `review/checks/02–04` |
| Oct 16 | Clickable prototype on the real graph: you → map → list → card | Yes, with Streamlit or FastAPI plus a simple front end |
| Oct 23 | Feedback round 1 (n ≈ 8) | Tight: Long Homework A is due the same day |
| Oct 30 | Mid-term: backtest table, round 1 changes | Yes |
| Nov 13 | Round 2; warm-intro paths; community-hole map | Yes |
| Dec 3 | Round 3; final backtest on the held-out years | Tight: Short Exam #6 is the same week |
| Dec 9 | Report and video | Yes, if the scope cuts below are made |

**Cut:** nightly recompute (use a static snapshot), email follow-up, and the optional citation-impact
replication (or report it as a one-line negative).

---

## Required changes
Ordered by impact on the grade.

1. **Replace falsifiable claim 1.** It is confounded and, as worded, already false (§3.4). Use the
   wording below: distance ≥ 3 pool, topic-only baseline on the same pool, stratified, with a held-out
   split. *(Course concepts 15/15/20% and Evaluation 10/15/20% at every stage.)*
2. **Drop "brokerage gain = Δ constraint" from the per-person ranking.** It is provably constant among
   far candidates (§2). Use network features that vary and that the user sees:
   **(a)** warm-intro paths (how many length-3 paths, and through which broker; L1 weak ties and local
   bridges, L13); **(b)** community-pair holes (topic similarity between two Louvain communities ×
   (1 − inter-community tie density); L10); **(c)** "communities your co-authors span" as the user's
   own brokerage profile. *(This is what decides between the 1 and 4 descriptions for course concepts.)*
3. **Re-target the primary users** to grad students (2nd year+) and postdocs with ≥ 1 UIUC paper;
   faculty are secondary. Undergrads come in only through a named advisor, as a stretch. Otherwise the
   network does nothing for the primary users. *(Users 15/20/15%, Objective.)*
4. **Plan the user rounds around the calendar:** the same 8–12 people, round 1 done by Oct 23, with
   a clickable prototype on real data by Oct 16. Report what each round changed. *(Mid-term Users &
   feedback 20%, and Design 25%.)*
5. **Make the network visible in the demo:** a map coloured by community, the user's position, the
   highlighted hole, and an intro path through a named broker. *(Video Course concepts 15% and Demo 30%.)*
6. **Add the missing related work and contrasts:** Illinois Experts, Liben-Nowell & Kleinberg,
   DeepConnect, CollabSeer and collaborator-recommendation work, Granovetter, Burt. *(Related work 10% × 3.)*
7. **Fix recency and identity:** recommend only people with UIUC work in the last ~2 years; add an
   "is this you?" picker with ORCID. *(Demo credibility; avoids embarrassing recommendations.)*
8. **Add a new Figure 1 sketch** of the four screens to the proposal. *(Preliminary design 15%.)*
9. **Ethics section and scope cuts** as in §4.4 and §5. *(Proposed work 20%, and avoids an
   indefensible metric.)*

---

## Suggested wording

**Falsifiable claim (backtest).**
> We freeze the UIUC co-authorship graph and topic profiles at 2015–2019 and consider only pairs of
> researchers that are **at least three steps apart**, the people our app recommends. Among these
> candidates, ranking by topic similarity **weighted by the number of warm-introduction paths** will
> place a researcher's actual new 2020–2024 co-author in the top 10 more often than topic similarity
> alone (paired bootstrap over researchers, 95% CI of the difference above zero; tuned on 2020–22,
> tested on 2023–24). In a pilot on 5,801 researchers, the lift was +6% with a CI that included zero, so
> this may well be false. We also expect, and will report, that triadic closure (Adamic–Adar) predicts
> *all* new ties better (pilot P@10 0.076 vs 0.026), but 87% of its suggestions are
> friends-of-friends the user can already reach, against 0% of ours.

**Falsifiable claim (users).**
> In a blinded, within-subject comparison on their own profile, participants will rate a larger share
> of our top-10 as both *relevant* (≥ 4/5) **and** *new to me* than of the topic-only list and the
> Adamic–Adar list. We will count it a failure if our relevant-and-new rate is not at least 10
> percentage points above both.

**Baselines (each tied to a lesson).**
| Baseline | Lesson | Role |
|---|---|---|
| Adamic–Adar / common neighbours ("people you may know") | L1 triadic closure | In-class alternative: strong ties versus our weak ties and local bridges |
| Topic similarity only, on the same distance ≥ 3 pool | none (content) | The "network removed" control. **The most important baseline.** |
| Degree ("most collaborative people") | L9 power laws / preferential attachment | The popularity control |
| Illinois Experts "Similar Profiles" (user study only) | — | Real-world incumbent |
| Girvan–Newman vs. Louvain for the map | L10 | Method choice: the pilot's timing evidence, plus Q and NMI against subfields |

**Metrics:** backtest P@10 and recall@50 (distance ≥ 3 pool) with CIs; share of friends-of-friends in
the top-10 (novelty); relevant-and-new rate; field distance of suggestions; stated intent to reach out;
the share of suggested people with UIUC work in the last 2 years (data quality).

---

## Risks still open
- Even with these changes, the network re-ranker may not beat topic-only in the backtest; the pilot CI
  includes zero. That is acceptable if reported candidly, and the user-study claim carries the value.
- OpenAlex topic vectors are coarse (about 4.5k topics). Topic similarity ≥ 0.4 can still pair people
  who only share a technique. Add "show the matching papers" on every card so users can judge.
- 4.2% of UIUC authorships have no author ID, and hyperauthored papers are capped at 100 authors.
  Physics and astronomy groups in big collaborations will look sparse. State this as a limitation.
- Turnover is high (47% of 2015–19 regulars have gone by 2021+), so a stale snapshot embarrasses the
  demo. Filter on recency.
