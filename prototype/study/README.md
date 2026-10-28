# Method-blinded exploratory study

This tooling does not contain real participant responses. Automated contract tests use in-memory fixtures and must never be reported as participant findings.

Recruit 15 consenting UIUC students across computing and application disciplines. First ask each participant to use the seed → map → recommendation flow and record, without coaching, whether they complete the task and correctly distinguish observed co-authorship from an unconfirmed introduction. Target at least 12/15 successes for each outcome. Keep only a pseudonymous ID, completion/comprehension outcomes, and anonymized observations in the facilitator log. Do not infer actual departmental appointments from community numbers.

Serve `prototype` on port 8765. The participant visits the web interface, then the study interface, chooses a research anchor closest to their interests, and rates all unique cards for that anchor. Each method contributes its actual top five from the SAME cross-community candidate population and shared pre-2020 graph. Identical candidates selected by multiple methods appear once; the private key attributes that rating to every selecting method. This preserves five ratings per method without arbitrarily favoring whichever method was deduplicated first. The session contains at most 15 unique cards. Randomized order and hidden method labels provide method blinding; investigators have the key, so this is not double blinding.

The ten SUS answers concern the interactive BridgeFinder application, not the static recommendation baselines. Session IDs use random UUIDs and persist in memory for that page session. Reloading starts a new session; do not reload mid-study. No defaults fill unanswered responses, no answers are sent to a server, and exports are voluntary. Exported JSON is an array containing one session. Keep the method key private from participants; the study page never fetches it. For collection, serve only the study assets/cards rather than a public repository directory containing the private key.

Combine consented session arrays into one JSON list outside the repository. Analyze with:

```bash
python prototype/study/analyze_study.py --responses /path/to/consented-sessions.json \
  --keys prototype/study/truth_keys.json --out /path/to/study-analysis.json
```

Invalid/incomplete card sets or SUS responses are excluded with reasons. Duplicate or missing participant IDs fail rather than pool participants. No valid sessions is an error. The participant is the analysis unit; overlapping candidates may induce correlations between method scores, handled by the paired comparison rather than treating cards as independent.

Primary outcome: participant-level Relevant-and-New rate (relevance ≥5 and novelty ≥5), BridgeFinder minus Adamic–Adar; target +25 percentage points and two-sided paired Wilcoxon p<.05. Report mean difference and paired t interval (exploratory small-sample interval); t-test p values are supplementary. Other rating/baseline comparisons form one exploratory family and use Holm correction of Wilcoxon p values. Require relevance and novelty means ≥5/7, actionability ≥5/7 and improvement over Topic-Only, and mean SUS ≥80. At N=15 this is exploratory, not a powered confirmatory study. Report exclusions, null results, uncertainty, sample composition and repeated-candidate handling.

The five formative sessions described in the report are author-confirmed qualitative evidence. No raw session notes were supplied. Add authentic anonymized notes when available; do not reconstruct quotes or frequencies from memory or generate them.
