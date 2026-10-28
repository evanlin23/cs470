"""Measure brokerage/triadic-closure behavior without changing the ranker."""
import argparse
import json
from pathlib import Path
from model import prepare_model, rank_candidates, candidate_features, MODEL_VERSION
from run_metadata import metadata_for


def audit(data_path, bundle_path):
    graph, _, authors, membership, autonomy = prepare_model(json.loads(Path(data_path).read_text()))
    bundle = json.loads(Path(bundle_path).read_text())
    counts = lambda: {'two_hop': 0, 'three_hop': 0, 'longer_than_three': 0, 'unreachable': 0}
    result = {**metadata_for(data_path, ['model.py', 'audit_recommendations.py'], MODEL_VERSION),
              'contexts': len(bundle['seeds']), 'all_seed_candidate_pairs': counts(), 'displayed_top10': counts(),
              'top5_overlap_with_closure': 0, 'top10_overlap_with_closure': 0, 'top5_overlap_with_topic_only': 0,
              'contexts_with_different_top5_from_closure': 0, 'examples_without_shared_coauthor': []}
    sizes = []
    def kind(row):
        return 'unreachable' if row['path_ids'] is None else 'two_hop' if len(row['path_ids']) == 3 else 'three_hop' if len(row['path_ids']) == 4 else 'longer_than_three'
    for seed in bundle['seeds']:
        rows = rank_candidates(graph, seed['id'], membership, autonomy)
        sizes.append(len(rows))
        all_rows = candidate_features(graph, seed['id'], membership, autonomy)
        aa = sorted([row for row in all_rows if row['shared_coauthors'] > 0], key=lambda row: (-row['shared_coauthors'], row['candidate_id']))
        topic = sorted(rows, key=lambda row: (-row['topic_similarity'], row['candidate_id']))
        bf5 = {row['candidate_id'] for row in rows[:5]}
        aa5 = {row['candidate_id'] for row in aa[:5]}
        result['top5_overlap_with_closure'] += len(bf5 & aa5)
        result['top10_overlap_with_closure'] += len({row['candidate_id'] for row in rows[:10]} & {row['candidate_id'] for row in aa[:10]})
        result['top5_overlap_with_topic_only'] += len(bf5 & {row['candidate_id'] for row in topic[:5]})
        result['contexts_with_different_top5_from_closure'] += bf5 != aa5
        assert [row['candidate_id'] for row in rows[:10]] == [row['candidate_id'] for row in bundle['recommendations'][seed['id']]]
        for row in all_rows:
            result['all_seed_candidate_pairs'][kind(row)] += 1
        for rank, row in enumerate(rows[:10], 1):
            result['displayed_top10'][kind(row)] += 1
            if kind(row) == 'three_hop':
                assert row['shared_coauthors'] == 0
                if len(result['examples_without_shared_coauthor']) < 3:
                    result['examples_without_shared_coauthor'].append({
                        'seed': seed['name'], 'candidate': authors[row['candidate_id']]['name'], 'rank': rank,
                        'shared_coauthors': row['shared_coauthors'], 'score': row['score'],
                        'route': [authors[node]['name'] for node in row['path_ids']]})
    result['candidate_count_range'] = [min(sizes), max(sizes)]
    result['displayed_slots'] = sum(result['displayed_top10'].values())
    result['top5_slots'] = 5*len(sizes)
    result['interpretation'] = 'Proposal-compliant recommendations are reachable at distance >=3 and have no shared coauthor. Simple common-neighbor triadic closure uses two-hop candidates; their disjoint pools enforce zero overlap, not evidence of superior quality.'
    assert result['displayed_top10']['two_hop'] == 0
    assert result['displayed_top10']['unreachable'] == 0
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='prototype/uiuc_data_scaled.json')
    parser.add_argument('--bundle', default='prototype/web/data.json')
    parser.add_argument('--out', default='prototype/review/closure-audit.json')
    args = parser.parse_args()
    result = audit(args.data, args.bundle)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
