"""Keep the paper, canonical results and actual analysis provenance in agreement."""
import hashlib
import json
from pathlib import Path
import re
import statistics
import unittest

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
JOBS=[('backtest_results_scaled.json','scaled-run.json'),
      ('citation_impact.json','citation-run.json'),
      ('network_stats.json','network-run.json')]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PublicationConsistencyTests(unittest.TestCase):
    def test_canonical_outputs_have_recorded_input_and_code(self):
        for result,manifest in JOBS:
            with self.subTest(result=result):
                canonical=ROOT/'results'/result
                record=json.loads((ROOT/'results'/manifest).read_text())
                self.assertEqual(record['result_file'],result)
                self.assertEqual(digest(canonical),record['result_sha256'])
                self.assertEqual(digest(ROOT/record['dataset_file']),record['dataset_sha256'])
                for name,expected in record['source_sha256'].items():
                    self.assertEqual(digest(ROOT/name),expected,name)

    def test_all_published_prediction_cells_match_current_outputs(self):
        source=(REPO/'midterm/latex/main.tex').read_text()
        data=json.loads((ROOT/'results/backtest_results_scaled.json').read_text())
        models=[('Topic-Only','Topic-Only'), ('Triadic closure','Triadic Closure'), ('BridgeFinder','BridgeFinder')]
        for label,model in models:
            row=next(line for line in source.splitlines() if line.startswith(label+'&'))
            self.assertEqual(re.findall(r'0\.\d{4}',row),[f'{data[model]["P@10"]:.4f}'])
        distances=data['new_tie_training_distance']
        beyond=distances['three']['share']+distances['four_or_more']['share']
        self.assertIn(f"Of the {distances['ties']:,} distinct new cross-community pairs behind Table~\\ref{{tab:results}}, only {100*distances['two']['share']:.0f}\\% joined authors who already shared a co-author, while {100*beyond:.0f}\\% joined authors three or more hops apart, inside BridgeFinder's candidate pool, and the remaining {100*distances['unreachable']['share']:.0f}\\% had no training path",source)
        count=re.search(r'We evaluated ([\d,]+) starting researchers\b',source)
        self.assertIsNotNone(count)
        self.assertEqual(int(count.group(1).replace(',','')),json.loads((ROOT/'results/scaled-run.json').read_text())['eligible_seeds'])

    def test_network_description_matches_canonical_statistics(self):
        source=(REPO/'midterm/latex/main.tex').read_text()
        stats=json.loads((ROOT/'results/network_stats.json').read_text())
        bundle=json.loads((ROOT/'web/data.json').read_text())
        rows=[row for rows in bundle['recommendations'].values() for row in rows]
        largest=stats['largest_component']
        expected=[f"Modularity in largest component & {largest['modularity']:.3f}",
                  f"which holds {100*largest['share']:.0f}\\% of authors, the same partition still scores {largest['modularity']:.3f}",
                  f"The {stats['constraint_largest_component']['route_intermediaries']} distinct intermediaries on these routes",
                  f"largest component, is {stats['constraint_largest_component']['median_route_intermediaries']:.2f}",
                  f"against {stats['constraint_largest_component']['median_all_authors']:.2f} for the median author there",
                  f"the bonus makes up {100*sum(.5*r['path_bonus'] for r in rows)/sum(r['score'] for r in rows):.0f}\\% of their summed scores",
                  f"Of the {len(rows)} displayed suggestions, {100*stats['displayed_suggestions_on_one_uiuc_paper']['share']:.0f}\\% appear on only one UIUC paper"]
        for text in expected:self.assertIn(text,source)

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

    def test_paper_figure_matches_current_full_data_demo(self):
        record=json.loads((REPO/'midterm/review/screenshots/capture.json').read_text())
        bundle=json.loads((ROOT/'web/data.json').read_text())
        self.assertEqual(record['dataset_sha256'],digest(ROOT/'uiuc_data_scaled.json'))
        self.assertEqual(record['model_version'],bundle['metadata']['model_version'])
        for name,expected in record['source_sha256'].items():
            self.assertEqual(digest(ROOT/'web'/name),expected,name)
        for name,expected in record['screenshot_sha256'].items():
            self.assertEqual(digest(REPO/'midterm/review/screenshots'/name),expected,name)
        row=next(r for r in bundle['recommendations'][record['seed_id']] if r['id']==record['candidate_id'])
        self.assertEqual(row['path_ids'],record['path_ids'])
        source=(REPO/'midterm/latex/main.tex').read_text()
        for name in record['path_names']:
            self.assertIn(name.replace('‐','-'),source)

    def test_ancillary_citation_note_matches_canonical_run(self):
        source=(REPO/'midterm/review/analysis-notes.md').read_text()
        result=json.loads((ROOT/'results/citation_impact.json').read_text())
        expected=[f"Of {result['total_eval_papers']:,} later papers, {result['n_cross_papers']:,} were cross-community, {result['n_within_papers']:,}",
                  f"and {result['n_unclassified_papers']:,} could not be classified",
                  f"Mean citations were {result['mean_citations_cross']:.2f} and {result['mean_citations_within']:.2f}",
                  f"a ratio of {result['impact_ratio']:.3f}",f"$p={result['p_value_two_sided']:.4f}$"]
        for text in expected:self.assertIn(text,source)


if __name__=='__main__':unittest.main()
