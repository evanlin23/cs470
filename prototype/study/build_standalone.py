"""Build the self-guided study as one HTML file that works offline or on a static host.

The page bundles the unchanged app (web/), its data, the public study cards and
the study flow from study/standalone/. It never includes truth_keys.json, so
the method behind each card stays hidden. Usage, from the repository root:

    python prototype/study/build_standalone.py

writes prototype/study/dist/bridgefinder-study.html.
"""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STUDY = Path(__file__).resolve().parent
PROTOTYPE = STUDY.parent
WEB = PROTOTYPE/'web'
SOURCE = STUDY/'standalone'
FORBIDDEN = ('truth_keys', '"models"')


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


def build():
    cards = json.loads(read(STUDY/'study_cards.json'))
    if any(key in json.dumps(cards) for key in FORBIDDEN):
        raise SystemExit('study_cards.json contains method information; refusing to build')
    app_doc = app_document()
    fingerprint = hashlib.sha256((app_doc + json.dumps(cards, sort_keys=True) + "".join(read(SOURCE/name) for name in ("shell.html", "standalone.js", "standalone.css"))).encode()).hexdigest()[:12]
    build_info = {'build_id': f'{git_commit()}-{fingerprint}', 'built_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                  'dataset_id': cards[0]['dataset_id']}
    css = '\n'.join([read(WEB/'styles.css'), re.sub(r'@import[^;]+;', '', read(STUDY/'study.css')), read(SOURCE/'standalone.css')])
    data = f'const CARDS={script_json(cards)};\nconst APP_DOC={script_json(app_doc)};\nconst BUILD={script_json(build_info)};'
    shell = read(SOURCE/'shell.html')
    for marker, value in (('{{CSS}}', css), ('{{DATA}}', data), ('{{JS}}', read(SOURCE/'standalone.js'))):
        if shell.count(marker) != 1:
            raise SystemExit(f'shell.html needs exactly one {marker}')
        shell = shell.replace(marker, value)
    if '</script' in read(SOURCE/'standalone.js').lower():
        raise SystemExit('standalone.js cannot be inlined safely')
    return shell, build_info


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', default=str(STUDY/'dist'/'bridgefinder-study.html'))
    args = parser.parse_args()
    page, info = build()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding='utf-8')
    print(f'Wrote {out} ({out.stat().st_size/1e6:.2f} MB), build {info["build_id"]}')


if __name__ == '__main__':
    main()
