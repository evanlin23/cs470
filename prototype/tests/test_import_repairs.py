"""import_answers.py must recover replies that chat apps damaged, exactly, and say so.

The fixture is synthetic. It copies the two kinds of damage seen in real replies:
percent-encoded braces, and part of the text turned into a Markdown link.
"""
import importlib.util
import json
from pathlib import Path
import unittest
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('import_answers', ROOT/'study/import_answers.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)

SESSION = {'schema_version': 1, 'study_protocol': 'quick-v1', 'participant_id': 'synthetic-0001',
           'seed_id': 'https://openalex.org/A1', 'shown': ['CARD_001', 'CARD_002'],
           'ratings': [{'card_id': 'CARD_001', 'relevant': True, 'knew': False}],
           'contact_choice': 'none', 'background': {'level': 'Undergraduate', 'field': 'Computer Science'}, 'comment': ''}


def wrap(body):
    return f'Some text\n-----BEGIN BRIDGEFINDER ANSWERS-----\n{body}\n-----END BRIDGEFINDER ANSWERS-----\n'


class ImportRepairTests(unittest.TestCase):
    def setUp(self):
        self.clean = json.dumps(SESSION, separators=(',', ':'))

    def test_clean_reply_is_untouched(self):
        [session] = importer.extract(wrap(self.clean))
        self.assertEqual(session, SESSION)

    def test_percent_encoded_braces(self):
        damaged = self.clean[0] + self.clean[1:-1].replace('{', '%7B').replace('}', '%7D') + self.clean[-1]
        [session] = importer.extract(wrap(damaged))
        self.assertEqual(session.pop('import_repairs'), ['decoded percent-encoded characters'])
        self.assertEqual(session, SESSION)

    def test_automatic_markdown_link(self):
        url = 'https://openalex.org/A1'
        start = self.clean.index(url) + len(url)
        end = self.clean.index('Computer') + len('Computer')
        label = self.clean[start:end]
        linked = self.clean[:start] + '[' + label.replace('{', '%7B').replace('}', '%7D') + '](' + url + urllib.parse.quote(label, safe=':/') + ')' + self.clean[end:]
        [session] = importer.extract(wrap(linked))
        self.assertIn('undid an automatic link', session.pop('import_repairs'))
        self.assertEqual(session, SESSION)

    def test_wrapped_lines(self):
        wrapped = '\n'.join(self.clean[i:i+40] for i in range(0, len(self.clean), 40))
        [session] = importer.extract(wrap(wrapped))
        self.assertEqual(session.pop('import_repairs'), ['rejoined wrapped lines'])
        self.assertEqual(session, SESSION)

    def test_truncated_reply_is_skipped(self):
        self.assertEqual(importer.extract(wrap(self.clean[:-20])), [])


if __name__ == '__main__':
    unittest.main()
