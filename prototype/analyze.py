"""MethodBridge pilot analysis: communities, structural holes, HITS, baselines.

Input: the JSON written by fetch.py (a time-frozen citer->cited graph around the
seed papers). Output: a printed report plus results JSON.

Pipeline
  1. Co-citation graph over cited works (seeds + candidates). Two works are linked
     when the same paper cites both; each citer adds 1/(k-1) per pair, where k is
     the number of works it cites, so long reviews don't dominate.
  2. Communities (L10): Louvain modularity. Greedy modularity (CNM) and
     Girvan-Newman (edge betweenness) are run as the in-class alternatives.
  3. Home field = communities that contain a seed paper.
  4. Structural hole (L1): hole(m) = 1 - share of m's co-citation weight that
     lands in the home field. A high hole score means few ties into your field.
  5. Authority (L6): HITS on citer->cited edges *within each community*, so a
     method's authority is measured among the people who actually use it.
  6. MethodBridge score = within-community authority x hole, for works outside
     the home field.
  Baselines: co-citation with the seeds (triadic closure, as in Connected Papers),
  in-degree (citation count before the freeze), and global HITS.
"""
import json
import sys
import time
from collections import Counter, defaultdict

import networkx as nx
from networkx.algorithms import community as nxc


def load(path):
    g = json.load(open(path))
    cited = list(dict.fromkeys(g["seeds"] + g["candidates"]))
    citer_lists = {d: set(g["citers"].get(d) or []) for d in cited}
    return g, cited, citer_lists


def cocitation_graph(cited, citer_lists):
    by_citer = defaultdict(list)
    for d in cited:
        for c in citer_lists[d]:
            by_citer[c].append(d)
    G = nx.Graph()
    G.add_nodes_from(cited)
    for c, ds in by_citer.items():
        k = len(ds)
        if k < 2:
            continue
        w = 1.0 / (k - 1)
        for i in range(k):
            for j in range(i + 1, k):
                a, b = ds[i], ds[j]
                if G.has_edge(a, b):
                    G[a][b]["weight"] += w
                else:
                    G.add_edge(a, b, weight=w)
    G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
    return G, by_citer


def girvan_newman_best(G, max_nodes=150, budget_s=120):
    """Girvan-Newman on the max_nodes highest-strength nodes; best-modularity level."""
    top = sorted(G.nodes, key=lambda n: -G.degree(n, weight="weight"))[:max_nodes]
    H = G.subgraph(top).copy()
    t0, best, best_q, levels = time.time(), None, -1, 0
    for part in nxc.girvan_newman(H):
        levels += 1
        q = nxc.modularity(H, part, weight="weight")
        if q > best_q:
            best, best_q = part, q
        if time.time() - t0 > budget_s or len(part) >= 25:
            break
    lv = nxc.louvain_communities(H, weight="weight", seed=0)
    return {
        "subgraph_nodes": H.number_of_nodes(),
        "subgraph_edges": H.number_of_edges(),
        "gn_seconds": round(time.time() - t0, 1),
        "gn_levels_explored": levels,
        "gn_best_modularity": round(best_q, 3),
        "gn_best_k": len(best) if best else None,
        "louvain_modularity_same_subgraph": round(nxc.modularity(H, lv, weight="weight"), 3),
        "louvain_k_same_subgraph": len(lv),
    }


def hits_within(comm_nodes, citer_lists):
    D = nx.DiGraph()
    for d in comm_nodes:
        for c in citer_lists[d]:
            D.add_edge("c:" + c, d)
    if D.number_of_edges() == 0:
        return {}, {}
    hubs, auths = nx.hits(D, max_iter=500, normalized=True)
    auths = {n: a for n, a in auths.items() if not n.startswith("c:")}
    hubs = {n[2:]: h for n, h in hubs.items() if n.startswith("c:")}
    m = max(auths.values()) or 1.0
    return {n: a / m for n, a in auths.items()}, hubs


def rank_of(order, item):
    try:
        return order.index(item) + 1
    except ValueError:
        return None


def main(graph_path, out_path):
    g, cited, citer_lists = load(graph_path)
    seeds, targets, meta = set(g["seeds"]), g["targets"], g["meta"]
    G, by_citer = cocitation_graph(cited, citer_lists)
    print(f"case: {g['case']}  (frozen at {g['freeze_year']})")
    print(f"co-citation graph: {G.number_of_nodes()} works, {G.number_of_edges()} edges, "
          f"{len(by_citer)} citing papers")

    t0 = time.time()
    louvain = nxc.louvain_communities(G, weight="weight", seed=0)
    t_lv = time.time() - t0
    q_lv = nxc.modularity(G, louvain, weight="weight")
    t0 = time.time()
    cnm = nxc.greedy_modularity_communities(G, weight="weight")
    t_cnm = time.time() - t0
    q_cnm = nxc.modularity(G, cnm, weight="weight")
    gn = girvan_newman_best(G)
    print(f"Louvain: k={len(louvain)} Q={q_lv:.3f} ({t_lv:.1f}s) | CNM: k={len(cnm)} Q={q_cnm:.3f} ({t_cnm:.1f}s)")
    print(f"Girvan-Newman on top-{gn['subgraph_nodes']} subgraph: Q={gn['gn_best_modularity']} "
          f"in {gn['gn_seconds']}s vs Louvain Q={gn['louvain_modularity_same_subgraph']} on the same subgraph")

    comm_of = {n: i for i, c in enumerate(louvain) for n in c}
    home = {comm_of[s] for s in seeds if s in comm_of}

    def label(i, k=3):
        venues = Counter((meta.get(n) or {}).get("venue") or "?" for n in louvain[i])
        return "; ".join(v for v, _ in venues.most_common(k))

    strength = dict(G.degree(weight="weight"))
    hole = {}
    for n in G:
        to_home = sum(d["weight"] for _, nb, d in G.edges(n, data=True) if comm_of[nb] in home)
        hole[n] = 1 - to_home / strength[n] if strength[n] else 0.0

    auth_within, hubs_within = {}, {}
    for i, c in enumerate(louvain):
        a, h = hits_within(c, citer_lists)
        auth_within.update(a)
        hubs_within[i] = h

    gD = nx.DiGraph()
    for d in G:
        for c in citer_lists[d]:
            gD.add_edge("c:" + c, d)
    _, gauth = nx.hits(gD, max_iter=500)

    seed_citers = set().union(*(citer_lists[s] for s in seeds if s in citer_lists))
    cands = [n for n in G if n not in seeds]
    min_size = 5
    scores = {
        "MethodBridge (hole x within-community HITS)": {
            n: (auth_within.get(n, 0) * hole[n]
                if comm_of[n] not in home and len(louvain[comm_of[n]]) >= min_size else 0.0)
            for n in cands},
        "Co-citation with seeds (triadic closure)": {n: len(citer_lists[n] & seed_citers) for n in cands},
        "In-degree (citations before freeze)": {n: len(citer_lists[n]) for n in cands},
        "Global HITS authority": {n: gauth.get(n, 0) for n in cands},
    }
    orders = {k: sorted(cands, key=lambda n: -v[n]) for k, v in scores.items()}

    print(f"\nhome field = communities {sorted(home)}: "
          + " | ".join(f"#{i} ({len(louvain[i])} works: {label(i, 2)})" for i in sorted(home)))
    print("\ntarget ranks among", len(cands), "candidates (lower is better; None = not reached by the walk)")
    target_rows = []
    for t, name in targets.items():
        row = {"target": name, "doi": t, "in_graph": t in G,
               "community": comm_of.get(t), "hole": round(hole.get(t, 0), 3) if t in G else None}
        for k, o in orders.items():
            row[k] = rank_of(o, t)
        target_rows.append(row)
        print(f"  {name[:60]:<60} in_graph={t in G}  community={comm_of.get(t)}  "
              + "  ".join(f"{k.split(' (')[0]}={row[k]}" for k in orders))

    def title(n):
        m = meta.get(n) or {}
        return f"{m.get('year', '?')} {(m.get('title') or n)[:70]} [{(m.get('venue') or '')[:28]}]"

    tops = {}
    for k, o in orders.items():
        print(f"\nTop 10 — {k}")
        tops[k] = []
        for n in o[:10]:
            tag = "  <== TARGET" if n in targets else ""
            print(f"  c{comm_of.get(n)}  hole={hole.get(n, 0):.2f}  {title(n)}{tag}")
            tops[k].append({"doi": n, "community": comm_of.get(n), "hole": round(hole.get(n, 0), 3),
                            "title": (meta.get(n) or {}).get("title"), "year": (meta.get(n) or {}).get("year"),
                            "venue": (meta.get(n) or {}).get("venue"), "is_target": n in targets})

    print("\nCommunities across the hole (size >= 5, ranked by best MethodBridge score)")
    comm_rows = []
    for i, c in enumerate(louvain):
        if i in home or len(c) < min_size:
            continue
        best = max(c, key=lambda n: scores["MethodBridge (hole x within-community HITS)"].get(n, 0))
        comm_rows.append((scores["MethodBridge (hole x within-community HITS)"].get(best, 0), i, best))
    comm_rows.sort(reverse=True)
    comm_out = []
    for s, i, best in comm_rows[:8]:
        h = sorted(hubs_within[i].items(), key=lambda kv: -kv[1])[:1]
        print(f"  #{i:<3} n={len(louvain[i]):<4} {label(i)[:70]}")
        print(f"        top authority: {title(best)}")
        comm_out.append({"community": i, "size": len(louvain[i]), "venues": label(i),
                         "top_authority": best, "top_authority_title": (meta.get(best) or {}).get("title"),
                         "top_hub": h[0][0] if h else None})

    out = {"case": g["case"], "freeze_year": g["freeze_year"],
           "graph": {"works": G.number_of_nodes(), "edges": G.number_of_edges(), "citers": len(by_citer)},
           "communities": {"louvain_k": len(louvain), "louvain_Q": round(q_lv, 3), "louvain_s": round(t_lv, 2),
                           "cnm_k": len(cnm), "cnm_Q": round(q_cnm, 3), "cnm_s": round(t_cnm, 2), "girvan_newman": gn},
           "home_communities": sorted(home), "targets": target_rows, "top10": tops,
           "communities_across_hole": comm_out}
    json.dump(out, open(out_path, "w"), indent=1)
    print("\nwrote", out_path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
