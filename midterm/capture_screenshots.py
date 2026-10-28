"""Capture the current prototype and record the exact example used in the paper."""
import hashlib
import json
import math
from pathlib import Path
import sys
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'prototype'))
from serve import make_server


def main():
    bundle = json.loads((ROOT / 'prototype/web/data.json').read_text())
    seed = bundle['seeds'][0]
    candidate = bundle['recommendations'][seed['id']][0]
    people = {row['id']: row['name'] for row in bundle['graph']['nodes']}
    out = ROOT / 'midterm/review/screenshots'
    out.mkdir(parents=True, exist_ok=True)
    server = make_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as engine:
            browser = engine.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=3)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/web/')
            page.wait_for_selector('.seed-card')
            page.screenshot(path=str(out / '01-seeds.png'))
            page.locator('.select-seed-btn').first.click()
            page.wait_for_selector('.map-node')
            page.locator('.map-container').screenshot(path=str(out / '02-map.png'))
            page.locator('.mini-rec').first.click()
            page.wait_for_selector('.path-flow')
            assert page.locator('.rec-name').inner_text() == candidate['name']
            names = page.locator('.path-step-node').all_inner_texts()
            assert len(names) == len(candidate['path_ids'])
            assert all(people[node] in text for node, text in zip(candidate['path_ids'], names))
            card = page.locator('.rec-card').first.bounding_box()
            route = page.locator('.path-flow').first.bounding_box()
            last = page.locator('.path-step-node').last.bounding_box()
            width = min(card['width'], max(800, math.ceil(last['x'] + last['width'] - card['x'] + 24)))
            page.screenshot(path=str(out / '03-recommendation.png'), clip={
                'x': card['x'], 'y': card['y'], 'width': width,
                'height': route['y'] + route['height'] - card['y'] + 12})
            assert page.locator('.ranking-details').first.get_attribute('open') is None
            page.locator('.ranking-details summary').first.click()
            assert page.locator('.metrics-bar').first.is_visible()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    record = {
        'dataset_sha256': hashlib.sha256((ROOT / 'prototype/uiuc_data_scaled.json').read_bytes()).hexdigest(),
        'model_version': bundle['metadata']['model_version'],
        'seed_id': seed['id'], 'seed_name': seed['name'],
        'candidate_id': candidate['id'], 'candidate_name': candidate['name'],
        'path_ids': candidate['path_ids'], 'path_names': [people[node] for node in candidate['path_ids']],
        'viewport': {'width': 1440, 'height': 1000, 'device_scale_factor': 3},
        'screenshot_sha256': {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                              for name in ['01-seeds.png', '02-map.png', '03-recommendation.png']},
        'source_sha256': {name: hashlib.sha256((ROOT / 'prototype/web' / name).read_bytes()).hexdigest()
                          for name in ['data.json', 'app.js', 'index.html', 'styles.css']},
    }
    (out / 'capture.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Captured current example:', ' → '.join(record['path_names']))


if __name__ == '__main__':
    main()
