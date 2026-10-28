"""Model and measurement invariants; fixtures are not participant evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import networkx as nx
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import prepare_model, rank_candidates, build_graphs
spec = importlib.util.spec_from_file_location('study_analysis', ROOT/'study/analyze_study.py')
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)

class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph, _, cls.authors, cls.membership, cls.autonomy = prepare_model(json.loads((ROOT/'uiuc_data_scaled.json').read_text()))
        cls.bundle = json.loads((ROOT/'web/data.json').read_text())
        cls.cards = json.loads((ROOT/'study/study_cards.json').read_text())
        cls.keys = json.loads((ROOT/'study/truth_keys.json').read_text())

    def test_displayed_rankings_match_model_and_paths_are_real(self):
        route_counts = {'two': 0, 'three': 0, 'unavailable': 0}
        for seed, displayed in self.bundle['recommendations'].items():
            expected = rank_candidates(self.graph, seed, self.membership, self.autonomy)[:10]
            self.assertEqual([r['candidate_id'] for r in expected], [r['candidate_id'] for r in displayed])
            for actual, model in zip(displayed, expected):
                self.assertAlmostEqual(actual['score'], model['score'], places=6)
                path = actual['path_ids']
                if path:
                    self.assertEqual(path[0], seed)
                    self.assertEqual(path[-1], actual['candidate_id'])
                    self.assertTrue(all(self.graph.has_edge(u,v) for u,v in zip(path,path[1:])))
                    self.assertEqual(len(path)-1, nx.shortest_path_length(self.graph,seed,path[-1]))
                    route_counts['two' if len(path)==3 else 'three'] += 1
                else:
                    self.assertEqual(actual['path_steps'], [])
                    self.assertNotIn(actual['candidate_id'], nx.single_source_shortest_path_length(self.graph, seed, cutoff=3))
                    route_counts['unavailable'] += 1
        self.assertGreater(route_counts['two'], 0)
        self.assertGreater(route_counts['three'], 0)
        # Explicit disconnected-graph fixture exercises unavailable routing.
        fixture = nx.Graph([('a','b'),('c','d')])
        nx.set_node_attributes(fixture, {n: {'topics': set()} for n in fixture})
        rows = rank_candidates(fixture, 'a', {'a':0,'b':0,'c':1,'d':1}, {n:0 for n in fixture})
        self.assertTrue(all(r['path_ids'] is None and r['path_bonus'] == .1 for r in rows))
        print('Validated route states:', route_counts)

    def test_study_has_five_unbiased_candidates_per_method(self):
        for seed in {c['seed_id'] for c in self.cards}:
            rows = [c for c in self.cards if c['seed_id']==seed]
            self.assertEqual(len(rows), len({self.keys[c['card_id']]['candidate_id'] for c in rows}))
            ranked = rank_candidates(self.graph,seed,self.membership,self.autonomy)
            for method, field in [('BridgeFinder','score'),('Triadic Closure','aa'),('Topic-Only','topic_similarity')]:
                expected = {r['candidate_id'] for r in sorted(ranked,key=lambda r:(-r[field],r['candidate_id']))[:5]}
                actual = {self.keys[c['card_id']]['candidate_id'] for c in rows if method in self.keys[c['card_id']]['models']}
                self.assertEqual(actual, expected)

    def test_future_publications_do_not_change_training_features(self):
        data = {'authors': {n: {'name': n} for n in ['a','b','c']}, 'papers': [
            {'year':2018,'authors':['a','b'],'topics':['training-only']},
            {'year':2022,'authors':['a','c'],'topics':['future-only']}]}
        train, evaluation, _ = build_graphs(data)
        self.assertEqual(set(train.edges()), {('a','b')})
        self.assertEqual(train.nodes['a']['topics'], {'training-only'})
        self.assertNotIn('c', train)
        self.assertTrue(evaluation.has_edge('a','c'))

    def test_export_analysis_validation_and_sus(self):
        seed=self.cards[0]['seed_id']
        rows=[c for c in self.cards if c['seed_id']==seed]
        # Explicitly synthetic, in-memory contract test. Never a study result.
        session={'schema_version':1,'dataset_id':self.cards[0]['dataset_id'],'participant_id':'contract-test', 'seed_id':seed, 'sus':[5,1]*5,
                 'ratings':[{'card_id':c['card_id'],'relevance':5,'novelty':5,'actionability':5} for c in rows]}
        result=analysis.analyze([session],self.keys)
        self.assertEqual(result['mean_sus'],100)
        self.assertEqual(result['n_participants'],1)
        self.assertIsNone(result['comparisons']['Triadic Closure:relevant_and_new']['p_wilcoxon'])
        for broken in [dict(session, ratings=session['ratings'][:-1]), dict(session,sus=[]),dict(session,purpose='automated-test')]:
            with self.assertRaises(ValueError): analysis.analyze([broken],self.keys)
        with self.assertRaises(ValueError): analysis.analyze([session,session],self.keys)
        self.assertEqual(analysis.sus_score([1,5]*5),0)
        second=copy.deepcopy(session); second['participant_id']='second-contract-test'
        for rating in second['ratings']: rating['novelty']=3
        paired_result=analysis.analyze([session,second],self.keys)
        self.assertEqual(paired_result['n_participants'],2)
        self.assertTrue(all('p_holm' in item for item in paired_result['comparisons'].values() if not item['primary']))
        self.assertEqual(analysis.paired([1,1],[1,1])['p_wilcoxon'],1)

if __name__=='__main__': unittest.main()
