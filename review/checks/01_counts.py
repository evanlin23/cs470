"""Check 1: UIUC institution, work/author counts 2015-2024, metadata completeness."""
import json, oa
UIUC = "I157725225"
F = f"institutions.id:{UIUC},publication_year:2015-2024"
out = {}
out["works_2015_2024"] = oa.get("/works", filter=F, per_page=1)["meta"]["count"]
out["works_by_year"] = {g["key"]: g["count"] for g in oa.get("/works", filter=F, group_by="publication_year")["group_by"]}
out["works_by_type"] = {g["key_display_name"]: g["count"] for g in oa.get("/works", filter=F, group_by="type")["group_by"]}
out["has_primary_topic"] = {g["key"]: g["count"] for g in oa.get("/works", filter=F, group_by="primary_topic.id")["group_by"][:0]}  # placeholder
out["topic_missing"] = oa.get("/works", filter=F + ",primary_topic.id:null", per_page=1)["meta"]["count"]
out["domains"] = {g["key_display_name"]: g["count"] for g in oa.get("/works", filter=F, group_by="primary_topic.domain.id")["group_by"]}
out["fields_top"] = {g["key_display_name"]: g["count"] for g in oa.get("/works", filter=F, group_by="primary_topic.field.id")["group_by"][:15]}
# authors whose last-known institution is UIUC (OpenAlex author entity)
out["authors_last_known_uiuc"] = oa.get("/authors", filter=f"last_known_institutions.id:{UIUC}", per_page=1)["meta"]["count"]
out["authors_affiliated_ever"] = oa.get("/authors", filter=f"affiliations.institution.id:{UIUC}", per_page=1)["meta"]["count"]
out["articles_2015_2024"] = oa.get("/works", filter=F + ",type:article", per_page=1)["meta"]["count"]
out.pop("has_primary_topic")
json.dump(out, open("results_01_counts.json", "w"), indent=1)
print(json.dumps(out, indent=1))
