"""Fetch UIUC co-authorship works and author profiles from OpenAlex.

OpenAlex API (free, keyless):
- Institution ROR: https://ror.org/047426m28 (University of Illinois Urbana-Champaign)
- OpenAlex ID: I157725225

Usage:
    python3 fetch_openalex.py --mailto your_netid@illinois.edu --max_works 5000 --out uiuc_corpus.json
"""
import argparse
from collections import Counter
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

OPENALEX_API = "https://api.openalex.org"
UIUC_ROR = "https://ror.org/047426m28"
UIUC_INST_ID = "I157725225"


def fetch_openalex_page(url, mailto):
    headers = {"User-Agent": f"BridgeFinder-Research (mailto:{mailto})"}
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt == 4:
                print(f"[Error] Failed to fetch {url}: {e}", file=sys.stderr)
                return None
            time.sleep(2 ** attempt)


def fetch_works(mailto, max_works=5000, start_year=2015, end_year=2024, cache_file="uiuc_raw_works.json"):
    if os.path.exists(cache_file):
        print(f"Loading cached works from {cache_file}...")
        with open(cache_file) as f:
            return json.load(f)

    print(f"Fetching UIUC works ({start_year}-{end_year}) from OpenAlex API...")
    works = []
    cursor = "*"
    per_page = 200

    base_filter = f"institutions.ror:{UIUC_ROR},publication_year:{start_year}-{end_year}"
    encoded_filter = urllib.parse.quote(base_filter)

    while cursor and len(works) < max_works:
        url = f"{OPENALEX_API}/works?filter={encoded_filter}&per-page={per_page}&cursor={urllib.parse.quote(cursor)}&select=id,doi,title,publication_year,authorships,topics,cited_by_count"
        data = fetch_openalex_page(url, mailto)
        if not data or "results" not in data:
            break

        results = data["results"]
        if not results:
            break

        works.extend(results)
        print(f"  Fetched {len(works)} / {min(max_works, data.get('meta', {}).get('count', max_works))} works...")
        cursor = data.get("meta", {}).get("next_cursor")
        time.sleep(0.1)  # Polite pool delay

    print(f"Total works fetched: {len(works)}. Saving to {cache_file}...")
    with open(cache_file, "w") as f:
        json.dump(works, f)
    return works


def extract_uiuc_coauthorship(works, min_collab=1):
    """Processes works into a clean author dictionary and co-authorship records."""
    print("Extracting UIUC faculty co-authorship relationships...")
    authors = {}
    papers = []

    for w in works:
        year = w.get("publication_year")
        if not year:
            continue

        paper_id = w.get("id")
        title = w.get("title") or "Untitled"
        topics = [t.get("display_name") for t in w.get("topics", []) if t.get("display_name")]
        citations = w.get("cited_by_count", 0)

        # Filter authors affiliated with UIUC on this paper
        uiuc_authors = []
        for a in w.get("authorships", []):
            author_obj = a.get("author", {})
            author_id = author_obj.get("id")
            name = author_obj.get("display_name")
            if not author_id or not name:
                continue

            is_uiuc = False
            for inst in a.get("institutions", []):
                inst_ror = inst.get("ror")
                inst_id = inst.get("id")
                if inst_ror == UIUC_ROR or (inst_id and UIUC_INST_ID in inst_id) or "Urbana" in inst.get("display_name", ""):
                    is_uiuc = True
                    break

            if is_uiuc:
                uiuc_authors.append(author_id)
                if author_id not in authors:
                    authors[author_id] = {
                        "id": author_id,
                        "name": name,
                        "topics": Counter(),
                        "paper_count": 0,
                    }
                authors[author_id]["paper_count"] += 1
                for t in topics:
                    authors[author_id]["topics"][t] += 1

        if len(uiuc_authors) >= 2:
            papers.append({
                "id": paper_id,
                "title": title,
                "year": year,
                "authors": uiuc_authors,
                "topics": topics,
                "citations": citations
            })

    # Convert topic counters to top-k lists
    for aid, data in authors.items():
        data["top_topics"] = [t for t, _ in data["topics"].most_common(10)]
        del data["topics"]

    print(f"Extracted {len(authors)} UIUC authors across {len(papers)} multi-authored UIUC papers.")
    return {"authors": authors, "papers": papers}


def main():
    parser = argparse.ArgumentParser(description="Harvest UIUC works from OpenAlex")
    parser.add_argument("--mailto", default="elin26@illinois.edu", help="Your UIUC email for the polite pool")
    parser.add_argument("--max_works", type=int, default=5000, help="Max works to harvest (use 20000+ for full run)")
    parser.add_argument("--out", default="prototype/new_collection.json", help="Output JSON path")
    args = parser.parse_args()

    works = fetch_works(args.mailto, max_works=args.max_works)
    corpus = extract_uiuc_coauthorship(works)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(corpus, f, indent=2)
    print(f"[Done] Corpus written to {args.out}")


if __name__ == "__main__":
    main()
