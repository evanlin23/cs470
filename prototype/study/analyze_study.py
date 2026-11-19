"""Analyze complete, validated study sessions at participant level.

Input: JSON list of browser session exports. No invented defaults or anonymous
participant pooling. Primary outcome: relevant-and-new versus triadic closure.
"""
import argparse
from collections import Counter
import json
import math
import statistics
from pathlib import Path
from scipy import stats

METHODS = ['BridgeFinder', 'Triadic Closure', 'Topic-Only']
DIMENSIONS = ['relevance', 'novelty', 'actionability']
STUDY_PROTOCOL = 'student-interest-v1'


def sus_score(values):
    if not isinstance(values, list) or len(values) != 10 or any(type(v) is not int or not 1 <= v <= 5 for v in values):
        raise ValueError('SUS requires exactly ten integer answers from 1 to 5')
    return 2.5 * sum(v-1 if i % 2 == 0 else 5-v for i, v in enumerate(values))


def paired(a, b):
    if not a or len(a) != len(b) or not all(type(v) in (int, float) and math.isfinite(v) for v in a+b):
        raise ValueError('Paired comparisons require equal nonempty finite numeric vectors')
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


def validate_keys(keys):
    if not isinstance(keys, dict) or not keys:
        raise ValueError('The method key must be a nonempty card-to-method mapping')
    revisions = set()
    groups = {}
    for card_id, key in keys.items():
        if not isinstance(card_id, str) or not card_id or not isinstance(key, dict):
            raise ValueError('Invalid card identity in method key')
        if not isinstance(key.get('seed_id'), str) or not key['seed_id'] or not isinstance(key.get('candidate_id'), str) or not key['candidate_id']:
            raise ValueError('Method key requires seed and candidate identities')
        methods = key.get('models')
        if not isinstance(methods, list) or not methods or any(not isinstance(m, str) or m not in METHODS for m in methods) or len(set(methods)) != len(methods):
            raise ValueError('Method key requires unique supported model labels')
        revision = key.get('dataset_id')
        if revision is not None and (not isinstance(revision, str) or len(revision) != 64 or any(c not in '0123456789abcdef' for c in revision)):
            raise ValueError('Invalid dataset revision in method key')
        revisions.add(revision)
        group = groups.setdefault(key['seed_id'], {'candidates': set(), 'counts': dict.fromkeys(METHODS, 0)})
        if key['candidate_id'] in group['candidates']:
            raise ValueError('Repeated candidates must share one card with multiple model labels')
        group['candidates'].add(key['candidate_id'])
        for method in methods:
            group['counts'][method] += 1
    if len(revisions) != 1 or any(count != 5 for group in groups.values() for count in group['counts'].values()):
        raise ValueError('Method key must use one dataset revision and five candidates per method per seed')
    return next(iter(revisions))


def analyze(sessions, keys):
    participants, excluded, seen = [], [], set()
    revision = validate_keys(keys)
    if not isinstance(sessions, list):
        raise ValueError('Input must be a list of exported session objects')
    for session in sessions:
        if not isinstance(session, dict):
            raise ValueError('Each input entry must be an exported session object, not a flat rating')
        pid = session.get('participant_id')
        if not isinstance(pid, str) or not pid.strip() or len(pid) > 128 or pid.strip() in seen:
            raise ValueError('Each session needs a unique nonempty participant_id of at most 128 characters')
        pid = pid.strip()
        seen.add(pid)
        if session.get('purpose') == 'automated-test':
            raise ValueError('Automated fixtures are not participant evidence')
        try:
            if type(session.get('schema_version')) is not int or session['schema_version'] != 1:
                raise ValueError('Unsupported or missing session schema_version')
            if session.get('study_protocol') != STUDY_PROTOCOL:
                raise ValueError('Session does not use the student-interest rating protocol')
            interest = session.get('research_interest')
            if not isinstance(interest, str) or not interest.strip() or len(interest) > 500:
                raise ValueError('Missing or invalid stated research interest')
            if revision is not None and session.get('dataset_id') != revision:
                raise ValueError('Session and method key come from different dataset revisions')
            seed = session.get('seed_id')
            if not isinstance(seed, str):
                raise ValueError('Missing or invalid seed_id')
            expected = {cid for cid, key in keys.items() if key['seed_id'] == seed}
            ratings = session.get('ratings')
            if not isinstance(ratings, list) or any(not isinstance(row, dict) or not isinstance(row.get('card_id'), str) for row in ratings):
                raise ValueError('Ratings must be a list of card objects')
            ids = [row['card_id'] for row in ratings]
            if not expected or len(ids) != len(set(ids)) or set(ids) != expected:
                raise ValueError('Incomplete, duplicate, or wrong-seed card set')
            values = {m: {d: [] for d in DIMENSIONS+['relevant_and_new']} for m in METHODS}
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
            sus = sus_score(session.get('sus'))
        except ValueError as error:
            excluded.append({'participant_id': pid, 'reason': str(error)})
            continue
        participants.append({'participant_id': pid, 'sus': sus,
                             'methods': {m: {d: statistics.mean(v) for d, v in dims.items()} for m, dims in values.items()}})
    if not participants:
        raise ValueError(f'No complete participant sessions; exclusions: {excluded}')
    summary = {'study_protocol': STUDY_PROTOCOL, 'dataset_id': revision, 'n_participants': len(participants), 'excluded': excluded,
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


def spearman(x, y):
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    value = stats.spearmanr(x, y).statistic
    return float(value) if math.isfinite(value) else None


def topic_overlap_check(sessions, keys, features, included):
    """Exploratory: do low-topic-overlap suggestions still feel relevant? (midterm grader's question)"""
    cards = features['cards']
    bf_cards = sorted(cid for cid, key in keys.items() if 'BridgeFinder' in key['models'])
    cut = statistics.median(cards[cid]['topic_similarity'] for cid in bf_cards)
    correlations, low, high, pooled = [], [], [], {'low': [], 'high': []}
    for session in sessions:
        if session.get('participant_id', '').strip() not in included:
            continue
        rows = [row for row in session['ratings'] if row['card_id'] in cards]
        rho = spearman([cards[row['card_id']]['topic_similarity'] for row in rows], [row['relevance'] for row in rows])
        if rho is not None:
            correlations.append(rho)
        mine = [row for row in rows if 'BridgeFinder' in keys[row['card_id']]['models']]
        lo = [row['relevance'] for row in mine if cards[row['card_id']]['topic_similarity'] < cut]
        hi = [row['relevance'] for row in mine if cards[row['card_id']]['topic_similarity'] >= cut]
        for row in mine:
            pooled['low' if cards[row['card_id']]['topic_similarity'] < cut else 'high'].append(int(row['relevance'] >= 5))
        if lo and hi:
            low.append(statistics.mean(lo))
            high.append(statistics.mean(hi))
    return {
        'note': 'Exploratory. BridgeFinder cards split at their median topic overlap; participant-level means.',
        'bridgefinder_overlap_cut': cut,
        'within_participant_spearman_overlap_vs_relevance': {'mean': statistics.mean(correlations) if correlations else None, 'n': len(correlations)},
        'bridgefinder_relevance_low_overlap_mean': statistics.mean(low) if low else None,
        'bridgefinder_relevance_high_overlap_mean': statistics.mean(high) if high else None,
        'high_minus_low': paired(high, low) if len(low) >= 1 else None,
        'bridgefinder_share_relevance_at_least_5': {key: (statistics.mean(v) if v else None) for key, v in pooled.items()},
    }


def self_guided_summary(sessions, included):
    rows = [s for s in sessions if s.get('participant_id', '').strip() in included]
    modes = Counter(s.get('collection_mode', 'moderated') for s in rows)
    guided = [s for s in rows if s.get('collection_mode') == 'self-guided-html-v1']
    count = lambda test: sum(1 for s in guided if test(s))
    app = lambda s: s.get('app') or {}
    check = lambda s: s.get('comprehension') or {}
    return {'collection_modes': dict(modes), 'self_guided': None if not guided else {
        'n': len(guided),
        'task_completed': count(lambda s: app(s).get('task_completed') is True),
        'opened_draft': count(lambda s: app(s).get('opened_draft') is True),
        'solid_lines_correct': count(lambda s: check(s).get('solid_lines_correct') is True),
        'dashed_lines_correct': count(lambda s: check(s).get('dashed_lines_correct') is True),
        'route_meaning_correct': count(lambda s: check(s).get('route_meaning_correct') is True),
        'median_app_seconds': statistics.median([app(s)['seconds'] for s in guided if isinstance(app(s).get('seconds'), (int, float))] or [0]),
    }}


def analyze_responses(responses_path, keys_path, out_path, features_path=None):
    sessions, keys = json.loads(Path(responses_path).read_text()), json.loads(Path(keys_path).read_text())
    result = analyze(sessions, keys)
    included = {s['participant_id'].strip() for s in sessions} - {e['participant_id'] for e in result['excluded']}
    result.update(self_guided_summary(sessions, included))
    if features_path:
        result['topic_overlap_check'] = topic_overlap_check(sessions, keys, json.loads(Path(features_path).read_text()), included)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2, allow_nan=False))
    print(json.dumps(result, indent=2, allow_nan=False))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--responses', required=True)
    parser.add_argument('--keys', default='prototype/study/truth_keys.json')
    parser.add_argument('--out', default='prototype/study/study_analysis_results.json')
    parser.add_argument('--card-features', help='card_features.json, for the exploratory topic-overlap check')
    args = parser.parse_args()
    try:
        analyze_responses(args.responses, args.keys, args.out, args.card_features)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Study analysis failed: {error}\n")
