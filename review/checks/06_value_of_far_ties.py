"""Check 6 (proposed replacement claim): do NEW 2020-24 ties that cross a 2015-19 hole
(distance >= 3 or cross-community) yield more-cited joint papers than new ties to friends-of-friends?
Citations are normalised by the mean of UIUC research works with the same primary field and year."""
import collections, itertools, json, statistics
import numpy as np, networkx as nx
from networkx.algorithms.community import louvain_communities
from common import load_works, build_graph, RESEARCH_TYPES, MAX_AUTHORS

works = list(load_works())
GA, _, npA = build_graph(works, (2015, 2019))
_, _, npB = build_graph(works, (2020, 2024))
cohort = {a for a in GA if npA[a] >= 2 and npB.get(a, 0) >= 1}
cid = {a: i for i, c in enumerate(louvain_communities(GA, weight="weight", seed=1)) for a in c}
norm = collections.defaultdict(list)
for w in works:
    if w["t"] in RESEARCH_TYPES and 2020 <= w["y"] <= 2024:
        norm[(w["f"], w["y"])].append(w["c"])
norm = {k: statistics.mean(v) or 1 for k, v in norm.items()}
pair_cites = collections.defaultdict(list)
for w in works:
    if w["t"] not in RESEARCH_TYPES or not (2020 <= w["y"] <= 2024) or len(w["a"]) > MAX_AUTHORS:
        continue
    ids = sorted({a[0] for a in w["a"] if a[0] and a[2] and a[0] in cohort})
    for u, v in itertools.combinations(ids, 2):
        pair_cites[(u, v)].append(w["c"] / norm[(w["f"], w["y"])])
groups = collections.defaultdict(list)
for (u, v), cs in pair_cites.items():
    val = statistics.mean(cs)
    if GA.has_edge(u, v):
        groups["persisting tie"].append(val); continue
    try:
        d = nx.shortest_path_length(GA, u, v)
    except nx.NetworkXNoPath:
        d = 99
    key = "new, distance 2 (friend of friend)" if d == 2 else "new, distance >=3"
    groups[key].append(val)
    if d >= 3:
        groups["new, distance >=3, cross-community" if cid[u] != cid[v] else "new, distance >=3, same community"].append(val)
R = {k: {"pairs": len(v), "mean_norm_cites": round(statistics.mean(v), 2), "median_norm_cites": round(statistics.median(v), 2)}
     for k, v in sorted(groups.items())}
from scipy.stats import mannwhitneyu
R["mannwhitney_far_vs_fof_p"] = float(f"{mannwhitneyu(groups['new, distance >=3'], groups['new, distance 2 (friend of friend)']).pvalue:.3g}")
json.dump(R, open("results_06_value.json", "w"), indent=1)
print(json.dumps(R, indent=1))
