"""Keep the final report's numbers in agreement with results/final_analysis.json and the canonical results."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PAPER = REPO/'final/latex/main.tex'
RESULT = ROOT/'results/final_analysis.json'
MANIFEST = ROOT/'results/final-analysis-run.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@unittest.skipUnless(RESULT.exists() and PAPER.exists(), 'final analysis or paper missing')
class FinalReportConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAPER.read_text()
        cls.result = json.loads(RESULT.read_text())
        cls.ranking = cls.result['ranking']

    def test_figures_show_the_current_app(self):
        """The final report's screenshots must come from the app as it is now."""
        figures = REPO/'final/latex/figures'
        record = json.loads((figures/'capture.json').read_text())
        self.assertEqual(record['dataset_sha256'], digest(ROOT/'uiuc_data_scaled.json'))
        for name, expected in record['source_sha256'].items():
            self.assertEqual(digest(ROOT/'web'/name), expected, f'{name} changed: recapture with midterm/capture_screenshots.py --out final/latex/figures')
        for name, expected in record['screenshot_sha256'].items():
            self.assertEqual(digest(figures/name), expected, name)
            self.assertIn(f'figures/{name}', self.source)
        for name in record['path_names']:
            self.assertIn(name, self.source)

    def test_manifest_matches_code_and_data(self):
        record = json.loads(MANIFEST.read_text())
        self.assertEqual(digest(RESULT), record['result_sha256'])
        self.assertEqual(digest(ROOT/record['dataset_file']), record['dataset_sha256'])
        for name, expected in record['source_sha256'].items():
            self.assertEqual(digest(ROOT/name), expected, name)

    def table_row(self, pool_label, method):
        """Return the numeric cells of the results-table row for a method within a pool block."""
        block = self.source.split('\\label{tab:results}')[1].split('\\end{tabular}')[0]
        current = None
        for line in block.splitlines():
            cells = [re.sub(r'\\textbf\{([^}]*)\}', r'\1', c).replace('\\\\', '').strip() for c in line.split('&')]
            if len(cells) < 8:
                continue
            current = cells[0] or current
            if current == pool_label and cells[1] == method:
                return [float(c) if c else None for c in cells[2:8]]
        self.fail(f'row {pool_label} / {method} not found')

    def test_results_table_matches_analysis(self):
        rows = [('Distant (3+ steps)', 'BridgeFinder', 'far:BridgeFinder'), ('Distant (3+ steps)', 'Personalized PageRank', 'far:Personalized PageRank'),
                ('Distant (3+ steps)', 'Path count only', 'far:Path count only'), ('Distant (3+ steps)', 'Topic-Only', 'far:Topic-Only'),
                ('Distant (3+ steps)', 'Co-author count', 'far:Degree'), ('Distant (3+ steps)', 'Random (expected)', 'far:Random (expected)'),
                ('Two-step', 'Personalized PageRank', 'two:Personalized PageRank'), ('Two-step', 'Triadic closure (shared co-authors)', 'two:Triadic closure'),
                ('Two-step', 'BridgeFinder score', 'two:BridgeFinder score'), ('Two-step', 'Topic-Only', 'two:Topic-Only'),
                ('Two-step', 'Random (expected)', 'two:Random (expected)')]
        for pool, label, key in rows:
            with self.subTest(method=label, pool=pool):
                values = self.table_row(pool, label)
                metric = self.ranking['metrics'][key]
                self.assertAlmostEqual(values[0], metric['P@10'], places=4)
                self.assertAlmostEqual(values[1], metric['R@10'], places=4)
                self.assertAlmostEqual(values[2], metric['NDCG@10'], places=4)
                self.assertAlmostEqual(values[3], round(metric['HR@10'], 3), places=3)
                profile = self.ranking['suggestion_profiles'].get(key)
                if profile:
                    self.assertEqual(int(values[4]), int(profile['median_degree_of_suggestions']))
                    self.assertAlmostEqual(values[5], round(profile['mean_topic_overlap_of_suggestions'], 3), places=3)

    def test_quoted_comparisons_match_bootstrap(self):
        comparisons = self.ranking['p10_comparisons_bootstrap']
        quoted = {'BridgeFinder minus Degree': 'co-author count (difference {d}, 95\\% CI {lo} to {hi})',
                  'BridgeFinder minus Path count only': 'path count alone ({d}, CI {lo} to {hi})',
                  'BridgeFinder minus Topic-Only': 'topic overlap alone ({d}, CI {lo} to {hi})',
                  'Triadic closure minus BridgeFinder score (both on two-hop pool)': '(difference {d}, CI {lo} to {hi})'}
        for key, template in quoted.items():
            with self.subTest(comparison=key):
                c = comparisons[key]
                text = template.format(d=f"{c['mean_difference']:.4f}", lo=f"{c['ci95'][0]:.4f}", hi=f"{c['ci95'][1]:.4f}")
                self.assertIn(text, self.source)
        ppr = comparisons['BridgeFinder minus Personalized PageRank']
        self.assertIn(f"(difference {ppr['mean_difference']:.4f}, CI $-${abs(ppr['ci95'][0]):.4f} to {ppr['ci95'][1]:.4f})", self.source)

    def test_pool_and_profile_facts(self):
        sizes = self.ranking['pool_sizes']
        self.assertIn(f"{int(sizes['two']['median'])} two-step candidates and {int(sizes['far']['median']):,} candidates three or more steps away", self.source)
        bf = self.ranking['suggestion_profiles']['far:BridgeFinder']
        self.assertIn(f"{100*bf['share_suggestions_one_training_paper']:.0f}\\% of BridgeFinder's top-ten suggestions have a single training paper", self.source)
        self.assertIn(f"({100*bf['precision_one_paper_suggestions']:.2f}\\% against {100*bf['precision_multi_paper_suggestions']:.2f}\\%)", self.source)
        self.assertIn(f"{100*bf['share_suggestions_zero_topic_overlap']:.0f}\\% of BridgeFinder's top-ten suggestions share no topic", self.source)
        rho = self.ranking['path_count_vs_degree_spearman_in_far_pool']['median_over_seeds']
        self.assertIn(f'has a median of only {rho:.2f}', self.source)
        self.assertIn(f"{self.ranking['seeds']:,} starting researchers", self.source)

    def test_validation_numbers(self):
        v = self.result['validation']
        val = v['validation_split']['metrics']
        self.assertEqual(v['selected_on_validation'], 'saturating lambda=0.5, two-paper minimum')
        self.assertIn(f"for the {v['validation_split']['seeds']:,} researchers who formed one", self.source)
        sat = {lam: val[f'saturating lambda={lam}']['P@10'] for lam in ['0.1', '0.25', '0.5', '1.0', '2.0', '5.0']}
        self.assertEqual(max(sat, key=sat.get), '0.5')
        coordinates = ' '.join(f"({lam.rstrip('0').rstrip('.') if '.' in lam else lam},{value:.4f})" for lam, value in sat.items())
        self.assertIn(coordinates, self.source)
        logs = ' '.join(f"({lam.rstrip('0').rstrip('.')},{val[f'log lambda={lam}']['P@10']:.4f})" for lam in ['0.1', '0.25', '0.5', '1.0', '2.0', '5.0'])
        self.assertIn(logs, self.source)
        filt = ' '.join(f"({lam.rstrip('0').rstrip('.')},{val[f'saturating lambda={lam}, two-paper minimum']['P@10']:.4f})" for lam in ['0.5', '1.0', '2.0'])
        self.assertIn(filt, self.source)
        self.assertIn(f"{{{val['Topic-Only']['P@10']:.4f}}}", self.source)
        self.assertIn(f"{{{val['Path count only']['P@10']:.4f}}}", self.source)
        large = v['validation_without_papers_over_25_authors']['metrics']['saturating lambda=0.5']['P@10']
        self.assertIn(f"did not help ({large:.4f} against {sat['0.5']:.4f})", self.source)
        test = v['test_split_check']
        diff = test['selected_minus_deployed_p10']
        self.assertIn(f"raises P@10 from {test['metrics']['saturating lambda=0.5']['P@10']:.4f} to {test['metrics']['saturating lambda=0.5, two-paper minimum']['P@10']:.4f} (difference {diff['mean_difference']:.4f}, CI {diff['ci95'][0]:.4f} to {diff['ci95'][1]:.4f})", self.source)
        self.assertEqual(test['metrics']['saturating lambda=0.5']['P@10'], self.ranking['metrics']['far:BridgeFinder']['P@10'])

    def test_worked_example_matches_saved_result(self):
        example = json.loads((ROOT/'results/final_example.json').read_text())
        record = json.loads((ROOT/'results/final-example-run.json').read_text())
        self.assertEqual(digest(ROOT/'results/final_example.json'), record['result_sha256'])
        for name, expected in record['source_sha256'].items():
            self.assertEqual(digest(ROOT/name), expected, name)
        block = self.source.split('\\label{tab:example}')[1].split('\\end{tabularx}')[0]
        for method in example['methods'].values():
            for row in method[:3]:
                line = next((l for l in block.splitlines() if f"& {row['name']}," in l), None)
                self.assertIsNotNone(line, row['name'])
                cells = [c.strip().rstrip('\\').strip() for c in line.split('&')]
                self.assertEqual(float(cells[2]), row['topic_overlap'], row['name'])
                self.assertEqual(int(cells[3]), row['coauthors'], row['name'])
                self.assertFalse(row['became_collaborator'])
        self.assertIn('None of these nine people wrote a paper with Gupta in 2020--2024', self.source)

    def test_new_ranking_measures(self):
        r = self.ranking
        self.assertIn(f"is {r['bridgefinder_p10_over_random_p10']:.0f} times the random expectation", self.source)
        big = r['large_team_papers']
        self.assertIn(f"The {big['papers']} training papers with more than {big['author_limit']} UIUC authors create {big['edges_only_from_large_papers']:,} edges that no smaller paper supports, {100*big['share_of_edges']:.0f}\\% of the training graph", self.source)
        share = r['suggestion_profiles']['any:Personalized PageRank']['share_suggestions_two_steps_away']
        self.assertIn(f"({r['metrics']['any:Personalized PageRank']['P@10']:.4f}), and {100*share:.0f}\\% of its top-ten suggestions are two steps away", self.source)
        c = r['p10_comparisons_bootstrap']['Random two-hop minus far BridgeFinder']
        self.assertIn(f"(difference {c['mean_difference']:.4f}, CI {c['ci95'][0]:.4f} to {c['ci95'][1]:.4f})", self.source)
        self.assertEqual(r['suggestion_profiles']['far:BridgeFinder']['share_suggestions_two_steps_away'], 0)

    def test_community_table(self):
        c = self.result['communities']
        rows = {r['method']: r for r in c['partitions']}
        block = self.source.split('\\label{tab:communities}')[1].split('\\end{tabular*}')[0]
        def row(label):
            line = next(l for l in block.splitlines() if l.startswith(label + ' &'))
            return [x.strip().rstrip('\\').strip() for x in line.split('&')]
        deployed = rows['Louvain seed 42 (deployed)']
        self.assertEqual(row('Louvain, deployed')[1:4], [f"{deployed['communities']}", f"{deployed['modularity']:.3f}", '1.00'])
        seeds = [r for name, r in rows.items() if name.startswith('Louvain seed') and 'deployed' not in name]
        cells = row('Louvain, 10 seeds')
        self.assertEqual(len(seeds), 10)
        self.assertEqual(cells[1], f"{min(r['communities'] for r in seeds)}--{max(r['communities'] for r in seeds)}")
        self.assertEqual(cells[2], f"{min(r['modularity'] for r in seeds):.3f}--{max(r['modularity'] for r in seeds):.3f}")
        self.assertEqual(cells[3], f"$\\geq${int(100*min(r['nmi_with_deployed'] for r in seeds))/100:.2f}")
        self.assertEqual(cells[5], f"{100*c['louvain_seed_range']['demo_overlap_mean']:.0f}\\%")
        for label, key in [('Greedy modularity', 'Greedy modularity (Clauset-Newman-Moore)'), ('Label propagation', 'Label propagation')]:
            r, cells = rows[key], row(label)
            self.assertEqual(cells[1:4], [f"{r['communities']:,}", f"{r['modularity']:.3f}", f"{r['nmi_with_deployed']:.2f}"])
            self.assertEqual(cells[5], f"{100*r['demo_top10_overlap_with_deployed']:.0f}\\%")
        for g in c['girvan_newman_subgraphs']:
            cells = row(f"{g['nodes']} ({g['edges']:,})")
            self.assertEqual(cells[2:4], [f"{g['girvan_newman']['best_modularity']:.3f}", f"{g['louvain']['modularity']:.3f}"])
            self.assertLess(g['girvan_newman']['best_modularity'], g['louvain']['modularity'])
        low = 1 - max(r['deployed_suggestions_still_cross_community'] for r in seeds)
        high = 1 - min(r['deployed_suggestions_still_cross_community'] for r in seeds)
        self.assertIn(f"between {100*low:.0f}\\% and {100*high:.0f}\\% of them would fall inside", self.source)


if __name__ == '__main__':
    unittest.main()
