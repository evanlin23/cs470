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
from model import compute_burt_constraint, compute_topic_similarity, rank_candidates
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

    def test_path_bonus_and_score_against_hand_calculation(self):
        graph=nx.Graph([('a','b'),('b','c'),('c','d'),('e','f')])
        nx.set_node_attributes(graph,{n:{'topics':{'same'}} for n in graph})
        membership={'a':0,'b':0,'c':1,'d':1,'e':2,'f':2}
        rows={r['candidate_id']:r for r in rank_candidates(graph,'a',membership,{n:.5 for n in graph})}
        self.assertEqual(rows['c']['path_bonus'],1)
        self.assertEqual(rows['d']['path_bonus'],.5)
        self.assertIsNone(rows['e']['path_ids'])
        self.assertAlmostEqual(rows['c']['score'],.60+.12*.5+.12*.5+.16)
        self.assertAlmostEqual(rows['d']['score'],.60+.12*.5+.16*.5)
        self.assertAlmostEqual(rows['e']['score'],.60+.12*.5+.16*.1)

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
