"""Temporal Backtest Engine for BridgeFinder.

Evaluates 2015-2019 collaboration topology against 2020-2024 ground-truth cross-community ties.
Implements leak-free temporal topic profiling (strictly pre-split publications).

Usage:
    python3 prototype/backtest.py --data prototype/uiuc_data_scaled.json --out prototype/results/backtest_results_scaled.json
"""
import argparse
import json
import math
import os
from collections import defaultdict

import networkx as nx
from networkx.algorithms import community as nxc


from model import build_graphs, prepare_training_model, rank_candidates, candidate_features, MODEL_VERSION
from run_metadata import metadata_for, save_manifest

def evaluate_baselines(g_train, g_eval, authors, min_eval_edges=1, metadata=None):
    # Canonical insertion order and tie breaks make this workflow reproducible.
    graph, membership, autonomy = prepare_training_model(g_train)
    communities = [set(n for n in graph if membership[n] == c) for c in sorted(set(membership.values()))]
    print(f"Identified {len(communities)} communities (Modularity Q = {nxc.modularity(graph, communities):.4f}).")
    truth = defaultdict(set)
    for u, v in g_eval.edges():
        if u in membership and v in membership and membership[u] != membership[v] and not graph.has_edge(u, v):
            truth[u].add(v)
            truth[v].add(u)
    seeds = sorted(u for u in truth if len(truth[u]) >= min_eval_edges)
    print(f"Eligible evaluation seeds with new cross-community ties: {len(seeds)}")
    if metadata is not None:
        metadata.update({'training_nodes': graph.number_of_nodes(), 'training_edges': graph.number_of_edges(),
                         'evaluation_nodes': g_eval.number_of_nodes(), 'evaluation_edges': g_eval.number_of_edges(),
                         'communities': len(communities), 'modularity': nxc.modularity(graph, communities),
                         'eligible_seeds': len(seeds), 'split_year': 2019, 'louvain_seed': 42,
                         'tie_break': 'author_id',
                         'weights': {'topic': 1.0, 'saturated_three_path_count': 0.5},
                         'minimum_hops': 3, 'require_reachable': True, 'edge_weight': 'joint_paper_count',
                         'baseline_pools': {'Topic-Only': 'reachable cross-community distance >=3',
                                            'Triadic Closure': 'native shared-contact cross-community',
                                            'triadic_closure_score': 'number of shared coauthors'},
                         'ground_truth': 'all new cross-community ties among training nodes'})
    models = ["Topic-Only", "Triadic Closure", "BridgeFinder"]
    metrics = {m: defaultdict(list) for m in models}
    for u in seeds:
        rows = candidate_features(graph, u, membership, autonomy)
        proposal = [r for r in rows if r['proposal_eligible']]
        shared_contact = [r for r in rows if r['shared_coauthors'] > 0]
        pools = [proposal, shared_contact, proposal]
        keys = [lambda r: r["topic_similarity"], lambda r: r["shared_coauthors"], lambda r: r["score"]]
        for model, key, pool in zip(models, keys, pools):
            ranked = sorted(pool, key=lambda r: (-key(r), r["candidate_id"]))
            ids = [r["candidate_id"] for r in ranked[:10]]
            hits5 = sum(v in truth[u] for v in ids[:5])
            hits10 = sum(v in truth[u] for v in ids)
            dcg = sum(1 / math.log2(i+2) for i, v in enumerate(ids) if v in truth[u])
            ideal = sum(1 / math.log2(i+2) for i in range(min(10, len(truth[u]))))
            for metric, value in zip(["P@5", "P@10", "R@10", "NDCG@10"], [hits5/5, hits10/10, hits10/len(truth[u]), dcg/ideal]):
                metrics[model][metric].append(value)
    summary = {m: {k: round(sum(v)/len(v), 4) for k, v in values.items()} for m, values in metrics.items()}
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description="Run BridgeFinder Temporal Backtest")
    parser.add_argument("--data", default="prototype/uiuc_data_scaled.json")
    parser.add_argument("--out", default="prototype/results/backtest_results_scaled.json")
    parser.add_argument("--manifest-out", help="Optional JSON sidecar with dataset/code hashes and seed counts")
    args = parser.parse_args()

    with open(args.data) as f:
        data = json.load(f)

    g_train, g_eval, authors = build_graphs(data, split_year=2019)
    metadata = metadata_for(args.data, ['model.py', 'backtest.py'], MODEL_VERSION)
    results = evaluate_baselines(g_train, g_eval, authors, metadata=metadata)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    if args.manifest_out:
        save_manifest(args.manifest_out, args.out, metadata)
    print(f"Results saved to {args.out}")


if __name__ == "__main__":
    main()
