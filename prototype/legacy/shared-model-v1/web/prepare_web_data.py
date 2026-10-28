"""Export the same temporal model used in backtests, with actual bounded paths."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model import prepare_model, rank_candidates, MODEL_VERSION
from topic_groups import classify_topics

COLORS = ["#2563EB", "#0284C7", "#16A34A", "#CA8A04", "#9333EA", "#EA580C", "#DC2626", "#0D9488"]


def build_and_export(data_path, out_path="prototype/web/data.json"):
    data = json.loads(Path(data_path).read_text())
    graph, _, authors, membership, autonomy = prepare_model(data)
    communities = sorted(set(membership.values()))
    palettes = {c: {"name": f"Community {c+1}", "color": COLORS[c % len(COLORS)]} for c in communities}
    seeds = []
    for c in communities[:8]:
        seeds.extend(sorted((n for n in graph if membership[n] == c), key=lambda n: (-graph.degree(n), n))[:6])
    for n in sorted(graph, key=lambda n: (-graph.degree(n), n)):
        if len(seeds) >= 50:
            break
        if n not in seeds:
            seeds.append(n)
    papers = {n: [] for n in graph}
    for paper in data["papers"]:
        if paper["year"] <= 2019:
            for n in paper["authors"]:
                if n in papers:
                    papers[n].append(paper["title"])
    def profile(n):
        c = membership[n]
        return {"id": n, "name": authors[n]["name"], "community_id": c,
                "community_name": palettes[c]["name"], "department": palettes[c]["name"],
                "topic_group": classify_topics(sorted(graph.nodes[n]["topics"])),
                "color": palettes[c]["color"], "degree": graph.degree(n),
                "burt_autonomy": round(autonomy[n], 3), "topics": sorted(graph.nodes[n]["topics"])[:5]}
    recommendations = {}
    visible = set(seeds)
    dashed = []
    for seed in seeds:
        recs = []
        for i, row in enumerate(rank_candidates(graph, seed, membership, autonomy)[:10], 1):
            candidate = row["candidate_id"]
            path = row["path_ids"]
            steps = ([{"role": "Your selected anchor", "title": authors[path[0]]["name"]}] +
                     [{"role": "Co-author intermediary" if n != candidate else "Candidate", "title": authors[n]["name"]} for n in path[1:]]) if path else []
            recs.append({**profile(candidate), **row, "rank": i, "score": round(row["score"], 6),
                         "path_steps": steps, "path_actionability": f"{len(path)-1}-hop co-authorship route" if path else "No route within 3 hops",
                         "sample_papers": papers[candidate][:2]})
            visible.add(candidate)
            if path:
                visible.update(path)
            dashed.append({"source": seed, "target": candidate, "type": "structural_hole", "seed_id": seed, "candidate_id": candidate})
        recommendations[seed] = recs
    links = [{"source": u, "target": v, "type": "intra"} for u, v in graph.edges() if u in visible and v in visible]
    bundle = {"metadata": {"model_version": MODEL_VERSION, "split_year": 2019, "source": Path(data_path).name,
                           "weights": [0.60, 0.12, 0.12, 0.16],
                           "topic_groups": "Keyword hints, not department labels; no effect on rankings", "routes": "Observed co-authorships, not verified social introductions"},
              "seeds": [profile(n) for n in seeds], "recommendations": recommendations,
              "graph": {"nodes": [profile(n) for n in sorted(visible)], "links": links+dashed},
              "colleges": {c: palettes[c] for c in sorted({membership[n] for n in visible})}}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(bundle, indent=2))
    print(f"Exported {len(seeds)} seeds and {sum(map(len,recommendations.values()))} recommendations")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="prototype/uiuc_data_scaled.json")
    parser.add_argument("--out", default="prototype/web/data.json")
    args = parser.parse_args()
    build_and_export(args.data, args.out)
