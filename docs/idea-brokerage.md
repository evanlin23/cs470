# Project spec (draft for review): finding people across the structural holes in UIUC research

CS 470 (Fall 2026), 4-credit project. Team: Evan Lin, Eric Liu.
Status: a pivot from "MethodBridge" (see `project-ideas.md`), after a pilot showed the paper-level version doesn't work (below).
Proposal due Fri Oct 2, 5:00pm Central; mid-semester report Oct 30; final report and video Dec 9.

## Problem and users
Students looking for research mentors, and researchers looking for collaborators, mostly find people through
their existing network: their advisor's contacts, their lab, their department. That surfaces people who are
already close to them. Burt (*Structural holes and good ideas*, 2004; on the course reading list) found that
people who **broker between groups that don't talk to each other** have better ideas. Nothing helps a UIUC
student or researcher see those gaps, or find a specific person on the other side who works on similar
problems but has no ties into their circle.

- **Primary users:** UIUC undergrad and grad students looking for research mentors or collaborators outside
  their lab.
- **Secondary users:** faculty and postdocs looking for interdisciplinary collaborators (e.g. for grants).

## What the app does
1. **You:** pick yourself (if you have papers), your advisor or lab, or a few people you know. Also describe
   your interests in a sentence, or pick topics.
2. **Campus hole map:** research communities at UIUC, detected from co-authorship (not department labels),
   with your position marked. Highlighted *structural holes* are pairs of communities whose topics overlap a
   lot but which have almost no co-authored papers between them.
3. **People across the hole:** a ranked list of researchers whose topics overlap yours but who are far from
   you in the co-authorship graph. Each comes with a "why": shared topics, network distance, and how much
   connecting to them would increase your brokerage.
4. **Person card:** their recent papers that match your interests, the shortest intro path through the graph
   if one exists (a weak tie who could introduce you), and a draft outreach email.

## Network analysis (course concepts)
- **Graph.** Nodes are researchers. Edges are co-authorship, from OpenAlex works with ≥1 UIUC author,
  2015–2024, ignoring papers with more than ~25 authors (hyperauthorship). Edges are weighted by the number
  of joint papers, with time decay. Node attributes are OpenAlex topic vectors (from works' topics) and
  department/institution.
- **Communities (Lesson 10):** Louvain modularity. Girvan–Newman is the in-class alternative. The earlier
  pilot found Girvan–Newman could not split a 150-node dense subgraph in 148 s, where Louvain finished in
  1.5 s on 610 nodes (Q = 0.51), so we have evidence for this choice.
- **Structural holes (Lesson 1, Burt):** Burt's **constraint** and **effective size** of each ego network.
  The **brokerage gain** of a candidate tie u–v is the drop in u's constraint if the tie were added.
  - Community-level hole = high topic similarity × low inter-community tie density.
- **Ranking people for user u:** topic similarity(u, v) × network distance(u, v) × brokerage gain(u, v), with
  a floor on topic similarity.
- **In-class baselines:**
  - **Triadic closure / friend-of-friend** (common neighbours), i.e. "people you may know".
  - **Topic similarity only** (no network).
  - **Degree / most-collaborative** ("famous people").
- **Intro paths (Lessons 1 and 13):** the shortest path to v through weak ties or local bridges, and existing
  brokers with high betweenness.

## Data
OpenAlex (the free API key is stored in this environment as `OPENALEX_API_KEY`). Use works filtered by the
UIUC institution ID, with authorships, institutions, topics and publication years. Expected cost is well under
$1. Students without papers (cold start) are placed through their advisor, lab or chosen contacts, plus
interest topics.

## Falsifiable claims
1. **Backtest.** Build the graph and topic vectors from 2015–2019. Look at pairs with high topic similarity
   that are far apart in that graph. They formed a new collaboration in 2020–2024 at a higher rate than
   (a) random topic-similar pairs and (b) friend-of-friend pairs of equal topic similarity. Also: ranking by
   hole score puts the actual future cross-community collaborators higher than triadic closure does.
   This shows the "holes" are real, viable opportunities rather than noise. It could be false.
2. **Users.** Students rate a larger share of suggestions as both "relevant" and "new to me" than for
   friend-of-friend or topic-only suggestions. This is within-subject, on their own interests.
3. **Optional replication of Burt on UIUC data.** Researchers with lower constraint have higher subsequent
   citation impact, controlling for field and seniority.

## Evaluation
- Backtest precision@k and recall of future collaborations vs the baselines.
- Relevant-and-new rate from user ratings.
- Field/department distance of suggestions.
- Whether users would actually send the outreach email (stated intent), and a follow-up on emails sent.

There are three feedback rounds (October, November, December), with 10–15 students per round recruited via
ACM@UIUC, research SIGs, the undergraduate research office and lab contacts.

## Prototype
A web app (Python back end with networkx, plus a web front end) with the four screens above. The graph is
precomputed nightly from OpenAlex.

## Lessons from the MethodBridge pilot (paper-level version, now dropped)
- On OpenCitations data (GeneRank case, frozen at 2004), the citation "weak-tie walk" from biology seed
  papers never reached PageRank or HITS. 0 of 600 candidates were targets. The OpenAlex run confirmed this:
  none of the 3,111 pre-2005 citers of the seeds cite them.
- What it did find "across the hole" was other biology subfields (lab protocols, BLAST, CLUSTAL). A true
  structural hole has no path, so walking citations can't cross it.
- That's why this version defines "similar" by topic overlap and "unconnected" by graph distance, computed
  over the whole campus graph, instead of walking from the user.

## Known risks / open questions
- OpenAlex author disambiguation and stale affiliations.
- The cold start for students with no papers.
- Whether students actually benefit from "brokerage", and whether faculty welcome cold outreach.
- Ethics and privacy of recommending people. The data is public, but the framing matters.
- Hyperauthorship and large lab papers inflating ties.
- Topic vectors may be too coarse to say two people do "similar research".
- The backtest may confound: topic-similar pairs collaborate more anyway.
