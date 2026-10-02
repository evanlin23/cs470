"""Tiny OpenAlex client: caches responses, records x-ratelimit-* cost headers. Never prints the API key."""
import hashlib, json, os, time, urllib.parse, urllib.request
BASE = "https://api.openalex.org"
CACHE = os.environ.get("OA_CACHE", os.path.join(os.path.dirname(__file__), ".cache"))
COSTLOG = os.path.join(os.path.dirname(__file__), "cost_log.jsonl")
os.makedirs(CACHE, exist_ok=True)

def get(path, **params):
    q = urllib.parse.urlencode(params)
    key = hashlib.sha1(f"{path}?{q}".encode()).hexdigest()
    fp = os.path.join(CACHE, key + ".json")
    if os.path.exists(fp):
        return json.load(open(fp))
    params["api_key"] = os.environ["OPENALEX_API_KEY"]
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.load(r)
                hdr = {k: v for k, v in r.headers.items() if k.lower().startswith("x-ratelimit")}
                break
        except Exception as e:  # never echo the URL (contains the key)
            err = type(e).__name__ + ":" + str(getattr(e, "code", ""))
            time.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"OpenAlex request failed: {path} {err}")
    with open(COSTLOG, "a") as f:
        f.write(json.dumps({"path": path, "params": {k: v for k, v in params.items() if k != "api_key"}, "headers": hdr}) + "\n")
    json.dump(data, open(fp, "w"))
    return data

def paginate(path, max_pages=10**6, **params):
    cursor = "*"; n = 0
    while cursor and n < max_pages:
        d = get(path, cursor=cursor, **params)
        yield from d["results"]
        cursor = d["meta"].get("next_cursor"); n += 1
