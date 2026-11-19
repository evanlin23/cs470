"""Write the network features behind each study card, for the topic-overlap check.

The midterm grader asked whether suggestions with little topic overlap still feel
relevant, because the path bonus supplies most of BridgeFinder's score. This file
lets analyze_study.py split ratings by each card's topic overlap. It holds no
method labels, but keep it out of the participant-facing pages like truth_keys.json.

    python prototype/study/card_features.py
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import prepare_model, candidate_features, MODEL_VERSION  # noqa: E402


def main():
    keys = json.loads((ROOT/'study/truth_keys.json').read_text())
    graph, _, _, membership = prepare_model(json.loads((ROOT/'uiuc_data_scaled.json').read_text()))
    features, cache = {}, {}
    for card_id, key in sorted(keys.items()):
        seed = key['seed_id']
        if seed not in cache:
            cache[seed] = {row['candidate_id']: row for row in candidate_features(graph, seed, membership)}
        row = cache[seed][key['candidate_id']]
        features[card_id] = {'topic_similarity': round(row['topic_similarity'], 4), 'three_hop_paths': row['three_hop_paths'],
                             'shared_coauthors': row['shared_coauthors'], 'distance': row['distance'],
                             'path_bonus_share_of_score': round(0.5*row['path_bonus']/row['score'], 4) if row['score'] else None}
    out = ROOT/'study/card_features.json'
    out.write_text(json.dumps({'model_version': MODEL_VERSION, 'dataset_id': next(iter(keys.values()))['dataset_id'], 'cards': features}, indent=1)+'\n')
    print(f'Wrote {out} ({len(features)} cards)')


if __name__ == '__main__':
    main()
