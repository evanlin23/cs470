# MethodBridge: Finding Methods Across the Structural Holes Between Research Fields

Evan Lin (elin26@illinois.edu) · Eric Liu ([NetID]@illinois.edu) · CS 470 project proposal, Fall 2026

![Figure 1. Core flow. (1) Seed papers and a jargon-free restatement of the problem. (2) The user's field and nearby fields; edge width is the number of citation ties, so thin edges are structural holes. (3) Methods ranked by authority in their own field × distance from the user's field, with the reasons shown. (4) A method card: a review to start from (HITS hub), key papers (authorities), and a researcher who bridges both fields. Values in panels 3–4 are illustrative.](fig1_core_flow.png)

## 1 Objective

Many advances are imports: a method that is routine in one field solves an open problem in another. PageRank [4] was published for web search in 1998 but reached gene ranking only in 2005, in GeneRank [7]. Diffusion models came to ML from thermodynamics [8]. Students starting a research project need such imports most, yet they know only their own literature. Missing them is costly: people who broker across structural holes have better ideas [1], and papers that combine atypical prior work have more impact [9]. Imports are hard to find because a method has different names in different fields (synonymy, Lesson 6). In our pilot, a jargon-free description of the GeneRank problem returned psychometrics and antenna papers on Crossref. **MethodBridge** uses the citation network instead. It finds methods that are central in another field but have few ties into yours.

## 2 Related work

*Connected Papers* [15], ResearchRabbit and Litmaps graph a seed's neighbors by co-citation. They reward strong ties to your seeds, so they rarely leave your field; we rank by weak ties across a hole. *Semantic Scholar* [16], Elicit and LLM assistants match on text, which inherits each field's vocabulary, or suggest methods with no evidence of who uses them. Each MethodBridge suggestion shows its evidence: the community that uses it, a review to start from, and a researcher who spans both fields. *Literature-based discovery* [10] and *analogy mining* [11, 12] need shared terms or crowd-annotated purposes; we need neither. Sourati and Evans [13] forecast discoveries from author–concept hypergraphs; we adopt their historical backtest for a tool aimed at one researcher.

## 3 Course concepts and network analysis

The core of the app is **structural holes and local bridges** (Lesson 1 [1, 2]), made concrete with **community discovery** (Lesson 10) and **HITS** (Lesson 6 [3]). (1) From 5–15 seed papers, a *weak-tie walk* collects the seeds' citers, a sample of those citers' references (the candidate methods), and the candidates' own citers, all frozen at a chosen year. (2) Louvain modularity [6] on the co-citation graph finds communities. Those containing seeds form the *home field*. (3) A candidate's *hole score* is 1 minus the share of its co-citation weight that falls inside the home field. (4) HITS runs within each community: authorities are a method's canonical papers, and hubs are reviews to start from. (5) The ranking score is authority × hole score.

**Alternatives from class.** Co-citation with the seeds (triadic closure), which existing tools use, scores any method across a hole near zero by definition. In-degree favors your own field's classics. {{GN_SENTENCE}}
**Data.** OpenCitations [17] (dated citation links) and Crossref. OpenAlex [18] (free key) adds fields, affiliations and abstracts.
**Claim that could be false.** In a backtest on 20–30 documented transfers (e.g. from [14]), with the graph frozen the year before each one, the imported method will rank in our top 10 more often than in the top 10 of co-citation, in-degree or keyword search. {{PILOT_SENTENCE}}

## 4 Proposed work

We will build a web app (Python back end, web front end) for the four screens in Figure 1, plus the backtest harness. **By Oct 30:** the pipeline, a 10-case backtest, a clickable prototype and feedback round 1. **Mid-November:** 20–30 cases, broker suggestions, round 2. **Dec 9:** round 3, evaluation, video. Each neighborhood is computed on demand from cached API calls ({{REQUESTS}}) rather than by indexing all of science.
*Assumptions:* citation communities approximate fields; a method can be represented by its canonical papers, so there is no text extraction; users can name 5–15 seed papers; open citation data covers their fields ({{COVERAGE}}); freezing the graph a year before each transfer prevents backtest leakage.

## 5 Preliminary design

In Figure 1, screen 1 asks for a jargon-free restatement, which prompts thinking across vocabularies [12]. Screen 2 keeps Connected Papers' familiar graph view but colors it by community, so holes appear as thin edges. Screen 3 explains each suggestion with "why" chips, because unexplained recommendations are hard to trust. Screen 4 turns a weak tie into action: a start-here review (HITS hub), the key papers (authorities), and a bridging researcher (ideally at Illinois), with a draft introduction email.

## 6 Users

UIUC graduate students (years 1–3) and undergraduate researchers starting or reframing a project: the need is greatest then, and they already have seed papers. We will recruit 12–15 per round, for three rounds, from CS and interdisciplinary units (iSchool, Beckman, NCSA, Carle Illinois) so home fields vary. We will reach them through graduate mailing lists, ACM@UIUC research SIGs, undergraduate research programs and our labs. Each participant judges suggestions for their own project, so the judges are domain experts. A within-subject design yields 200+ paired judgments per round.

## 7 Evaluation

(1) **Backtest Hit@10 and MRR** of the imported method, against co-citation, in-degree and keyword search: an objective test of whether the network finds real transfers. (2) **Novel-and-useful rate:** the share of suggestions rated both "new to me" and "worth trying" (≥4/5), against the participant's usual tools and an LLM asked the same question. (3) **Field distance** of suggestions, which separates crossing a hole from being merely useful. (4) **Time to a first usable lead.** Success means beating co-citation on (1) and the baselines on (2). We will report where we do not.

*Use of AI.* Claude (Anthropic) helped brainstorm against the rubric, write the pilot code and draft this text. We ran the pilot and checked its output and all references.

## References

[1] R. S. Burt. 2004. Structural holes and good ideas. *American Journal of Sociology* 110(2), 349–399.
[2] M. S. Granovetter. 1973. The strength of weak ties. *American Journal of Sociology* 78(6), 1360–1380.
[3] J. M. Kleinberg. 1999. Authoritative sources in a hyperlinked environment. *Journal of the ACM* 46(5), 604–632.
[4] S. Brin and L. Page. 1998. The anatomy of a large-scale hypertextual Web search engine. *Computer Networks and ISDN Systems* 30(1–7), 107–117.
[5] M. E. J. Newman and M. Girvan. 2004. Finding and evaluating community structure in networks. *Physical Review E* 69, 026113.
[6] V. D. Blondel, J.-L. Guillaume, R. Lambiotte, and E. Lefebvre. 2008. Fast unfolding of communities in large networks. *Journal of Statistical Mechanics*, P10008.
[7] J. L. Morrison, R. Breitling, D. J. Higham, and D. R. Gilbert. 2005. GeneRank: Using search engine technology for the analysis of microarray experiments. *BMC Bioinformatics* 6, 233.
[8] J. Sohl-Dickstein, E. Weiss, N. Maheswaranathan, and S. Ganguli. 2015. Deep unsupervised learning using nonequilibrium thermodynamics. In *Proc. ICML*.
[9] B. Uzzi, S. Mukherjee, M. Stringer, and B. Jones. 2013. Atypical combinations and scientific impact. *Science* 342(6157), 468–472.
[10] D. R. Swanson. 1986. Fish oil, Raynaud's syndrome, and undiscovered public knowledge. *Perspectives in Biology and Medicine* 30(1), 7–18.
[11] T. Hope, J. Chan, A. Kittur, and D. Shahaf. 2017. Accelerating innovation through analogy mining. In *Proc. KDD*, 235–243.
[12] J. Chan, J. C. Chang, T. Hope, D. Shahaf, and A. Kittur. 2018. SOLVENT: A mixed initiative system for finding analogies between research papers. *Proc. ACM Hum.-Comput. Interact.* 2(CSCW), 31.
[13] J. Sourati and J. A. Evans. 2023. Accelerating science with human-aware artificial intelligence. *Nature Human Behaviour* 7, 1682–1696.
[14] D. F. Gleich. 2015. PageRank beyond the Web. *SIAM Review* 57(3), 321–363.
[15] Connected Papers. https://www.connectedpapers.com
[16] Semantic Scholar. https://www.semanticscholar.org
[17] S. Peroni and D. Shotton. 2020. OpenCitations, an infrastructure organization for open scholarship. *Quantitative Science Studies* 1(1), 428–444.
[18] J. Priem, H. Piwowar, and R. Orr. 2022. OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv:2205.01833.
