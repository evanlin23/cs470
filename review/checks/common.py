"""Shared loading / graph-building for the review checks."""
import gzip, json, itertools, collections
import networkx as nx

RESEARCH_TYPES = {"article", "conference-paper", "preprint", "review", "book-chapter", "book", "letter"}
MAX_AUTHORS = 25  # the spec's hyperauthorship cut-off

def load_works(path="data/uiuc_works.jsonl.gz"):
    with gzip.open(path, "rt") as f:
        for line in f:
            yield json.loads(line)

def build_graph(works, years, uiuc_only=True, max_authors=MAX_AUTHORS, types=RESEARCH_TYPES):
    """Co-authorship graph. Nodes = OpenAlex author IDs (UIUC-affiliated on that paper if uiuc_only).
    Edge weight = number of joint papers. Returns (G, per-author topic Counter, per-author paper count)."""
    G = nx.Graph()
    topics = collections.defaultdict(collections.Counter)
    npapers = collections.Counter()
    lo, hi = years
    for w in works:
        if not (lo <= w["y"] <= hi) or w["t"] not in types:
            continue
        auths = [a for a in w["a"] if a[0] and (a[2] or not uiuc_only)]
        ids = sorted({a[0] for a in auths})
        for a in ids:
            npapers[a] += 1
            for tid, score, _sf in w["tp"]:
                topics[a][tid] += score
        G.add_nodes_from(ids)
        if len(w["a"]) > max_authors or w["tr"]:
            continue
        for u, v in itertools.combinations(ids, 2):
            if G.has_edge(u, v):
                G[u][v]["weight"] += 1
            else:
                G.add_edge(u, v, weight=1)
    return G, topics, npapers
