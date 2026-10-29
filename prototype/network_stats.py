"""Describe the training co-authorship graph the paper interprets.

Reports modularity inside the largest component (disconnected pieces inflate
whole-graph modularity), Burt's constraint for the intermediaries on the demo's
displayed introduction routes, and how many displayed suggestions appear on only
one retained UIUC paper.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import statistics

import networkx as nx
from networkx.algorithms import community as nxc

from model import build_graphs, prepare_training_model, MODEL_VERSION
from run_metadata import metadata_for, save_manifest


def describe(graph, membership, bundle, paper_counts, first_paper):
    components = sorted(nx.connected_components(graph), key=len, reverse=True)
    giant = graph.subgraph(components[0])
    groups = {}
    for node in giant:
        groups.setdefault(membership[node], set()).add(node)
    constraint = nx.constraint(giant, weight='weight')
    routes = [row['path_ids'] for rows in bundle['recommendations'].values() for row in rows]
    intermediaries = sorted({node for path in routes for node in path[1:-1]})
    one_paper = sum(paper_counts[path[-1]] == 1 for path in routes)
    # One-paper suggestions that share that paper with another suggestion for the same researcher.
    teamed = 0
    for rows in bundle['recommendations'].values():
        singles = [first_paper[row['id']] for row in rows if paper_counts[row['id']] == 1]
        teamed += sum(singles.count(paper) > 1 for paper in singles)
    return {
        'nodes': graph.number_of_nodes(), 'edges': graph.number_of_edges(),
        'components': len(components),
        'largest_component': {'nodes': giant.number_of_nodes(), 'share': round(giant.number_of_nodes()/graph.number_of_nodes(), 4),
                              'communities': len(groups), 'modularity': round(nxc.modularity(giant, groups.values()), 4)},
        'constraint_largest_component': {
            'median_all_authors': round(statistics.median(constraint.values()), 4),
            'median_route_intermediaries': round(statistics.median(constraint[n] for n in intermediaries), 4),
            'route_intermediaries': len(intermediaries)},
        'displayed_suggestions_on_one_uiuc_paper': {'count': one_paper, 'share': round(one_paper/len(routes), 4),
                                                    'sharing_that_paper_with_another_suggestion': teamed},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='prototype/uiuc_data_scaled.json')
    parser.add_argument('--bundle', default=str(Path(__file__).resolve().parent/'web/data.json'))
    parser.add_argument('--out', default='prototype/results/network_stats.json')
    parser.add_argument('--manifest-out', help='Optional JSON sidecar with dataset/code hashes')
    args = parser.parse_args()
    with open(args.data) as f:
        data = json.load(f)
    g_train, _, _ = build_graphs(data)
    graph, membership = prepare_training_model(g_train)
    paper_counts = Counter(author for paper in data['papers'] for author in paper['authors'])
    first_paper = {}
    for paper in data['papers']:
        for author in paper['authors']:
            first_paper.setdefault(author, paper['id'])
    with open(args.bundle) as f:
        result = describe(graph, membership, json.load(f), paper_counts, first_paper)
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(result, f, indent=2)
    if args.manifest_out:
        save_manifest(args.manifest_out, args.out, metadata_for(args.data, ['model.py', 'network_stats.py'], MODEL_VERSION))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
