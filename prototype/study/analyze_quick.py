"""Analyze the one-minute study (protocol quick-v1) at the participant level.

Each participant rated six blinded cards for one starting researcher, two from each
method's top five, with "Relevant to my interests?" and "Had you heard of them?",
then picked the one person they would most like to contact (or none).

Primary outcome: share of a participant's cards that are relevant and new (relevant
yes, heard of no), BridgeFinder minus triadic closure, two-sided paired Wilcoxon.
A card chosen by two methods counts for both.

    python prototype/study/analyze_quick.py --responses quick_sessions.json \
        --keys prototype/study/truth_keys.json --card-features prototype/study/card_features.json \
        --out quick-analysis.json
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics

from scipy import stats

METHODS = ['BridgeFinder', 'Triadic Closure', 'Topic-Only']
PROTOCOL = 'quick-v1'


def paired(a, b):
    difference = [x - y for x, y in zip(a, b)]
    result = {'mean_difference': statistics.mean(difference), 'n': len(a)}
    if len(a) < 2 or all(d == 0 for d in difference):
        return {**result, 'p_wilcoxon': None if len(a) < 2 else 1.0, 'ci95': None}
    sem = stats.sem(difference)
    ci = [result['mean_difference']]*2 if sem == 0 else [float(v) for v in stats.t.interval(.95, len(a)-1, loc=result['mean_difference'], scale=sem)]
    return {**result, 'p_wilcoxon': float(stats.wilcoxon(difference).pvalue), 'ci95': ci}


def validate(session, keys, revision):
    if session.get('study_protocol') != PROTOCOL or session.get('schema_version') != 1:
        raise ValueError('not a quick-v1 session')
    if revision and session.get('dataset_id') != revision:
        raise ValueError('dataset revision differs from the method key')
    seed, shown = session.get('seed_id'), session.get('shown')
    if not isinstance(shown, list) or len(shown) != 6 or len(set(shown)) != 6:
        raise ValueError('needs six distinct shown cards')
    if any(card not in keys or keys[card]['seed_id'] != seed for card in shown):
        raise ValueError('cards do not belong to the chosen starting researcher')
    ratings = {row.get('card_id'): row for row in session.get('ratings') or [] if isinstance(row, dict)}
    if set(ratings) != set(shown) or any(type(ratings[c].get(k)) is not bool for c in shown for k in ('relevant', 'knew')):
        raise ValueError('every shown card needs yes/no answers to both questions')
    choice = session.get('contact_choice')
    if choice != 'none' and choice not in shown:
        raise ValueError('missing or invalid contact choice')
    if any(sum(m in keys[c]['models'] for c in shown) < 2 for m in METHODS):
        raise ValueError('each method needs at least two shown cards')
    return ratings, choice


def analyze(sessions, keys, features=None):
    revision = next(iter(keys.values())).get('dataset_id')
    people, excluded, seen = [], [], set()
    for session in sessions:
        pid = str(session.get('participant_id', '')).strip()
        if not pid or pid in seen:
            excluded.append({'participant_id': pid, 'reason': 'missing or duplicate participant_id'})
            continue
        seen.add(pid)
        try:
            ratings, choice = validate(session, keys, revision)
        except ValueError as error:
            excluded.append({'participant_id': pid, 'reason': str(error)})
            continue
        person = {'participant_id': pid, 'session': session, 'choice': choice, 'methods': {}}
        for m in METHODS:
            mine = [ratings[c] for c in session['shown'] if m in keys[c]['models']]
            person['methods'][m] = {
                'relevant': statistics.mean(r['relevant'] for r in mine),
                'new': statistics.mean(not r['knew'] for r in mine),
                'relevant_and_new': statistics.mean(r['relevant'] and not r['knew'] for r in mine),
                'cards': len(mine),
                'chosen': int(choice != 'none' and m in keys[choice]['models'])}
        people.append(person)
    if not people:
        raise ValueError(f'No valid quick-v1 sessions; exclusions: {excluded}')
    summary = {'study_protocol': PROTOCOL, 'n_participants': len(people), 'excluded': excluded, 'methods': {}, 'comparisons': {}}
    for m in METHODS:
        summary['methods'][m] = {d: statistics.mean(p['methods'][m][d] for p in people) for d in ('relevant', 'new', 'relevant_and_new')}
    exploratory = []
    for baseline in METHODS[1:]:
        for d in ('relevant', 'new', 'relevant_and_new'):
            key = f'BridgeFinder vs {baseline}: {d}'
            c = paired([p['methods']['BridgeFinder'][d] for p in people], [p['methods'][baseline][d] for p in people])
            c['primary'] = baseline == 'Triadic Closure' and d == 'relevant_and_new'
            summary['comparisons'][key] = c
            if not c['primary'] and c['p_wilcoxon'] is not None:
                exploratory.append(key)
    ordered = sorted(exploratory, key=lambda k: summary['comparisons'][k]['p_wilcoxon'])
    previous = 0.0
    for index, key in enumerate(ordered):
        previous = min(1.0, max(previous, summary['comparisons'][key]['p_wilcoxon']*(len(ordered)-index)))
        summary['comparisons'][key]['p_holm'] = previous
    choosers = [p for p in people if p['choice'] != 'none']
    summary['contact_choice'] = {
        'none': len(people) - len(choosers),
        'chose_someone': len(choosers),
        **{m: {'chosen': sum(p['methods'][m]['chosen'] for p in choosers),
               'expected_if_random': round(sum(p['methods'][m]['cards']/6 for p in choosers), 2),
               'p_binomial_two_sided': (float(stats.binomtest(sum(p['methods'][m]['chosen'] for p in choosers), len(choosers),
                                                             statistics.mean(p['methods'][m]['cards']/6 for p in choosers)).pvalue) if choosers else None)}
           for m in METHODS}}
    summary['note_on_choice'] = 'A chosen card that two methods suggested counts for both; expected counts assume a uniformly random pick among the six cards.'
    seconds = [p['session'].get('seconds') for p in people if isinstance(p['session'].get('seconds'), (int, float))]
    summary['median_seconds'] = statistics.median(seconds) if seconds else None
    summary['background'] = {'level': dict(Counter((p['session'].get('background') or {}).get('level') for p in people)),
                             'fields': sorted(f for f in ((p['session'].get('background') or {}).get('field') for p in people) if f)}
    apps = [p['session']['app'] for p in people if p['session'].get('app')]
    summary['optional_app'] = {'opened': len(apps), 'task_completed': sum(bool(a.get('task_completed')) for a in apps),
                               'opened_card': sum(bool(a.get('opened_card')) for a in apps), 'opened_draft': sum(bool(a.get('opened_draft')) for a in apps)}
    if features:
        cards = features['cards']
        bf = sorted(c for c, k in keys.items() if 'BridgeFinder' in k['models'])
        cut = statistics.median(cards[c]['topic_similarity'] for c in bf)
        low, high = [], []
        for p in people:
            ratings = {r['card_id']: r for r in p['session']['ratings']}
            for c in p['session']['shown']:
                if 'BridgeFinder' in keys[c]['models']:
                    (low if cards[c]['topic_similarity'] < cut else high).append(int(ratings[c]['relevant']))
        summary['topic_overlap_check'] = {'note': 'Exploratory, pooled over cards. BridgeFinder cards split at their median topic overlap.',
                                          'cut': cut, 'relevant_share_low_overlap': statistics.mean(low) if low else None, 'n_low': len(low),
                                          'relevant_share_high_overlap': statistics.mean(high) if high else None, 'n_high': len(high)}
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--responses', required=True)
    parser.add_argument('--keys', default='prototype/study/truth_keys.json')
    parser.add_argument('--card-features')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    features = json.loads(Path(args.card_features).read_text()) if args.card_features else None
    result = analyze(json.loads(Path(args.responses).read_text()), json.loads(Path(args.keys).read_text()), features)
    Path(args.out).write_text(json.dumps(result, indent=2, allow_nan=False))
    print(json.dumps({k: v for k, v in result.items() if k != 'excluded'}, indent=2)[:4000])
    if result['excluded']:
        print(f"Excluded {len(result['excluded'])}: {result['excluded']}")


if __name__ == '__main__':
    main()
