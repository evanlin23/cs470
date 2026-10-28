"""Collect the complete matching OpenAlex corpus, resuming only verified checkpoints.

The default has no work limit. A capped/interrupted run never replaces the dataset.
Optional OPENALEX_API_KEY is used without logging its value or authenticated URLs.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

OPENALEX_API = 'https://api.openalex.org'
UIUC_ROR = 'https://ror.org/047426m28'
UIUC_INST_ID = 'I157725225'


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def fetch_openalex_page(url, mailto):
    # Never print this URL: it can contain a real API key or proxy placeholder.
    parameters = {'mailto': mailto} if mailto else {}
    if os.environ.get('OPENALEX_API_KEY'):
        parameters['api_key'] = os.environ['OPENALEX_API_KEY']
    if parameters:
        url += ('&' if '?' in url else '?') + urllib.parse.urlencode(parameters)
    request = urllib.request.Request(url, headers={'User-Agent': 'BridgeFinder-Research'})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 4:
                raise RuntimeError(f'OpenAlex returned HTTP {error.code}; collection is incomplete.') from None
        except urllib.error.URLError as error:
            if 'Tunnel connection failed: 403' in str(error.reason):
                raise RuntimeError('The environment proxy denied OpenAlex access (CONNECT 403). No dataset was published.') from None
            if attempt == 4:
                raise RuntimeError('OpenAlex network request failed; collection is incomplete.') from None
        except (TimeoutError, json.JSONDecodeError):
            if attempt == 4:
                raise RuntimeError('OpenAlex timed out or returned invalid JSON; collection is incomplete.') from None
        time.sleep(min(2 ** attempt, 15))


def query_definition(start_year, end_year):
    if not 1 <= start_year <= end_year <= 9999:
        raise ValueError('Invalid publication-year interval')
    return {'institution_id': UIUC_INST_ID, 'institution_ror': UIUC_ROR,
            'start_year': start_year, 'end_year': end_year,
            'filter': f'institutions.id:{UIUC_INST_ID},publication_year:{start_year}-{end_year}',
            'selection': None,  # Full objects preserve any authorship-truncation flags.
            'page_size': 200}


def works_url(query, cursor=None, count_only=False):
    parameters = {'filter': query['filter'], 'per-page': 1 if count_only else query['page_size']}
    if count_only:
        parameters['select'] = 'id'
    if cursor is not None:
        parameters['cursor'] = cursor
    return OPENALEX_API + '/works?' + urllib.parse.urlencode(parameters)


def response_count(response):
    count = response.get('meta', {}).get('count') if isinstance(response, dict) else None
    if type(count) is not int or count < 0:
        raise RuntimeError('OpenAlex did not return a valid total count; completeness cannot be verified.')
    return count


def iter_cached_works(cache_dir, state):
    seen = set()
    for index in range(state['pages']):
        page = json.loads((Path(cache_dir) / f'page-{index:06d}.json').read_text())
        if not isinstance(page, list):
            raise ValueError('Invalid cached page')
        for work in page:
            if not isinstance(work, dict) or not isinstance(work.get('id'), str) or not work['id']:
                raise ValueError('A work is missing its stable identity')
            if work['id'] not in seen:
                seen.add(work['id'])
                yield work


def collect_works(mailto, cache_dir, max_works=0, start_year=2015, end_year=2024, fetch_page=None, delay=1):
    """Exhaust the query or retain an explicitly incomplete, resumable checkpoint."""
    fetch_page = fetch_page or fetch_openalex_page
    if max_works < 0:
        raise ValueError('max_works must be zero (uncapped) or positive')
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    state_path = cache_dir / 'checkpoint.json'
    query = query_definition(start_year, end_year)
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if not isinstance(state, dict) or state.get('schema_version') != 1 or state.get('query') != query:
            raise ValueError('Cache is legacy or belongs to a different query. Choose a fresh cache directory.')
        if type(state.get('pages')) is not int or state['pages'] < 0 or type(state.get('complete')) is not bool:
            raise ValueError('Invalid checkpoint')
    else:
        state = {'schema_version': 1, 'query': query, 'started_at': timestamp(), 'pages': 0,
                 'next_cursor': '*', 'complete': False, 'api_counts': [], 'unique_works': 0}
        atomic_json(state_path, state)
    seen = {work['id'] for work in iter_cached_works(cache_dir, state)}
    if len(seen) != state['unique_works']:
        raise ValueError('Cached pages disagree with the checkpoint; use a fresh cache directory.')
    if state['complete']:
        return state
    cursors = set()
    while state['next_cursor'] is not None:
        if max_works and len(seen) >= max_works:
            return state
        cursor = state['next_cursor']
        if cursor in cursors:
            raise RuntimeError('OpenAlex repeated a cursor; collection is incomplete.')
        cursors.add(cursor)
        response = fetch_page(works_url(query, cursor), mailto)
        count = response_count(response)
        results = response.get('results')
        if not isinstance(results, list):
            raise RuntimeError('OpenAlex returned no valid results list; collection is incomplete.')
        if 'next_cursor' not in response['meta']:
            raise RuntimeError('OpenAlex omitted cursor status; collection is incomplete.')
        next_cursor = response['meta']['next_cursor']
        if next_cursor is not None and (not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor):
            raise RuntimeError('OpenAlex returned an invalid next cursor; collection is incomplete.')
        if not results and next_cursor is not None:
            raise RuntimeError('OpenAlex returned an empty page with a continuation; collection is incomplete.')
        for work in results:
            if not isinstance(work, dict) or not isinstance(work.get('id'), str) or not work['id']:
                raise RuntimeError('OpenAlex returned a work without an ID; collection is incomplete.')
            year = work.get('publication_year')
            if type(year) is not int or not start_year <= year <= end_year:
                raise RuntimeError('A returned work does not match the year query; collection is incomplete.')
            seen.add(work['id'])
        atomic_json(cache_dir / f'page-{state["pages"]:06d}.json', results)
        state.update(pages=state['pages'] + 1, next_cursor=next_cursor, unique_works=len(seen), updated_at=timestamp())
        if count not in state['api_counts']:
            state['api_counts'].append(count)
        atomic_json(state_path, state)
        print(f'Collected {len(seen):,} unique works; API reports {count:,}.', flush=True)
        if delay:
            time.sleep(delay)
    # Reconcile after exhaustion. A changed total cannot silently count as complete.
    final_count = response_count(fetch_page(works_url(query, count_only=True), mailto))
    if final_count not in state['api_counts']:
        state['api_counts'].append(final_count)
    state['final_api_count'] = final_count
    atomic_json(state_path, state)
    if state['api_counts'] != [final_count] or len(seen) != final_count:
        raise RuntimeError('Collected IDs do not reconcile with a stable API total. Start a fresh cache and retry; no dataset was published.')
    state.update(complete=True, completed_at=timestamp())
    atomic_json(state_path, state)
    return state


def extract_uiuc_coauthorship(works):
    """Retain papers with two distinct UIUC-affiliated authors, using exact IDs."""
    authors, papers, seen = {}, [], set()
    for work in works:
        if work['id'] in seen:
            continue
        seen.add(work['id'])
        if work.get('is_authors_truncated'):
            raise RuntimeError('Truncated authorships need resolution before publishing a complete relevant corpus.')
        retained = {}
        for authorship in work.get('authorships', []):
            author = authorship.get('author') or {}
            author_id = author.get('id')
            if not author_id:
                continue
            institutions = authorship.get('institutions') or []
            if any(inst.get('ror') == UIUC_ROR or (inst.get('id') or '').rstrip('/').split('/')[-1] == UIUC_INST_ID for inst in institutions):
                retained[author_id] = author.get('display_name') or author_id
        if len(retained) < 2:
            continue
        topics = [t['display_name'] for t in work.get('topics', []) if t.get('display_name')]
        for author_id, name in retained.items():
            record = authors.setdefault(author_id, {'id': author_id, 'name': name, 'topics': Counter(), 'paper_count': 0})
            record['paper_count'] += 1
            record['topics'].update(topics)
        papers.append({'id': work['id'], 'title': work.get('title') or 'Untitled',
                       'year': work['publication_year'], 'authors': sorted(retained), 'topics': topics,
                       'citations': work.get('cited_by_count', 0)})
    for record in authors.values():
        record['top_topics'] = [t for t, _ in record.pop('topics').most_common(10)]
    return {'authors': authors, 'papers': papers}


def run_harvest(out, cache_dir, mailto='', max_works=0, start_year=2015, end_year=2024, fetch_page=None, delay=1):
    fetch_page = fetch_page or fetch_openalex_page
    institution = fetch_page(OPENALEX_API + '/institutions/' + UIUC_INST_ID, mailto)
    if institution.get('ror') != UIUC_ROR or (institution.get('id') or '').split('/')[-1] != UIUC_INST_ID:
        raise RuntimeError('OpenAlex institution identity did not match UIUC; no dataset was published.')
    state = collect_works(mailto, cache_dir, max_works, start_year, end_year, fetch_page, delay)
    if not state['complete']:
        raise RuntimeError('Collection is capped/incomplete. Resume without --max_works; no dataset was published.')
    corpus = extract_uiuc_coauthorship(iter_cached_works(cache_dir, state))
    encoded = (json.dumps(corpus, indent=2) + '\n').encode()
    manifest = {key: value for key, value in state.items() if key != 'next_cursor'}
    manifest.update(dataset_file=Path(out).name, dataset_sha256=hashlib.sha256(encoded).hexdigest(),
                    retained_papers=len(corpus['papers']), retained_authors=len(corpus['authors']),
                    inclusion=f'{start_year}–{end_year} works with at least two distinct authors affiliated with UIUC on that work',
                    scope='Complete exhausted API traversal with reconciled work IDs; OpenAlex is mutable and not every real-world paper is indexed.')
    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.tmp')
    temporary.write_bytes(encoded)
    temporary.replace(target)
    atomic_json(target.with_suffix('.collection.json'), manifest)
    print(f'Published {len(corpus["papers"]):,} relevant papers from {state["unique_works"]:,} collected works.')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mailto', default='')
    parser.add_argument('--max_works', '--max-works', type=int, default=0, help='Zero means uncapped; a capped run only checkpoints and never publishes')
    parser.add_argument('--start-year', type=int, default=2015)
    parser.add_argument('--end-year', type=int, default=2024)
    parser.add_argument('--cache-dir', type=Path, default=Path('.build/openalex-full'))
    parser.add_argument('--out', type=Path, default=Path('prototype/uiuc_data_scaled.json'))
    args = parser.parse_args()
    try:
        run_harvest(args.out, args.cache_dir, args.mailto, args.max_works, args.start_year, args.end_year)
    except (RuntimeError, ValueError, OSError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
