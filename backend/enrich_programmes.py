"""
enrich_programmes.py — Seed Interest Tags & Composition Percentages
===================================================================

Applies the curated interest tags and study-time composition for all
programmes, keyed by slug:

  1. To the live MongoDB database — via $set on ONLY these two fields
     (plus updated_at), so admin-panel edits to names, descriptions,
     etc. always survive re-runs.
  2. To ../database_dump/programmes.json — so fresh installs get the
     fields straight from import_database.py.

Usage:
    python enrich_programmes.py             # seed DB + dump from CURATION
    python enrich_programmes.py --db-only   # seed only the database
    python enrich_programmes.py --dump-only # seed only the JSON dump
    python enrich_programmes.py --pull      # reverse: copy DB values into
                                            # the dump (after admin curation)
"""

import json
import os
import sys
from datetime import datetime, timezone

from pymongo import MongoClient

from models.taxonomy import DIMENSION_IDS, INTEREST_IDS

# Configuration (matches import_database.py)
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "central_course_guide"
DUMP_FILE = os.path.join(os.path.dirname(__file__), "..", "database_dump", "programmes.json")

# ---------------------------------------------------------------------------
# Curated data — interest tags + composition per programme slug.
# Compositions must sum to exactly 100 (validated at startup).
# ---------------------------------------------------------------------------
CURATION: dict[str, dict] = {
    # --- Health & Sciences ---
    "doctor-of-pharmacy-pharmd-top-up": {
        "interest_tags": ["health", "science"],
        "composition": {"theory": 30, "practicals": 40, "mathematics": 10, "people": 20},
    },
    "pharmacy": {
        "interest_tags": ["health", "science"],
        "composition": {"theory": 35, "practicals": 35, "mathematics": 15, "people": 15},
    },
    "public-health": {
        "interest_tags": ["health", "society", "science"],
        "composition": {"theory": 35, "practicals": 25, "mathematics": 15, "people": 25},
    },
    "physician-assistantship": {
        "interest_tags": ["health", "science"],
        "composition": {"theory": 30, "practicals": 45, "people": 25},
    },
    "nursing": {
        "interest_tags": ["health", "science"],
        "composition": {"theory": 30, "practicals": 45, "people": 25},
    },
    "master-of-public-health": {
        "interest_tags": ["health", "society"],
        "composition": {"theory": 35, "practicals": 25, "mathematics": 15, "people": 25},
    },
    # --- Law ---
    "laws": {
        "interest_tags": ["law", "society"],
        "composition": {"theory": 55, "people": 25, "practicals": 20},
    },
    # --- Engineering, IT & Built Environment ---
    "civil-engineering": {
        "interest_tags": ["building", "numbers"],
        "composition": {"mathematics": 35, "practicals": 30, "theory": 20, "coding": 10, "creativity": 5},
    },
    "computer-science-and-information-technology": {
        "interest_tags": ["technology", "numbers"],
        "composition": {"coding": 45, "mathematics": 20, "theory": 20, "practicals": 15},
    },
    "bsc-real-estate": {
        "interest_tags": ["business", "building", "numbers"],
        "composition": {"theory": 30, "mathematics": 25, "practicals": 20, "people": 25},
    },
    "bsc-planning": {
        "interest_tags": ["building", "society", "environment"],
        "composition": {"theory": 30, "practicals": 25, "creativity": 15, "mathematics": 15, "people": 15},
    },
    "bachelor-of-architecture": {
        "interest_tags": ["building", "creativity"],
        "composition": {"creativity": 40, "practicals": 30, "mathematics": 15, "theory": 15},
    },
    # --- Design ---
    "bachelor-of-science-in-fashion-design": {
        "interest_tags": ["creativity", "business"],
        "composition": {"creativity": 45, "practicals": 35, "theory": 10, "people": 10},
    },
    "bachelor-of-science-in-interior-design": {
        "interest_tags": ["creativity", "building"],
        "composition": {"creativity": 45, "practicals": 30, "theory": 15, "mathematics": 10},
    },
    "bachelor-of-scienc-in-landscape-design": {
        "interest_tags": ["creativity", "environment", "building"],
        "composition": {"creativity": 40, "practicals": 35, "theory": 15, "mathematics": 10},
    },
    "bachelor-of-science-in-graphic-design": {
        "interest_tags": ["creativity", "media", "technology"],
        "composition": {"creativity": 50, "practicals": 25, "coding": 10, "theory": 15},
    },
    # --- Arts & Social Sciences ---
    "communication-and-media-studies": {
        "interest_tags": ["media", "creativity", "society"],
        "composition": {"theory": 30, "creativity": 30, "practicals": 20, "people": 20},
    },
    "economics-and-development-studies": {
        "interest_tags": ["numbers", "society", "business"],
        "composition": {"mathematics": 35, "theory": 40, "people": 10, "practicals": 15},
    },
    "social-sciences": {
        "interest_tags": ["society", "leadership"],
        "composition": {"theory": 45, "people": 30, "practicals": 15, "mathematics": 10},
    },
    "master-of-arts-in-development-policy": {
        "interest_tags": ["society", "leadership"],
        "composition": {"theory": 45, "people": 25, "practicals": 20, "mathematics": 10},
    },
    "master-of-philosophy-in-development-policy": {
        "interest_tags": ["society", "leadership"],
        "composition": {"theory": 50, "people": 20, "practicals": 15, "mathematics": 15},
    },
    "mphil-economics": {
        "interest_tags": ["numbers", "society"],
        "composition": {"mathematics": 45, "theory": 40, "practicals": 10, "people": 5},
    },
    # --- Business ---
    "marketing": {
        "interest_tags": ["business", "media"],
        "composition": {"theory": 30, "people": 30, "creativity": 20, "practicals": 20},
    },
    "management-and-public-administration": {
        "interest_tags": ["leadership", "business", "society"],
        "composition": {"theory": 40, "people": 35, "practicals": 15, "mathematics": 10},
    },
    "human-resource-management": {
        "interest_tags": ["leadership", "business"],
        "composition": {"theory": 35, "people": 40, "practicals": 15, "mathematics": 10},
    },
    "accounting": {
        "interest_tags": ["numbers", "business"],
        "composition": {"mathematics": 45, "theory": 30, "practicals": 15, "people": 10},
    },
    "banking-and-finance": {
        "interest_tags": ["numbers", "business"],
        "composition": {"mathematics": 40, "theory": 30, "practicals": 15, "people": 15},
    },
    "doctor-of-business-administration-dba": {
        "interest_tags": ["business", "leadership"],
        "composition": {"theory": 50, "people": 20, "practicals": 20, "mathematics": 10},
    },
    "phd-finance": {
        "interest_tags": ["numbers", "business"],
        "composition": {"mathematics": 40, "theory": 45, "practicals": 10, "people": 5},
    },
    "msc-accounting": {
        "interest_tags": ["numbers", "business"],
        "composition": {"mathematics": 40, "theory": 35, "practicals": 15, "people": 10},
    },
    "mphll-accounting": {
        "interest_tags": ["numbers", "business"],
        "composition": {"mathematics": 35, "theory": 45, "practicals": 10, "people": 10},
    },
    "mba-finance": {
        "interest_tags": ["numbers", "business"],
        "composition": {"mathematics": 35, "theory": 30, "people": 20, "practicals": 15},
    },
    "mba-general-management": {
        "interest_tags": ["leadership", "business"],
        "composition": {"theory": 35, "people": 35, "practicals": 20, "mathematics": 10},
    },
    "mba-human-resource-management": {
        "interest_tags": ["leadership", "business"],
        "composition": {"theory": 35, "people": 40, "practicals": 15, "mathematics": 10},
    },
    "mba-marketing": {
        "interest_tags": ["business", "media"],
        "composition": {"theory": 30, "people": 30, "creativity": 20, "practicals": 20},
    },
    "mba-agribusiness": {
        "interest_tags": ["business", "environment"],
        "composition": {"theory": 30, "practicals": 25, "mathematics": 20, "people": 25},
    },
    "mba-project-management-option": {
        "interest_tags": ["leadership", "building", "business"],
        "composition": {"theory": 30, "people": 30, "practicals": 25, "mathematics": 15},
    },
    # --- Theology & Education ---
    "ma-religious-studies": {
        "interest_tags": ["faith", "society", "teaching"],
        "composition": {"theory": 60, "people": 25, "practicals": 15},
    },
    "mphil-theology": {
        "interest_tags": ["faith", "teaching"],
        "composition": {"theory": 65, "people": 20, "practicals": 15},
    },
    "award-for-training-in-higher-education-athe": {
        "interest_tags": ["teaching", "leadership"],
        "composition": {"theory": 35, "people": 35, "practicals": 30},
    },
}


def validate_curation():
    """Abort loudly if any curated entry violates the taxonomy rules."""
    errors = []
    for slug, data in CURATION.items():
        for tag in data["interest_tags"]:
            if tag not in INTEREST_IDS:
                errors.append(f"{slug}: unknown interest tag {tag!r}")
        comp = data["composition"]
        for dim in comp:
            if dim not in DIMENSION_IDS:
                errors.append(f"{slug}: unknown composition dimension {dim!r}")
        total = sum(comp.values())
        if total != 100:
            errors.append(f"{slug}: composition totals {total}, expected 100")
    if errors:
        print("Curation data is invalid:")
        for err in errors:
            print(f"    - {err}")
        sys.exit(1)


def load_dump() -> list[dict]:
    with open(DUMP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dump(docs: list[dict]):
    with open(DUMP_FILE, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)
        f.write("\n")


def seed_database(db):
    """$set curated fields on the live DB, keyed by slug."""
    updated, missing = 0, []
    for slug, data in CURATION.items():
        result = db["programmes"].update_one(
            {"slug": slug},
            {"$set": {
                "interest_tags": data["interest_tags"],
                "composition": data["composition"],
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        if result.matched_count:
            updated += 1
        else:
            missing.append(slug)

    print(f"Database: enriched {updated} programme(s)")
    for slug in missing:
        print(f"Slug not found in DB: {slug}")

    uncurated = db["programmes"].count_documents({"slug": {"$nin": list(CURATION)}})
    if uncurated:
        print(f"{uncurated} programme(s) in DB have no curation entry")


def seed_dump():
    """Merge curated fields into database_dump/programmes.json, keyed by slug."""
    docs = load_dump()
    updated, uncurated = 0, []
    for doc in docs:
        data = CURATION.get(doc.get("slug"))
        if data:
            doc["interest_tags"] = data["interest_tags"]
            doc["composition"] = data["composition"]
            updated += 1
        else:
            uncurated.append(doc.get("slug"))
    save_dump(docs)

    print(f"Dump: enriched {updated}/{len(docs)} programme(s)")
    for slug in uncurated:
        print(f"No curation entry for dump programme: {slug}")


def pull_from_db(db):
    """Reverse direction: copy interest_tags/composition from the DB into the dump."""
    docs = load_dump()
    updated = 0
    for doc in docs:
        live = db["programmes"].find_one(
            {"slug": doc.get("slug")},
            {"interest_tags": 1, "composition": 1},
        )
        if live is None:
            print(f"Slug not found in DB: {doc.get('slug')}")
            continue
        doc["interest_tags"] = live.get("interest_tags", [])
        doc["composition"] = live.get("composition", {})
        updated += 1
    save_dump(docs)
    print(f"Dump: pulled tags/composition from DB for {updated}/{len(docs)} programme(s)")


def connect():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command("ping")
    return client[DATABASE_NAME]


def main():
    validate_curation()
    args = set(sys.argv[1:])

    try:
        if "--pull" in args:
            pull_from_db(connect())
        elif "--dump-only" in args:
            seed_dump()
        elif "--db-only" in args:
            seed_database(connect())
        else:
            seed_database(connect())
            seed_dump()
        print("\nEnrichment complete!")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MongoDB is running on localhost:27017")
        sys.exit(1)


if __name__ == "__main__":
    main()
