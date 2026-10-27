"""Temporal Backtest Engine for BridgeFinder.

Evaluates 2015-2019 collaboration topology against 2020-2024 ground-truth cross-community ties.
Implements leak-free temporal topic profiling (strictly pre-split publications).

Usage:
    python3 prototype/backtest.py --data prototype/uiuc_data.json --out prototype/results/backtest_results.json
"""
import argparse
import json
import math
import os
import sys
from collections import defaultdict, Counter

import networkx as nx
from networkx.algorithms import community as nxc


def build_graphs(data, split_year=2019):
    """Constructs weighted training graph (<= split_year) and evaluation graph (> split_year)
    with strict leak-free temporal topic profiling (pre-split only).
    """
    papers = data["papers"]
    authors = data["authors"]

    g_train = nx.Graph()
    g_eval = nx.Graph()

    # Accumulate author topics STRICTLY from training-window papers (<= split_year)
    train_author_topics = defaultdict(Counter)

    for p in papers:
        year = p["year"]
        auths = p["authors"]
        n_auth = len(auths)
        if n_auth < 2:
            continue
        weight = 1.0 / (n_auth - 1.0)

        target_g = g_train if year <= split_year else g_eval

        if year <= split_year:
            for t in p.get("topics", []):
                for a in auths:
                    train_author_topics[a][t] += 1

        for i in range(n_auth):
            for j in range(i + 1, n_auth):
                u, v = auths[i], auths[j]
                if target_g.has_edge(u, v):
                    target_g[u][v]["weight"] += weight
                else:
                    target_g.add_edge(u, v, weight=weight)

    # Assign leak-free topics to training graph nodes
    for aid, ainfo in authors.items():
        if aid in g_train:
            top_k = [t for t, _ in train_author_topics[aid].most_common(10)]
            g_train.add_node(aid, name=ainfo.get("name", aid), topics=set(top_k))
        if aid in g_eval:
            g_eval.add_node(aid, name=ainfo.get("name", aid))

    print(f"Training Graph (<= {split_year}): {g_train.number_of_nodes()} nodes, {g_train.number_of_edges()} edges")
    print(f"Evaluation Graph (> {split_year}): {g_eval.number_of_nodes()} nodes, {g_eval.number_of_edges()} edges")
    return g_train, g_eval, authors


def compute_burt_constraint(G):
    """Computes Burt's aggregate network constraint C_i and autonomy H_i = 1 - C_i."""
    burt_autonomy = {}
    node_strength = {n: sum(d.get("weight", 1.0) for _, d in G[n].items()) for n in G.nodes()}

    for i in G.nodes():
        neighbors = list(G.neighbors(i))
        k = len(neighbors)
        if k <= 1:
            burt_autonomy[i] = 0.0
            continue

        total_w = node_strength[i]
        p = {nbr: G[i][nbr].get("weight", 1.0) / total_w for nbr in neighbors}

        C_i = 0.0
        for j in neighbors:
            indirect = 0.0
            for q in neighbors:
                if q != j and G.has_edge(q, j):
                    total_q = node_strength.get(q, 0.0)
                    p_qj = G[q][j].get("weight", 1.0) / total_q if total_q > 0 else 0
                    indirect += p[q] * p_qj
            c_ij = (p[j] + indirect) ** 2
            C_i += c_ij

        burt_autonomy[i] = max(0.0, 1.0 - C_i)

    return burt_autonomy


def compute_topic_similarity(topics_u, topics_v):
    if not topics_u or not topics_v:
        return 0.0
    intersection = len(topics_u & topics_v)
    union = len(topics_u | topics_v)
    return intersection / union if union > 0 else 0.0


def three_hop_path_counts(G, seed):
    """Count simple 3-edge paths seed -> a -> b -> candidate."""
    counts = Counter()
    for a in G.neighbors(seed):
        for b in G.neighbors(a):
            if b == seed:
                continue
            for cand in G.neighbors(b):
                if cand not in (seed, a, b):
                    counts[cand] += 1
    return counts


def evaluate_baselines(g_train, g_eval, authors, min_eval_edges=1):
    print("Running Louvain community detection on training graph...")
    comps = [c for c in nx.connected_components(g_train) if len(c) > 1]
    if not comps:
        print("Graph has no connected edges.")
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

    burt_autonomy = compute_burt_constraint(sub_g)
    betweenness = nx.betweenness_centrality(sub_g, k=min(200, len(sub_nodes)))

    # Ground truth: newly formed edges in g_eval across different communities
    ground_truth = defaultdict(set)
    for u, v in g_eval.edges():
        if u in node_to_comm and v in node_to_comm:
            if not sub_g.has_edge(u, v):
                if node_to_comm[u] != node_to_comm[v]:
                    ground_truth[u].add(v)
                    ground_truth[v].add(u)

    eval_seeds = [u for u in ground_truth if len(ground_truth[u]) >= min_eval_edges]
    print(f"Eligible evaluation seeds with new cross-community ties: {len(eval_seeds)}")

    models = [
        "Preferential Attachment",
        "Global Betweenness",
        "Topic-Only",
        "Triadic Closure (Adamic-Adar)",
        "BridgeFinder (Proposal Topic+Path)",
        "BridgeFinder"
    ]
    metrics = {m: {"p5": [], "p10": [], "r10": [], "ndcg10": []} for m in models}

    for idx, u in enumerate(eval_seeds):
        u_comm = node_to_comm[u]
        u_topics = sub_g.nodes[u].get("topics", set())
        actual_targets = ground_truth[u]

        candidates = [v for v in sub_nodes if v != u and not sub_g.has_edge(u, v) and node_to_comm[v] != u_comm]
        if not candidates:
            continue

        scores = {m: {} for m in models}

        # 1. Preferential Attachment
        k_u = sub_g.degree(u)
        for v in candidates:
            scores["Preferential Attachment"][v] = k_u * sub_g.degree(v)

        # 2. Global Betweenness
        for v in candidates:
            scores["Global Betweenness"][v] = betweenness.get(v, 0.0)

        # Precompute 2-hop neighbors and path counts
        u_nbrs = list(sub_g.neighbors(u))
        aa_scores = defaultdict(float)
        two_hop_nodes = set()
        for w in u_nbrs:
            deg = sub_g.degree(w)
            if deg > 1:
                inv_log = 1.0 / math.log(deg)
                for nw in sub_g.neighbors(w):
                    if nw != u:
                        aa_scores[nw] += inv_log
                        two_hop_nodes.add(nw)

        path_counts = three_hop_path_counts(sub_g, u)

        # 3. Topic-Only (Leak-Free)
        for v in candidates:
            scores["Topic-Only"][v] = compute_topic_similarity(u_topics, sub_g.nodes[v].get("topics", set()))

        # 4. Triadic Closure (Adamic-Adar)
        for v in candidates:
            scores["Triadic Closure (Adamic-Adar)"][v] = aa_scores.get(v, 0.0)

        # 5. Proposal-Faithful Topic + Introduction Path (lambda = 0.5)
        for v in candidates:
            sim = scores["Topic-Only"][v]
            c = path_counts.get(v, 0)
            path_bonus = c / (1.0 + c)
            scores["BridgeFinder (Proposal Topic+Path)"][v] = sim + 0.5 * path_bonus

        # 6. BridgeFinder Multi-Objective (eta = 0.4)
        for v in candidates:
            topic_sim = scores["Topic-Only"][v]
            aut = burt_autonomy.get(v, 0.0)
            v_nbrs = list(sub_g.neighbors(v))
            ext_u = sum(1 for w in v_nbrs if node_to_comm.get(w) == u_comm)
            bsi = ext_u / len(v_nbrs) if v_nbrs else 0.0
            path_prob = 1.0 if v in two_hop_nodes else (0.5 if path_counts.get(v, 0) > 0 else 0.1)

            b_struct = 0.3 * aut + 0.3 * bsi + 0.4 * path_prob
            scores["BridgeFinder"][v] = 0.6 * topic_sim + 0.4 * b_struct

        # Metrics computation
        for m in models:
            ranked = sorted(candidates, key=lambda c: scores[m][c], reverse=True)
            top5 = ranked[:5]
            top10 = ranked[:10]

            hits5 = sum(1 for c in top5 if c in actual_targets)
            metrics[m]["p5"].append(hits5 / 5.0)

            hits10 = sum(1 for c in top10 if c in actual_targets)
            metrics[m]["p10"].append(hits10 / 10.0)
            metrics[m]["r10"].append(hits10 / len(actual_targets))

            dcg = sum((1.0 / math.log2(rank + 2)) for rank, c in enumerate(top10) if c in actual_targets)
            idcg = sum(1.0 / math.log2(r + 2) for r in range(min(10, len(actual_targets))))
            metrics[m]["ndcg10"].append(dcg / idcg if idcg > 0 else 0.0)

    summary = {}
    print("\n" + "=" * 80)
    print(f"{'Model / Algorithm':<36} {'P@5':<10} {'P@10':<10} {'R@10':<10} {'NDCG@10':<10}")
    print("-" * 80)
    for m in models:
        p5 = sum(metrics[m]["p5"]) / len(metrics[m]["p5"]) if metrics[m]["p5"] else 0.0
        p10 = sum(metrics[m]["p10"]) / len(metrics[m]["p10"]) if metrics[m]["p10"] else 0.0
        r10 = sum(metrics[m]["r10"]) / len(metrics[m]["r10"]) if metrics[m]["r10"] else 0.0
        ndcg10 = sum(metrics[m]["ndcg10"]) / len(metrics[m]["ndcg10"]) if metrics[m]["ndcg10"] else 0.0
        summary[m] = {"P@5": round(p5, 4), "P@10": round(p10, 4), "R@10": round(r10, 4), "NDCG@10": round(ndcg10, 4)}
        print(f"{m:<36} {p5:<10.4f} {p10:<10.4f} {r10:<10.4f} {ndcg10:<10.4f}")
    print("=" * 80 + "\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Run BridgeFinder Temporal Backtest")
    parser.add_argument("--data", default="prototype/uiuc_data.json")
    parser.add_argument("--out", default="prototype/results/backtest_results.json")
    args = parser.parse_args()

    with open(args.data) as f:
        data = json.load(f)

    g_train, g_eval, authors = build_graphs(data, split_year=2019)
    results = evaluate_baselines(g_train, g_eval, authors)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {args.out}")


if __name__ == "__main__":
    main()
