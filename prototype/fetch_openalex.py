"""Fetch a time-frozen citation neighbourhood for a MethodBridge backtest from OpenAlex.

Drop-in alternative to fetch.py: writes the same JSON schema, so analyze.py runs
unchanged. Ids are lowercase DOIs where OpenAlex has one, else OpenAlex W-ids.

Needs OPENALEX_API_KEY in the environment (sent as the api_key parameter; never
logged). Every response is cached under CACHE_DIR keyed by the URL without the
key, so re-runs make no new requests. Spend is read from the x-ratelimit-cost-usd
header and appended to CACHE_DIR/spend.log.

Expansion (the same weak-tie walk as fetch.py):
  1. citers of each seed, published on or before the freeze year (with their
     referenced_works, so step 2 needs no extra requests)
  2. a sample of those citers -> their references -> candidates cited by >=2
  3. citers (<= freeze year) of every candidate, capped at MAX_CITERS per work
"""
import hashlib
import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

CACHE_DIR = os.environ.get("MB_CACHE", os.path.join(os.path.dirname(__file__), "cache"))
API = "https://api.openalex.org"
KEY = os.environ.get("OPENALEX_API_KEY", "")
WORKERS = 6
MAX_CITERS = int(os.environ.get("MB_MAX_CITERS", 1500))
BUDGET_USD = float(os.environ.get("MB_BUDGET_USD", 0.9))  # hard stop for this process

_lock = threading.Lock()
stats = {"requests": 0, "cache_hits": 0, "usd": 0.0, "remaining_usd": None}


def _get(path, params, tries=5):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    for i in range(tries):
        if stats["usd"] >= BUDGET_USD:
            raise RuntimeError(f"budget {BUDGET_USD} USD reached; stopping")
        try:
            req = urllib.request.Request(url + (f"&api_key={KEY}" if KEY else ""),
                                         headers={"User-Agent": "MethodBridge-pilot (CS 470)"})
            with urllib.request.urlopen(req, timeout=120) as r:
                cost = float(r.headers.get("x-ratelimit-cost-usd") or 0)
                with _lock:
                    stats["requests"] += 1
                    stats["usd"] += cost
                    stats["remaining_usd"] = r.headers.get("x-ratelimit-remaining-usd")
                    with open(os.path.join(CACHE_DIR, "spend.log"), "a") as f:
                        f.write(f"{time.time():.0f}\t{cost}\t{path}\t{urllib.parse.urlencode(params)[:200]}\n")
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                print(f"  HTTP {e.code} on {url[:200]}", file=sys.stderr)
                return None
            time.sleep(2 ** i)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if i == tries - 1:
                print(f"  giving up on {url[:200]}: {e}", file=sys.stderr)
                return None
            time.sleep(2 ** i)
    return None


def _cached(kind, path, params):
    key = hashlib.sha1((path + "?" + urllib.parse.urlencode(sorted(params.items()))).encode()).hexdigest()
    p = os.path.join(CACHE_DIR, "openalex", kind, key + ".json")
    if os.path.exists(p):
        stats["cache_hits"] += 1
        with open(p) as f:
            return json.load(f)
    data = _get(path, params)
    if data is not None:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(data, f)
    return data


def short(wid):
    return wid.rsplit("/", 1)[-1] if wid else wid


def ident(w):
    """Lowercase DOI if present, else the W-id."""
    d = w.get("doi")
    if d:
        return d.lower().replace("https://doi.org/", "")
    return short(w["id"])


META_SELECT = "id,doi,title,publication_year,primary_location,primary_topic,referenced_works"


def lookup(ids=(), dois=()):
    """Batch-fetch works by W-id or DOI, 100 per request. Returns {W-id: work}."""
    out = {}
    for field, vals in (("openalex", list(ids)), ("doi", list(dois))):
        vals = sorted(set(vals))
        for i in range(0, len(vals), 100):
            chunk = vals[i:i + 100]
            data = _cached("lookup", "works", {"filter": f"{field}:" + "|".join(chunk),
                                               "per-page": 100, "select": META_SELECT})
            for w in (data or {}).get("results", []):
                out[short(w["id"])] = w
    return out


def citers(wid, freeze_year, select="id,doi", cap=None):
    """Works citing wid published <= freeze_year, cursor-paged, capped. Returns (works, total, capped)."""
    cap = cap or MAX_CITERS
    works, cursor, total = [], "*", 0
    while cursor and len(works) < cap:
        data = _cached("cites", "works", {"filter": f"cites:{wid},publication_year:<{freeze_year + 1}",
                                          "select": select, "per-page": 200, "cursor": cursor})
        if not data:
            break
        total = data["meta"]["count"]
        works.extend(data["results"])
        cursor = data["meta"].get("next_cursor") if data["results"] else None
    return works[:cap], total, total > cap


def pmap(fn, items):
    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(fn, items))


def meta_of(w):
    src = ((w.get("primary_location") or {}).get("source") or {})
    field = (((w.get("primary_topic") or {}).get("field")) or {}).get("display_name")
    return {"title": w.get("title") or "", "venue": src.get("display_name") or "",
            "year": w.get("publication_year"), "field": field, "openalex": short(w["id"])}


def expand(seed_dois, freeze_year, citer_sample=1200, max_candidates=600, rng_seed=0, extra=()):
    t0 = time.time()
    seed_works = lookup(dois=[s for s in seed_dois if s.startswith("10.")],
                        ids=[s for s in seed_dois if not s.startswith("10.")])
    got = {ident(w) for w in seed_works.values()} | set(seed_works)
    missing = sorted(s for s in seed_dois if s.lower() not in got and s not in got)
    if missing:
        print(f"    seeds not found in OpenAlex: {missing}")
    seed_w = sorted(seed_works)
    seed_ids = {ident(seed_works[w]) for w in seed_w}

    print(f"[1] citers of {len(seed_w)} seeds (<= {freeze_year})")
    sc = dict(zip(seed_w, pmap(lambda w: citers(w, freeze_year, "id,doi,referenced_works", cap=5000), seed_w)))
    pool = {}
    for ws, _, _ in sc.values():
        for c in ws:
            if short(c["id"]) not in seed_works:
                pool[short(c["id"])] = c
    order = sorted(pool)
    random.Random(rng_seed).shuffle(order)
    sample = order[:citer_sample]
    print(f"    {len(pool)} distinct citers; sampling {len(sample)}  ({time.time() - t0:.0f}s, "
          f"{stats['requests']} req, ${stats['usd']:.4f})")

    print("[2] references of sampled citers -> candidate methods")
    freq = {}
    for c in sample:
        for r in set(map(short, pool[c].get("referenced_works") or [])):
            if r not in seed_works:
                freq[r] = freq.get(r, 0) + 1
    cand_w = [w for w, n in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])) if n >= 2][:max_candidates]
    print(f"    {len(freq)} referenced works; {len(cand_w)} candidates cited by >=2 sampled citers")

    print(f"[3] citers of every candidate (cap {MAX_CITERS})")
    nodes_w = seed_w + cand_w
    works = dict(seed_works)
    works.update(lookup(ids=[w for w in cand_w + list(extra) if w not in works]))
    res = dict(zip(nodes_w, pmap(lambda w: citers(w, freeze_year), nodes_w)))
    for w in seed_w:  # seeds: reuse step-1 lists (larger cap) for consistency
        res[w] = sc[w]
    print(f"    done  ({time.time() - t0:.0f}s, {stats['requests']} req, ${stats['usd']:.4f})")

    edges, capped, freq_out, cands = {}, {}, {}, []
    for w in nodes_w:
        if w not in works:
            continue
        i = ident(works[w])
        ws, total, hit = res[w]
        lst = edges.setdefault(i, [])
        seen = set(lst)
        for c in ws:
            ci = ident(c)
            if ci not in seen and ci != i:
                lst.append(ci)
                seen.add(ci)
        if hit:
            capped[i] = total
        if w in cand_w and i not in seed_ids and i not in cands:
            cands.append(i)
            freq_out[i] = freq_out.get(i, 0) + freq[w]
    meta = {ident(w): meta_of(w) for w in works.values()}
    return {"seeds": sorted(seed_ids), "candidates": cands, "freeze_year": freeze_year,
            "citers": edges, "candidate_freq": freq_out, "meta": meta,
            "fetch": {"source": "openalex", "max_citers": MAX_CITERS, "capped": capped,
                      "seed_citer_pool": len(pool), "sample": len(sample),
                      "referenced_works": len(freq), "seeds_missing": missing}}


def resolve_targets(targets):
    """Case targets may be DOIs or W-ids; map them to the ids used in the graph."""
    dois = [t for t in targets if t.startswith("10.")]
    wids = [t for t in targets if t.startswith("W")]
    found = lookup(ids=wids, dois=dois)
    by_doi = {ident(w): w for w in found.values()}
    out = {}
    for t, name in targets.items():
        w = found.get(t) or by_doi.get(t.lower())
        out[ident(w) if w else t.lower()] = name
    return out, found


if __name__ == "__main__":
    case = json.load(open(sys.argv[1]))
    os.makedirs(CACHE_DIR, exist_ok=True)
    targets, twork = resolve_targets(case["targets"])
    out = expand(case["seeds"], case["freeze_year"], case.get("citer_sample", 1200),
                 case.get("max_candidates", 600), extra=list(twork))
    out["targets"] = targets
    out["case"] = case["name"]
    for w in twork.values():
        out["meta"].setdefault(ident(w), meta_of(w))
    out["fetch"]["targets_reached"] = {t: t in out["candidates"] for t in targets}
    out["fetch"]["stats"] = dict(stats)
    with open(sys.argv[2], "w") as f:
        json.dump(out, f)
    print("targets reached by walk:", out["fetch"]["targets_reached"])
    print(f"requests={stats['requests']} cache_hits={stats['cache_hits']} spend=${stats['usd']:.4f} "
          f"remaining_today=${stats['remaining_usd']}")
    print("wrote", sys.argv[2])
