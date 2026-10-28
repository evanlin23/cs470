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
from collections import Counter, defaultdict

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

# Keyword rules mapping OpenAlex topic display names to the 8 UIUC college buckets
COLLEGE_KEYWORDS = {
    0: [
        "computer vision", "natural language processing", "machine learning",
        "artificial intelligence", "deep learning", "software", "distributed computing",
        "programming", "compiler", "database", "cryptography", "computer graphics",
        "robotics", "algorithms", "neural network", "reinforcement learning",
        "high-performance computing", "cloud computing", "cybersecurity"
    ],
    1: [
        "electrical", "semiconductor", "cmos", "vlsi", "signal processing",
        "wireless", "antenna", "photonics", "power electronics", "microelectronics",
        "integrated circuit", "radar", "telecommunications", "control systems",
        "electromagnetic", "5g", "mimo", "fpga", "embedded systems", "smart grid"
    ],
    2: [
        "genomic", "dna ", "epigenetics", "rna", "crispr", "gene expression",
        "cell biology", "molecular biology", "protein", "microbiome",
        "gut microbiota", "probiotics", "immunology", "virology", "neuroscience",
        "bioinformatics", "biophysics", "biomarker", "metabolic", "enzyme"
    ],
    3: [
        "crop", "agronomy", "plant ", "photosynthesis", "soil", "soybean", "maize",
        "corn", "wheat", "horticulture", "livestock", "animal nutrition", "poultry",
        "swine", "cattle", "veterinary", "food biotechnology", "agricultural",
        "weed", "pest", "irrigation", "forestry", "aquaculture"
    ],
    4: [
        "materials science", "condensed matter", "superconduct", "quantum",
        "graphene", "nanomaterials", "thin film", "crystallography", "alloy",
        "mechanics of materials", "metamaterials", "plasmonics", "astrophysics",
        "cosmology", "particle physics", "optics", "laser", "fluid dynamics",
        "thermodynamics", "fracture", "composite"
    ],
    5: [
        "human-computer interaction", "information science", "library",
        "social media", "bibliometrics", "scientometrics", "digital humanities",
        "crowdsourcing", "online communities", "misinformation", "privacy",
        "explainable ai", "fairness", "education", "pedagogy", "usability",
        "visualization", "civic", "governance", "sociology"
    ],
    6: [
        "clinical", "patient", "surgery", "oncology", "cancer", "cardiovascular",
        "stroke", "mri", "ultrasound", "medical imaging", "rehabilitation",
        "pediatric", "psychiatry", "public health", "epidemiology", "911",
        "hospital", "pathology", "neuroimaging", "exercise", "physical activity",
        "aging", "muscle", "cortisol", "diet", "nutritional studies", "infant"
    ],
    7: [
        "catalysis", "catalytic", "polymer", "organic synthesis", "electrochemistry",
        "battery", "electrolyte", "chemical engineering", "zeolite", "mof",
        "metal-organic", "spectroscopy", "mass spectrometry", "chromatography",
        "supramolecular", "photochemistry", "reaction kinetics", "nanoparticle",
        "fuel cell", "desalination", "membrane"
    ]
}


def classify_topics_to_college(topics):
    """Score a list of OpenAlex topic strings against COLLEGE_KEYWORDS."""
    scores = Counter()
    text = " | ".join(t.lower() for t in topics)
    for cid, kw_list in COLLEGE_KEYWORDS.items():
        for kw in kw_list:
            if kw in text:
                scores[cid] += 1
    if scores:
        return scores.most_common(1)[0][0]
    return None


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
    communities = sorted(communities, key=len, reverse=True)
    node_to_comm = {}
    for cid, comm in enumerate(communities):
        for n in comm:
            node_to_comm[n] = cid

    # Determine dominant college for each Louvain community via topic keyword voting
    comm_to_college = {}
    for cid, comm in enumerate(communities):
        comm_votes = Counter()
        for n in comm:
            col = classify_topics_to_college(sub_g.nodes[n].get("topics", []))
            if col is not None:
                comm_votes[col] += 1
        comm_to_college[cid] = comm_votes.most_common(1)[0][0] if comm_votes else (cid % 8)

    # Assign each node to its direct topic match, falling back to its community's dominant college
    node_to_college = {}
    for n in sub_g.nodes():
        direct_col = classify_topics_to_college(sub_g.nodes[n].get("topics", []))
        if direct_col is not None:
            node_to_college[n] = direct_col
        else:
            node_to_college[n] = comm_to_college.get(node_to_comm.get(n, 0), 0)

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

    # Select top 50 faculty seeds ensuring balanced coverage across all 8 colleges
    sorted_nodes = sorted(sub_nodes, key=lambda n: sub_g.degree(n), reverse=True)
    top_50_seeds = []
    seen = set()

    for col_id in range(8):
        col_members = [n for n in sorted_nodes if node_to_college.get(n) == col_id and sub_g.degree(n) >= 5]
        for n in col_members[:6]:
            if n not in seen:
                seen.add(n)
                top_50_seeds.append(n)

    for n in sorted_nodes:
        if len(top_50_seeds) >= 50:
            break
        if n not in seen:
            seen.add(n)
            top_50_seeds.append(n)

    print(f"Selected {len(top_50_seeds)} top UIUC faculty seeds across all 8 categories.")

    # Build D3 Graph nodes and links
    d3_node_ids = set(top_50_seeds)
    for col_id in range(8):
        c_nodes = [n for n in sorted_nodes if node_to_college.get(n) == col_id][:18]
        d3_node_ids.update(c_nodes)

    d3_nodes = []
    for nid in d3_node_ids:
        col_id = node_to_college.get(nid, 0)
        pal = COLLEGE_PALETTE.get(col_id, COLLEGE_PALETTE[0])
        d3_nodes.append({
            "id": nid,
            "name": authors.get(nid, {}).get("name", nid),
            "community_id": col_id,
            "community_name": pal["name"],
            "color": pal["color"],
            "degree": sub_g.degree(nid),
            "burt_autonomy": round(autonomy.get(nid, 0.0), 3),
            "topics": list(sub_g.nodes[nid].get("topics", []))[:5]
        })

    d3_links = []
    for u in d3_node_ids:
        for v in sub_g.neighbors(u):
            if v in d3_node_ids and u < v:
                d3_links.append({
                    "source": u,
                    "target": v,
                    "type": "intra",
                    "weight": round(sub_g[u][v].get("weight", 1.0), 2)
                })

    # Synthesize dashed structural hole bridges between college leaders
    comm_leaders = {}
    for col_id in range(8):
        c_nodes = [n for n in d3_node_ids if node_to_college.get(n) == col_id]
        if c_nodes:
            comm_leaders[col_id] = max(c_nodes, key=lambda n: sub_g.degree(n))

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
        u_col = node_to_college[u]
        u_topics = set(sub_g.nodes[u].get("topics", []))
        u_nbrs = list(sub_g.neighbors(u))

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

        # Require candidate to be in both a different Louvain community AND a different college category
        cross_candidates = [
            v for v in sub_nodes
            if v != u and not sub_g.has_edge(u, v)
            and node_to_comm.get(v) != u_comm
            and node_to_college.get(v) != u_col
        ]

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
            cand_col = node_to_college.get(v, 0)
            pal = COLLEGE_PALETTE.get(cand_col, COLLEGE_PALETTE[0])
            common_nbrs = list(nx.common_neighbors(sub_g, u, v)) if is_2hop else []

            broker_name = authors.get(common_nbrs[0], {}).get("name", "Departmental Colleague") if common_nbrs else "UIUC Interdisciplinary Liaison"
            u_name = authors.get(u, {}).get("name", "Faculty Seed")
            v_name = authors.get(v, {}).get("name", "Candidate Scholar")

            path_steps = [
                {"role": "Initiator", "title": "Student / Researcher (You)"},
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
        col_id = node_to_college.get(u, 0)
        pal = COLLEGE_PALETTE.get(col_id, COLLEGE_PALETTE[0])
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