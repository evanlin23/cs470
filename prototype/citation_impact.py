"""Citation Impact Analysis: Testing Burt's Structural Hole Hypothesis.

Compares downstream citation counts between:
1. Cross-community collaborative publications (bridging structural holes)
2. Within-community collaborative publications (closed triadic cohesion)

Usage:
    python3 prototype/citation_impact.py --data prototype/uiuc_data_scaled.json --out prototype/results/citation_impact.json
"""
import argparse
import itertools
import json
import os
import sys

import networkx as nx
from networkx.algorithms import community as nxc
import numpy as np
from scipy import stats


def load_and_partition(data_path, split_year=2019):
    print(f"Loading dataset from {data_path}...")
    with open(data_path) as f:
        data = json.load(f)

    papers = data["papers"]
    authors = data["authors"]

    g_train = nx.Graph()
    for p in papers:
        if p["year"] <= split_year:
            auths = p["authors"]
            n = len(auths)
            if n < 2:
                continue
            w = 1.0 / (n - 1.0)
            for i in range(n):
                for j in range(i + 1, n):
                    u, v = auths[i], auths[j]
                    if g_train.has_edge(u, v):
                        g_train[u][v]["weight"] += w
                    else:
                        g_train.add_edge(u, v, weight=w)

    print(f"Training Graph (<= {split_year}): {g_train.number_of_nodes()} nodes, {g_train.number_of_edges()} edges")
    return data, g_train


def analyze_citation_impact(data, g_train, split_year=2019):
    # Detect Louvain communities on largest components of training graph
    comps = [c for c in nx.connected_components(g_train) if len(c) > 1]
    if not comps:
        print("Error: No connected components in training graph.")
        return {}

    sub_nodes = set().union(*comps)
    sub_g = g_train.subgraph(sub_nodes).copy()

    communities = nxc.louvain_communities(sub_g, seed=42)
    node_to_comm = {}
    for cid, comm in enumerate(communities):
        for n in comm:
            node_to_comm[n] = cid

    modularity = nxc.modularity(sub_g, communities)
    print(f"Identified {len(communities)} communities (Modularity Q = {modularity:.4f}).")

    eval_papers = [p for p in data["papers"] if p["year"] > split_year]
    print(f"Evaluating {len(eval_papers)} post-{split_year} papers...")

    cross_community_papers = []
    within_community_papers = []

    for p in eval_papers:
        auths = p.get("authors", [])
        if len(auths) < 2:
            continue

        assigned_comms = {node_to_comm[a] for a in auths if a in node_to_comm}
        if len(assigned_comms) == 0:
            continue

        cites = p.get("citations", 0)

        # Check if paper features a newly formed tie not in training graph
        is_new_collab = any(
            (u in node_to_comm and v in node_to_comm and not sub_g.has_edge(u, v))
            for u, v in itertools.combinations(auths, 2)
        )

        paper_record = {
            "id": p["id"],
            "title": p["title"],
            "year": p["year"],
            "citations": cites,
            "num_communities": len(assigned_comms),
            "is_new_collab": is_new_collab
        }

        if len(assigned_comms) > 1:
            cross_community_papers.append(paper_record)
        else:
            within_community_papers.append(paper_record)

    print(f"Found {len(cross_community_papers)} cross-community papers, {len(within_community_papers)} within-community papers.")

    cross_cites = [p["citations"] for p in cross_community_papers]
    within_cites = [p["citations"] for p in within_community_papers]

    if not cross_cites or not within_cites:
        print("Insufficient citation sample sizes.")
        return {}

    mean_cross = float(np.mean(cross_cites))
    median_cross = float(np.median(cross_cites))
    mean_within = float(np.mean(within_cites))
    median_within = float(np.median(within_cites))

    impact_ratio = mean_cross / mean_within if mean_within > 0 else 0.0

    # Two-sample Mann-Whitney U test (non-parametric for citation distributions)
    mwu = stats.mannwhitneyu(cross_cites, within_cites, alternative="greater")
    mwu_twoside = stats.mannwhitneyu(cross_cites, within_cites, alternative="two-sided")

    results = {
        "n_cross_papers": len(cross_community_papers),
        "n_within_papers": len(within_community_papers),
        "mean_citations_cross": round(mean_cross, 2),
        "mean_citations_within": round(mean_within, 2),
        "median_citations_cross": round(median_cross, 2),
        "median_citations_within": round(median_within, 2),
        "impact_ratio": round(impact_ratio, 3),
        "mann_whitney_u": float(mwu.statistic),
        "p_value_one_sided": float(mwu.pvalue),
        "p_value_two_sided": float(mwu_twoside.pvalue),
        "statistically_significant": float(mwu_twoside.pvalue) < 0.05
    }

    print("\n" + "=" * 65)
    print("      BURT CITATION IMPACT ANALYSIS (2020-2024 COLLABORATIONS)")
    print("=" * 65)
    print(f"Cross-Community Papers (Bridging Ties): {results['n_cross_papers']}")
    print(f"  Mean Citations:   {results['mean_citations_cross']:.2f}")
    print(f"  Median Citations: {results['median_citations_cross']:.2f}")
    print("-" * 65)
    print(f"Within-Community Papers (Cohesive Ties): {results['n_within_papers']}")
    print(f"  Mean Citations:   {results['mean_citations_within']:.2f}")
    print(f"  Median Citations: {results['median_citations_within']:.2f}")
    print("-" * 65)
    print(f"Impact Ratio (E[Cross] / E[Within]): {results['impact_ratio']:.3f}x")
    print(f"Mann-Whitney U Test: U = {results['mann_whitney_u']:.1f}, p = {results['p_value_two_sided']:.4e}")
    print(f"Statistically Significant (p < 0.05): {results['statistically_significant']}")
    print("=" * 65 + "\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="Citation Impact Analysis")
    parser.add_argument("--data", default="prototype/uiuc_data_scaled.json", help="Path to input UIUC dataset")
    parser.add_argument("--out", default="prototype/results/citation_impact.json", help="Output path for results")
    args = parser.parse_args()

    data, g_train = load_and_partition(args.data)
    results = analyze_citation_impact(data, g_train)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[Done] Impact analysis saved to {args.out}")


if __name__ == "__main__":
    main()
