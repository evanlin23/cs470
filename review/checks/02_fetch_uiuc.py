"""Check 2: stream all UIUC works 2015-2024 into a compact JSONL (data/uiuc_works.jsonl.gz).
~548 requests x $0.0001. Raw pages are not cached (some are >10 MB because of hyperauthorship)."""
import gzip, json, os, sys, time, urllib.parse, urllib.request
UIUC = "https://openalex.org/I157725225"
SEL = "id,publication_year,type,authorships,primary_topic,topics,cited_by_count"
os.makedirs("data", exist_ok=True)
out = gzip.open("data/uiuc_works.jsonl.gz", "wt")
cursor, pages, cost = "*", 0, 0.0
last_hdr = {}
while cursor:
    p = {"filter": "institutions.id:I157725225,publication_year:2015-2024", "select": SEL,
         "per_page": 200, "cursor": cursor, "api_key": os.environ["OPENALEX_API_KEY"]}
    for a in range(6):
        try:
            with urllib.request.urlopen("https://api.openalex.org/works?" + urllib.parse.urlencode(p), timeout=120) as r:
                d = json.load(r); last_hdr = {k: v for k, v in r.headers.items() if k.lower().startswith("x-ratelimit")}
            break
        except Exception as e:
            print("retry", a, type(e).__name__, getattr(e, "code", ""), file=sys.stderr); time.sleep(2 ** a)
    else:
        sys.exit("failed")
    cost += float(last_hdr.get("X-RateLimit-Cost-USD", 0))
    for w in d["results"]:
        auths = []
        for a in w["authorships"]:
            insts = [i["id"] for i in a.get("institutions", [])]
            auths.append([a["author"]["id"], a["author"]["display_name"], UIUC in insts,
                          a["author"].get("orcid"), len(insts) == 0])
        pt = w.get("primary_topic") or {}
        out.write(json.dumps({
            "id": w["id"], "y": w["publication_year"], "t": w["type"], "c": w.get("cited_by_count", 0),
            "tr": w.get("is_authors_truncated", False), "a": auths,
            "pt": pt.get("id"), "sf": (pt.get("subfield") or {}).get("id"), "f": (pt.get("field") or {}).get("display_name"),
            "tp": [[t["id"], round(t.get("score", 0), 3), (t.get("subfield") or {}).get("id")] for t in (w.get("topics") or [])],
        }) + "\n")
    cursor = d["meta"].get("next_cursor"); pages += 1
    if pages % 50 == 0:
        print(pages, "pages", round(cost, 4), "USD", file=sys.stderr, flush=True)
out.close()
json.dump({"pages": pages, "cost_usd": round(cost, 4), "last_headers": last_hdr}, open("results_02_fetch_cost.json", "w"), indent=1)
print("done", pages, cost)
