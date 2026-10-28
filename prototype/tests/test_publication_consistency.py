"""Keep the paper, canonical results and actual analysis provenance in agreement."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
JOBS=[('backtest_results.json','pilot-backtest.json','pilot-run.json'),
      ('backtest_results_scaled.json','scaled-backtest.json','scaled-run.json'),
      ('citation_impact.json','citation-impact.json','citation-run.json')]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PublicationConsistencyTests(unittest.TestCase):
    def test_canonical_outputs_and_paper_copies_have_recorded_input_and_code(self):
        for result,copy,manifest in JOBS:
            with self.subTest(result=result):
                canonical=ROOT/'results'/result
                record=json.loads((ROOT/'results'/manifest).read_text())
                self.assertEqual(record,json.loads((REPO/'midterm/review'/manifest).read_text()))
                self.assertEqual(record['result_file'],result)
                self.assertEqual(digest(canonical),record['result_sha256'])
                self.assertEqual(digest(REPO/'midterm/review'/copy),record['result_sha256'])
                self.assertEqual(digest(ROOT/record['dataset_file']),record['dataset_sha256'])
                for name,expected in record['source_sha256'].items():
                    self.assertEqual(digest(ROOT/name),expected,name)

    def test_all_published_prediction_cells_match_current_outputs(self):
        source=(REPO/'midterm/latex/main.tex').read_text()
        data=[json.loads((ROOT/'results'/name).read_text()) for name in ['backtest_results.json','backtest_results_scaled.json']]
        models=[('Pref. attachment','Preferential Attachment'),('Betweenness','Global Betweenness'),('Topic-Only','Topic-Only'),
                ('Adamic--Adar','Triadic Closure (Adamic-Adar)'),('BridgeFinder','BridgeFinder')]
        for label,model in models:
            row=next(line for line in source.splitlines() if line.startswith(label+'&'))
            self.assertEqual(re.findall(r'0\.\d{4}',row),[f'{run[model][metric]:.4f}' for run in data for metric in ['P@5','NDCG@10']])
        counts=re.search(r'We evaluated ([\d,]+) starting researchers in the pilot sample and ([\d,]+) in the larger sample',source)
        self.assertIsNotNone(counts)
        for name,count in zip(['pilot-run.json','scaled-run.json'],counts.groups()):
            self.assertEqual(int(count.replace(',','')),json.loads((ROOT/'results'/name).read_text())['eligible_seeds'])

    def test_report_closure_summary_matches_displayed_data_and_audit(self):
        audit=json.loads((ROOT/'review/closure-audit.json').read_text())
        bundle=json.loads((ROOT/'web/data.json').read_text())
        paths=[row['path_ids'] for rows in bundle['recommendations'].values() for row in rows]
        self.assertEqual(audit['displayed_slots'],len(paths))
        self.assertEqual(audit['displayed_top10']['two_hop'],sum(path is not None and len(path)==3 for path in paths))
        self.assertEqual(audit['displayed_top10']['three_hop'],sum(path is not None and len(path)==4 for path in paths))
        for name,expected in audit['source_sha256'].items():self.assertEqual(digest(ROOT/name),expected)
        source=(REPO/'midterm/latex/main.tex').read_text()
        self.assertEqual(audit['displayed_top10']['two_hop'],0)
        self.assertEqual(audit['displayed_top10']['unreachable'],0)
        self.assertIn('at least three hops',source)

    def test_citation_counts_and_statistics_in_paper_match_canonical_run(self):
        source=(REPO/'midterm/latex/main.tex').read_text()
        result=json.loads((ROOT/'results/citation_impact.json').read_text())
        expected=[f"Of {result['total_eval_papers']:,} later papers, {result['n_cross_papers']:,} were cross-community, {result['n_within_papers']:,}",
                  f"and {result['n_unclassified_papers']:,} could not be classified",
                  f"Mean citations were {result['mean_citations_cross']:.2f} and {result['mean_citations_within']:.2f}",
                  f"a ratio of {result['impact_ratio']:.3f}",f"$p={result['p_value_two_sided']:.4f}$"]
        for text in expected:self.assertIn(text,source)


if __name__=='__main__':unittest.main()
