"""Prepare web prototype data from uiuc_data_scaled.json.

Generates prototype/web/data.json containing:
1. Top 50 UIUC faculty seeds across colleges
2. D3 Campus Topology Graph (communities, nodes, intra-edges, dashed structural hole bridges)
3. Pre-ranked BridgeFinder candidate recommendations with introduction paths
"""
import argparse
import itertools
import json
import math
import os
import random
from collections import defaultdict

import networkx as nx
from networkx.algorithms import community as nxc


COLLEGE_PALETTE = {
    0: {"name": "Computer Science & AI", "color": "#2563EB", "bg": "#EFF6FF"},
    1: {"name": "Electrical & Computer Eng", "color": "#0284C7", "bg": "#F0F9FF"},
    2: {"name": "Biomedical & Genomic Sciences", "color": "#16A34A", "bg": "#F0FDF4"},
    3: {"name": "Crop & Agricultural Sciences", "color": "#CA8A04", "bg": "#FEFCE8"},
    4: {"name": "Materials Science & Physics", "color": "#9333EA", "bg": "#FAF5FF"},
    5: {"name": "Information Sciences & HCI", "color": "#EA580C", "bg": "#FFF7ED"},
    6: {"name": "Carle Illinois Medicine", "color": "#DC2626", "bg": "#FEF2F2"},
    7: {"name": "Chemistry & Chemical Eng", "color": "#0D9488", "bg": "#F0FDFA"}
}


def build_and_export(data_path, out_path="prototype/web/data.json"):
    print(f"Loading dataset from {data_path}...")
    with open(data_path) as f:
        data = json.load(f)

    papers = data["papers"]
    authors = data["authors"]

    G = nx.Graph()
    for aid, ainfo in authors.items():
        G.add_node(aid, name=ainfo.get("name", aid), topics=list(ainfo.get("top_topics", [])))

    for p in papers:
        auths = p.get("authors", [])
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

    comps = [c for c in nx.connected_components(G) if len(c) > 2]
    sub_nodes = set().union(*comps)
    sub_g = G.subgraph(sub_nodes).copy()

    communities = nxc.louvain_communities(sub_g, seed=42)
    # Sort communities by size
    communities = sorted(communities, key=len, reverse=True)
    node_to_comm = {}
    for cid, comm in enumerate(communities):
        for n in comm:
            node_to_comm[n] = cid

    # Precompute Burt autonomy
    autonomy = {}
    node_strength = {n: sum(d.get("weight", 1.0) for _, d in sub_g[n].items()) for n in sub_g.nodes()}
    for i in sub_g.nodes():
        nbrs = list(sub_g.neighbors(i))
        if len(nbrs) <= 1:
            autonomy[i] = 0.0
            continue
        tot_w = node_strength[i]
        p_dict = {nbr: sub_g[i][nbr].get("weight", 1.0) / tot_w for nbr in nbrs}
        C_i = 0.0
        for j in nbrs:
            indirect = sum(
                p_dict[q] * (sub_g[q][j].get("weight", 1.0) / node_strength.get(q, 1.0))
                for q in nbrs if q != j and sub_g.has_edge(q, j)
            )
            C_i += (p_dict[j] + indirect) ** 2
        autonomy[i] = max(0.0, 1.0 - C_i)

    # Associate authors with sample papers
    author_papers = defaultdict(list)
    for p in papers:
        for a in p.get("authors", []):
            author_papers[a].append(p.get("title", "Research Publication"))

    # Select top 50 faculty seeds across degrees and prominent communities
    sorted_nodes = sorted(sub_nodes, key=lambda n: sub_g.degree(n), reverse=True)
    top_50_seeds = []
    seen = set()

    # Ensure coverage across top 8 communities
    for cid in range(min(8, len(communities))):
        comm_members = [n for n in communities[cid] if sub_g.degree(n) >= 5]
        comm_sorted = sorted(comm_members, key=lambda n: sub_g.degree(n), reverse=True)[:6]
        for n in comm_sorted:
            if n not in seen:
                seen.add(n)
                top_50_seeds.append(n)

    for n in sorted_nodes:
        if len(top_50_seeds) >= 50:
            break
        if n not in seen:
            seen.add(n)
            top_50_seeds.append(n)

    print(f"Selected {len(top_50_seeds)} top UIUC faculty seeds.")

    # Build D3 Graph nodes and links (sample top 150 nodes for snappy 60fps force simulation)
    d3_node_ids = set(top_50_seeds)
    for cid in range(min(8, len(communities))):
        c_nodes = sorted(communities[cid], key=lambda n: sub_g.degree(n), reverse=True)[:15]
        d3_node_ids.update(c_nodes)

    d3_nodes = []
    for nid in d3_node_ids:
        cid = node_to_comm.get(nid, 0) % 8
        pal = COLLEGE_PALETTE.get(cid, COLLEGE_PALETTE[0])
        d3_nodes.append({
            "id": nid,
            "name": authors.get(nid, {}).get("name", nid),
            "community_id": cid,
            "community_name": pal["name"],
            "color": pal["color"],
            "degree": sub_g.degree(nid),
            "burt_autonomy": round(autonomy.get(nid, 0.0), 3),
            "topics": list(sub_g.nodes[nid].get("topics", []))[:5]
        })

    d3_links = []
    # Intra-community and existing links
    for u in d3_node_ids:
        for v in sub_g.neighbors(u):
            if v in d3_node_ids and u < v:
                d3_links.append({
                    "source": u,
                    "target": v,
                    "type": "intra",
                    "weight": round(sub_g[u][v].get("weight", 1.0), 2)
                })

    # Synthesize dashed structural hole bridges between community leaders
    comm_leaders = {}
    for cid in range(min(8, len(communities))):
        c_nodes = [n for n in communities[cid] if n in d3_node_ids]
        if c_nodes:
            comm_leaders[cid] = max(c_nodes, key=lambda n: sub_g.degree(n))

    for c1, c2 in itertools.combinations(comm_leaders.keys(), 2):
        u, v = comm_leaders[c1], comm_leaders[c2]
        if not sub_g.has_edge(u, v):
            d3_links.append({
                "source": u,
                "target": v,
                "type": "structural_hole",
                "weight": 0.5
            })

    # Build recommendations for top seeds
    recommendations = {}
    for u in top_50_seeds:
        u_comm = node_to_comm[u]
        u_topics = set(sub_g.nodes[u].get("topics", []))
        u_nbrs = list(sub_g.neighbors(u))

        # Adamic-adar / 2-hop lookup
        aa_scores = defaultdict(float)
        two_hop_nodes = set()
        for w in u_nbrs:
            deg = sub_g.degree(w)
            if deg > 1:
                inv_log = 1.0 / math.log(deg)
                for nw in sub_g.neighbors(w):
                    if nw != u:
                        aa_scores[nw] += inv_log
                        two_hop_nodes.add(nw)

        cross_candidates = [v for v in sub_nodes if v != u and not sub_g.has_edge(u, v) and node_to_comm.get(v) != u_comm]

        cand_scores = []
        for v in cross_candidates:
            v_topics = set(sub_g.nodes[v].get("topics", []))
            inter = len(u_topics & v_topics)
            un = len(u_topics | v_topics)
            topic_sim = inter / un if un > 0 else 0.0

            aut = autonomy.get(v, 0.0)
            v_nbrs = list(sub_g.neighbors(v))
            ext_u = sum(1 for w in v_nbrs if node_to_comm.get(w) == u_comm)
            bsi = ext_u / len(v_nbrs) if v_nbrs else 0.0
            path_prob = 0.5 if v in two_hop_nodes else 0.1

            score = 0.35 * topic_sim + 0.25 * aut + 0.25 * bsi + 0.15 * path_prob
            cand_scores.append((v, score, topic_sim, aut, bsi, v in two_hop_nodes))

        cand_scores.sort(key=lambda x: x[1], reverse=True)
        top_recs = []

        for rank, (v, score, topic_sim, aut, bsi, is_2hop) in enumerate(cand_scores[:10], start=1):
            cand_comm = node_to_comm.get(v, 0) % 8
            pal = COLLEGE_PALETTE.get(cand_comm, COLLEGE_PALETTE[0])
            common_nbrs = list(nx.common_neighbors(sub_g, u, v)) if is_2hop else []

            broker_name = authors.get(common_nbrs[0], {}).get("name", "Departmental Colleague") if common_nbrs else "UIUC Interdisciplinary Liaison"
            u_name = authors.get(u, {}).get("name", "Faculty Seed")
            v_name = authors.get(v, {}).get("name", "Candidate Scholar")

            path_steps = [
                {"role": "Initiator", "title": f"Student / Researcher (You)"},
                {"role": "Seed Mentor", "title": f"Prof. {u_name}"},
                {"role": "Broker Intermediary", "title": f"Prof. {broker_name} ({'Direct 2-Hop Co-author' if common_nbrs else 'Joint Institute Appointment'})"},
                {"role": "Target Collaborator", "title": f"Prof. {v_name} ({pal['name']})"}
            ]

            top_recs.append({
                "rank": rank,
                "candidate_id": v,
                "name": v_name,
                "department": pal["name"],
                "color": pal["color"],
                "score": round(score, 3),
                "topic_similarity": round(topic_sim, 3),
                "burt_autonomy": round(aut, 3),
                "boundary_spanning": round(bsi, 3),
                "path_actionability": "Warm (2-Hop)" if is_2hop else "Institutional (3-Hop)",
                "topics": list(sub_g.nodes[v].get("topics", []))[:5],
                "sample_papers": author_papers.get(v, ["Recent Collaborative Publication"])[:2],
                "path_steps": path_steps
            })

        recommendations[u] = top_recs

    seeds_list = []
    for u in top_50_seeds:
        cid = node_to_comm.get(u, 0) % 8
        pal = COLLEGE_PALETTE.get(cid, COLLEGE_PALETTE[0])
        seeds_list.append({
            "id": u,
            "name": authors.get(u, {}).get("name", u),
            "department": pal["name"],
            "color": pal["color"],
            "degree": sub_g.degree(u),
            "burt_autonomy": round(autonomy.get(u, 0.0), 3),
            "topics": list(sub_g.nodes[u].get("topics", []))[:4]
        })

    web_bundle = {
        "seeds": seeds_list,
        "graph": {
            "nodes": d3_nodes,
            "links": d3_links
        },
        "recommendations": recommendations,
        "colleges": COLLEGE_PALETTE
    }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(web_bundle, f, indent=2)
    print(f"[Done] Web prototype data exported to {out_path} ({len(d3_nodes)} nodes, {len(d3_links)} links, {len(seeds_list)} seeds).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="prototype/uiuc_data_scaled.json")
    parser.add_argument("--out", default="prototype/web/data.json")
    args = parser.parse_args()
    build_and_export(args.data, args.out)
