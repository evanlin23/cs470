"""Analyze complete, validated study sessions at participant level.

Input: JSON list of browser session exports. No invented defaults or anonymous
participant pooling. Primary outcome: relevant-and-new versus Adamic–Adar.
"""
import argparse
import json
import math
import statistics
from pathlib import Path
from scipy import stats

METHODS = ['BridgeFinder', 'Triadic Closure', 'Topic-Only']
DIMENSIONS = ['relevance', 'novelty', 'actionability']


def sus_score(values):
    if len(values) != 10 or any(type(v) is not int or not 1 <= v <= 5 for v in values):
        raise ValueError('SUS requires exactly ten integer answers from 1 to 5')
    return 2.5 * sum(v-1 if i % 2 == 0 else 5-v for i, v in enumerate(values))


def paired(a, b):
    difference = [x-y for x, y in zip(a, b)]
    result = {'mean_difference': statistics.mean(difference), 'n': len(a)}
    if len(a) < 2:
        return {**result, 'p_ttest': None, 'p_wilcoxon': None, 'ci95': None}
    if all(d == 0 for d in difference):
        return {**result, 'p_ttest': 1.0, 'p_wilcoxon': 1.0, 'ci95': [0.0, 0.0]}
    mean = statistics.mean(difference)
    sem = stats.sem(difference)
    ci = [mean, mean] if sem == 0 else list(stats.t.interval(.95, len(a)-1, loc=mean, scale=sem))
    p_t = float(stats.ttest_rel(a, b).pvalue) if sem else None
    return {**result, 'p_ttest': p_t if p_t is None or math.isfinite(p_t) else None,
            'p_wilcoxon': float(stats.wilcoxon(difference).pvalue), 'ci95': [float(v) for v in ci]}


def analyze(sessions, keys):
    participants, excluded, seen = [], [], set()
    if not isinstance(sessions, list):
        raise ValueError('Input must be a list of exported session objects')
    for session in sessions:
        pid = session.get('participant_id')
        if not isinstance(pid, str) or not pid or pid in seen:
            raise ValueError('Each session needs a unique nonempty participant_id')
        seen.add(pid)
        if session.get('purpose') == 'automated-test':
            raise ValueError('Automated fixtures are not participant evidence')
        seed = session.get('seed_id')
        expected = {cid for cid, key in keys.items() if key['seed_id'] == seed}
        ratings = session.get('ratings', [])
        ids = [row.get('card_id') for row in ratings]
        if not expected or len(ids) != len(set(ids)) or set(ids) != expected:
            excluded.append({'participant_id': pid, 'reason': 'incomplete, duplicate, or wrong-seed card set'})
            continue
        values = {m: {d: [] for d in DIMENSIONS+['relevant_and_new']} for m in METHODS}
        try:
            for row in ratings:
                for dimension in DIMENSIONS:
                    if type(row.get(dimension)) is not int or not 1 <= row[dimension] <= 7:
                        raise ValueError('Missing or invalid rating')
                for method in keys[row['card_id']]['models']:
                    for dimension in DIMENSIONS:
                        values[method][dimension].append(row[dimension])
                    values[method]['relevant_and_new'].append(int(row['relevance'] >= 5 and row['novelty'] >= 5))
            if any(len(values[m]['relevance']) != 5 for m in METHODS):
                raise ValueError('Each method must contribute exactly five candidates')
            sus = sus_score(session.get('sus', []))
        except ValueError as error:
            excluded.append({'participant_id': pid, 'reason': str(error)})
            continue
        participants.append({'participant_id': pid, 'sus': sus,
                             'methods': {m: {d: statistics.mean(v) for d, v in dims.items()} for m, dims in values.items()}})
    if not participants:
        raise ValueError(f'No complete participant sessions; exclusions: {excluded}')
    summary = {'n_participants': len(participants), 'excluded': excluded,
               'mean_sus': statistics.mean(p['sus'] for p in participants), 'methods': {}, 'comparisons': {}}
    for m in METHODS:
        summary['methods'][m] = {d: statistics.mean(p['methods'][m][d] for p in participants) for d in DIMENSIONS+['relevant_and_new']}
    exploratory = []
    for baseline in METHODS[1:]:
        for dimension in DIMENSIONS+['relevant_and_new']:
            key = f'{baseline}:{dimension}'
            comparison = paired([p['methods']['BridgeFinder'][dimension] for p in participants], [p['methods'][baseline][dimension] for p in participants])
            comparison['primary'] = baseline == 'Triadic Closure' and dimension == 'relevant_and_new'
            comparison['significant'] = comparison['p_wilcoxon'] is not None and comparison['p_wilcoxon'] < .05 if comparison['primary'] else None
            summary['comparisons'][key] = comparison
            if not comparison['primary'] and comparison['p_wilcoxon'] is not None:
                exploratory.append((key, comparison['p_wilcoxon']))
    previous = 0.0
    for index, (key, pvalue) in enumerate(sorted(exploratory, key=lambda item: item[1])):
        adjusted = min(1.0, max(previous, pvalue*(len(exploratory)-index)))
        summary['comparisons'][key]['p_holm'] = adjusted
        summary['comparisons'][key]['significant'] = adjusted < .05
        previous = adjusted
    return summary


def analyze_responses(responses_path, keys_path, out_path):
    result = analyze(json.loads(Path(responses_path).read_text()), json.loads(Path(keys_path).read_text()))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2, allow_nan=False))
    print(json.dumps(result, indent=2, allow_nan=False))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--responses', required=True)
    parser.add_argument('--keys', default='prototype/study/truth_keys.json')
    parser.add_argument('--out', default='prototype/study/study_analysis_results.json')
    args = parser.parse_args()
    analyze_responses(args.responses, args.keys, args.out)
