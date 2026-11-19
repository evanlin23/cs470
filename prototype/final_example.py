"""The worked example in the final report: top suggestions of three methods for one researcher.

    python prototype/final_example.py --out prototype/results/final_example.json
"""
import argparse
import json
from pathlib import Path

import final_analysis as fa
from model import prepare_model, candidate_features, MODEL_VERSION
from run_metadata import metadata_for, save_manifest

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--data', default=str(ROOT/'uiuc_data_scaled.json'))
    parser.add_argument('--name', default='Indranil Gupta')
    parser.add_argument('--out', default=str(ROOT/'results'/'final_example.json'))
    parser.add_argument('--manifest-out', default=str(ROOT/'results'/'final-example-run.json'))
    args = parser.parse_args()
    data = json.loads(Path(args.data).read_text())
    graph, evaluation, authors, membership = prepare_model(data)
    fa.G.update(ppr=fa.ppr_operator(graph))
    seed = next(a for a in sorted(graph) if authors[a]['name'] == args.name)
    rows = candidate_features(graph, seed, membership)
    ppr, index = fa.personalized_pagerank(seed), fa.G['ppr'][1]
    for row in rows:
        row['ppr'] = float(ppr[index[row['candidate_id']]])
    truth = fa.ground_truth(graph, evaluation, membership)[seed]
    pools = {'BridgeFinder': ([r for r in rows if r['proposal_eligible']], lambda r: r['score']),
             'Personalized PageRank, distant pool': ([r for r in rows if r['proposal_eligible']], lambda r: r['ppr']),
             'Triadic closure': ([r for r in rows if r['distance'] == 2], lambda r: r['shared_coauthors'])}
    result = {'seed': args.name, 'seed_topics': sorted(graph.nodes[seed]['topics']), 'new_ties_2020_2024': len(truth), 'methods': {}}
    for method, (pool, key) in pools.items():
        top = sorted(pool, key=lambda r: (-key(r), r['candidate_id']))[:5]
        result['methods'][method] = [{'name': authors[r['candidate_id']]['name'], 'topic_overlap': round(r['topic_similarity'], 2),
                                      'coauthors': graph.degree(r['candidate_id']), 'three_step_routes': r['three_hop_paths'],
                                      'distance': r['distance'], 'topics': sorted(graph.nodes[r['candidate_id']]['topics'])[:4],
                                      'became_collaborator': r['candidate_id'] in truth} for r in top]
    Path(args.out).write_text(json.dumps(result, indent=2)+'\n')
    save_manifest(args.manifest_out, args.out, metadata_for(args.data, ['model.py', 'final_analysis.py', 'final_example.py'], MODEL_VERSION))
    print(f'Saved {args.out}')


if __name__ == '__main__':
    main()
