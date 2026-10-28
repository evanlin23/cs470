"""Happy-path Chromium workflow tests. Starts the public-asset server automatically.

No participant answers or statistics are retained. --artifacts writes only UI
screenshots and a test summary, outside the report's existing screenshots.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import threading
import unittest

from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from serve import make_server
spec=importlib.util.spec_from_file_location('analysis',ROOT/'study/analyze_study.py')
analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)
ARTIFACTS=None


class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=make_server(port=0)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.engine=sync_playwright().start()
        cls.browser=cls.engine.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        cls.bundle=json.loads((ROOT/'web/data.json').read_text())
        cls.cards=json.loads((ROOT/'study/study_cards.json').read_text())
        cls.keys=json.loads((ROOT/'study/truth_keys.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.engine.stop();cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
        self.page=self.context.new_page();self.errors=[]
        self.page.on('pageerror',lambda error:self.errors.append(str(error)))

    def tearDown(self):
        try:self.assertEqual(self.errors,[])
        finally:self.context.close()

    def web(self):
        self.page.goto(self.base+'/web/');expect(self.page.locator('.seed-card')).to_have_count(50)

    def study(self):
        self.page.goto(self.base+'/study/');expect(self.page.locator('#startStudy')).to_be_enabled()

    def choose_first(self):
        self.web();self.page.locator('.select-seed-btn').first.click();expect(self.page.locator('#screenMap')).to_be_visible()

    def no_overflow(self):
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),self.page.evaluate('innerWidth'))

    def rate_card(self,value=5):
        for dimension in ['relevance','novelty','actionability']:
            self.page.get_by_role('radio',name=f'{dimension} {value}',exact=True).check()
        self.page.locator('#nextBtn').click()

    def finish_cards(self):
        count=len([row for row in self.cards if row['seed_id']==self.page.locator('#seedSelect').input_value()])
        for _ in range(count):self.rate_card()
        expect(self.page.locator('#summaryView')).to_be_visible()
        return count

    def fill_sus(self):
        for i in range(10):self.page.locator(f'#sus-{i}').select_option('5' if i%2==0 else '1')

    def export(self):
        with self.page.expect_download() as event:self.page.locator('#exportResponses').click()
        download=event.value
        self.assertEqual(download.suggested_filename,'study_responses.json')
        return json.loads(Path(download.path()).read_text())


    def test_search_filters_and_empty_state(self):
        self.web()
        for seed in self.bundle['seeds']:
            self.page.locator('#seedSearchInput').fill(seed['name'])
            self.assertIn(seed['name'],self.page.locator('#seedGrid').inner_text())
        self.page.locator('#seedSearchInput').fill('no-such-researcher-123')
        expect(self.page.locator('.seed-card')).to_have_count(0);expect(self.page.locator('#emptySearch')).to_be_visible()
        self.page.locator('#clearFilters').click();expect(self.page.locator('.seed-card')).to_have_count(50)
        groups=sorted({str(row['community_id']) for row in self.bundle['seeds']})
        for group in groups:
            self.page.locator('#communityFilter').select_option(group)
            expect(self.page.locator('.seed-card')).to_have_count(sum(str(row['community_id'])==group for row in self.bundle['seeds']))
        self.page.locator('#clearFilters').click()
        for area in sorted({row['topic_group'] for row in self.bundle['seeds']}):
            self.page.locator('#topicFilter').select_option(area)
            expect(self.page.locator('.seed-card')).to_have_count(sum(row['topic_group']==area for row in self.bundle['seeds']))

    def test_all_fifty_starting_researchers_render_matching_maps_and_cards(self):
        self.web()
        for seed in self.bundle['seeds']:
            self.page.get_by_role('button',name=f"Explore {seed['name']}",exact=True).click()
            expect(self.page.locator('#sidebarSeedName')).to_have_text(seed['name'])
            expected=self.bundle['recommendations'][seed['id']]
            expect(self.page.locator('.mini-rec')).to_have_count(len(expected))
            expect(self.page.locator('line[data-kind="structural_hole"]')).to_have_count(len(expected))
            self.assertTrue(self.page.locator('#topoMapSvg circle').evaluate_all('(nodes)=>nodes.every(n=>{const b=n.getBoundingClientRect();return Number.isFinite(b.x)&&Number.isFinite(b.y)&&b.width>0})'))
            self.page.locator('#mapAllCards').click()
            self.assertEqual(self.page.locator('.rec-name').all_text_contents(),[row['name'] for row in expected])
            self.page.locator('#changeSeed').click()

    def test_actual_map_click_keyboard_zoom_and_fit(self):
        self.choose_first()
        line=self.page.locator('line[data-kind="structural_hole"]').first
        label=line.get_attribute('aria-label');line.click()
        expect(self.page.locator('.rec-card')).to_have_count(1)
        self.assertEqual('Inspect '+self.page.locator('.rec-name').inner_text(),label)
        self.page.locator('#showAllCards').click();expect(self.page.locator('.rec-card')).to_have_count(10)
        self.page.locator('[data-screen=map]').click()
        original=self.page.locator('#topoMapSvg > g').get_attribute('transform')
        self.page.locator('#zoomIn').click();self.assertNotEqual(self.page.locator('#topoMapSvg > g').get_attribute('transform'),original)
        self.page.locator('#resetZoom').click();self.assertEqual(self.page.locator('#topoMapSvg > g').get_attribute('transform'),original)
        line=self.page.locator('line[data-kind="structural_hole"]').last;label=line.get_attribute('aria-label');line.focus();self.page.keyboard.press('Enter')
        self.assertEqual('Inspect '+self.page.locator('.rec-name').inner_text(),label)

    def test_browser_back_forward_reload_and_shareable_selection(self):
        self.choose_first();seed=self.bundle['seeds'][0]
        self.page.locator('.mini-rec').nth(2).click();name=self.page.locator('.rec-name').inner_text();url=self.page.url
        self.page.reload();expect(self.page.locator('.rec-name')).to_have_text(name)
        self.page.go_back();expect(self.page.locator('#screenMap')).to_be_visible()
        self.page.go_forward();expect(self.page.locator('.rec-name')).to_have_text(name)
        other=self.context.new_page();other.goto(url);expect(other.locator('.rec-name')).to_have_text(name)
        expect(other.locator('#recsSeedHeaderName')).to_have_text(seed['name']);other.close()


    def test_copy_success_uses_edited_text(self):
        self.choose_first();self.page.locator('.mini-rec').first.click();self.page.locator('.outreach-button').click()
        self.page.locator('#modalEmailText').fill('Edited text')
        with self.page.expect_download() as event:self.page.locator('#downloadDraft').click()
        self.assertEqual(event.value.suggested_filename,'bridgefinder-outreach.txt')
        self.assertEqual(Path(event.value.path()).read_text(),'Edited text')
        self.page.evaluate("Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.copiedText=text}}})")
        self.page.locator('#copyDraft').click();expect(self.page.locator('#copyStatus')).to_have_text('Message copied.')
        self.assertEqual(self.page.evaluate('window.copiedText'),'Edited text')

    def test_mobile_and_tablet_no_overflow_in_all_views(self):
        for width in [360,390,768]:
            self.page.set_viewport_size({'width':width,'height':844})
            self.choose_first();self.no_overflow()
            self.page.locator('.mini-rec').first.click();self.no_overflow()
            self.page.locator('.outreach-button').click();self.no_overflow()
            expect(self.page.locator('#modalEmailText')).to_be_editable();self.page.keyboard.press('Escape')
            self.study();self.no_overflow();self.page.locator('#startStudy').click();self.no_overflow()
            self.page.get_by_role('radio',name='relevance 5',exact=True).check()
            self.page.goto('about:blank');self.page.evaluate('void 0')
            # New tab context per width prevents intentionally saved study drafts from changing the next starting view.
            self.context.clear_cookies();self.page.goto(self.base+'/study/');self.page.evaluate('sessionStorage.clear()');self.page.goto('about:blank')






    def test_keyboard_can_choose_researcher_and_rate_card(self):
        self.web();button=self.page.locator('.select-seed-btn').first;button.focus();self.page.keyboard.press('Enter')
        expect(self.page.locator('#screenMap')).to_be_visible()
        self.page.locator('.mini-rec').first.focus();self.page.keyboard.press('Enter');expect(self.page.locator('.rec-card')).to_have_count(1)
        self.study();self.page.locator('#startStudy').focus();self.page.keyboard.press('Enter')
        radio=self.page.get_by_role('radio',name='relevance 1',exact=True);radio.focus();self.page.keyboard.press('Space');expect(radio).to_be_checked()
        self.page.keyboard.press('ArrowRight');expect(self.page.get_by_role('radio',name='relevance 2',exact=True)).to_be_checked()

    def test_each_study_seed_card_count_and_no_hidden_methods(self):
        self.study()
        for seed_id in dict.fromkeys(card['seed_id'] for card in self.cards):
            self.page.locator('#seedSelect').select_option(seed_id);self.page.locator('#startStudy').click()
            count=sum(card['seed_id']==seed_id for card in self.cards)
            expect(self.page.locator('#cardCounterBadge')).to_have_text(f'Card 1 of {count}')
            text=self.page.locator('#cardView').inner_text()
            self.assertNotIn('Adamic',text);self.assertNotIn('Topic-Only',text)
            self.page.once('dialog',lambda dialog:dialog.accept());self.page.locator('#resetStudy').click()
            expect(self.page.locator('#setupView')).to_be_visible()

    def test_study_answers_order_and_identity_survive_reload(self):
        self.study();self.page.locator('#startStudy').click();name=self.page.locator('#candidateName').inner_text()
        self.rate_card();draft=json.loads(self.page.evaluate("sessionStorage.getItem('bridgefinder-study-v2')"))
        self.page.reload();expect(self.page.locator('#cardCounterBadge')).to_have_text(f"Card 2 of {len(draft['order'])}")
        restored=json.loads(self.page.evaluate("sessionStorage.getItem('bridgefinder-study-v2')"));self.assertEqual(restored,draft)
        self.page.locator('#prevBtn').click();expect(self.page.locator('#candidateName')).to_have_text(name)
        for dim in ['relevance','novelty','actionability']:expect(self.page.get_by_role('radio',name=f'{dim} 5',exact=True)).to_be_checked()

    def test_actual_study_download_round_trips_through_analyzer(self):
        self.study();self.page.locator('#startStudy').click()
        count=self.finish_cards()
        self.fill_sus();self.page.locator('#backToCards').click();self.page.locator('#nextBtn').click()
        expect(self.page.locator('#sus-0')).to_have_value('5')
        self.page.reload();expect(self.page.locator('#summaryView')).to_be_visible();expect(self.page.locator('#sus-1')).to_have_value('1')
        payload=self.export();self.assertEqual(len(payload[0]['ratings']),count)
        self.assertEqual(payload[0]['dataset_id'],self.cards[0]['dataset_id'])
        result=analysis.analyze(payload,self.keys);self.assertEqual(result['n_participants'],1);self.assertEqual(result['mean_sus'],100)
        # Synthetic browser answers and statistics are not persisted as human evidence.





    def test_capture_final_desktop_and_mobile_views(self):
        self.choose_first()
        if ARTIFACTS:self.page.screenshot(path=str(ARTIFACTS/'desktop-map.png'))
        self.page.locator('.mini-rec').first.click()
        disclosure=self.page.locator('.ranking-details');disclosure.locator('summary').click()
        expect(disclosure.locator('.metrics-bar')).to_be_visible()
        disclosure.locator('summary').click()
        if ARTIFACTS:self.page.screenshot(path=str(ARTIFACTS/'desktop-card.png'))
        self.page.set_viewport_size({'width':390,'height':844});self.no_overflow()
        if ARTIFACTS:self.page.screenshot(path=str(ARTIFACTS/'mobile-card.png'),full_page=True)
        self.study();self.page.locator('#startStudy').click();self.no_overflow()
        if ARTIFACTS:self.page.screenshot(path=str(ARTIFACTS/'mobile-study.png'),full_page=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--artifacts',type=Path);args=parser.parse_args()
    ARTIFACTS=args.artifacts
    if ARTIFACTS:ARTIFACTS.mkdir(parents=True,exist_ok=True)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(BrowserTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if ARTIFACTS:(ARTIFACTS/'browser-summary.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'browser':'system Chromium','human_participant_data':False},indent=2))
    sys.exit(not result.wasSuccessful())
