"""Check 4: is the 2015-2019 -> 2020-2024 backtest feasible and informative?
- Cohort: authors with >=2 UIUC papers in 2015-19 AND >=1 in 2020-24 (still on campus).
- Outcome: a pair NOT tied in 2015-19 co-authors a (<=25-author) paper in 2020-24.
- Shows the base-rate confound (topic similarity and graph distance) and runs the spec's ranking
  against the in-class baselines, plus a topic-matched comparison."""
import collections, json, math, random, statistics, time
import numpy as np, networkx as nx, scipy.sparse as sp
from networkx.algorithms.community import louvain_communities
from common import load_works, build_graph, RESEARCH_TYPES, MAX_AUTHORS

random.seed(0); np.random.seed(0)
works = list(load_works())
GA, topA, npA = build_graph(works, (2015, 2019))
GB, _, npB = build_graph(works, (2020, 2024))
cohort = sorted(a for a in GA if npA[a] >= 2 and npB.get(a, 0) >= 1)
idx = {a: i for i, a in enumerate(cohort)}
N = len(cohort)
R = {"GA_nodes": GA.number_of_nodes(), "GA_edges": GA.number_of_edges(), "cohort": N,
     "authors_A_ge2_papers": sum(c >= 2 for c in npA.values())}
R["share_A_ge2_still_publishing_at_uiuc_in_B"] = round(N / R["authors_A_ge2_papers"], 3)

# new ties among cohort
new = collections.defaultdict(set)
for u, v in GB.edges():
    if u in idx and v in idx and not GA.has_edge(u, v):
        new[u].add(v); new[v].add(u)
R["new_tie_pairs"] = sum(len(s) for s in new.values()) // 2
R["persisting_pairs"] = sum(1 for u, v in GB.edges() if GA.has_edge(u, v) and u in idx and v in idx)

# topic vectors (TF-IDF over OpenAlex topics, 2015-19 only), cosine
tids = {t: i for i, t in enumerate({t for a in cohort for t in topA[a]})}
rows, cols, vals = [], [], []
df = collections.Counter(t for a in cohort for t in topA[a])
for a in cohort:
    for t, s in topA[a].items():
        rows.append(idx[a]); cols.append(tids[t]); vals.append(s * math.log(N / df[t]))
X = sp.csr_matrix((vals, (rows, cols)), shape=(N, len(tids)))
X = sp.diags(1 / np.sqrt(np.asarray(X.multiply(X).sum(1)).ravel() + 1e-12)) @ X

# adjacency over all GA nodes for CN / Adamic-Adar
allnodes = list(GA); gi = {a: i for i, a in enumerate(allnodes)}
A = nx.to_scipy_sparse_array(GA, nodelist=allnodes, weight=None, format="csr")
degs = np.asarray(A.sum(1)).ravel()
Aaa = A @ sp.diags(1 / np.log(np.maximum(degs, 2)))
cohort_g = np.array([gi[a] for a in cohort])
degA = np.array([GA.degree(a) for a in cohort])

# Louvain communities on 2015-19 (for "cross-community")
t = time.time()
comms = louvain_communities(GA, weight="weight", seed=1)
R["louvain_A_seconds"] = round(time.time() - t, 1)
cid = {a: i for i, c in enumerate(comms) for a in c}
ccoh = np.array([cid[a] for a in cohort])

def constraint_local(u, extra=None):
    """Burt constraint of u (weighted, undirected), optionally with a hypothetical new tie u-extra."""
    Nu = {j: d["weight"] for j, d in GA[u].items()}
    if extra is not None:
        Nu[extra] = Nu.get(extra, 0) + 1
    if not Nu:
        return 1.0
    su = sum(Nu.values()); pu = {j: w / su for j, w in Nu.items()}
    sq = {q: sum(d["weight"] for d in GA[q].values()) + (1 if q == extra else 0) for q in Nu}
    c = 0.0
    for j in Nu:
        ind = sum(pu[q] * GA[q][j]["weight"] / sq[q] for q in Nu if q != j and GA.has_edge(q, j))
        c += (pu[j] + ind) ** 2
    return c

egos = [a for a in cohort if new[a] and GA.degree(a) > 0]
R["egos_with_new_ties"] = len(egos)
egos = random.sample(egos, min(1500, len(egos)))
K = 10
methods = ["random", "degree (popular people)", "Adamic-Adar (triadic closure)", "topic only",
           "topic x distance", "spec: topic x distance x brokerage gain",
           "topic, far candidates only (d>=3)", "proposed: topic x warm-intro paths (d=3)"]
hits = {m: [] for m in methods}
hits_far = {m: [] for m in methods}
fof_share = {m: [] for m in methods}  # share of a method's top-10 who are friends-of-friends (d=2)           # only count new ties at distance >=3 as hits
rate = collections.defaultdict(lambda: [0, 0])  # (sim bin, dist bin) -> [new, total]
gain_vs_dist = []
matched = []  # (sim decile among far candidates of this ego, gain above median within decile?, new tie)
far_new_cross, far_new_same = 0, 0
t = time.time()
for e in egos:
    i = idx[e]
    sim = (X[i] @ X.T).toarray().ravel()
    dist = nx.single_source_shortest_path_length(GA, e, cutoff=6)
    d = np.array([dist.get(a, 99) for a in cohort], dtype=float)
    a1 = A[[gi[e]]]
    aa = (a1 @ Aaa).toarray().ravel()[cohort_g]
    p3 = ((a1 @ A) @ A).toarray().ravel()[cohort_g]  # number of length-3 walks = warm-intro routes
    y = np.array([a in new[e] for a in cohort])
    mask = d >= 2  # candidates: not self, not already tied
    for s, dd, yy in zip(sim[mask], d[mask], y[mask]):
        sb = 0 if s < .05 else 1 if s < .1 else 2 if s < .2 else 3 if s < .4 else 4
        db = 2 if dd == 2 else 3 if dd == 3 else 4 if dd <= 5 else 6
        rate[(sb, db)][0] += yy; rate[(sb, db)][1] += 1
    cand = np.where(mask)[0]
    # brokerage gain only for the 200 most topic-similar candidates (the spec's similarity floor)
    top = cand[np.argsort(-sim[cand])[:200]]
    c0 = constraint_local(e)
    gain = np.zeros(N)
    for j in top:
        gain[j] = c0 - constraint_local(e, cohort[j])
        gain_vs_dist.append((gain[j], min(d[j], 7)))
    far_top = [j for j in top if d[j] >= 3]
    if len(far_top) >= 2:
        g = gain[far_top]
        matched.append((len(far_top), len(set(np.round(g, 12))), float(g.max() - g.min())))
    dcap = np.minimum(d, 7)
    scores = {
        "random": np.random.rand(N),
        "degree (popular people)": degA + 1e-6 * np.random.rand(N),
        "Adamic-Adar (triadic closure)": aa + 1e-6 * sim,
        "topic only": sim,
        "topic x distance": np.where(sim >= sim[top].min(), sim * dcap, 0),
        "spec: topic x distance x brokerage gain": sim * dcap * gain,
        "topic, far candidates only (d>=3)": np.where(d >= 3, sim, 0),
        "proposed: topic x warm-intro paths (d=3)": np.where(d >= 3, sim * (1 + np.log1p(np.where(d == 3, p3, 0))), 0),
    }
    yfar = y & (d >= 3)
    for m, sc in scores.items():
        sc = np.where(mask, sc, -np.inf)
        topk = np.argpartition(-sc, K)[:K]
        hits[m].append(y[topk].sum() / K)
        fof_share[m].append(float((d[topk] == 2).mean()))
        if yfar.any():
            hits_far[m].append(yfar[topk].sum() / K)
    for j in np.where(yfar)[0]:
        if ccoh[j] == cid[e]: far_new_same += 1
        else: far_new_cross += 1
def boot(a, b, n=2000):
    a, b = np.array(a), np.array(b); diffs = []
    for _ in range(n):
        k = np.random.randint(0, len(a), len(a)); diffs.append(a[k].mean() - b[k].mean())
    return [round(float(np.percentile(diffs, 2.5)), 4), round(float(np.percentile(diffs, 97.5)), 4)]
spec = "spec: topic x distance x brokerage gain"
R["share_of_top10_that_are_friends_of_friends"] = {m: round(float(np.mean(v)), 3) for m, v in fof_share.items()}
R["ci95_spec_minus_topic_far"] = boot(hits_far[spec], hits_far["topic only"])
R["ci95_spec_minus_topicxdist_far"] = boot(hits_far[spec], hits_far["topic x distance"])
R["ci95_warmintro_minus_topic_far_only"] = boot(hits_far["proposed: topic x warm-intro paths (d=3)"], hits_far["topic, far candidates only (d>=3)"])
R["ci95_spec_minus_adamicadar_all"] = boot(hits[spec], hits["Adamic-Adar (triadic closure)"])
# Burt gain is the same for every candidate at distance >= 3 (no contact of u touches v)
R["far_candidates_distinct_gain_values_per_ego"] = {
    "egos_checked": len(matched),
    "egos_with_exactly_1_distinct_gain_among_far_candidates": sum(k == 1 for _, k, _ in matched),
    "max_gain_spread_among_far_candidates": max(r for _, _, r in matched)}
R["backtest_seconds"] = round(time.time() - t, 1)
R["precision_at_10_all_new_ties"] = {m: round(float(np.mean(v)), 4) for m, v in hits.items()}
R["precision_at_10_new_ties_at_distance_ge3"] = {m: round(float(np.mean(v)), 4) for m, v in hits_far.items()}
R["egos_with_a_distance_ge3_new_tie"] = len(hits_far["random"])
tbl = {}
for (sb, db), (k, n) in sorted(rate.items()):
    tbl[f"sim{['<.05','.05-.1','.1-.2','.2-.4','>=.4'][sb]}|dist{ {2:'2',3:'3',4:'4-5',6:'6+/none'}[db]}"] = [int(k), int(n), round(k / n * 1000, 3)]
R["new_tie_rate_per_1000_by_sim_and_distance"] = tbl
g = np.array(gain_vs_dist)
from scipy.stats import spearmanr
R["spearman_gain_vs_distance_top200"] = round(spearmanr(g[:, 0], g[:, 1]).correlation, 3)
R["gain_by_distance_median"] = {int(k): round(float(np.median(g[g[:, 1] == k, 0])), 4) for k in sorted(set(g[:, 1]))}
R["far_new_ties_cross_vs_same_community"] = [far_new_cross, far_new_same]
json.dump(R, open("results_04_backtest.json", "w"), indent=1)
print(json.dumps(R, indent=1))
