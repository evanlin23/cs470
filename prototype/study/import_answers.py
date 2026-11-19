"""Collect answers pasted back from the self-guided study page.

Give it any text files that contain the pasted replies (one reply per file, or
many replies pasted into one file) and/or the downloaded answer files. It
finds every BEGIN/END block, keeps one copy per participant, and writes:

  sessions.json   input for analyze_study.py
  round3_log.csv  one row per participant: background, what they did in the
                  app, the quick-check answers and the debrief

Keep every output outside the repository: these are private study data.

    python prototype/study/import_answers.py replies/*.txt --out /path/to/private
    python prototype/study/analyze_study.py --responses /path/to/private/sessions.json \
        --keys prototype/study/truth_keys.json --out /path/to/private/study-analysis.json
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

BLOCK = re.compile(r'-----BEGIN BRIDGEFINDER ANSWERS-----\s*(.*?)\s*-----END BRIDGEFINDER ANSWERS-----', re.S)
COLUMNS = ['code', 'participant_id', 'started_at', 'finished_at', 'level', 'field', 'seeking_research', 'tried_before',
           'research_interest', 'seed_id', 'app_seconds', 'chose_researcher', 'opened_card', 'opened_draft', 'task_completed',
           'cards_opened', 'researchers_explored', 'explanation_opened', 'searches', 'screens_visited', 'opened_candidates',
           'solid_lines', 'solid_lines_correct', 'dashed_lines', 'dashed_lines_correct', 'route_meaning', 'route_meaning_correct',
           'route_names', 'stuck', 'debrief_confusing', 'debrief_contact', 'debrief_trust', 'debrief_change', 'debrief_use', 'build_id']


def extract(text):
    sessions = []
    for raw in BLOCK.findall(text):
        # Mail and chat apps may wrap long lines; JSON ignores whitespace between tokens only,
        # so rejoin wrapped lines without adding characters.
        candidate = raw.strip()
        for attempt in (candidate, candidate.replace('\r', '').replace('\n', '')):
            try:
                sessions.append(json.loads(attempt))
                break
            except json.JSONDecodeError:
                continue
        else:
            print('Skipped one block that is not valid JSON (it may have been cut off).', file=sys.stderr)
    return sessions


def row(session):
    app, check, debrief, background = (session.get(key) or {} for key in ('app', 'comprehension', 'debrief', 'background'))
    events = app.get('events') or []
    screens = [event.get('screen') for event in events if event.get('type') == 'screen']
    return {
        'code': f"P-{session['participant_id'][:6].upper()}", 'participant_id': session['participant_id'],
        'started_at': session.get('started_at'), 'finished_at': session.get('finished_at'),
        'level': background.get('level'), 'field': background.get('field'), 'seeking_research': background.get('seeking'),
        'tried_before': background.get('tried_before'), 'research_interest': session.get('research_interest'),
        'seed_id': session.get('seed_id'), 'app_seconds': app.get('seconds'),
        **{key: app.get(key) for key in ('chose_researcher', 'opened_card', 'opened_draft', 'task_completed', 'cards_opened',
                                         'researchers_explored', 'explanation_opened', 'searches')},
        'screens_visited': ' > '.join(screen for screen in screens if screen),
        'opened_candidates': '; '.join(event.get('candidate', '') for event in events if event.get('type') == 'card_opened'),
        **{key: check.get(key) for key in ('solid_lines', 'solid_lines_correct', 'dashed_lines', 'dashed_lines_correct',
                                           'route_meaning', 'route_meaning_correct', 'route_names', 'stuck')},
        **{f'debrief_{key}': debrief.get(key) for key in ('confusing', 'contact', 'trust', 'change', 'use')},
        'build_id': session.get('build_id'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--out', type=Path, required=True, help='private output folder, outside the repository')
    args = parser.parse_args()
    found = [session for path in args.files for session in extract(path.read_text(encoding='utf-8', errors='replace'))]
    unique = {}
    for session in found:
        pid = session.get('participant_id')
        if not isinstance(pid, str) or not pid:
            print('Skipped a block without a participant_id.', file=sys.stderr)
            continue
        if pid in unique and unique[pid] != session:
            print(f'Participant {pid[:6]} sent two different answer sets; keeping the one that finished last.', file=sys.stderr)
            if (session.get('finished_at') or '') < (unique[pid].get('finished_at') or ''):
                continue
        unique[pid] = session
    if not unique:
        raise SystemExit('No answer blocks found.')
    args.out.mkdir(parents=True, exist_ok=True)
    sessions = sorted(unique.values(), key=lambda s: s.get('finished_at') or '')
    (args.out/'sessions.json').write_text(json.dumps(sessions, indent=1), encoding='utf-8')
    with open(args.out/'round3_log.csv', 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(row(session) for session in sessions)
    builds = sorted({s.get('build_id') for s in sessions})
    print(f'{len(sessions)} participants from {len(found)} blocks in {len(args.files)} files. Builds: {", ".join(map(str, builds))}')
    print(f'Wrote {args.out/"sessions.json"} and {args.out/"round3_log.csv"}')


if __name__ == '__main__':
    main()
