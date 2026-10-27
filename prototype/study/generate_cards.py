"""Double-Blind User Study Card Generator.

Selects 5 representative UIUC seed profiles across CS, ECE, Bioengineering,
Crop Sciences, and Information Sciences. For each seed, generates 15 candidate cards
(5 BridgeFinder, 5 Triadic Closure, 5 Topic-Only). Shuffles and strips model tags.

Usage:
    python3 prototype/study/generate_cards.py --data prototype/uiuc_data_scaled.json --out prototype/study/study_cards.json
"""
import argparse
import json
import math
import os
import random
from collections import defaultdict

import networkx as nx
from networkx.algorithms import community as nxc


DEPT_KEYWORDS = {
    "Computer Science": ["Computer Science", "Artificial Intelligence", "Machine Learning", "Algorithms", "Natural Language Processing"],
    "Electrical & Computer Engineering": ["Electrical Engineering", "Signal Processing", "Optics", "Electronic Engineering", "Semiconductor"],
    "Bioengineering": ["Bioengineering", "Biomedical Engineering", "Biophysics", "Nanotechnology", "Cell Biology"],
    "Crop Sciences": ["Agronomy", "Crop", "Genetics", "Plant Science", "Botany", "Agriculture"],
    "Information Sciences": ["Information Science", "Human-Computer Interaction", "Data Science", "Sociology", "Library and Information Science"]
}


def build_graph(data, split_year=2019):
    papers = data["papers"]
    authors = data["authors"]

    G = nx.Graph()
    for aid, ainfo in authors.items():
        G.add_node(aid, name=ainfo.get("name", aid), topics=set(ainfo.get("top_topics", [])))

    for p in papers:
        if p["year"] <= split_year:
            auths = p["authors"]
            n = len(auths)
            if n < 2:
                continue
            w = 1.0 / (n - 1.0)
            for i in range(n):
                for j in range(i + 1, n):
                    u, v = auths[i], auths[j]
                    if G.has_edge(u, v):
                        G[u][v]["weight"] += w
                    else:
                        G.add_edge(u, v, weight=w)
    return G, authors, papers


def select_seed_profiles(G, authors, papers):
    """Find one high-degree representative faculty per target discipline."""
    selected_seeds = {}
    author_papers = defaultdict(list)
    for p in papers:
        for aid in p["authors"]:
            author_papers[aid].append(p)

    # Sort authors by degree in G
    sorted_nodes = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)

    used_nodes = set()
    for dept, kw_list in DEPT_KEYWORDS.items():
        for n in sorted_nodes:
            if n in used_nodes or G.degree(n) < 5:
                continue
            author_topics = G.nodes[n]["topics"]
            if any(any(kw.lower() in t.lower() for kw in kw_list) for t in author_topics):
                selected_seeds[dept] = {
                    "id": n,
                    "name": authors[n]["name"],
                    "department": dept,
                    "topics": list(author_topics)[:6],
                    "degree": G.degree(n)
                }
                used_nodes.add(n)
                break

    # Fallback if any dept wasn't found
    for dept in DEPT_KEYWORDS:
        if dept not in selected_seeds:
            for n in sorted_nodes:
                if n not in used_nodes and G.degree(n) >= 3:
                    selected_seeds[dept] = {
                        "id": n,
                        "name": authors[n]["name"],
                        "department": dept,
                        "topics": list(G.nodes[n]["topics"])[:6],
                        "degree": G.degree(n)
                    }
                    used_nodes.add(n)
                    break

    return selected_seeds


def compute_burt_autonomy(G):
    autonomy = {}
    node_strength = {n: sum(d.get("weight", 1.0) for _, d in G[n].items()) for n in G.nodes()}
    for i in G.nodes():
        nbrs = list(G.neighbors(i))
        if len(nbrs) <= 1:
            autonomy[i] = 0.0
            continue
        tot_w = node_strength[i]
        p = {nbr: G[i][nbr].get("weight", 1.0) / tot_w for nbr in nbrs}
        C_i = 0.0
        for j in nbrs:
            indirect = sum(
                p[q] * (G[q][j].get("weight", 1.0) / node_strength.get(q, 1.0))
                for q in nbrs if q != j and G.has_edge(q, j)
            )
            C_i += (p[j] + indirect) ** 2
        autonomy[i] = max(0.0, 1.0 - C_i)
    return autonomy


def generate_study_cards(G, authors, papers, seeds):
    comps = [c for c in nx.connected_components(G) if len(c) > 1]
    sub_nodes = set().union(*comps)
    sub_g = G.subgraph(sub_nodes).copy()

    communities = nxc.louvain_communities(sub_g, seed=42)
    node_to_comm = {n: cid for cid, comm in enumerate(communities) for n in comm}
    burt_autonomy = compute_burt_autonomy(sub_g)

    author_papers = defaultdict(list)
    for p in papers:
        for a in p["authors"]:
            author_papers[a].append(p["title"])

    all_cards = []
    truth_keys = {}

    card_counter = 1

    for dept, sinfo in seeds.items():
        u = sinfo["id"]
        if u not in sub_nodes:
            continue

        u_comm = node_to_comm[u]
        u_topics = sub_g.nodes[u]["topics"]
        u_nbrs = list(sub_g.neighbors(u))

        candidates = [v for v in sub_nodes if v != u and not sub_g.has_edge(u, v)]

        # 1. Triadic Closure (Adamic-Adar)
        aa_scores = defaultdict(float)
        two_hop_nodes = set()
        for w in u_nbrs:
            deg = sub_g.degree(w)
            if deg > 1:
                inv_log = 1.0 / math.log(deg)
                for nbr_w in sub_g.neighbors(w):
                    if nbr_w != u:
                        aa_scores[nbr_w] += inv_log
                        two_hop_nodes.add(nbr_w)

        # 2. Topic-Only
        topic_scores = {}
        for v in candidates:
            v_topics = sub_g.nodes[v]["topics"]
            inter = len(u_topics & v_topics)
            un = len(u_topics | v_topics)
            topic_scores[v] = inter / un if un > 0 else 0.0

        # 3. BridgeFinder (Cross-Community + Topic + Autonomy + BSI + Path)
        bf_scores = {}
        cross_candidates = [v for v in candidates if node_to_comm[v] != u_comm]
        for v in cross_candidates:
            topic_sim = topic_scores.get(v, 0.0)
            aut = burt_autonomy.get(v, 0.0)
            v_nbrs = list(sub_g.neighbors(v))
            ext_u = sum(1 for w in v_nbrs if node_to_comm.get(w) == u_comm)
            bsi = ext_u / len(v_nbrs) if v_nbrs else 0.0
            path_prob = 0.5 if v in two_hop_nodes else 0.1
            bf_scores[v] = 0.35 * topic_sim + 0.25 * aut + 0.25 * bsi + 0.15 * path_prob

        # Select top 5 for each
        top_aa = sorted([v for v in candidates if aa_scores[v] > 0], key=lambda v: aa_scores[v], reverse=True)[:5]
        top_topic = sorted(candidates, key=lambda v: topic_scores[v], reverse=True)[:5]
        top_bf = sorted(cross_candidates, key=lambda v: bf_scores[v], reverse=True)[:5]

        seed_card_pool = []
        for v in top_bf:
            seed_card_pool.append((v, "BridgeFinder"))
        for v in top_aa:
            seed_card_pool.append((v, "Triadic Closure"))
        for v in top_topic:
            seed_card_pool.append((v, "Topic-Only"))

        # Deduplicate candidates within seed while preserving model attribution
        seen_cand = set()
        seed_final_items = []
        for v, model_name in seed_card_pool:
            if v not in seen_cand:
                seen_cand.add(v)
                seed_final_items.append((v, model_name))

        # Shuffle order for double-blind evaluation
        random.seed(42 + card_counter)
        random.shuffle(seed_final_items)

        for v, model_name in seed_final_items:
            card_id = f"CARD_{card_counter:03d}"
            cand_name = authors.get(v, {}).get("name", "UIUC Faculty Researcher")
            cand_topics = list(sub_g.nodes[v]["topics"])[:5]
            cand_papers = author_papers.get(v, ["Recent Collaborative Publication"])[:2]

            # Synthesize introduction path
            common_nbrs = list(nx.common_neighbors(sub_g, u, v)) if sub_g.has_node(u) and sub_g.has_node(v) else []
            if common_nbrs:
                broker = authors.get(common_nbrs[0], {}).get("name", "Colleague")
                path_desc = f"{sinfo['name']} → Prof. {broker} → {cand_name} (Warm 2-Hop Path)"
            else:
                path_desc = f"{sinfo['name']} → UIUC Interdisciplinary Institute / Departmental Liaison → {cand_name} (Cold Institutional Path)"

            all_cards.append({
                "card_id": card_id,
                "seed_id": u,
                "seed_name": sinfo["name"],
                "seed_department": sinfo["department"],
                "seed_topics": sinfo["topics"][:4],
                "candidate_name": cand_name,
                "candidate_topics": cand_topics,
                "sample_papers": cand_papers,
                "introduction_path": path_desc
            })

            truth_keys[card_id] = {
                "model": model_name,
                "candidate_id": v,
                "seed_id": u,
                "seed_dept": sinfo["department"]
            }
            card_counter += 1

    return all_cards, truth_keys


def main():
    parser = argparse.ArgumentParser(description="Generate double-blind study cards")
    parser.add_argument("--data", default="prototype/uiuc_data_scaled.json")
    parser.add_argument("--out", default="prototype/study/study_cards.json")
    parser.add_argument("--keys", default="prototype/study/truth_keys.json")
    args = parser.parse_args()

    data_file = args.data if os.path.exists(args.data) else "prototype/uiuc_data.json"
    print(f"Loading data from {data_file}...")
    with open(data_file) as f:
        data = json.load(f)

    G, authors, papers = build_graph(data)
    seeds = select_seed_profiles(G, authors, papers)
    print(f"Selected {len(seeds)} representative seeds across disciplines:")
    for dept, s in seeds.items():
        print(f"  [{dept}] {s['name']} (Degree: {s['degree']}, Topics: {', '.join(s['topics'][:3])})")

    cards, truth_keys = generate_study_cards(G, authors, papers, seeds)
    print(f"Generated {len(cards)} anonymized evaluation cards across {len(seeds)} seed disciplines.")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(cards, f, indent=2)

    with open(args.keys, "w") as f:
        json.dump(truth_keys, f, indent=2)

    print(f"[Done] Cards saved to {args.out}")
    print(f"[Done] Secret model truth keys saved to {args.keys}")


if __name__ == "__main__":
    main()
