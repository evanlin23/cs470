"""Check 5: stale affiliations (OpenAlex last_known_institutions) and the cold start.
Costs ~6 requests."""
import collections, json, random
import oa
from common import load_works, build_graph
random.seed(0)
UIUC = "https://openalex.org/I157725225"
works = list(load_works())
_, _, npA = build_graph(works, (2015, 2019))
_, _, npB = build_graph(works, (2020, 2024))
lastyear = collections.defaultdict(int)
for w in works:
    for a in w["a"]:
        if a[0] and a[2]:
            lastyear[a[0]] = max(lastyear[a[0]], w["y"])
R = {}
active = [a for a, c in npA.items() if c >= 3]
left = [a for a in active if lastyear[a] <= 2020]
stayed = [a for a in active if lastyear[a] >= 2024]
R["authors_ge3_papers_2015_19"] = len(active)
R["no_uiuc_paper_after_2020"] = len(left)
R["uiuc_paper_in_2024"] = len(stayed)

def fetch(ids):
    out = []
    for k in range(0, len(ids), 50):
        chunk = "|".join(i.rsplit("/", 1)[1] for i in ids[k:k + 50])
        out += oa.get("/authors", filter=f"openalex:{chunk}", per_page=50,
                      select="id,display_name,last_known_institutions,works_count,orcid")["results"]
    return out

for name, grp in [("left_by_2020", left), ("still_publishing_2024", stayed)]:
    s = fetch(random.sample(grp, 100))
    lk = [UIUC in [i["id"] for i in (r.get("last_known_institutions") or [])] for r in s]
    R[f"{name}_sample_n"] = len(s)
    R[f"{name}_last_known_includes_uiuc"] = sum(lk)
    R[f"{name}_with_orcid"] = sum(bool(r.get("orcid")) for r in s)
    R[f"{name}_works_count_median"] = sorted(r["works_count"] for r in s)[len(s) // 2]

# cold start: newcomers in 2020-24 (proxy for students) - can they be placed via an anchor co-author?
newc = [a for a, c in npB.items() if a not in npA]
first = {}
for w in sorted(works, key=lambda w: w["y"]):
    if w["y"] < 2020: continue
    ids = [a[0] for a in w["a"] if a[0] and a[2]]
    for a in ids:
        if a in npB and a not in npA and a not in first:
            first[a] = [b for b in ids if b != a]
anch = sum(any(npA.get(b, 0) >= 5 for b in first.get(a, [])) for a in newc)
R["newcomers_2020_24"] = len(newc)
R["newcomers_with_1_paper"] = sum(npB[a] == 1 for a in newc)
R["newcomers_whose_first_paper_has_established_uiuc_coauthor"] = anch
json.dump(R, open("results_05_affiliation_coldstart.json", "w"), indent=1)
print(json.dumps(R, indent=1))
