"""Fetch a time-frozen citation neighbourhood for a MethodBridge backtest.

Data: OpenCitations Index v2 (citation links with dates) and Crossref (titles,
venues). Both are free and keyless. Every response is cached under CACHE_DIR, so
re-runs make no new requests.

Expansion (a "weak-tie walk" outward from the user's seed papers):
  1. citers of each seed, published on or before the freeze year
  2. a sample of those citers -> their references = candidate methods
  3. citers (<= freeze year) of every candidate -> bipartite citer->cited graph
"""
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

CACHE_DIR = os.environ.get("MB_CACHE", os.path.join(os.path.dirname(__file__), "cache"))
OC = "https://api.opencitations.net/index/v2"
MAILTO = os.environ.get("MB_MAILTO", "")
WORKERS = 6


def _get(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"MethodBridge-pilot (mailto:{MAILTO})"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if i == tries - 1:
                print(f"  giving up on {url}: {e}", file=sys.stderr)
                return None
            time.sleep(2 ** i)


def _cached(kind, key, url):
    path = os.path.join(CACHE_DIR, kind, re.sub(r"[^A-Za-z0-9._-]", "_", key) + ".json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    data = _get(url)
    if data is None:
        return None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)
    return data


def _ident(field):
    """Prefer the DOI; fall back to the OpenCitations omid for works without one."""
    m = re.search(r"doi:(\S+)", field)
    if m:
        return m.group(1).lower()
    m = re.search(r"omid:(\S+)", field)
    return m.group(1) if m else field


def _year(s):
    try:
        return int(s[:4])
    except (TypeError, ValueError):
        return None


def references(doi):
    rows = _cached("refs", doi, f"{OC}/references/doi:{urllib.parse.quote(doi)}") or []
    return [_ident(r["cited"]) for r in rows]


def citers(doi, freeze_year):
    rows = _cached("cites", doi, f"{OC}/citations/doi:{urllib.parse.quote(doi)}") or []
    return [_ident(r["citing"]) for r in rows if (_year(r.get("creation")) or 9999) <= freeze_year]


def crossref_meta(dois):
    """Titles/venues/years for a list of DOIs, 40 per request, cached per DOI."""
    out, todo = {}, []
    for d in dois:
        p = os.path.join(CACHE_DIR, "meta", re.sub(r"[^A-Za-z0-9._-]", "_", d) + ".json")
        if os.path.exists(p):
            with open(p) as f:
                out[d] = json.load(f)
        elif d.startswith("10."):
            todo.append(d)
    for i in range(0, len(todo), 40):
        chunk = todo[i:i + 40]
        q = urllib.parse.urlencode({
            "filter": ",".join("doi:" + d for d in chunk),
            "rows": 100,
            "select": "DOI,title,container-title,published,type",
            "mailto": MAILTO,
        })
        data = _get("https://api.crossref.org/works?" + q)
        items = (data or {}).get("message", {}).get("items", [])
        for it in items:
            d = it["DOI"].lower()
            rec = {
                "title": (it.get("title") or [""])[0],
                "venue": (it.get("container-title") or [""])[0],
                "year": ((it.get("published") or {}).get("date-parts") or [[None]])[0][0],
            }
            out[d] = rec
            p = os.path.join(CACHE_DIR, "meta", re.sub(r"[^A-Za-z0-9._-]", "_", d) + ".json")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                json.dump(rec, f)
    return out


def pmap(fn, items):
    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(fn, items))


def expand(seeds, freeze_year, citer_sample=1200, max_candidates=600, rng_seed=0):
    t0 = time.time()
    print(f"[1] citers of {len(seeds)} seeds (<= {freeze_year})")
    seed_citers = dict(zip(seeds, pmap(lambda d: citers(d, freeze_year), seeds)))
    pool = sorted({c for cs in seed_citers.values() for c in cs if c.startswith("10.")} - set(seeds))
    random.Random(rng_seed).shuffle(pool)
    sample = pool[:citer_sample]
    print(f"    {len(pool)} distinct citers; sampling {len(sample)}  ({time.time() - t0:.0f}s)")

    print("[2] references of sampled citers -> candidate methods")
    refs = dict(zip(sample, pmap(references, sample)))
    freq = {}
    for rs in refs.values():
        for r in set(rs):
            if r.startswith("10.") and r not in seeds:
                freq[r] = freq.get(r, 0) + 1
    cands = [d for d, n in sorted(freq.items(), key=lambda kv: -kv[1]) if n >= 2][:max_candidates]
    print(f"    {len(freq)} referenced works; {len(cands)} candidates cited by >=2 sampled citers  ({time.time() - t0:.0f}s)")

    print("[3] citers of every candidate (bipartite citer->cited graph)")
    nodes = list(seeds) + cands
    edges = dict(zip(nodes, pmap(lambda d: citers(d, freeze_year), nodes)))
    print(f"    done  ({time.time() - t0:.0f}s)")

    meta = crossref_meta(nodes)
    return {"seeds": list(seeds), "candidates": cands, "freeze_year": freeze_year,
            "citers": edges, "candidate_freq": {d: freq[d] for d in cands}, "meta": meta}


if __name__ == "__main__":
    case = json.load(open(sys.argv[1]))
    out = expand(case["seeds"], case["freeze_year"], case.get("citer_sample", 1200), case.get("max_candidates", 600))
    out["targets"] = case["targets"]
    out["case"] = case["name"]
    with open(sys.argv[2], "w") as f:
        json.dump(out, f)
    print("wrote", sys.argv[2])
