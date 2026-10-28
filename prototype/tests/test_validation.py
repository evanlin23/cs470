"""Malformed-data regression tests and independent measurement oracles.

All sessions here are clearly synthetic test inputs, not human observations.
"""
import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from topic_groups import classify_topics
from model import compute_burt_constraint, compute_topic_similarity, rank_candidates, candidate_features
import networkx as nx
spec=importlib.util.spec_from_file_location('analysis',ROOT/'study/analyze_study.py')
analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards=json.loads((ROOT/'study/study_cards.json').read_text())
        cls.keys=json.loads((ROOT/'study/truth_keys.json').read_text())
        seed=cls.cards[0]['seed_id']
        cls.session={'schema_version':1,'dataset_id':cls.cards[0]['dataset_id'],'participant_id':'synthetic-contract',
                     'seed_id':seed,'sus':[5,1]*5,'ratings':[{'card_id':row['card_id'],'relevance':5,'novelty':5,'actionability':5} for row in cls.cards if row['seed_id']==seed]}

    def test_topic_labels_are_hints_not_community_ids(self):
        self.assertEqual(classify_topics(['Natural Language Processing and Machine Learning']),'Computing and AI')
        self.assertEqual(classify_topics(['Crop growth and soil']),'Agriculture and environment')
        self.assertEqual(classify_topics(['Unmatched example']),'Other topics')
        self.assertEqual(classify_topics([]),'Other topics')
        self.assertEqual(classify_topics(['SOIL','crop']),classify_topics(['crop','soil']))

    def test_burt_autonomy_matches_independent_networkx_oracle(self):
        graph=nx.Graph();graph.add_weighted_edges_from([('a','b',2),('a','c',1),('b','c',1),('c','d',3)])
        actual=compute_burt_constraint(graph);constraint=nx.constraint(graph,weight='weight')
        for node in graph:
            self.assertAlmostEqual(actual[node],max(0,1-constraint[node]))
        self.assertEqual(compute_burt_constraint(nx.empty_graph(1))[0],0)
        self.assertEqual(compute_topic_similarity({'one','two'},{'two','three'}),1/3)
        self.assertEqual(compute_topic_similarity(set(),{'one'}),0)

    def test_proposal_score_and_eligibility_against_hand_calculation(self):
        graph=nx.Graph([('start','broker'),('broker','near'),('near','far'),('x','y')])
        nx.set_node_attributes(graph,{'start':{'topics':{'relevant'}},'broker':{'topics':set()},
                                      'near':{'topics':{'unrelated'}},'far':{'topics':{'relevant'}},
                                      'x':{'topics':{'relevant'}},'y':{'topics':{'relevant'}}})
        groups={'start':0,'broker':0,'near':1,'far':1,'x':2,'y':2}
        autonomy=compute_burt_constraint(graph)
        rows=rank_candidates(graph,'start',groups,autonomy)
        self.assertEqual([row['candidate_id'] for row in rows],['far'])
        self.assertEqual(rows[0]['distance'],3)
        self.assertEqual(rows[0]['three_hop_paths'],1)
        self.assertEqual(rows[0]['path_bonus'],.5)
        self.assertAlmostEqual(rows[0]['score'],1.25)
        self.assertEqual(rows[0]['aa'],0)
        all_rows={row['candidate_id']:row for row in candidate_features(graph,'start',groups,autonomy)}
        self.assertGreater(all_rows['near']['aa'],0)
        self.assertFalse(all_rows['near']['proposal_eligible'])
        self.assertFalse(all_rows['x']['proposal_eligible'])
        self.assertIsNone(all_rows['x']['path_ids'])

    def test_four_hop_candidates_remain_eligible_without_three_path_bonus(self):
        graph=nx.path_graph(['a','b','c','d','e'])
        nx.set_node_attributes(graph,{n:{'topics':{'same'}} for n in graph})
        groups={n:0 if n in ['a','b'] else 1 for n in graph}
        rows={row['candidate_id']:row for row in rank_candidates(graph,'a',groups,compute_burt_constraint(graph))}
        self.assertEqual(rows['e']['distance'],4)
        self.assertEqual(rows['e']['path_bonus'],0)
        self.assertEqual(rows['e']['score'],1)
        self.assertNotIn('c',rows)

    def test_rejects_mismatched_dataset_and_unsupported_schema(self):
        for key,value in [('dataset_id','0'*64),('schema_version',None),('schema_version',True),('schema_version',2)]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):analysis.analyze([{**self.session,key:value}],self.keys)

    def test_malformed_sessions_fail_with_value_error_not_type_error(self):
        invalid=[None,{},'text',[None],[[]],[{'participant_id':None}],[{**self.session,'ratings':None}],
                 [{**self.session,'ratings':[None]}],[{**self.session,'ratings':[{'card_id':[]}]}],
                 [{**self.session,'sus':None}],[{**self.session,'sus':[True]*10}]]
        for payload in invalid:
            with self.subTest(payload=str(payload)[:80]),self.assertRaises(ValueError):analysis.analyze(payload,self.keys)

    def test_missing_extra_duplicate_and_out_of_range_ratings_are_excluded(self):
        invalid=[]
        for field,value in [('relevance',0),('novelty',8),('actionability',True),('relevance',float('nan')),('novelty','5')]:
            session=copy.deepcopy(self.session);session['ratings'][0][field]=value;invalid.append(session)
        for field,value in [('ratings',self.session['ratings'][:-1]),('ratings',self.session['ratings']+[self.session['ratings'][0]]),('seed_id','unknown')]:
            invalid.append({**self.session,field:value})
        for i,session in enumerate(invalid):
            session['participant_id']=f'bad-{i}'
            result=analysis.analyze([self.session,session],self.keys)
            self.assertEqual(result['n_participants'],1)
            self.assertEqual(len(result['excluded']),1)

    def test_rejects_incompatible_private_keys_and_duplicate_identity(self):
        for payload in [None,[],{},{'a':'BridgeFinder'},{'a':{'seed_id':'s','candidate_id':'c','models':['unknown']}}]:
            with self.subTest(payload=payload),self.assertRaises(ValueError):analysis.analyze([self.session],payload)
        changed=copy.deepcopy(self.keys);next(iter(changed.values()))['models']=['BridgeFinder']*2
        with self.assertRaises(ValueError):analysis.analyze([self.session],changed)
        second={**self.session,'participant_id':' '+self.session['participant_id']+' '}
        with self.assertRaises(ValueError):analysis.analyze([self.session,second],self.keys)

    def test_paired_inference_and_holm_use_participants(self):
        expected=analysis.paired([.8,.6,.2],[.2,.2,.2])
        self.assertEqual(expected['n'],3)
        self.assertAlmostEqual(expected['mean_difference'],1/3)
        self.assertTrue(all(math.isfinite(v) for v in expected['ci95']))
        for a,b in [([],[]),([1],[1,2]),([float('inf')],[1])]:
            with self.assertRaises(ValueError):analysis.paired(a,b)
        sessions=[]
        for i in range(3):
            session=copy.deepcopy(self.session);session['participant_id']=f'synthetic-{i}'
            for row in session['ratings']:
                row['novelty']=max(1,7-i*2) if 'BridgeFinder' in self.keys[row['card_id']]['models'] else 2
            sessions.append(session)
        result=analysis.analyze(sessions,self.keys)
        self.assertEqual(result['n_participants'],3)
        exploratory=sorted((row['p_wilcoxon'],row['p_holm']) for row in result['comparisons'].values() if not row['primary'])
        previous=0
        for index,(pvalue,adjusted) in enumerate(exploratory):
            expected=min(1,max(previous,pvalue*(len(exploratory)-index)))
            self.assertAlmostEqual(adjusted,expected);previous=expected
        json.dumps(result,allow_nan=False)

    def test_cli_rejects_invalid_input_and_writes_no_false_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'synthetic-input.json';output=Path(tmp)/'output.json';source.write_text('[]')
            command=[sys.executable,str(ROOT/'study/analyze_study.py'),'--responses',str(source),'--keys',str(ROOT/'study/truth_keys.json'),'--out',str(output)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertIn('No complete participant',result.stderr);self.assertFalse(output.exists())
            source.write_text(json.dumps([self.session]));result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(json.loads(output.read_text())['n_participants'],1)

if __name__=='__main__':unittest.main()
