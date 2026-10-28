"""Completeness tests with synthetic API pages, never publication evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fetch_openalex import UIUC_INST_ID, UIUC_ROR, collect_works, extract_uiuc_coauthorship, run_harvest


def work(identity):
    return {'id': identity, 'publication_year': 2018, 'title': identity, 'topics': [],
            'authorships': [{'author': {'id': author, 'display_name': author},
                            'institutions': [{'id': 'https://openalex.org/' + UIUC_INST_ID}]} for author in ['a', 'b']]}


def response(works, cursor, count=3):
    return {'meta': {'count': count, 'next_cursor': cursor}, 'results': works}


def api(url, mailto):
    if '/institutions/' in url:
        return {'id': 'https://openalex.org/' + UIUC_INST_ID, 'ror': UIUC_ROR}
    if 'cursor=%2A' in url:
        return response([work('one'), work('two')], 'second')
    if 'cursor=second' in url:
        return response([work('two'), work('three')], None)
    return response([], None)


class CollectionTests(unittest.TestCase):
    def test_uncapped_pagination_deduplicates_and_reconciles_before_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / 'dataset.json'
            manifest = run_harvest(out, Path(temporary) / 'cache', fetch_page=api, delay=0)
            self.assertTrue(manifest['complete'])
            self.assertEqual(manifest['unique_works'], 3)
            self.assertEqual(manifest['retained_papers'], 3)
            self.assertEqual(manifest['retained_authors'], 2)
            self.assertEqual(len(json.loads(out.read_text())['papers']), 3)
            self.assertEqual(json.loads(out.with_suffix('.collection.json').read_text()), manifest)

    def test_capped_run_does_not_publish_and_resumes_to_exhaustion(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / 'dataset.json'
            out.write_text('existing dataset')
            cache = Path(temporary) / 'cache'
            with self.assertRaisesRegex(RuntimeError, 'capped/incomplete'):
                run_harvest(out, cache, max_works=2, fetch_page=api, delay=0)
            self.assertEqual(out.read_text(), 'existing dataset')
            calls = []
            def resume(url, mailto):
                calls.append(url)
                return api(url, mailto)
            result = run_harvest(out, cache, fetch_page=resume, delay=0)
            self.assertTrue(result['complete'])
            self.assertFalse(any('cursor=%2A' in url for url in calls))

    def test_failed_page_preserves_old_dataset_and_resumable_checkpoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / 'dataset.json'
            out.write_text('existing dataset')
            cache = Path(temporary) / 'cache'
            def interrupted(url, mailto):
                if 'cursor=second' in url:
                    raise RuntimeError('simulated API failure')
                return api(url, mailto)
            with self.assertRaisesRegex(RuntimeError, 'simulated'):
                run_harvest(out, cache, fetch_page=interrupted, delay=0)
            state = json.loads((cache / 'checkpoint.json').read_text())
            self.assertFalse(state['complete'])
            self.assertEqual(state['next_cursor'], 'second')
            self.assertEqual(out.read_text(), 'existing dataset')
            self.assertFalse(out.with_suffix('.collection.json').exists())
            self.assertTrue(run_harvest(out, cache, fetch_page=api, delay=0)['complete'])

    def test_legacy_and_wrong_query_cache_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            cache = Path(temporary)
            (cache / 'checkpoint.json').write_text('[]')
            with self.assertRaisesRegex(ValueError, 'legacy'):
                collect_works('', cache, fetch_page=api, delay=0)
            (cache / 'checkpoint.json').unlink()
            collect_works('', cache, max_works=2, fetch_page=api, delay=0)
            with self.assertRaisesRegex(ValueError, 'different query'):
                collect_works('', cache, start_year=2016, fetch_page=api, delay=0)

    def test_changed_total_prevents_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / 'dataset.json'
            def changed(url, mailto):
                value = api(url, mailto)
                if '/works?' in url and 'cursor=' not in url:
                    value['meta']['count'] = 4
                return value
            with self.assertRaisesRegex(RuntimeError, 'stable API total'):
                run_harvest(out, Path(temporary) / 'cache', fetch_page=changed, delay=0)
            self.assertFalse(out.exists())

    def test_exact_affiliation_and_distinct_authors_define_relevant_papers(self):
        duplicate = work('duplicate-author')
        duplicate['authorships'] = [duplicate['authorships'][0]] * 2
        false_match = work('other-urbana')
        false_match['authorships'][1]['institutions'] = [{'id': 'https://openalex.org/Iother', 'display_name': 'Other University in Urbana'}]
        result = extract_uiuc_coauthorship([work('valid'), work('valid'), duplicate, false_match])
        self.assertEqual([p['id'] for p in result['papers']], ['valid'])
        self.assertEqual(result['authors']['a']['paper_count'], 1)

    def test_truncated_authorships_are_not_silently_treated_as_complete(self):
        truncated = {**work('truncated'), 'is_authors_truncated': True}
        with self.assertRaisesRegex(RuntimeError, 'Truncated'):
            extract_uiuc_coauthorship([truncated])


if __name__ == '__main__':
    unittest.main()
