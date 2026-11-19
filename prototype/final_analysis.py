"""Analyses added for the final report. They never change the deployed model, app or study cards.

1. ranking   Same-pool comparison on the 2020-2024 test: every ranker scores the same
             candidates, so the effect of the score is separated from the effect of distance.
             Adds in-class alternatives (personalized PageRank, degree) and a random baseline.
2. validate  Parameter choices tuned on a separate split (graph <=2017, ties in 2018-2019):
             path-bonus weight and form, a two-paper minimum, and large-team papers.
             The chosen setting is then scored once on the test split.
3. communities  Louvain against label propagation, greedy modularity and Girvan-Newman, with
             seed stability measured on what the app shows.
4. failures  Where the network analysis performs poorly: popularity, one-paper authors,
             topic overlap of hits.

    python prototype/final_analysis.py --part all --out prototype/results/final_analysis.json
"""
import argparse
from collections import Counter, defaultdict
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import random
import statistics
import time

import networkx as nx
from networkx.algorithms import community as nxc
import numpy as np
from scipy import sparse

from model import build_graphs, prepare_training_model, candidate_features, rank_candidates, MODEL_VERSION
from run_metadata import metadata_for, save_manifest

ROOT = Path(__file__).resolve().parent
K = 10
ALPHA = 0.85          # PageRank damping: restart to the seed with probability 0.15
BOOTSTRAP = 2000
G = {}                # read-only state shared with forked workers


# ---------------------------------------------------------------- shared helpers
def ground_truth(graph, evaluation, membership):
    truth = defaultdict(set)
    for u, v in evaluation.edges():
        if u in membership and v in membership and membership[u] != membership[v] and not graph.has_edge(u, v):
            truth[u].add(v)
            truth[v].add(u)
    return truth


def training_paper_counts(data, split_year):
    counts = Counter()
    for paper in data['papers']:
        if paper['year'] <= split_year and len(paper['authors']) >= 2:
            counts.update(paper['authors'])
    return counts


def ppr_operator(graph):
    nodes = sorted(graph)
    index = {node: i for i, node in enumerate(nodes)}
    rows, cols, vals = [], [], []
    for u, v, data in graph.edges(data=True):
        w = data.get('weight', 1.0)
        rows += [index[u], index[v]]; cols += [index[v], index[u]]; vals += [w, w]
    adjacency = sparse.csr_matrix((vals, (rows, cols)), shape=(len(nodes), len(nodes)))
    strength = np.asarray(adjacency.sum(axis=1)).ravel()
    transition = sparse.diags(1.0/np.where(strength > 0, strength, 1.0)) @ adjacency
    return transition.T.tocsr(), index


def personalized_pagerank(seed, iterations=40):
    operator, index = G['ppr']
    restart = np.zeros(operator.shape[0]); restart[index[seed]] = 1.0
    x = restart.copy()
    for _ in range(iterations):
        x = ALPHA*(operator @ x) + (1-ALPHA)*restart
    return x


def metrics(ranked_ids, truth):
    top = ranked_ids[:K]
    hits = [v in truth for v in top]
    dcg = sum(1/math.log2(i+2) for i, hit in enumerate(hits) if hit)
    ideal = sum(1/math.log2(i+2) for i in range(min(K, len(truth))))
    return {'P@10': sum(hits)/K, 'R@10': sum(hits)/len(truth), 'NDCG@10': dcg/ideal, 'HR@10': float(any(hits))}


def expected_random(pool, truth):
    """Exact expectation of each metric for a uniformly random top-10 from the pool."""
    if not pool:
        return {'P@10': 0.0, 'R@10': 0.0, 'NDCG@10': 0.0, 'HR@10': 0.0}
    n, positives = len(pool), sum(r['candidate_id'] in truth for r in pool)
    k = min(K, n)
    rate = positives/n
    ideal = sum(1/math.log2(i+2) for i in range(min(K, len(truth))))
    miss_all = math.comb(n-positives, k)/math.comb(n, k) if n-positives >= k else 0.0
    return {'P@10': k*rate/K, 'R@10': k*rate/len(truth), 'NDCG@10': rate*sum(1/math.log2(i+2) for i in range(k))/ideal, 'HR@10': 1-miss_all}


def ranked(pool, key):
    return [r['candidate_id'] for r in sorted(pool, key=lambda r: (-key(r), r['candidate_id']))]


def summarize(per_seed):
    return {name: {m: round(statistics.mean(v[m] for v in values), 4) for m in values[0]} for name, values in per_seed.items()}


def paired_bootstrap(a, b, seed=7):
    a, b = np.asarray(a), np.asarray(b)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(a), size=(BOOTSTRAP, len(a)))
    diffs = (a[draws] - b[draws]).mean(axis=1)
    return {'mean_difference': round(float((a-b).mean()), 4), 'ci95': [round(float(np.percentile(diffs, 2.5)), 4), round(float(np.percentile(diffs, 97.5)), 4)]}


def run_parallel(function, seeds, workers):
    if workers <= 1:
        return [function(s) for s in seeds]
    with mp.get_context('fork').Pool(workers) as pool:
        return pool.map(function, seeds, chunksize=16)


def large_team_share(data, graph, limit=25):
    """How much of the training graph comes from papers with more than `limit` UIUC authors."""
    small, big, papers_big = set(), set(), 0
    for paper in data['papers']:
        if paper['year'] > 2019 or len(paper['authors']) < 2:
            continue
        pairs = {tuple(sorted((a, b))) for i, a in enumerate(paper['authors']) for b in paper['authors'][i+1:]}
        if len(paper['authors']) > limit:
            big |= pairs; papers_big += 1
        else:
            small |= pairs
    only_big = big - small
    return {'author_limit': limit, 'papers': papers_big, 'edges_only_from_large_papers': len(only_big),
            'share_of_edges': round(len(only_big)/graph.number_of_edges(), 4)}


# ---------------------------------------------------------------- 1. same-pool ranking (test split)
def score_seed_ranking(seed):
    graph, membership, truth, degree = G['graph'], G['membership'], G['truth'][seed], G['degree']
    rows = candidate_features(graph, seed, membership)
    ppr = personalized_pagerank(seed)
    index = G['ppr'][1]
    for r in rows:
        r['degree'] = degree[r['candidate_id']]
        r['ppr'] = ppr[index[r['candidate_id']]]
    far = [r for r in rows if r['proposal_eligible']]
    two = [r for r in rows if r['distance'] == 2]
    reachable = [r for r in rows if r['distance'] is not None]
    rankers = {
        'far:Random (expected)': None,
        'far:Degree': (far, lambda r: r['degree']),
        'far:Path count only': (far, lambda r: r['three_hop_paths']),
        'far:Topic-Only': (far, lambda r: r['topic_similarity']),
        'far:Personalized PageRank': (far, lambda r: r['ppr']),
        'far:BridgeFinder': (far, lambda r: r['score']),
        'two:Random (expected)': None,
        'two:Triadic closure': (two, lambda r: r['shared_coauthors']),
        'two:Topic-Only': (two, lambda r: r['topic_similarity']),
        'two:BridgeFinder score': (two, lambda r: r['score']),
        'two:Personalized PageRank': (two, lambda r: r['ppr']),
        'any:Personalized PageRank': (reachable, lambda r: r['ppr']),
    }
    out, profile = {}, {}
    for name, spec in rankers.items():
        if spec is None:
            out[name] = expected_random(far if name.startswith('far') else two, truth)
            continue
        pool, key = spec
        ids = ranked(pool, key)
        out[name] = metrics(ids, truth)
        chosen = {r['candidate_id']: r for r in pool}
        top = [chosen[i] for i in ids[:K]]
        profile[name] = {'degree': [r['degree'] for r in top], 'topic': [r['topic_similarity'] for r in top],
                         'distance_two': [r['distance'] == 2 for r in top],
                         'hit_topic': [r['topic_similarity'] for r in top if r['candidate_id'] in truth],
                         'one_paper': [G['papers'][r['candidate_id']] == 1 for r in top],
                         'hit_one_paper': [r['candidate_id'] in truth for r in top if G['papers'][r['candidate_id']] == 1],
                         'hit_multi_paper': [r['candidate_id'] in truth for r in top if G['papers'][r['candidate_id']] > 1]}
    sizes = {'far': len(far), 'two': len(two), 'far_positive': sum(r['candidate_id'] in truth for r in far),
             'two_positive': sum(r['candidate_id'] in truth for r in two)}
    # Degree correlation of the path count inside the far pool (is the bonus a popularity proxy?)
    corr = None
    if len(far) > 10:
        c3 = np.array([r['three_hop_paths'] for r in far], float); deg = np.array([r['degree'] for r in far], float)
        if c3.std() > 0 and deg.std() > 0:
            from scipy.stats import spearmanr
            corr = float(spearmanr(c3, deg).statistic)
    return out, profile, sizes, corr


def part_ranking(data, workers):
    train, evaluation, _ = build_graphs(data, split_year=2019)
    graph, membership = prepare_training_model(train)
    truth = ground_truth(graph, evaluation, membership)
    seeds = sorted(truth)[:G.get('limit')]
    G.update(graph=graph, membership=membership, truth=truth, degree=dict(graph.degree()),
             ppr=ppr_operator(graph), papers=training_paper_counts(data, 2019))
    started = time.time()
    results = run_parallel(score_seed_ranking, seeds, workers)
    per_seed = defaultdict(list)
    profiles = defaultdict(lambda: defaultdict(list))
    sizes = defaultdict(list)
    correlations = []
    for out, profile, size, corr in results:
        for name, values in out.items():
            per_seed[name].append(values)
        for name, values in profile.items():
            for key, items in values.items():
                profiles[name][key].extend(items)
        for key, value in size.items():
            sizes[key].append(value)
        if corr is not None:
            correlations.append(corr)
    p10 = {name: [v['P@10'] for v in values] for name, values in per_seed.items()}
    comparisons = {f'BridgeFinder minus {other.split(":", 1)[1]}': paired_bootstrap(p10['far:BridgeFinder'], p10[other])
                   for other in ['far:Random (expected)', 'far:Degree', 'far:Path count only', 'far:Topic-Only', 'far:Personalized PageRank']}
    comparisons['Triadic closure minus BridgeFinder score (both on two-hop pool)'] = paired_bootstrap(p10['two:Triadic closure'], p10['two:BridgeFinder score'])
    comparisons['Two-hop BridgeFinder score minus far BridgeFinder'] = paired_bootstrap(p10['two:BridgeFinder score'], p10['far:BridgeFinder'])
    comparisons['Random two-hop minus far BridgeFinder'] = paired_bootstrap(p10['two:Random (expected)'], p10['far:BridgeFinder'])
    ratio_to_random = statistics.mean(p10['far:BridgeFinder'])/statistics.mean(p10['far:Random (expected)'])
    profile_summary = {}
    for name, values in profiles.items():
        profile_summary[name] = {
            'median_degree_of_suggestions': statistics.median(values['degree']),
            'mean_topic_overlap_of_suggestions': round(statistics.mean(values['topic']), 4),
            'share_suggestions_zero_topic_overlap': round(sum(t == 0 for t in values['topic'])/len(values['topic']), 4),
            'mean_topic_overlap_of_hits': round(statistics.mean(values['hit_topic']), 4) if values['hit_topic'] else None,
            'share_suggestions_one_training_paper': round(statistics.mean(values['one_paper']), 4),
            'share_suggestions_two_steps_away': round(statistics.mean(values['distance_two']), 4),
            'precision_one_paper_suggestions': round(statistics.mean(values['hit_one_paper']), 4) if values['hit_one_paper'] else None,
            'precision_multi_paper_suggestions': round(statistics.mean(values['hit_multi_paper']), 4) if values['hit_multi_paper'] else None,
        }
    return {
        'split': {'train': '2015-2019', 'test': '2020-2024'}, 'seeds': len(seeds), 'seconds': round(time.time()-started, 1),
        'pools': {'far': 'cross-community, reachable, distance >=3 (the deployed pool)', 'two': 'cross-community, distance 2 (triadic closure pool)',
                  'any': 'cross-community, reachable, any distance >=2'},
        'pool_sizes': {key: {'median': statistics.median(v), 'mean': round(statistics.mean(v), 1)} for key, v in sizes.items()},
        'metrics': summarize(per_seed), 'p10_comparisons_bootstrap': comparisons,
        'bridgefinder_p10_over_random_p10': round(ratio_to_random, 1),
        'large_team_papers': large_team_share(data, graph),
        'suggestion_profiles': profile_summary,
        'path_count_vs_degree_spearman_in_far_pool': {'median_over_seeds': round(statistics.median(correlations), 3), 'seeds': len(correlations)},
        'pagerank': {'damping': ALPHA, 'iterations': 40, 'edge_weight': 'joint_paper_count'},
    }


# ---------------------------------------------------------------- 2. validation sweep
LAMBDAS = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]


def validation_configs():
    configs = [('Topic-Only', 'sat', 0.0, False)]
    configs += [(f'saturating lambda={lam}', 'sat', lam, False) for lam in LAMBDAS[1:]]
    configs += [(f'log lambda={lam}', 'log', lam, False) for lam in LAMBDAS[1:]]
    configs += [('Path count only', 'raw', math.inf, False)]
    configs += [(f'saturating lambda={lam}, two-paper minimum', 'sat', lam, True) for lam in [0.0, 0.5, 1.0, 2.0]]
    return configs


def config_key(form, lam):
    if lam == math.inf:
        return lambda r: r['three_hop_paths']
    if form == 'log':
        return lambda r: r['topic_similarity'] + lam*math.log1p(r['three_hop_paths'])
    return lambda r: r['topic_similarity'] + lam*r['three_hop_paths']/(1+r['three_hop_paths'])


def score_seed_validation(seed):
    rows = candidate_features(G['graph'], seed, G['membership'])
    far = [r for r in rows if r['proposal_eligible']]
    filtered = [r for r in far if G['papers'][r['candidate_id']] >= 2]
    truth = G['truth'][seed]
    out = {}
    for name, form, lam, minimum in G['configs']:
        out[name] = metrics(ranked(filtered if minimum else far, config_key(form, lam)), truth)
    out['Triadic closure'] = metrics(ranked([r for r in rows if r['distance'] == 2], lambda r: r['shared_coauthors']), truth)
    return out


def evaluate_split(data, split_year, eval_last_year, workers, configs, drop_large=None):
    papers = [p for p in data['papers'] if p['year'] <= eval_last_year]
    if drop_large:
        papers = [p for p in papers if not (p['year'] <= split_year and len(p['authors']) > drop_large)]
    train, evaluation, _ = build_graphs({'papers': papers, 'authors': data['authors']}, split_year=split_year)
    graph, membership = prepare_training_model(train)
    truth = ground_truth(graph, evaluation, membership)
    G.update(graph=graph, membership=membership, truth=truth, configs=configs,
             papers=training_paper_counts({'papers': papers}, split_year))
    seeds = sorted(truth)[:G.get('limit')]
    results = run_parallel(score_seed_validation, seeds, workers)
    per_seed = defaultdict(list)
    for out in results:
        for name, values in out.items():
            per_seed[name].append(values)
    return {'seeds': len(seeds), 'communities': len(set(membership.values())), 'metrics': summarize(per_seed),
            'p10': {name: [v['P@10'] for v in values] for name, values in per_seed.items()}}


def part_validate(data, workers):
    started = time.time()
    configs = validation_configs()
    val = evaluate_split(data, 2017, 2019, workers, configs)
    val_large = evaluate_split(data, 2017, 2019, workers, [c for c in configs if c[0] in ('Topic-Only', 'saturating lambda=0.5')], drop_large=25)
    candidates = [c for c in configs if c[0] not in ('Topic-Only',)]
    best = max(candidates, key=lambda c: (val['metrics'][c[0]]['P@10'], -configs.index(c)))
    deployed = next(c for c in configs if c[0] == 'saturating lambda=0.5')
    chosen = [deployed] if best == deployed else [deployed, best]
    test = evaluate_split(data, 2019, 2024, workers, [configs[0], *chosen])
    test_comparison = None
    if best != deployed:
        test_comparison = paired_bootstrap(test['p10'][best[0]], test['p10'][deployed[0]])
    for block in (val, val_large, test):
        block.pop('p10')
    return {'validation_split': {'train': '2015-2017', 'validate': '2018-2019', **val},
            'validation_without_papers_over_25_authors': {'note': 'training papers with more than 25 UIUC authors removed', **val_large},
            'selected_on_validation': best[0], 'deployed': deployed[0],
            'test_split_check': {'train': '2015-2019', 'test': '2020-2024', **test, 'selected_minus_deployed_p10': test_comparison},
            'seconds': round(time.time()-started, 1)}


# ---------------------------------------------------------------- 3. community detection
def nmi(a, b, nodes):
    n = len(nodes)
    pa, pb, joint = Counter(a[x] for x in nodes), Counter(b[x] for x in nodes), Counter((a[x], b[x]) for x in nodes)
    h = lambda counts: -sum(c/n*math.log(c/n) for c in counts.values())
    mutual = sum(c/n*math.log((c/n)/((pa[i]/n)*(pb[j]/n))) for (i, j), c in joint.items())
    return 2*mutual/(h(pa)+h(pb))


def membership_of(communities):
    return {node: i for i, c in enumerate(sorted(communities, key=lambda c: (-len(c), sorted(c)))) for node in c}


def girvan_newman_trial(graph, limit_seconds):
    start = time.time()
    best_q, best_k, levels = -1.0, 1, 0
    for partition in nxc.girvan_newman(graph):
        levels += 1
        q = nxc.modularity(graph, partition)
        if q > best_q:
            best_q, best_k = q, len(partition)
        if time.time()-start > limit_seconds or len(partition) >= graph.number_of_nodes()//2:
            break
    return {'best_modularity': round(best_q, 4), 'communities_at_best': best_k, 'levels_computed': levels,
            'seconds': round(time.time()-start, 1), 'stopped_by_time_limit': time.time()-start > limit_seconds}


def part_communities(data, cnm_seconds_cap):
    train, _, _ = build_graphs(data, split_year=2019)
    graph, deployed = prepare_training_model(train)
    nodes = sorted(graph)
    giant = graph.subgraph(max(nx.connected_components(graph), key=len))
    bundle = json.loads((ROOT/'web'/'data.json').read_text())
    demo = [s['id'] for s in bundle['seeds']]
    shown = {s: [r['candidate_id'] for r in rank_candidates(graph, s, deployed)[:K]] for s in demo}

    def describe(name, membership, seconds):
        groups = defaultdict(set)
        for node, c in membership.items():
            groups[c].add(node)
        sizes = sorted((len(g) for g in groups.values()), reverse=True)
        giant_groups = defaultdict(set)
        for node in giant:
            giant_groups[membership[node]].add(node)
        tops = {s: [r['candidate_id'] for r in rank_candidates(graph, s, membership)[:K]] for s in demo}
        overlap = statistics.mean(len(set(tops[s]) & set(shown[s]))/K for s in demo)
        still_cross = statistics.mean(sum(membership[c] != membership[s] for c in shown[s])/len(shown[s]) for s in demo)
        return {'method': name, 'communities': len(sizes), 'largest_community_share': round(sizes[0]/len(nodes), 4),
                'singleton_communities': sum(size == 1 for size in sizes),
                'modularity': round(nxc.modularity(graph, list(groups.values())), 4),
                'modularity_largest_component': round(nxc.modularity(giant, list(giant_groups.values())), 4),
                'nmi_with_deployed': round(nmi(membership, deployed, nodes), 4), 'seconds': round(seconds, 1),
                'demo_top10_overlap_with_deployed': round(overlap, 4),
                'deployed_suggestions_still_cross_community': round(still_cross, 4)}

    rows = [describe('Louvain seed 42 (deployed)', deployed, 0.0)]
    timings = {}
    for seed in range(10):
        t = time.time(); communities = nxc.louvain_communities(graph, seed=seed); timings[seed] = time.time()-t
        rows.append(describe(f'Louvain seed {seed}', membership_of(communities), timings[seed]))
    t = time.time(); communities = list(nxc.label_propagation_communities(graph))
    rows.append(describe('Label propagation', membership_of(communities), time.time()-t))
    cnm = None
    if cnm_seconds_cap:
        t = time.time(); communities = list(nxc.greedy_modularity_communities(graph, weight='weight'))
        cnm = describe('Greedy modularity (Clauset-Newman-Moore)', membership_of(communities), time.time()-t)
        rows.append(cnm)
    # Girvan-Newman on growing neighbourhoods of one demo researcher; compare with Louvain on the same subgraph.
    gn = []
    center = demo[0]
    order = list(nx.bfs_tree(graph, center))
    for size in (50, 100, 150, 200):
        sub = graph.subgraph(order[:size]).copy()
        trial = girvan_newman_trial(sub, limit_seconds=240)
        t = time.time(); louvain = nxc.louvain_communities(sub, seed=42); lt = time.time()-t
        gn.append({'nodes': sub.number_of_nodes(), 'edges': sub.number_of_edges(), 'girvan_newman': trial,
                   'louvain': {'modularity': round(nxc.modularity(sub, louvain), 4), 'communities': len(louvain), 'seconds': round(lt, 3)}})
        if trial['stopped_by_time_limit']:
            break
    louvain_q = [r['modularity'] for r in rows if r['method'].startswith('Louvain seed') and 'deployed' not in r['method']]
    return {'graph': {'nodes': graph.number_of_nodes(), 'edges': graph.number_of_edges()}, 'partitions': rows,
            'louvain_seed_range': {'modularity_min': min(louvain_q), 'modularity_max': max(louvain_q),
                                   'nmi_min': min(r['nmi_with_deployed'] for r in rows[1:11]),
                                   'demo_overlap_min': min(r['demo_top10_overlap_with_deployed'] for r in rows[1:11]),
                                   'demo_overlap_mean': round(statistics.mean(r['demo_top10_overlap_with_deployed'] for r in rows[1:11]), 4),
                                   'seconds_mean': round(statistics.mean(timings.values()), 1)},
            'girvan_newman_subgraphs': gn, 'girvan_newman_center': center}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--data', default=str(ROOT/'uiuc_data_scaled.json'))
    parser.add_argument('--part', choices=['ranking', 'validate', 'communities', 'all'], default='all')
    parser.add_argument('--out', default=str(ROOT/'results'/'final_analysis.json'))
    parser.add_argument('--manifest-out')
    parser.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 1)))
    parser.add_argument('--skip-cnm', action='store_true', help='skip greedy modularity on the full graph (slow)')
    parser.add_argument('--limit', type=int, help='smoke test only: score the first N seeds')
    args = parser.parse_args()
    G['limit'] = args.limit
    data = json.loads(Path(args.data).read_text())
    out_path = Path(args.out)
    result = json.loads(out_path.read_text()) if out_path.exists() else {}
    parts = ['ranking', 'validate', 'communities'] if args.part == 'all' else [args.part]
    for part in parts:
        print(f'Running {part}...', flush=True)
        if part == 'ranking':
            result['ranking'] = part_ranking(data, args.workers)
        elif part == 'validate':
            result['validation'] = part_validate(data, args.workers)
        else:
            result['communities'] = part_communities(data, cnm_seconds_cap=not args.skip_cnm)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2)+'\n')
    metadata = metadata_for(args.data, ['model.py', 'final_analysis.py'], MODEL_VERSION)
    if args.manifest_out:
        save_manifest(args.manifest_out, out_path, metadata)
    print(f'Saved {out_path}')


if __name__ == '__main__':
    main()
