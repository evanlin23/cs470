"""Generate method-hidden cards using the shared temporal model.

Overlapping top-five candidates are shown once and attributed to every model
that selected them, preserving paired comparisons without a priority bias.
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model import prepare_model, rank_candidates, path_description, MODEL_VERSION


def generate(data):
    graph, _, authors, membership, autonomy = prepare_model(data)
    groups = sorted(set(membership.values()))[:5]
    cards, keys = [], {}
    for group in groups:
        seed = min((n for n in graph if membership[n] == group), key=lambda n: (-graph.degree(n), n))
        rows = rank_candidates(graph, seed, membership, autonomy)
        selections = {}
        for method, field in [('BridgeFinder', 'score'), ('Triadic Closure', 'aa'), ('Topic-Only', 'topic_similarity')]:
            for row in sorted(rows, key=lambda r: (-r[field], r['candidate_id']))[:5]:
                selections.setdefault(row['candidate_id'], {'row': row, 'methods': []})['methods'].append(method)
        items = sorted(selections.items())
        random.Random(42 + group).shuffle(items)
        for candidate, selection in items:
            row = selection['row']
            card_id = f'CARD_{len(cards)+1:03d}'
            papers = [p['title'] for p in data['papers'] if p['year'] <= 2019 and candidate in p['authors']][:2]
            cards.append({'card_id': card_id, 'seed_id': seed, 'seed_name': authors[seed]['name'],
                          'seed_department': f'Community {group+1}', 'seed_topics': sorted(graph.nodes[seed]['topics'])[:4],
                          'candidate_name': authors[candidate]['name'], 'candidate_topics': sorted(graph.nodes[candidate]['topics'])[:5],
                          'sample_papers': papers, 'introduction_path': path_description(row, authors), 'path_ids': row['path_ids']})
            keys[card_id] = {'models': selection['methods'], 'candidate_id': candidate, 'seed_id': seed}
    # Bind public cards and hidden attribution to one immutable dataset revision.
    revision = hashlib.sha256(json.dumps({'cards': cards, 'keys': keys, 'model': MODEL_VERSION},
                                         sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    for card in cards:
        card['dataset_id'] = revision
        keys[card['card_id']]['dataset_id'] = revision
    return cards, keys


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='prototype/uiuc_data_scaled.json')
    parser.add_argument('--out', default='prototype/study/study_cards.json')
    parser.add_argument('--keys', default='prototype/study/truth_keys.json')
    args = parser.parse_args()
    cards, keys = generate(json.loads(Path(args.data).read_text()))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.keys).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(cards, indent=2))
    Path(args.keys).write_text(json.dumps(keys, indent=2))
    print(f'Exported {len(cards)} unique cards across {len({c["seed_id"] for c in cards})} seeds')
