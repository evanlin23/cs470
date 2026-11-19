"""Build the self-guided study as one HTML file that works offline or on a static host.

The page bundles the unchanged app (web/), its data, the public study cards and
the study flow from study/standalone/. It never includes truth_keys.json, so
the method behind each card stays hidden. Usage, from the repository root:

    python prototype/study/build_standalone.py

writes prototype/study/dist/bridgefinder-study.html (the one-minute study, the default
link) and prototype/study/dist/bridgefinder-study-full.html (the full 25-minute version).
"""
import argparse
import hashlib
import json
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STUDY = Path(__file__).resolve().parent
PROTOTYPE = STUDY.parent
WEB = PROTOTYPE/'web'
SOURCE = STUDY/'standalone'
FORBIDDEN = ('truth_keys', '"models"', 'Triadic Closure', 'Topic-Only')


def script_json(value):
    """JSON that is safe inside an inline <script>: no '<' can end the element."""
    return json.dumps(value, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')


def read(path):
    return Path(path).read_text(encoding='utf-8')


def app_document():
    page = read(WEB/'index.html')
    data = json.loads(read(WEB/'data.json'))
    for name in ('app.js', 'vendor/d3.v7.min.js', 'styles.css'):
        if '</script' in read(WEB/name).lower() or '<!--' in read(WEB/name):
            raise SystemExit(f'{name} cannot be inlined safely')
    head = (f'<style>{read(WEB/"styles.css")}</style>\n'
            f'<script>window.__BF_DATA__={script_json(data)};</script>\n'
            f'<script>{read(SOURCE/"app_shim.js")}</script>\n'
            f'<script>{read(WEB/"vendor/d3.v7.min.js")}</script>')
    replacements = [
        ('<link rel="stylesheet" href="styles.css">', head),
        ('<script defer src="vendor/d3.v7.min.js"></script>', ''),
        ('<script defer src="app.js"></script>', ''),
        ('</body>', f'<script>{read(WEB/"app.js")}</script>\n<script>{read(SOURCE/"app_logger.js")}</script>\n</body>'),
    ]
    for old, new in replacements:
        if page.count(old) != 1:
            raise SystemExit(f'web/index.html changed: expected one {old!r}')
        page = page.replace(old, new)
    return page


def git_commit():
    try:
        return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=PROTOTYPE, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return 'unknown'


AREA_LABELS = {
    'Naiman A. Khan': 'Nutrition and metabolic health',
    'Stephen P. Long': 'Crops, bioenergy and climate',
    'John A. Rogers': 'Materials, sensors and devices',
    'Tarek Abdelzaher': 'Computing, sensor networks and data',
    'Karen M. Tabb': 'Maternal and public health',
}
SETS_PER_SEED = 40


def quick_sets(cards, keys, seed=2026):
    """Prepared six-card sets: two cards from each method's top five, as card IDs only.

    The method key is read here at build time and never written into the page.
    """
    rng = random.Random(seed)
    sets = {}
    for seed_id in dict.fromkeys(card['seed_id'] for card in cards):
        ids = [card['card_id'] for card in cards if card['seed_id'] == seed_id]
        by_method = {m: sorted(i for i in ids if m in keys[i]['models']) for m in ('Triadic Closure', 'BridgeFinder', 'Topic-Only')}
        found, attempts = [], 0
        while len(found) < SETS_PER_SEED and attempts < 10000:
            attempts += 1
            chosen = rng.sample(by_method['Triadic Closure'], 2) + rng.sample(by_method['BridgeFinder'], 2)
            chosen += rng.sample([i for i in by_method['Topic-Only'] if i not in chosen], 2)
            key = sorted(chosen)
            if key not in found:
                found.append(key)
        sets[seed_id] = found
    return sets


def page(variant, cards, app_doc, build_info):
    css = [read(WEB/'styles.css'), re.sub(r'@import[^;]+;', '', read(STUDY/'study.css')), read(SOURCE/'standalone.css')]
    if variant == 'quick':
        keys = json.loads(read(STUDY/'truth_keys.json'))
        areas = [{'seed_id': c['seed_id'], 'seed_name': c['seed_name'], 'label': AREA_LABELS.get(c['seed_name'], ' and '.join(c['seed_topics'][:2]))}
                 for c in dict((c['seed_id'], c) for c in cards).values()]
        data = (f'const CARDS={script_json(cards)};\nconst SETS={script_json(quick_sets(cards, keys))};\n'
                f'const AREAS={script_json(areas)};\nconst APP_DOC={script_json(app_doc)};\nconst BUILD={script_json(build_info)};')
        shell, script = read(SOURCE/'quick.html'), read(SOURCE/'quick.js')
        css.append(read(SOURCE/'quick.css'))
    else:
        data = f'const CARDS={script_json(cards)};\nconst APP_DOC={script_json(app_doc)};\nconst BUILD={script_json(build_info)};'
        shell, script = read(SOURCE/'shell.html'), read(SOURCE/'standalone.js')
    if '</script' in script.lower():
        raise SystemExit('study script cannot be inlined safely')
    for marker, value in (('{{CSS}}', '\n'.join(css)), ('{{DATA}}', data), ('{{JS}}', script)):
        if shell.count(marker) != 1:
            raise SystemExit(f'page template needs exactly one {marker}')
        shell = shell.replace(marker, value)
    if any(word in shell for word in FORBIDDEN):
        raise SystemExit('built page contains method information; refusing to write it')
    return shell


def build(variant):
    cards = json.loads(read(STUDY/'study_cards.json'))
    if any(key in json.dumps(cards) for key in FORBIDDEN):
        raise SystemExit('study_cards.json contains method information; refusing to build')
    app_doc = app_document()
    sources = ''.join(read(SOURCE/name) for name in sorted(p.name for p in SOURCE.iterdir()))
    fingerprint = hashlib.sha256((variant + app_doc + json.dumps(cards, sort_keys=True) + sources).encode()).hexdigest()[:12]
    build_info = {'build_id': f'{git_commit()}-{variant}-{fingerprint}', 'built_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                  'dataset_id': cards[0]['dataset_id']}
    return page(variant, cards, app_doc, build_info), build_info


OUTPUTS = {'quick': 'bridgefinder-study.html', 'full': 'bridgefinder-study-full.html'}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--variant', choices=['quick', 'full', 'all'], default='all')
    parser.add_argument('--out-dir', default=str(STUDY/'dist'))
    args = parser.parse_args()
    for variant in (['quick', 'full'] if args.variant == 'all' else [args.variant]):
        built, info = build(variant)
        out = Path(args.out_dir)/OUTPUTS[variant]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(built, encoding='utf-8')
        print(f'Wrote {out} ({out.stat().st_size/1e6:.2f} MB), build {info["build_id"]}')


if __name__ == '__main__':
    main()
