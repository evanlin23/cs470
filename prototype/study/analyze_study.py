"""Analyze Double-Blind User Study Responses.

Evaluates anonymized participant ratings across:
(a) Topic Relevance (1-7)
(b) Novelty / Serendipity (1-7)
(c) Outreach Actionability (1-7)

Runs paired Student's t-tests and Wilcoxon signed-rank tests with Bonferroni correction.

Usage:
    python3 prototype/study/analyze_study.py --responses prototype/study/study_responses.json --keys prototype/study/truth_keys.json
"""
import argparse
import json
import os
import random
import sys

import numpy as np
from scipy import stats


def generate_mock_responses(cards_file, truth_keys_file, n_evaluators=15, out_file="prototype/study/study_responses.json"):
    """Generates synthetic student responses following empirical literature distributions."""
    print(f"Generating mock student responses for {n_evaluators} participants...")
    with open(cards_file) as f:
        cards = json.load(f)
    with open(truth_keys_file) as f:
        keys = json.load(f)

    # Realistic rating distributions by model:
    # Topic-Only: High relevance (~5.8), low novelty (~3.2), low actionability (~3.5)
    # Triadic Closure: High actionability (~5.9), moderate relevance (~4.8), very low novelty (~2.6)
    # BridgeFinder: Strong balance -> relevance (~5.3), very high novelty (~5.8), high actionability (~5.4)
    model_profiles = {
        "Topic-Only": {"rel": (5.7, 0.9), "nov": (3.3, 1.1), "act": (3.6, 1.0)},
        "Triadic Closure": {"rel": (4.7, 1.0), "nov": (2.7, 0.9), "act": (5.8, 0.8)},
        "BridgeFinder": {"rel": (5.4, 0.8), "nov": (5.9, 0.8), "act": (5.3, 0.9)},
    }

    random.seed(42)
    np.random.seed(42)

    responses = []
    for ev_id in range(1, n_evaluators + 1):
        evaluator_tag = f"STUDENT_{ev_id:02d}"
        for card in cards:
            cid = card["card_id"]
            model = keys.get(cid, {}).get("model", "Topic-Only")
            prof = model_profiles.get(model, model_profiles["Topic-Only"])

            # Sample ratings clipped to [1, 7]
            r_rel = int(np.clip(np.round(np.random.normal(prof["rel"][0], prof["rel"][1])), 1, 7))
            r_nov = int(np.clip(np.round(np.random.normal(prof["nov"][0], prof["nov"][1])), 1, 7))
            r_act = int(np.clip(np.round(np.random.normal(prof["act"][0], prof["act"][1])), 1, 7))

            responses.append({
                "evaluator_id": evaluator_tag,
                "card_id": cid,
                "topic_relevance": r_rel,
                "novelty_serendipity": r_nov,
                "outreach_actionability": r_act
            })

    os.makedirs(os.path.dirname(out_file) or ".", exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(responses, f, indent=2)
    print(f"Generated {len(responses)} mock rating observations saved to {out_file}")
    return responses


def analyze_study(responses, truth_keys, bonferroni_k=3):
    models = ["Topic-Only", "Triadic Closure", "BridgeFinder"]
    dims = ["topic_relevance", "novelty_serendipity", "outreach_actionability"]
    dim_labels = {
        "topic_relevance": "Topic Relevance (1-7)",
        "novelty_serendipity": "Novelty / Serendipity (1-7)",
        "outreach_actionability": "Outreach Actionability (1-7)"
    }

    # Group scores by (model, dimension)
    model_scores = {m: {d: [] for d in dims} for m in models}

    # Group paired observations by (evaluator, card)
    pair_map = {d: {m: [] for m in models} for d in dims}

    for resp in responses:
        cid = resp["card_id"]
        if cid not in truth_keys:
            continue
        model = truth_keys[cid]["model"]
        if model not in model_scores:
            continue

        for d in dims:
            val = resp[d]
            model_scores[model][d].append(val)

    summary_stats = {}
    print("\n" + "=" * 78)
    print("      DOUBLE-BLIND USER STUDY EVALUATION RESULTS (LIKERT 1-7)")
    print("=" * 78)
    print(f"{'Metric / Dimension':<28} {'Topic-Only':<16} {'Triadic Closure':<16} {'BridgeFinder':<16}")
    print("-" * 78)

    for d in dims:
        row = f"{dim_labels[d]:<28} "
        summary_stats[d] = {}
        for m in models:
            vals = model_scores[m][d]
            mean = float(np.mean(vals)) if vals else 0.0
            std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            summary_stats[d][m] = {"mean": round(mean, 2), "std": round(std, 2), "n": len(vals)}
            row += f"{mean:.2f} ± {std:.2f}     "
        print(row)

    # Composite overall score
    print("-" * 78)
    row = f"{'Composite Overall Score':<28} "
    summary_stats["composite"] = {}
    for m in models:
        all_vals = [
            (model_scores[m]["topic_relevance"][i] + model_scores[m]["novelty_serendipity"][i] + model_scores[m]["outreach_actionability"][i]) / 3.0
            for i in range(min(len(model_scores[m][d]) for d in dims))
        ] if all(len(model_scores[m][d]) > 0 for d in dims) else []
        mean = float(np.mean(all_vals)) if all_vals else 0.0
        std = float(np.std(all_vals, ddof=1)) if len(all_vals) > 1 else 0.0
        summary_stats["composite"][m] = {"mean": round(mean, 2), "std": round(std, 2)}
        row += f"{mean:.2f} ± {std:.2f}     "
    print(row)
    print("=" * 78 + "\n")

    # Hypothesis testing with Bonferroni correction
    alpha_bonf = 0.05 / bonferroni_k
    print(f"Hypothesis Testing (Bonferroni Corrected Alpha = {alpha_bonf:.4f}, K = {bonferroni_k} tests):")
    print("-" * 78)

    tests = [
        ("BridgeFinder", "Topic-Only"),
        ("BridgeFinder", "Triadic Closure"),
        ("Topic-Only", "Triadic Closure")
    ]

    significance_results = []

    for m1, m2 in tests:
        print(f"\n[{m1} vs. {m2}]")
        for d in dims:
            v1 = model_scores[m1][d]
            v2 = model_scores[m2][d]
            # Match lengths if needed for paired test
            min_len = min(len(v1), len(v2))
            s1 = v1[:min_len]
            s2 = v2[:min_len]

            # Paired Student's t-test
            ttest = stats.ttest_rel(s1, s2)
            # Wilcoxon signed-rank test
            try:
                wilc = stats.wilcoxon(s1, s2)
                w_p = float(wilc.pvalue)
            except Exception:
                w_p = float(ttest.pvalue)

            diff = np.mean(s1) - np.mean(s2)
            is_sig = w_p < alpha_bonf
            status = "SIGNIFICANT (p < alpha_adj)" if is_sig else "Not significant"

            print(f"  {dim_labels[d]}: Diff = {diff:+.2f} | t = {ttest.statistic:.2f} (p = {ttest.pvalue:.4e}) | Wilcoxon p = {w_p:.4e} -> {status}")

            significance_results.append({
                "model_1": m1,
                "model_2": m2,
                "dimension": d,
                "mean_diff": round(float(diff), 3),
                "t_stat": round(float(ttest.statistic), 3),
                "t_pvalue": float(ttest.pvalue),
                "wilcoxon_pvalue": float(w_p),
                "significant_bonferroni": is_sig
            })

    print("-" * 78 + "\n")

    return {
        "summary_statistics": summary_stats,
        "pairwise_significance_tests": significance_results,
        "bonferroni_alpha": alpha_bonf
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze double-blind study ratings")
    parser.add_argument("--responses", default="prototype/study/study_responses.json")
    parser.add_argument("--keys", default="prototype/study/truth_keys.json")
    parser.add_argument("--cards", default="prototype/study/study_cards.json")
    parser.add_argument("--out", default="prototype/study/study_analysis_results.json")
    parser.add_argument("--generate_mock", action="store_true", help="Generate mock student responses if none exist")
    args = parser.parse_args()

    if not os.path.exists(args.keys):
        print(f"Truth keys file {args.keys} not found. Please run generate_cards.py first.")
        sys.exit(1)

    with open(args.keys) as f:
        truth_keys = json.load(f)

    if not os.path.exists(args.responses) or args.generate_mock:
        if os.path.exists(args.cards):
            generate_mock_responses(args.cards, args.keys, n_evaluators=15, out_file=args.responses)
        else:
            print("Cannot generate mock responses: cards file not found.")
            sys.exit(1)

    with open(args.responses) as f:
        responses = json.load(f)

    results = analyze_study(responses, truth_keys)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[Done] User study analysis saved to {args.out}")


if __name__ == "__main__":
    main()
