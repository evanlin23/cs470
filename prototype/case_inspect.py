"""Print a transfer paper's references with their OpenAlex fields (to write leakage-safe cases)."""
import json, sys
import fetch_openalex as F

for doi in sys.argv[1:]:
    tw = F.lookup(dois=[doi]) if doi.startswith("10.") else F.lookup(ids=[doi])
    if not tw:
        print("NOT FOUND", doi); continue
    w = list(tw.values())[0]
    m = F.meta_of(w)
    refs = [F.short(r) for r in w.get("referenced_works") or []]
    print(f"\n=== {doi} {m['year']} {m['title'][:80]} | field={m['field']} | {len(refs)} refs indexed")
    rw = F.lookup(ids=refs)
    for r in refs:
        x = rw.get(r)
        if not x: print("   ?", r); continue
        mm = F.meta_of(x)
        print(f"   {F.ident(x):45} {mm['year']} [{(mm['field'] or '-')[:22]:22}] {mm['title'][:70]} | {mm['venue'][:30]}")
