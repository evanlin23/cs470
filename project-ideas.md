# CS 470 (Fall 2026) — 4-credit project ideas, built from the rubrics

Sources: the [course page](https://sundaram.cs.illinois.edu/CS470.html), the four rubrics
([proposal](https://sundaram.cs.illinois.edu/Rubrics/proposal_CS470.pdf),
[mid-semester](https://sundaram.cs.illinois.edu/Rubrics/mid-term_report_CS470.pdf),
[final report](https://sundaram.cs.illinois.edu/Rubrics/final_report_CS470.pdf),
[presentation](https://sundaram.cs.illinois.edu/Rubrics/presentation_CS470.pdf)), the two
example reports, and the [supplementary readings](https://sundaram.cs.illinois.edu/CS470_readings.html).

**Deadlines:** proposal **Fri Oct 2, 5:00pm** (1 page + unlimited references) · mid-semester
report **Fri Oct 30** (4–5 pp) · final report (10–12 pp, ACM format) + 10-min video **Wed Dec 9**.
The project is 25% of the grade; the report and the video count equally.

---

## 1. What the rubrics actually reward

| Component | Proposal | Mid-semester | Final report | Video |
|---|---|---|---|---|
| Objective | 10% | 10% | 10% | — |
| Related work | 10% | 10% | 10% | (in Content 25%) |
| **Course concepts & network analysis** | **15%** | **15%** | **20%** | **15%** |
| Proposed work / Design & implementation | 20% | **25%** | 20% | Demo **30%** |
| Preliminary design | 15% | — | — | — |
| **Users (& feedback)** | **15%** | **20%** | 15% | (in Content) |
| Evaluation | 10% | 15% | **20%** | (in Content) |
| Writing / delivery / visuals | 5% | 5% | 5% | 30% |

Every component is scored 4/3/2/1/0, and you get (score ÷ 4) × weight.

### Tests every idea has to pass

1. **The network analysis has to carry weight.** The "Not yet competent" level for course concepts
   says: *"The app could be built, and would behave the same way, with the network analysis
   removed."* If a graph algorithm doesn't change what the user sees, you lose 15–20% at
   every stage.
2. **The method has to be argued against an alternative covered in class**, such as PageRank vs. HITS
   vs. in-degree, Girvan–Newman vs. modularity, or a global vs. a local threshold. By the final
   report, that argument has to rest on evidence, not assertion.
3. **The data source has to be named in the proposal and real by Oct 30.** The mid-semester level
   for running only on toy data is "Competent (2)". Pick data you can get **this week**.
4. **The proposal needs a falsifiable claim.** "What the analysis is expected to reveal is stated as a claim
   that could turn out to be false." Most proposals will miss this, so it's an easy place to stand out.
5. **Every metric needs a baseline.** A useful trick is to make the **in-class alternative from (2) the
   evaluation baseline**. One comparison then covers both components.
6. **You need users you can reach repeatedly.** The mid-semester report needs ≥1 feedback round *and what
   it changed*. The final needs *several* rounds and how the design changed across them. Pick a
   population you can go back to every 2–3 weeks.
7. **Plan for a working demo, end to end.** The demo is 30% of the video. The final report accepts a
   Figma prototype, but the course page says it should be "mature and ready to be put into
   development". A live core flow is safer.

> Note on the two example reports (DoDates!, YourWay): both are **CS 514** reports. They are good
> models for *user research and iteration* (YourWay especially), but they have almost no network
> analysis. Under this CS 470 rubric, DoDates! would score near the bottom on Course concepts.
> Don't copy their technical core.

---

## 2. Ideas (ranked)

Each idea lists: the problem and users · the core concept (lesson) · the in-class alternative,
which doubles as the baseline · data · a falsifiable claim · the prototype · how to reach users ·
metrics · risks.

### #1 — Slop-resistant Bluesky feed ranked by trust propagation (HITS / PageRank)

*This matches the instructor's own example: "a better social media feed … reducing the spread of AI slop."*

- **Problem / users.** Engagement-ranked feeds reward whatever collects likes. Engagement farms
  and AI-slop accounts game raw counts the same way link farms gamed early search. The users are
  students and academics on Bluesky who want a feed that is high-signal *and* engaging.
- **Core concept.** L6 (hubs/authorities, PageRank). Score a post by *who* endorsed it, with
  endorsement weighted by the endorser's PageRank or authority in the follow/like graph, seeded
  from the user's own follows (personalized PageRank). L9 also applies: slop engagement tends to
  be heavy-tailed and concentrated.
- **In-class alternative = baseline.** Raw in-degree (like count) vs. PageRank vs. HITS, all
  run on the same candidate pool.
- **Data.** Bluesky's public firehose via Jetstream (posts, likes, reposts, follows). It's free,
  real and live. Restrict to one topic community (e.g. academic, tech or UIUC accounts) to keep
  computation small.
- **Falsifiable claim.** *"Among the top-100 posts by like-count in topic T, a blind panel labels a
  larger share low-effort/AI-generated than among the top-100 by personalized PageRank. Slop
  accounts have high in-degree but low PageRank, because their engagement comes from low-PageRank
  accounts."* This would be false if slop gets genuine endorsement from well-connected users,
  which is an interesting result either way.
- **Prototype.** A real **custom feed generator**: people subscribe from inside the Bluesky app,
  so you don't build a client. Add a companion web page that explains why each post ranked (the
  endorser chain) and a slider between "engagement" and "trust". The `bluesky-social/feed-generator`
  starter kit and Skyfeed exist as references.
- **Users / reach.** UIUC students and the CS 470 class (Campuswire), ACM@UIUC, and Bluesky itself.
  To include people without accounts, run blind A/B tests in a web viewer that shows two
  unlabeled feeds side by side. Target n ≈ 25–40 for the preference test.
- **Metrics.** Blind pairwise preference (feed A vs. B); slop rate per 50 posts, labeled by 2 raters
  against a written rubric (report Cohen's κ); engagement per impression from your own feed logs;
  author diversity.
- **Related work.** Brin & Page '98; Kleinberg '99; TrustRank (Gyöngyi et al., VLDB '04); Twitter's
  WTF/SALSA (Gupta et al., WWW '13); bridging-based ranking and Community Notes (Ovadya & Thorburn
  '23; Wojcik et al. '22); Bluesky's Discover feed and Skyfeed.
- **Risks.** Defining "slop" (write the labeling rubric early). Cold start for new users (fall back to
  topic-level PageRank). Likely to be a popular choice, so differentiate with the "why this post"
  explainer and the evaluation.

### #2 — Network-aware coffee chats for clubs ("Donut, but it builds bridges")

- **Problem / users.** RSOs and cohorts break into cliques, and new, transfer and **Chicago-campus**
  members never integrate. Random-pairing bots (Donut) produce one-off chats that don't stick.
  The users are RSO organizers and members.
- **Core concept.** L1 (triadic closure, weak ties, local bridges, homophily) and L10 (communities).
  Pair people across community boundaries **who share one mutual contact**. Closing an open triad
  makes the new tie more likely to persist (Kossinets & Watts '06), and crossing communities
  creates a bridge.
- **In-class alternative = baseline.** Random pairing (Donut's default) vs. homophily matching
  (same major or interests) vs. pure friend-of-friend pairing within a community.
- **Data.** The club's Discord or Slack interaction graph (who replies to or mentions whom), collected
  by a bot with consent, or a roster survey ("name up to 5 people you talk to").
- **Falsifiable claim.** *"Cross-community pairs that close an open triad have a higher 2-week
  follow-up interaction rate than random pairs, and the club graph's modularity drops over the
  semester."*
- **Prototype.** A Discord bot plus an organizer dashboard (community map, pairing rationale), and a
  member card with an icebreaker ("you both know Priya; you're in different sub-teams").
- **Users / reach.** 1–2 RSOs with 30–100 members each. **Weekly pairings give you natural feedback
  rounds**, the best fit here for the "several rounds" requirement in Users & feedback.
- **Metrics.** Logged follow-up interactions; self-reported meetups; cross-community edges added;
  member satisfaction. Compare A/B across alternating weeks or a random half of the club.
- **Related work.** Donut, Lunchclub, Timeleft; Granovetter '73; Burt '04; Kossinets & Watts '06;
  Rajkumar et al., *Science* '22 (LinkedIn's causal test of weak ties).
- **Risks.** Small n means low statistical power, so report effect sizes and be candid. Consent and
  privacy around interaction logs. Meetups are slow, so start by mid-October.

### #3 — "I'm in if…": conditional RSVPs that tip events over the threshold

- **Problem / users.** Study sessions, club events and intramural teams die from coordination
  failure: everyone would come *if* others did. This is the low equilibrium. The users are RSO
  organizers and students (including CS 470 final-exam study groups).
- **Core concept.** L11 (network effects: the r(x)·f(x) curve, the unstable tipping point) and L12
  (linear-threshold cascades). Users RSVP conditionally ("I'm in if ≥k of my friends are"). The app
  runs the threshold cascade on the friend graph and fires "it's on!" when the high equilibrium is
  reachable.
- **In-class alternative = baseline.** A *global* population threshold (ch. 17, "if ≥N people
  go") vs. a *local* network threshold (ch. 19, "if ≥k of my friends go"). Which one predicts
  attendance better is an open empirical question. The app baseline is plain RSVP
  (GroupMe poll, Partiful).
- **Data.** Real conditional RSVPs and friend lists from live events, plus a willingness-to-attend
  survey to *estimate the actual r(x) curve* for a campus event, which turns the textbook
  derivation into real data.
- **Falsifiable claim.** *"Local-threshold RSVPs predict actual attendance better than global
  thresholds; for events below the tipping point, conditional RSVPs raise turnout over plain
  RSVPs."*
- **Prototype.** A mobile web app: create event → conditional RSVP → live "cascade progress" view →
  confirmation. Show clusters that are blocking the cascade (cascade capacity, dense clusters).
- **Users / reach.** RSOs running several events in Oct–Nov, and classmates' study groups.
- **Metrics.** Turnout vs. RSVP (no-show rate), the share of events reaching quorum, and attendance
  prediction error (local vs. global).
- **Related work.** PledgeBank (mySociety, "I'll do it if N others will"); Kickstarter's
  all-or-nothing model; Partiful; Granovetter '78; Centola, *Science* '10; Ugander et al., *PNAS* '12.
- **Risks.** You need enough real events before Dec 9. Friend-graph entry friction (import from a
  group chat or invite links).

### #4 — Agentic moderation that sees coordination, not only content

*This matches the instructor's example: "develop an agentic moderation system."*

- **Problem / users.** Brigades and spam rings post messages that are each borderline on their own.
  Content-only moderation (AutoMod, toxicity classifiers, LLMs) misses the *coordination*. The users
  are Discord moderators of UIUC course and club servers.
- **Core concept.** L10 (community discovery) on a co-activity graph: accounts that act on the same
  targets in the same short window. Raids appear as unusually dense, synchronized clusters.
  Optionally L1, structural balance on the signed reply graph, to detect conflict. An LLM agent
  summarizes each flagged cluster and drafts an action; a human approves it.
- **In-class alternative = baseline.** Girvan–Newman (betweenness) vs. modularity-based detection
  for finding the clusters. The system baseline is **the same agent with the network signal
  removed**, which answers the "remove the network analysis" test directly.
- **Data.** Bluesky co-repost and co-reply graphs, where spam/repost rings are common (real, public).
  Consenting UIUC Discord servers through a bot. Replayed or injected raids for controlled tests.
- **Falsifiable claim.** *"High-density, high-synchrony co-activity clusters contain later-banned
  accounts at >5× the base rate, and the network signal flags raids earlier (fewer messages in) than
  content-only moderation."*
- **Prototype.** A Discord bot and a mod dashboard: alert → cluster view → agent summary → one-click
  action.
- **Users / reach.** Mods of large UIUC servers (expert but few). Supplement with a broader survey.
- **Metrics.** Precision/recall on labeled incidents, time-to-detection, mod actions per incident,
  mod trust ratings.
- **Related work.** Pacheco et al., ICWSM '21 (coordinated networks); Kumar et al., WWW '18 (Reddit
  conflict and brigading); Perspective API; Discord AutoMod.
- **Risks.** Few real raids during the semester (plan the replay set). A small expert user pool
  (justify its quality over size). Ethics and consent.

### #5 — Research-lab finder for undergrads (HITS on the co-authorship/citation graph)

- **Problem / users.** Undergrads looking for research cold-email the most famous professors
  (in-degree), hear nothing back, and miss the grad students and postdocs who actually run projects.
  The users are UIUC CS undergrads, a large and easy-to-reach group.
- **Core concept.** L6 (HITS): within a topic subgraph, *authorities* are who's central in the
  sub-area, and *hubs* (broad grad students and postdocs linked to many authorities) are the best
  first contacts. L13 (decentralized search and weak ties) suggests an intro path through coauthors.
- **In-class alternative = baseline.** Citation count (in-degree) vs. PageRank vs. HITS. The app
  baseline is the department directory plus Google Scholar.
- **Data.** OpenAlex: free, open works/authors/citations, filterable to Illinois authors.
- **Falsifiable claim.** *"Students rate HITS-ranked recommendations more relevant than
  citation-ranked ones, and 'hub' contacts answer inquiries at a higher rate than top authorities."*
- **Prototype.** A web app: enter interests or paste a paper you liked → ranked people with "why" →
  suggested contact path and email draft.
- **Users / reach.** ACM@UIUC, WCS and CS advising channels, plus 3–5 grad students as expert judges.
- **Metrics.** nDCG from user relevance ratings, time-to-shortlist vs. baseline, inquiry response
  rate (longer horizon).
- **Related work.** Connected Papers, Semantic Scholar, CSRankings, Google Scholar; Kleinberg '99.
- **Risks.** Author-name disambiguation; defining topic subgraphs. Response rates may not arrive
  before December.

### #6 — Team former that respects structural balance (signed networks)

- **Problem / users.** Course and club project teams are formed randomly or by self-selection, which
  leaves isolates and puts people who don't get along in the same group. The users are
  TAs/instructors and RSO project leads.
- **Core concept.** L1 (structural balance). Students privately mark "+ want to work with / − prefer
  not". The app partitions them into k teams that minimize frustrated edges and unbalanced
  triangles (weak balance → k factions).
- **In-class alternative = baseline.** Unsigned community detection (modularity, L10) vs. the
  signed balance partition, which shows whether the signs matter. The app baseline is random or
  skill-balanced teams (CATME-style).
- **Data.** SNAP signed networks (Epinions, Slashdot) to validate the algorithm, plus a live
  preference survey from a club or class.
- **Falsifiable claim.** *"Balance-optimized teams report higher satisfaction and fewer conflicts at
  the mid-project check-in than skill-balanced random teams."*
- **Prototype.** A student preference form and an organizer tool that shows the partition with a
  balance score and lets the organizer adjust and lock members.
- **Related work.** CATME Team-Maker (Layton et al. '10); Leskovec et al., CHI '10 (signed networks);
  Marvel et al., *PNAS* '11.
- **Risks.** Negative ties are sensitive: never reveal them, and discuss the ethics. You need a real
  team-formation event between Oct and Nov.

### #7 — Privacy-leak mirror: what your friends reveal about you (homophily inference)

*This matches the instructor's example: "a new social media app focused on … privacy concerns".*

- **Problem / users.** Hiding your major, politics or identity on a profile doesn't help when
  homophily lets anyone infer it from your friends. The users are students who manage their own
  social-media privacy.
- **Core concept.** L1 (homophily, measured with the in-class cross-edge test against 2pq). Show how
  accurately each hidden attribute can be inferred, which few ties or communities drive the leak, and
  what-if controls such as hiding a friend list or specific ties.
- **In-class alternative = baseline.** Neighbor majority vote vs. community-level (L10) inference.
  The app baseline is a standard privacy-settings page.
- **Data.** Facebook100 (100 campus networks from 2005 with dorm, major and year; access is
  restricted, so check availability) or SNAP soc-Pokec (profiles with attributes).
- **Falsifiable claim.** *"A hidden attribute is inferable at >70% accuracy for most users, and hiding
  <10% of ties, chosen by community, halves that accuracy."*
- **Related work.** Jernigan & Mistree, *First Monday* '09; Zheleva & Getoor, WWW '09; Mislove et
  al., WSDM '10.
- **Risks.** The "app" can drift into an analysis tool. Real users' graphs are hard to obtain
  ethically, so the demo uses dataset personas.

### #8 — Fair-price campus sublease/move-out market (matching markets + bargaining)

- **Problem / users.** Spring subleases (posted Nov–Dec) and move-out sales run through chaotic
  Facebook or Discord posts. Popular units get swarmed (a constricted set) and others go unfilled.
  The users are students subleasing or buying.
- **Core concept.** L4 (preferred-seller graph, constricted sets, market-clearing prices via the
  ascending procedure), L5 (Nash bargaining with outside options for 1:1 deals), and L7 (VCG prices
  = the minimal market-clearing prices, so bidding is truthful).
- **In-class alternative = baseline.** Sequential second-price auctions (L3) vs. market clearing.
  The app baseline is first-come posted prices.
- **Data.** Valuations elicited from real students for real listings, plus simulated markets
  calibrated to them.
- **Falsifiable claim.** *"Market-clearing allocation yields higher total welfare and fewer unfilled
  listings than first-come posted pricing."*
- **Risks.** Two-sided recruitment is hard, and there are lease and legal edge cases. This is the
  most distinctive idea on the list and the hardest to get real users for.

### Smaller ideas you could fold in

- **Structural-virality dashboard for RSO social accounts.** Is reach a real cascade or one big
  broadcast? (Goel et al., *Mgmt. Sci.* '16; L12, L9; Bluesky repost trees.)
- **Course Q&A router.** HITS on the asker→answerer graph routes Campuswire or Discord questions to
  peers likely to answer. Validate offline on the Stack Exchange data dump (L6).
- **Network-structured wisdom of crowds.** Workload or grade-cutoff estimates where who sees whose
  guess follows a decentralized network (Becker et al., *PNAS* '17; Lorenz et al., *PNAS* '11; L14).

---

## 3. How the ideas compare on the rubric's risk points

● strong · ◐ workable · ○ risky

| # | Idea | Network is core | Alternative = baseline | Real data by Oct 30 | Repeat user access | Live demo | Scope risk |
|---|---|---|---|---|---|---|---|
| 1 | Slop-resistant feed | ● | ● | ● | ◐ | ● | ◐ |
| 2 | Bridge-building chats | ● | ● | ◐ | ● | ● | ● low |
| 3 | Conditional RSVPs | ● | ● | ◐ | ● | ● | ● low |
| 4 | Network-aware moderation | ● | ● | ● | ○ | ● | ○ high |
| 5 | Research-lab finder | ● | ● | ● | ● | ● | ◐ |
| 6 | Balance team former | ● | ● | ◐ | ◐ | ● | ◐ |
| 7 | Privacy-leak mirror | ● | ◐ | ◐ | ◐ | ◐ | ◐ |
| 8 | Fair-price sublease market | ● | ● | ○ | ○ | ◐ | ○ high |

**Recommendation.**
- **#1** if you want the highest technical ceiling and an idea the instructor explicitly asked for.
- **#2 or #3** if you want the safest path to "Sophisticated" on Users & feedback, which is 15–20%
  at every stage and where most projects lose points.
- **#5** is the best compromise: real data today, a huge reachable user base, and a clean
  in-degree vs. PageRank vs. HITS story.

---

## 4. One-page proposal skeleton, mapped to the rubric

Roughly 500–550 words plus one figure and references. Use the rubric's own words as signposts so the
grader can find each element.

1. **Objective (10%)**, 3–4 sentences. Who has the problem, a concrete number or anecdote showing it
   matters, and why now.
2. **Related work (10%)**, 3–4 items, one line each: what it does, then *"Unlike X, we …"*. Include at
   least one existing **app** and one **paper**. The rubric penalizes "an obvious comparable app …
   missing".
3. **Course concept & network analysis (15%)**, which needs four labeled pieces:
   (a) the concept and lesson; (b) *"We choose A over B (covered in class) because …"*;
   (c) **Data:** source, size and access method; (d) **Hypothesis:** a claim that could be false.
4. **Proposed work (20%).** What the finished prototype does, in one sentence. A 3-checkpoint plan
   (Oct 30 / mid-Nov / Dec 9). An **Assumptions:** list, stated explicitly as the rubric asks.
5. **Preliminary design (15%).** **One figure** showing 3–4 key screens of the core flow, end to end.
   *Refer to it in the text* ("Figure 1 shows…"); the Writing component checks this.
6. **Users (15%).** Who, how many (give a target n), **why they match the problem**, and **how you
   will reach them** (name the RSO, channel or class).
7. **Evaluation (10%).** 2–3 metrics, each with a reason, how it's measured with real users, and the
   **named baseline**.
8. **AI-use note.** The course requires documenting how generative AI was used, and that applies to
   this brainstorm too.

### Milestones the later rubrics require

- **By Oct 30 (mid-semester):** a core flow you can demo; the analysis run on **real** data with
  results that are *interpreted*, not just "it runs"; **≥1 feedback round and what it changed**;
  the evaluation plan with a baseline per metric.
- **By Dec 9 (final + video):** several feedback rounds showing how the design changed; results vs.
  the baseline; **a candid account of where the network analysis performed poorly, and why**
  (explicitly required for a 4); a 10-minute video with a live end-to-end demo tied back to design
  decisions.
