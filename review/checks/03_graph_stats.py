"""Check 3: campus co-authorship graph 2015-2024: size, density, components, degrees,
hyperauthorship, disambiguation red flags, Louvain communities, Burt constraint / effective size."""
import collections, json, math, random, statistics, time
import networkx as nx
from networkx.algorithms.community import louvain_communities, modularity
from common import load_works, build_graph, RESEARCH_TYPES

random.seed(0)
works = list(load_works())
R = {}
R["works_total"] = len(works)
rw = [w for w in works if w["t"] in RESEARCH_TYPES]
R["works_research_types"] = len(rw)

# --- hyperauthorship ---
na = [len(w["a"]) for w in rw]
R["authors_per_work"] = {"median": statistics.median(na), "p90": sorted(na)[int(.9 * len(na))],
                         "p99": sorted(na)[int(.99 * len(na))], "max": max(na)}
R["share_works_gt25_authors"] = round(sum(n > 25 for n in na) / len(na), 4)
R["share_works_gt100_authors"] = round(sum(n > 100 for n in na) / len(na), 4)
R["works_authors_truncated_flag"] = sum(w["tr"] for w in rw)
# pairs a >25-author paper would add if kept
R["pairs_from_gt25_if_kept"] = sum(n * (n - 1) // 2 for n in na if n > 25)
R["pairs_from_le25"] = sum(n * (n - 1) // 2 for n in na if n <= 25)
# UIUC author-slots on >25-author papers
slots = [(len(w["a"]) > 25, sum(a[2] for a in w["a"])) for w in rw]
R["share_uiuc_author_slots_on_gt25"] = round(sum(s for big, s in slots if big) / sum(s for _, s in slots), 4)

# --- disambiguation / metadata red flags ---
all_slots = [a for w in rw for a in w["a"]]
uiuc_slots = [a for a in all_slots if a[2]]
R["authorships_total"] = len(all_slots)
R["authorships_null_author_id"] = sum(a[0] is None for a in all_slots)
R["authorships_no_institution"] = sum(a[4] for a in all_slots)
R["uiuc_authorships"] = len(uiuc_slots)
R["uiuc_authorships_null_author_id"] = sum(a[0] is None for a in uiuc_slots)
R["works_without_any_uiuc_flagged_author"] = sum(not any(a[2] for a in w["a"]) for w in rw)
# ORCIDs mapped to >1 author ID (split profiles) and IDs with >1 ORCID (merged profiles)
orc2ids, id2orcs, name2ids = collections.defaultdict(set), collections.defaultdict(set), collections.defaultdict(set)
for a in uiuc_slots:
    if a[0] and a[3]:
        orc2ids[a[3]].add(a[0]); id2orcs[a[0]].add(a[3])
    if a[0]:
        name2ids[a[1].lower()].add(a[0])
R["uiuc_orcids"] = len(orc2ids)
R["uiuc_orcids_split_over_multiple_ids"] = sum(len(s) > 1 for s in orc2ids.values())
R["uiuc_ids_with_multiple_orcids"] = sum(len(s) > 1 for s in id2orcs.values())
R["uiuc_names_with_multiple_ids"] = sum(len(s) > 1 for s in name2ids.values())
R["uiuc_distinct_names"] = len(name2ids)
R["examples_name_multi_id"] = sorted(((n, len(s)) for n, s in name2ids.items() if len(s) > 1), key=lambda x: -x[1])[:8]
R["topics_missing_research_works"] = sum(not w["tp"] for w in rw)

# --- graph ---
t = time.time()
G, topics, npapers = build_graph(works, (2015, 2024))
R["build_seconds"] = round(time.time() - t, 1)
n, m = G.number_of_nodes(), G.number_of_edges()
comps = sorted(nx.connected_components(G), key=len, reverse=True)
deg = sorted((d for _, d in G.degree()), reverse=True)
R["graph"] = {"nodes": n, "edges": m, "density": f"{nx.density(G):.2e}", "components": len(comps),
              "isolates": nx.number_of_isolates(G), "giant_nodes": len(comps[0]),
              "giant_share": round(len(comps[0]) / n, 3), "second_component": len(comps[1]),
              "deg_mean": round(2 * m / n, 2), "deg_median": statistics.median(deg),
              "deg_p90": deg[int(.1 * n)], "deg_p99": deg[int(.01 * n)], "deg_max": deg[0],
              "authors_with_1_paper": sum(c == 1 for c in npapers.values()),
              "authors_with_ge5_papers": sum(c >= 5 for c in npapers.values())}
hist = collections.Counter(min(d, 50) for d in deg)
R["degree_hist_capped50"] = dict(sorted(hist.items()))
GC = G.subgraph(comps[0]).copy()
R["giant_avg_clustering_sample"] = round(nx.average_clustering(GC, nodes=random.sample(list(GC), 2000)), 3)

# core: authors with >=3 UIUC papers (the "researchers" a user would be shown)
core = [a for a, c in npapers.items() if c >= 3]
H = G.subgraph(core).copy()
Hc = H.subgraph(max(nx.connected_components(H), key=len)).copy()
R["core_ge3_papers"] = {"nodes": H.number_of_nodes(), "edges": H.number_of_edges(),
                        "giant_nodes": Hc.number_of_nodes()}

# --- Louvain on the core giant component ---
sub = json.load(open("data/subfields.json"))
t = time.time()
comms = louvain_communities(Hc, weight="weight", seed=1, resolution=1.0)
R["louvain_seconds"] = round(time.time() - t, 1)
R["louvain_Q"] = round(modularity(Hc, comms, weight="weight"), 3)
sizes = sorted((len(c) for c in comms), reverse=True)
R["louvain_k"] = len(comms)
R["louvain_sizes_top10"] = sizes[:10]
R["louvain_k_ge20"] = sum(s >= 20 for s in sizes)
# Meaningfulness: dominant subfield per author; community purity and NMI
author_sf = {}
sfc = collections.defaultdict(collections.Counter)
for w in works:
    if w["t"] in RESEARCH_TYPES and w["sf"]:
        for a in w["a"]:
            if a[0] and a[2]:
                sfc[a[0]][w["sf"]] += 1
for a in Hc:
    if sfc[a]:
        author_sf[a] = sfc[a].most_common(1)[0][0]
labels_c, labels_s = [], []
desc = []
for i, c in enumerate(sorted(comms, key=len, reverse=True)):
    cnt = collections.Counter(author_sf[a] for a in c if a in author_sf)
    for a in c:
        if a in author_sf:
            labels_c.append(i); labels_s.append(author_sf[a])
    if i < 12:
        top = cnt.most_common(3)
        tot = sum(cnt.values())
        desc.append({"size": len(c), "top_subfields": [(sub.get(s, s), round(k / tot, 2)) for s, k in top]})
R["louvain_top12"] = desc
try:
    from sklearn.metrics import normalized_mutual_info_score as nmi
    R["nmi_community_vs_subfield"] = round(nmi(labels_c, labels_s), 3)
    shuf = labels_c[:]; random.shuffle(shuf)
    R["nmi_shuffled_baseline"] = round(nmi(shuf, labels_s), 3)
except ImportError:
    pass
big = [c for c in comms if len(c) >= 20]
pur = [collections.Counter(author_sf[a] for a in c if a in author_sf).most_common(1)[0][1] /
       max(1, sum(1 for a in c if a in author_sf)) for c in big]
R["median_purity_comms_ge20"] = round(statistics.median(pur), 2)
R["n_distinct_subfields_in_core"] = len(set(labels_s))

# --- Burt constraint / effective size ---
sample = random.sample(list(Hc), 500)
t = time.time(); C = nx.constraint(Hc, nodes=sample, weight="weight"); tc = time.time() - t
t = time.time(); E = nx.effective_size(Hc, nodes=sample, weight="weight"); te = time.time() - t
R["constraint_500_nodes_seconds"] = round(tc, 2)
R["effective_size_500_nodes_seconds"] = round(te, 2)
R["est_constraint_all_core_minutes"] = round(tc / 500 * Hc.number_of_nodes() / 60, 1)
cs = [C[a] for a in sample if not math.isnan(C[a])]
R["constraint_summary"] = {"median": round(statistics.median(cs), 3), "min": round(min(cs), 3), "max": round(max(cs), 3)}
from scipy.stats import spearmanr
d = [Hc.degree(a) for a in sample]
R["spearman_constraint_vs_degree"] = round(spearmanr([C[a] for a in sample], d).correlation, 3)
R["spearman_effsize_vs_degree"] = round(spearmanr([E[a] for a in sample], d).correlation, 3)
# constraint vs number of distinct communities in ego network (does it capture brokerage beyond degree?)
cid = {a: i for i, c in enumerate(comms) for a in c}
ncom = [len({cid[b] for b in Hc[a]}) for a in sample]
R["spearman_constraint_vs_n_neighbor_communities"] = round(spearmanr([C[a] for a in sample], ncom).correlation, 3)
# partial: within degree band 5-15
band = [a for a in sample if 5 <= Hc.degree(a) <= 15]
R["degree5to15_n"] = len(band)
R["degree5to15_spearman_constraint_vs_ncomm"] = round(spearmanr([C[a] for a in band], [len({cid[b] for b in Hc[a]}) for a in band]).correlation, 3)
json.dump(R, open("results_03_graph.json", "w"), indent=1)
import pickle; pickle.dump({"comms": comms}, open("data/louvain.pkl", "wb"))
print(json.dumps(R, indent=1))
