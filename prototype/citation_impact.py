"""Burt's Citation Impact Hypothesis Test on UIUC Co-Authorship Data.

Compares 2020-2024 citation counts of Cross-Community papers (spanning Louvain
communities from the 2015-2019 training graph) vs. Within-Community papers.

Usage:
    python3 prototype/citation_impact.py --data prototype/uiuc_data_scaled.json --out prototype/results/citation_impact.json
"""
import argparse
import json
import os
import statistics
import networkx as nx
from networkx.algorithms import community as nxc
from scipy import stats


def run_citation_impact(data_path, out_path, split_year=2019):
    with open(data_path) as f:
        data = json.load(f)

    papers = data["papers"]
    g_train = nx.Graph()
    for p in papers:
        if p["year"] <= split_year and len(p["authors"]) <= 25:
            auths = p["authors"]
            w = 1.0 / (len(auths) - 1.0)
            for i in range(len(auths)):
                for j in range(i + 1, len(auths)):
                    u, v = auths[i], auths[j]
                    if g_train.has_edge(u, v):
                        g_train[u][v]["weight"] += w
                    else:
                        g_train.add_edge(u, v, weight=w)

    # Louvain communities on training graph
    communities = nxc.louvain_communities(g_train, seed=42)
    node_to_comm = {}
    for cid, comm in enumerate(communities):
        for u in comm:
            node_to_comm[u] = cid

    cross_citations = []
    within_citations = []
    unclassified_count = 0

    for p in papers:
        if p["year"] > split_year and len(p["authors"]) <= 25:
            known_comms = {node_to_comm[a] for a in p["authors"] if a in node_to_comm}
            if len(known_comms) >= 2:
                cross_citations.append(p.get("citations", 0))
            elif len(known_comms) == 1:
                within_citations.append(p.get("citations", 0))
            else:
                unclassified_count += 1

    mean_cross = statistics.mean(cross_citations) if cross_citations else 0.0
    med_cross = statistics.median(cross_citations) if cross_citations else 0.0
    std_cross = statistics.stdev(cross_citations) if len(cross_citations) > 1 else 0.0
    mean_within = statistics.mean(within_citations) if within_citations else 0.0
    med_within = statistics.median(within_citations) if within_citations else 0.0
    std_within = statistics.stdev(within_citations) if len(within_citations) > 1 else 0.0
    ratio = mean_cross / mean_within if mean_within > 0 else 0.0

    u_stat, p_val_two_sided = stats.mannwhitneyu(cross_citations, within_citations, alternative="two-sided")

    result = {
        "n_cross_papers": len(cross_citations),
        "n_within_papers": len(within_citations),
        "n_unclassified_papers": unclassified_count,
        "total_eval_papers": len(cross_citations) + len(within_citations) + unclassified_count,
        "mean_citations_cross": round(mean_cross, 2),
        "std_citations_cross": round(std_cross, 2),
        "median_citations_cross": round(med_cross, 1),
        "mean_citations_within": round(mean_within, 2),
        "std_citations_within": round(std_within, 2),
        "median_citations_within": round(med_within, 1),
        "impact_ratio": round(ratio, 3),
        "mann_whitney_u": float(u_stat),
        "p_value_two_sided": round(float(p_val_two_sided), 4),
    }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="prototype/uiuc_data_scaled.json")
    parser.add_argument("--out", default="prototype/results/citation_impact.json")
    args = parser.parse_args()
    run_citation_impact(args.data, args.out)
