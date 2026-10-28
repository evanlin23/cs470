"""Shared, deterministic temporal model for evaluation, demo and study."""
import math
from collections import Counter, defaultdict
import networkx as nx
from networkx.algorithms import community as nxc
MODEL_VERSION = "proposal-path-v2"
def build_graphs(data, split_year=2019):
    """Constructs weighted training graph (<= split_year) and evaluation graph (> split_year)
    with strict leak-free temporal topic profiling (pre-split only).
    """
    papers = data["papers"]
    authors = data["authors"]

    g_train = nx.Graph()
    g_eval = nx.Graph()

    # Accumulate author topics STRICTLY from training-window papers (<= split_year)
    train_author_topics = defaultdict(Counter)

    for p in papers:
        year = p["year"]
        auths = p["authors"]
        n_auth = len(auths)
        if n_auth < 2:
            continue
        weight = 1.0  # Proposal: each joint paper adds one collaboration.

        target_g = g_train if year <= split_year else g_eval

        if year <= split_year:
            for t in p.get("topics", []):
                for a in auths:
                    train_author_topics[a][t] += 1

        for i in range(n_auth):
            for j in range(i + 1, n_auth):
                u, v = auths[i], auths[j]
                if target_g.has_edge(u, v):
                    target_g[u][v]["weight"] += weight
                else:
                    target_g.add_edge(u, v, weight=weight)

    # Assign leak-free topics to training graph nodes
    for aid, ainfo in sorted(authors.items()):
        if aid in g_train:
            top_k = [t for t, _ in train_author_topics[aid].most_common(10)]
            g_train.add_node(aid, name=ainfo.get("name", aid), topics=set(top_k))
        if aid in g_eval:
            g_eval.add_node(aid, name=ainfo.get("name", aid))

    print(f"Training Graph (<= {split_year}): {g_train.number_of_nodes()} nodes, {g_train.number_of_edges()} edges")
    print(f"Evaluation Graph (> {split_year}): {g_eval.number_of_nodes()} nodes, {g_eval.number_of_edges()} edges")
    return g_train, g_eval, authors


def compute_burt_constraint(G):
    """Computes Burt's aggregate network constraint C_i and autonomy H_i = 1 - C_i."""
    burt_autonomy = {}
    node_strength = {n: sum(d.get("weight", 1.0) for _, d in G[n].items()) for n in G.nodes()}

    for i in G.nodes():
        neighbors = list(G.neighbors(i))
        k = len(neighbors)
        if k <= 1:
            burt_autonomy[i] = 0.0
            continue

        total_w = node_strength[i]
        p = {nbr: G[i][nbr].get("weight", 1.0) / total_w for nbr in neighbors}

        C_i = 0.0
        for j in neighbors:
            indirect = 0.0
            for q in neighbors:
                if q != j and G.has_edge(q, j):
                    total_q = node_strength.get(q, 0.0)
                    p_qj = G[q][j].get("weight", 1.0) / total_q if total_q > 0 else 0
                    indirect += p[q] * p_qj
            c_ij = (p[j] + indirect) ** 2
            C_i += c_ij

        burt_autonomy[i] = max(0.0, 1.0 - C_i)

    return burt_autonomy


def compute_topic_similarity(topics_u, topics_v):
    if not topics_u or not topics_v:
        return 0.0
    intersection = len(topics_u & topics_v)
    union = len(topics_u | topics_v)
    return intersection / union if union > 0 else 0.0


def three_hop_path_counts(G, seed):
    """Count simple 3-edge paths seed -> a -> b -> candidate."""
    counts = Counter()
    for a in G.neighbors(seed):
        for b in G.neighbors(a):
            if b == seed:
                continue
            for cand in G.neighbors(b):
                if cand not in (seed, a, b):
                    counts[cand] += 1
    return counts



def prepare_training_model(train):
    """Canonical graph, partition and autonomy shared by every consumer."""
    nodes = sorted(n for n in train if train.degree(n) > 0)
    graph = nx.Graph()
    graph.add_nodes_from((n, train.nodes[n]) for n in nodes)
    graph.add_edges_from((u, v, dict(train[u][v])) for u, v in sorted(tuple(sorted(e)) for e in train.edges()))
    communities = sorted(nxc.louvain_communities(graph, seed=42), key=lambda c: (-len(c), sorted(c)))
    membership = {n: i for i, c in enumerate(communities) for n in c}
    return graph, membership, compute_burt_constraint(graph)


def prepare_model(data, split_year=2019):
    train, evaluation, authors = build_graphs(data, split_year)
    graph, membership, autonomy = prepare_training_model(train)
    return graph, evaluation, authors, membership, autonomy


def candidate_features(graph, seed, membership, autonomy):
    """All non-coauthor, cross-community candidates for native baseline comparisons.

    Only reachable candidates with shortest distance >=3 are eligible for the
    proposal's ranking. Native Adamic–Adar retains its shared-contact pool.
    """
    paths = nx.single_source_shortest_path(graph, seed)
    counts = three_hop_path_counts(graph, seed)
    rows = []
    for candidate in sorted(graph):
        if candidate == seed or graph.has_edge(seed, candidate) or membership[candidate] == membership[seed]:
            continue
        topic = compute_topic_similarity(graph.nodes[seed]["topics"], graph.nodes[candidate]["topics"])
        bsi = sum(membership[w] == membership[seed] for w in graph[candidate]) / graph.degree(candidate)
        path = paths.get(candidate)
        distance = len(path)-1 if path else None
        aa = sum(1 / math.log(graph.degree(w)) for w in nx.common_neighbors(graph, seed, candidate))
        count = counts[candidate]
        bonus = count / (1.0 + count)
        rows.append({"candidate_id": candidate, "topic_similarity": topic,
                     "burt_autonomy": autonomy[candidate], "boundary_spanning": bsi,
                     "three_hop_paths": count, "path_bonus": bonus, "path_ids": path,
                     "distance": distance, "proposal_eligible": distance is not None and distance >= 3,
                     "score": topic + 0.5 * bonus, "aa": aa})
    return rows


def rank_candidates(graph, seed, membership, autonomy):
    rows = [row for row in candidate_features(graph, seed, membership, autonomy) if row['proposal_eligible']]
    return sorted(rows, key=lambda row: (-row['score'], row['candidate_id']))


def path_description(row, authors):
    path = row["path_ids"]
    if not path:
        return "No observed co-authorship route exists in this graph."
    names = " → ".join(authors[n]["name"] for n in path)
    return f"{names} ({len(path)-1} co-authorship hops; acquaintance and willingness to introduce are unverified)"
