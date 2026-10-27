"""Statistical Analysis for BridgeFinder Double-Blind User Study.

Fixes methodological pooling bug: aggregates ratings per participant and method
first (N participants -> df = N-1) before running paired Student's t-tests and
Wilcoxon signed-rank tests with Bonferroni correction (alpha = 0.05 / 3 = 0.0167).

Usage:
    python3 prototype/study/analyze_study.py --responses prototype/study/study_responses.json --keys prototype/study/truth_keys.json
"""
import argparse
import json
import os
import sys
import statistics
from collections import defaultdict
from scipy import stats


def analyze_responses(responses_path, keys_path, out_path):
    if not os.path.exists(responses_path):
        print(f"[Notice] {responses_path} not found. Collect real participant exports from prototype/study/index.html first.")
        sys.exit(0)

    with open(responses_path) as f:
        responses = json.load(f)
    with open(keys_path) as f:
        truth_keys = json.load(f)

    # Group by participant_id -> method -> dimension -> list of card ratings
    per_participant = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    relevant_and_new = defaultdict(lambda: defaultdict(list))

    for entry in responses:
        pid = entry.get("participant_id", "anon")
        cid = str(entry.get("card_id"))
        method = truth_keys.get(cid)
        if not method:
            continue
        rel = float(entry["relevance"])
        nov = float(entry["novelty"])
        act = float(entry["actionability"])

        per_participant[pid][method]["relevance"].append(rel)
        per_participant[pid][method]["novelty"].append(nov)
        per_participant[pid][method]["actionability"].append(act)
        relevant_and_new[pid][method].append(1.0 if (rel >= 5.0 and nov >= 5.0) else 0.0)

    methods = ["BridgeFinder", "Triadic Closure", "Topic-Only"]
    dims = ["relevance", "novelty", "actionability"]

    # Compute participant-level means (proper unit of analysis for paired tests)
    pids = [
        pid for pid in per_participant
        if all(m in per_participant[pid] for m in methods)
    ]
    print(f"Analyzing N = {len(pids)} complete participant evaluations (Bonferroni alpha = 0.0167)...")

    summary = {"n_participants": len(pids), "methods": {}, "paired_tests": {}}

    for m in methods:
        summary["methods"][m] = {}
        for d in dims:
            p_means = [statistics.mean(per_participant[pid][m][d]) for pid in pids]
            summary["methods"][m][d] = {
                "mean": round(statistics.mean(p_means), 2) if p_means else 0.0,
                "std": round(statistics.stdev(p_means), 2) if len(p_means) > 1 else 0.0,
            }
        rn_means = [statistics.mean(relevant_and_new[pid][m]) for pid in pids]
        summary["methods"][m]["relevant_and_new_rate"] = round(statistics.mean(rn_means), 3) if rn_means else 0.0

    # Paired tests across participant means: BridgeFinder vs baselines
    for baseline in ["Triadic Closure", "Topic-Only"]:
        pair_key = f"BridgeFinder_vs_{baseline.replace(' ', '_')}"
        summary["paired_tests"][pair_key] = {}
        for d in dims:
            bf_vec = [statistics.mean(per_participant[pid]["BridgeFinder"][d]) for pid in pids]
            bl_vec = [statistics.mean(per_participant[pid][baseline][d]) for pid in pids]
            if len(bf_vec) >= 2:
                t_stat, p_t = stats.ttest_rel(bf_vec, bl_vec)
                try:
                    w_stat, p_w = stats.wilcoxon(bf_vec, bl_vec)
                except ValueError:
                    w_stat, p_w = 0.0, 1.0
                summary["paired_tests"][pair_key][d] = {
                    "t_stat": round(float(t_stat), 3),
                    "p_ttest": float(p_t),
                    "w_stat": round(float(w_stat), 3),
                    "p_wilcoxon": float(p_w),
                    "significant_bonferroni": bool(p_t < 0.0167),
                }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--responses", default="prototype/study/study_responses.json")
    parser.add_argument("--keys", default="prototype/study/truth_keys.json")
    parser.add_argument("--out", default="prototype/study/study_analysis_results.json")
    args = parser.parse_args()
    analyze_responses(args.responses, args.keys, args.out)
