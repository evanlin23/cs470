# Source checks for the related-work comparisons

Each comparison in Section 2 that goes beyond a product description was checked against a readable source.

## Tang et al. (primary source)

Source supplied by the author as `2339530.2339730.pdf`. The document title, authors and printed pagination match the citation in the midterm.

Jie Tang, Sen Wu, Jimeng Sun and Hang Su. *Cross-domain Collaboration Recommendation*. Proceedings of the 18th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2012, pp. 1285–1293.

Uploaded PDF SHA-256: `8cda3a0ce9b3b3e68ee8ce5babd02c5ce850a34b308840a7be48a86e4dc7d6f7`.

The source was read for its problem definition, methods and evaluation. Page references below are the paper's printed page numbers. The PDF remains the user's attachment rather than being republished in the repository or Overleaf project.

### Verified claims

| Claim | Primary-source support |
|---|---|
| The model represents researchers using publications and words from those publications. | §2, p. 1286, defines user attributes and domain-specific topic distributions. The recommendation query is an author with a topic model. |
| CTL learns topics associated with collaboration across fields. | Abstract, p. 1285; §3.3, pp. 1288–1289. Cross-domain Topic Learning separates single-domain documents from jointly authored documents and models collaboration topics. |
| The method uses network structure as well as topics. | Figure 2, p. 1287; §3.3, p. 1289, “Cross-domain recommendation via random walk.” Learned topics are incorporated into the collaboration graph, and random walk with restart ranks target-domain authors. |
| Complementary expertise is part of the method's motivation and representation. | Abstract and introduction, p. 1285; §3, p. 1287; §3.3, pp. 1288–1289. The model relates topics from different fields rather than requiring identical topic labels. This is a capability and motivation, not proof that every suggestion is complementary or useful. |
| The reported evaluation concerns publication-based collaborations. | §4.1–4.2, p. 1290, uses historical collaboration data to predict continued or new cross-domain collaborations. It does not establish student usability or willingness to make an introduction. |

### Comparison with BridgeFinder

The paper contributes a learned model of cross-field topic relationships combined with a network-ranking procedure. Its need for publication-based author representations limits direct use for a student with no papers. This is a limitation relative to our target task, not a claim that the method could never be adapted for students.

BridgeFinder uses a chosen researcher as the student's interest proxy. Its fixed Jaccard-topic/path score and >=3-hop cross-community eligibility use the existing co-authorship graph, and the interface shows an observed shortest route. It does not fit CTL or learn mappings between different fields' topics. This keeps our implemented method explicit while acknowledging a capability it lacks. Selecting a researcher remains an imperfect proxy for personal interests, which the planned student ratings assess directly.

Do not claim that Tang ignores network structure, that only BridgeFinder uses paths, or that our method outperforms CTL. We did not run a head-to-head comparison. Our backtest concerns new ties only and is not an exact replication of Tang's continued-or-new collaboration evaluation. Keep the main paper's one current dataset and one historical metric.

The original proposal is unchanged. Its older statement that Tang does not use network structure is contradicted by this primary source and must not be copied into the authors' midterm rewrite.

## ReferralWeb

Cited paper: H. Kautz, B. Selman and M. Shah. *Referral Web: Combining Social Networks and Collaborative Filtering*. Communications of the ACM 40(3):63–65, 1997. The bibliographic record was confirmed, but the ACM full text was not reachable from this environment, and the open-access companion article (*The Hidden Web*, AI Magazine 18(2):27–36, 1997) could not be downloaded.

The paragraph therefore states only what an open-access secondary source attributes to the CACM paper. That source is S. Perugini, M. A. Gonçalves and E. A. Fox, *A Connection-Centric Survey of Recommender Systems Research*, arXiv:cs/0205059v2 (2003), pp. 17–18, cited in the paper as well.

| Claim in the paper | Support in the survey (citing Kautz et al., CACM 1997) |
|---|---|
| Links people whose names appear close together in Web documents | "an edge exists between two individuals if their names appear in close proximity in a web document" |
| Users explore the resulting network | "Kautz et al. intended for users to interactively explore the implicit, existing social network" |
| Chain of acquaintances to a known researcher | Goal "finding referral chains", e.g. "What is my relationship to Marvin Minsky?" |
| Colleagues and colleagues of colleagues who know a topic | Goal "searching for experts", e.g. "What colleagues of mine, or colleagues of colleagues of mine, know about simulated annealing?" |
| Chain and colleague queries start from the user, so the user must be in the network, and answers stay within a few links | Both example questions above are posed from the user ("my", "of mine") and reach at most colleagues of colleagues |

The survey also lists proximity search near a known expert, which does not start from the user. The paper's wording is limited to chain and colleague queries for that reason. Do not claim ReferralWeb used co-authorship specifically, or that it ranked by topic, unless the full text is checked.
