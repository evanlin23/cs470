"""End-to-end Chromium test of the self-guided study page (dist/bridgefinder-study.html).

Runs the whole flow twice, opened from a file and from a static web server (as on
GitHub Pages), and checks that the copied answers pass analyze_study.py. The
answers are synthetic test input and are never written to the repository.

    python prototype/study/build_standalone.py
    python prototype/tests/standalone_workflow.py [--artifacts DIR] [--chromium PATH]
"""
import argparse
import csv
import functools
import http.server
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT/'study'/'dist'/'bridgefinder-study.html'
spec = importlib.util.spec_from_file_location('analysis', ROOT/'study/analyze_study.py')
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)
ARTIFACTS = None
CHROMIUM = '/opt/pw-browsers/chromium'
ANSWERS = re.compile(r'-----BEGIN BRIDGEFINDER ANSWERS-----\n(.*)\n-----END BRIDGEFINDER ANSWERS-----', re.S)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class StandaloneStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PAGE.exists():
            raise unittest.SkipTest('Build the page first with build_standalone.py')
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(PAGE.parent)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.engine = sync_playwright().start()
        cls.browser = cls.engine.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--no-sandbox'])
        cls.cards = json.loads((ROOT/'study/study_cards.json').read_text())
        cls.keys = json.loads((ROOT/'study/truth_keys.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.engine.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def shot(self, page, name):
        if ARTIFACTS:
            ARTIFACTS.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(ARTIFACTS/f'{name}.png'), full_page=True)

    def run_flow(self, url, label, seed_index):
        context = self.browser.new_context(viewport={'width': 1280, 'height': 900})
        page = context.new_page()
        errors, external = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: external.append(request.url) if not request.url.startswith(('file:', 'data:', 'blob:', 'about:', 'http://127.0.0.1')) else None)
        page.goto(url)
        expect(page.get_by_role('heading', name='Help us test BridgeFinder')).to_be_visible()
        self.shot(page, f'{label}-1-welcome')
        page.get_by_role('button', name='Start').click()
        expect(page.locator('[data-error="welcome"]')).to_contain_text('tick the box')
        page.get_by_label('I am a UIUC student').check()
        page.get_by_role('button', name='Start').click()

        page.get_by_label('Undergraduate').check()
        page.get_by_label('What is your major or program?').fill('Food Science')
        page.get_by_label('Yes, now').check()
        page.locator('[data-radio="tried_before"]').get_by_label('No').check()
        page.get_by_role('button', name='Continue').click()
        page.get_by_label('What research topic').fill('Gut health and diet in children')
        page.get_by_role('button', name='Continue').click()

        expect(page.get_by_role('heading', name='Try the app on your own')).to_be_visible()
        app = page.frame_locator('iframe.app-frame')
        explore = app.locator('.select-seed-btn').first
        expect(explore).to_be_visible(timeout=20000)
        app.locator('#seedSearchInput').fill('nutrition')
        page.wait_for_timeout(1500)
        app.locator('#clearFilters').click()
        explore.click()
        expect(app.locator('#screenMap')).to_be_visible()
        expect(app.locator('#topoMapSvg line').first).to_be_attached(timeout=10000)
        self.shot(page, f'{label}-2-app-map')
        first = app.locator('.mini-rec').first
        first.click()
        card = app.locator('article.rec-card')
        expect(card).to_have_count(1)
        route = [name.strip() for name in app.locator('.path-step-node').evaluate_all('nodes => nodes.map(n => n.lastChild.textContent)')]
        app.locator('.ranking-details summary').click()
        app.get_by_role('button', name='Draft an email').click()
        expect(app.locator('#introModal')).to_have_attribute('open', '')
        app.locator('#closeDraft').click()
        page.wait_for_timeout(300)
        page.get_by_role('button', name="I'm done with the app").click()

        expect(page.get_by_role('heading', name='Quick check')).to_be_visible()
        page.get_by_role('button', name='Continue').click()
        expect(page.locator('[data-error="check"]')).to_contain_text('questions 1 to 3')
        page.locator('[data-radio="solid_lines"]').get_by_label('The two people have published a paper together').check()
        page.locator('[data-radio="dashed_lines"]').get_by_label('A suggested connection that does not exist yet').check()
        page.locator('[data-radio="route_meaning"]').get_by_label("I'm not sure").check()
        page.get_by_label('who was on its route').fill(', '.join(route[1:-1]))
        page.get_by_role('button', name='Continue').click()

        seeds = list(dict.fromkeys(card['seed_id'] for card in self.cards))
        seed = seeds[seed_index]
        expected = sum(card['seed_id'] == seed for card in self.cards)
        page.locator(f'input[name="seed"][value="{seed}"]').check()
        page.get_by_role('button', name='Start rating').click()
        for index in range(expected):
            expect(page.locator('#stepBadge')).to_have_text(f'Card {index+1} of {expected}')
            if index == 0:
                page.get_by_role('button', name='Next card').click()
                expect(page.locator('[data-error="cards"]')).to_contain_text('all three')
            for offset, dimension in enumerate(['relevance', 'novelty', 'actionability']):
                page.locator(f'input[name="{dimension}"][value="{(index + offset) % 7 + 1}"]').check(force=True)
            if index == 3:
                page.reload()
                expect(page.locator('#stepBadge')).to_have_text(f'Card 4 of {expected}')
                expect(page.locator('input[name="relevance"]:checked')).to_have_value(str((index) % 7 + 1))
            if index == 1:
                self.shot(page, f'{label}-3-card')
            page.locator('#nextCard').click()

        for item in range(10):
            page.locator(f'input[name="sus{item}"][value="{item % 5 + 1}"]').check(force=True)
        page.get_by_role('button', name='Continue').click()
        page.get_by_label('What one thing would you change').fill('Show why a person was suggested.')
        page.get_by_role('button', name='Finish').click()
        expect(page.get_by_role('heading', name='Last step: send us your answers')).to_be_visible()
        page.get_by_role('button', name='Copy my answers').click()
        expect(page.locator('#copyStatus')).not_to_be_empty()
        self.shot(page, f'{label}-4-send')
        raw = page.locator('#answersText').input_value()
        self.assertEqual(errors, [], f'{label}: page errors')
        self.assertEqual(external, [], f'{label}: unexpected network requests')
        context.close()

        session = json.loads(ANSWERS.search(raw).group(1))
        self.assertEqual(session['study_protocol'], 'student-interest-v1')
        self.assertEqual(session['seed_id'], seed)
        self.assertEqual(len(session['ratings']), expected)
        summary = session['app']
        self.assertTrue(summary['task_completed'], summary)
        self.assertTrue(summary['explanation_opened'])
        self.assertEqual(summary['cards_opened'], 1)
        types = [event['type'] for event in summary['events']]
        for event in ['screen', 'researcher_chosen', 'suggestion_from_list', 'card_opened', 'draft_opened', 'search']:
            self.assertIn(event, types)
        opened = next(event for event in summary['events'] if event['type'] == 'card_opened')
        self.assertEqual(opened['route'], route)
        self.assertTrue(session['comprehension']['solid_lines_correct'])
        self.assertTrue(session['comprehension']['dashed_lines_correct'])
        self.assertFalse(session['comprehension']['route_meaning_correct'])
        self.assertEqual(session['background']['field'], 'Food Science')
        return session, raw

    def test_file_and_static_host(self):
        runs = [self.run_flow(PAGE.as_uri(), 'file', 0),
                self.run_flow(f'http://127.0.0.1:{self.server.server_port}/{PAGE.name}', 'http', 2)]
        result = analysis.analyze([session for session, _ in runs], self.keys)
        self.assertEqual(result['n_participants'], 2)
        self.assertEqual(result['excluded'], [])
        # Both replies pasted into one file, the second one wrapped by a mail client.
        with tempfile.TemporaryDirectory() as scratch:
            scratch = Path(scratch)
            wrapped = '\n'.join('\n'.join(line[i:i+76] for i in range(0, len(line), 76)) for line in runs[1][1].split('\n'))
            (scratch/'replies.txt').write_text(f'Hi! Here you go:\n{runs[0][1]}\n\nthanks\n{wrapped}', encoding='utf-8')
            subprocess.run([sys.executable, str(ROOT/'study/import_answers.py'), str(scratch/'replies.txt'), '--out', str(scratch/'out')], check=True, capture_output=True)
            imported = json.loads((scratch/'out/sessions.json').read_text())
            self.assertEqual(sorted(s['participant_id'] for s in imported), sorted(s['participant_id'] for s, _ in runs))
            self.assertEqual(analysis.analyze(imported, self.keys)['n_participants'], 2)
            with open(scratch/'out/round3_log.csv', newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(row['task_completed'] == 'True' for row in rows))

    def test_mobile_app_step(self):
        context = self.browser.new_context(**self.engine.devices['iPhone 13'])
        page = context.new_page()
        page.goto(PAGE.as_uri())
        page.get_by_label('I am a UIUC student').check()
        page.get_by_role('button', name='Start').click()
        page.get_by_label("Master's student").check()
        page.get_by_label('What is your major or program?').fill('CS')
        page.get_by_label('Not really').check()
        page.locator('[data-radio="tried_before"]').get_by_label('No').check()
        page.get_by_role('button', name='Continue').click()
        page.get_by_label('What research topic').fill('sensor networks')
        page.get_by_role('button', name='Continue').click()
        expect(page.frame_locator('iframe.app-frame').locator('.select-seed-btn').first).to_be_visible(timeout=20000)
        width = page.evaluate('document.documentElement.scrollWidth')
        self.assertLessEqual(width, page.viewport_size['width'] + 1)
        self.shot(page, 'mobile-app')
        context.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifacts', type=Path)
    parser.add_argument('--chromium', default=CHROMIUM)
    args, rest = parser.parse_known_args()
    ARTIFACTS, CHROMIUM = args.artifacts, args.chromium
    unittest.main(argv=[sys.argv[0], *rest], verbosity=2)
