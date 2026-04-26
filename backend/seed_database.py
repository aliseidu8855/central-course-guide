#!/usr/bin/env python3
"""
seed_database.py — Central Course Guide Database Seeder & Web Scraper

This script performs two phases:
  Phase 1 — Seeds the 10 official schools into MongoDB.
  Phase 2 — Scrapes central.edu.gh school pages for departments
            (programmes) and inserts them linked to their parent school.

Usage:
    # From the backend/ directory (with venv activated):
    pip install pymongo httpx beautifulsoup4
    python seed_database.py

Requirements (already in requirements.txt except scraping libs):
    pymongo, httpx, beautifulsoup4

The script is IDEMPOTENT: it drops and re-creates collections on every run
so you can re-run it safely without duplicating data.
"""

import logging
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


# Configuration

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "central_course_guide"
BASE_URL = "https://central.edu.gh"
REQUEST_TIMEOUT = 20  # seconds per HTTP request
SCRAPE_DELAY = 1.5    # polite delay between requests (seconds)


# Logging Setup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("seed")


# Authoritative list of schools — exactly as specified by the client.
# Each entry includes the official name and the URL slug used on
# central.edu.gh/schoolpage/{slug}.


SCHOOLS = [
    {"name": "School of Pharmacy",                       "slug": "sop",          "code": "SOP"},
    {"name": "Central Law School",                       "slug": "facultyoflaw", "code": "CLS"},
    {"name": "School of Medical Sciences",               "slug": "somah",        "code": "SMS"},
    {"name": "School of Nursing & Midwifery",            "slug": "snm",          "code": "SNM"},
    {"name": "School of Engineering & Technology",       "slug": "soeat",        "code": "SET"},
    {"name": "Faculty of Arts & Social Sciences",        "slug": "fass",         "code": "FASS"},
    {"name": "School of Architecture & Design",          "slug": "sad",          "code": "SAD"},
    {"name": "Central Business School",                  "slug": "cbs",          "code": "CBS"},
    {"name": "School of Graduate Studies & Research",    "slug": "sogs",         "code": "SGS"},
    {"name": "Centre for Distance & Professional Education", "slug": "code",     "code": "CDPE"},
]


# Text cleaning utilities

def clean_text(raw: str) -> str:
    """
    Normalize and clean scraped text:
      1. Unicode-normalize (NFKC) to collapse special whitespace chars.
      2. Replace non-breaking spaces, tabs, etc. with regular spaces.
      3. Collapse multiple spaces into one.
      4. Strip leading / trailing whitespace.
      5. Fix common HTML artefacts (e.g. &amp; already decoded by BS4).
    """
    if not raw:
        return ""
    # Step 1: Unicode normalization
    text = unicodedata.normalize("NFKC", raw)
    # Step 2-3: Collapse whitespace
    text = re.sub(r"[\s\u00a0\u200b\u200c\u200d\ufeff]+", " ", text)
    # Step 4: Strip
    text = text.strip()
    return text


def make_slug(name: str) -> str:
    """
    Generate a URL-safe slug from a name.
    e.g. "Central Law School" → "central-law-school"
    """
    slug = name.lower()
    slug = re.sub(r"[&]+", "and", slug)       # & → and
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)  # Remove non-alphanumeric
    slug = re.sub(r"[\s-]+", "-", slug)        # Spaces/hyphens → single hyphen
    return slug.strip("-")


def title_case_programme(raw: str) -> str:
    """
    Convert ALL-CAPS department names to proper Title Case.
    e.g. "COMPUTER SCIENCE AND INFORMATION TECHNOLOGY"
       → "Computer Science and Information Technology"
    
    Preserves words that are already mixed-case (e.g. 'PhD').
    """
    # Minor words that should stay lowercase (unless first word)
    minor_words = {"and", "or", "of", "the", "in", "for", "to", "a", "an"}
    words = raw.split()
    result = []
    for i, word in enumerate(words):
        # If the word is already mixed case (e.g. 'PhD'), keep it
        if not word.isupper() and not word.islower():
            result.append(word)
        elif word.lower() in minor_words and i > 0:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    return " ".join(result)


# Database connection

def connect_to_mongodb() -> MongoClient:
    """
    Establish a synchronous PyMongo connection and verify it's alive.
    Exits the script with a clear error message on failure.
    """
    log.info("Connecting to MongoDB at %s …", MONGO_URI)
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Force a connection check
        client.admin.command("ping")
        log.info("✅  MongoDB connection successful.")
        return client
    except ConnectionFailure as exc:
        log.error("❌  Could not connect to MongoDB: %s", exc)
        log.error("    Make sure mongod is running on %s", MONGO_URI)
        sys.exit(1)


# Phase 1: Seed Schools

def seed_schools(db) -> dict[str, str]:
    """
    Drop the 'schools' collection and insert the 10 official schools.
    
    Returns:
        A dict mapping school slug → inserted ObjectId (as string),
        used later to link programmes to their parent school.
    """
    log.info("=" * 60)
    log.info("PHASE 1 — Seeding Schools")
    log.info("=" * 60)

    col = db["schools"]
    col.drop()
    log.info("Dropped existing 'schools' collection.")

    documents = []
    for school in SCHOOLS:
        doc = {
            "name": school["name"],
            "code": school["code"],
            "slug": make_slug(school["name"]),
            "website_slug": school["slug"],       # slug used on central.edu.gh
            "url": f"{BASE_URL}/schoolpage/{school['slug']}",
            "description": None,
            "dean": None,
            "location": "Miotso Campus, Dawhenya, Accra",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        documents.append(doc)

    result = col.insert_many(documents)
    log.info("✅  Inserted %d schools.", len(result.inserted_ids))

    # Build lookup: website_slug → _id
    slug_to_id = {}
    for doc, oid in zip(SCHOOLS, result.inserted_ids):
        slug_to_id[doc["slug"]] = str(oid)
        log.info("    • %-50s  id=%s", doc["name"], oid)

    return slug_to_id


# Phase 2: Scraping Engine

def fetch_page(client: httpx.Client, url: str) -> Optional[BeautifulSoup]:
    """
    Fetch a single page and return a BeautifulSoup parse tree.
    Returns None on any failure (logged as a warning).
    """
    try:
        resp = client.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except httpx.HTTPStatusError as exc:
        log.warning("HTTP %d for %s", exc.response.status_code, url)
    except httpx.RequestError as exc:
        log.warning("Request failed for %s: %s", url, exc)
    except Exception as exc:
        log.warning("Unexpected error fetching %s: %s", url, exc)
    return None


def scrape_departments(soup: BeautifulSoup) -> list[dict]:
    """
    Extract department names and their /expand/{id} URLs from a school page.

    Site structure (observed across all school pages):
        <h4>DEPARTMENTS</h4>
        <a href="/expand/{id}">DEPT NAME</a>  (repeated)
        <h4>ADMINSTRATIVE STAFF</h4>
        <a href="/expand/{id}">STAFF NAME</a> (repeated)
        <h4>LECTURERS</h4>
        <a href="/expand/{id}">LECTURER NAME</a> (repeated)

    The page renders headings and links at the same DOM level, so we
    use document-order positions to extract only the links that fall
    between the DEPARTMENTS heading and the next section heading.

    Returns a list of dicts: [{"name": "...", "expand_url": "..."}, ...]
    """
    departments = []

    # Step 1: Locate ALL headings and ALL /expand/ links in the page,
    #         preserving their document order via sourceline/sourcepos.
    all_headings = soup.find_all(["h4", "h3", "h2", "h5"])
    all_expand_links = soup.find_all("a", href=lambda h: h and "/expand/" in h)

    # Find the DEPARTMENTS heading and the next section heading after it
    dept_heading = None
    next_section_heading = None
    section_keywords = ["ADMINSTRATIVE", "ADMINISTRATIVE", "LECTURERS", "STAFF"]

    for i, heading in enumerate(all_headings):
        heading_text = clean_text(heading.get_text()).upper()
        if "DEPARTMENT" in heading_text:
            dept_heading = heading
            # Look for the next heading that signals a different section
            for j in range(i + 1, len(all_headings)):
                next_text = clean_text(all_headings[j].get_text()).upper()
                if any(kw in next_text for kw in section_keywords):
                    next_section_heading = all_headings[j]
                    break
            break

    if dept_heading is None:
        log.warning("    No DEPARTMENTS heading found on page.")
        return departments

    # Step 2: Use find_all_next to get all /expand/ links that come
    #         AFTER the DEPARTMENTS heading in document order.
    #         Stop when we hit the next section heading.
    links_after_dept = dept_heading.find_all_next("a", href=lambda h: h and "/expand/" in h)

    # If we found a next section heading, also get all links after it
    # so we can exclude them.
    links_to_exclude = set()
    if next_section_heading:
        for link in next_section_heading.find_all_next("a", href=lambda h: h and "/expand/" in h):
            links_to_exclude.add(id(link))

    # Collect only the links between DEPARTMENTS and the next section
    seen_ids = set()
    for link in links_after_dept:
        if id(link) in links_to_exclude:
            continue

        href = link.get("href", "")
        expand_id = href.split("/")[-1]

        if expand_id in seen_ids:
            continue
        seen_ids.add(expand_id)

        name = clean_text(link.get_text())
        if not name:
            continue

        departments.append({
            "raw_name": name,
            "name": title_case_programme(clean_text(name)),
            "expand_url": BASE_URL + (href if href.startswith("/") else "/" + href),
            "expand_id": expand_id,
        })

    return departments


def scrape_all_schools(
    db,
    slug_to_id: dict[str, str],
    http_client: httpx.Client,
) -> int:
    """
    Phase 2: For each school, scrape its page on central.edu.gh,
    extract department/programme names, and insert them into MongoDB.

    Returns the total number of programmes inserted.
    """
    log.info("")
    log.info("=" * 60)
    log.info("PHASE 2 — Scraping Programmes from central.edu.gh")
    log.info("=" * 60)

    col = db["programmes"]
    col.drop()
    log.info("Dropped existing 'programmes' collection.")

    total_inserted = 0

    for school in SCHOOLS:
        school_name = school["name"]
        school_slug = school["slug"]
        school_id = slug_to_id[school_slug]
        url = f"{BASE_URL}/schoolpage/{school_slug}"

        log.info("")
        log.info("─" * 50)
        log.info("Scraping: %s", school_name)
        log.info("URL:      %s", url)
        log.info("─" * 50)

        try:
            soup = fetch_page(http_client, url)
            if soup is None:
                log.warning("⚠️  SKIPPED %s — page fetch failed.", school_name)
                continue

            departments = scrape_departments(soup)

            if not departments:
                log.warning(
                    "⚠️  No departments found for %s. "
                    "The page structure may differ or content may be JS-rendered.",
                    school_name,
                )
                continue

            # Build programme documents
            programme_docs = []
            for dept in departments:
                doc = {
                    "name": dept["name"],
                    "raw_name": dept["raw_name"],
                    "slug": make_slug(dept["name"]),
                    "school_id": school_id,
                    "school_name": school_name,
                    "source_url": dept["expand_url"],
                    "source_id": dept["expand_id"],
                    "code": None,          # Not available from scraping
                    "duration_years": None, # Not available from scraping
                    "description": None,
                    "career_paths": [],
                    "is_reviewed": False,   # Flag for admin panel review
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                programme_docs.append(doc)

            result = col.insert_many(programme_docs)
            count = len(result.inserted_ids)
            total_inserted += count

            for dept in departments:
                log.info("    ✓ %s", dept["name"])

            log.info("    → Inserted %d programme(s) for %s.", count, school_name)

        except Exception as exc:
            log.error(
                "❌  Unexpected error scraping %s: %s",
                school_name,
                exc,
                exc_info=True,
            )
            log.info("    Continuing with remaining schools…")

        # Be polite to the server
        time.sleep(SCRAPE_DELAY)

    return total_inserted


# Phase 3: Post-scrape data quality report

def print_summary(db, total_programmes: int):
    """Print a summary of what ended up in the database."""
    log.info("")
    log.info("=" * 60)
    log.info("SEED COMPLETE — Summary")
    log.info("=" * 60)

    schools_count = db["schools"].count_documents({})
    programmes_count = db["programmes"].count_documents({})

    log.info("  Schools in DB:     %d", schools_count)
    log.info("  Programmes in DB:  %d", programmes_count)
    log.info("")

    # Per-school breakdown
    log.info("  Per-school breakdown:")
    for school in db["schools"].find({}, {"name": 1}):
        prog_count = db["programmes"].count_documents(
            {"school_id": str(school["_id"])}
        )
        marker = "⚠️ " if prog_count == 0 else "  "
        log.info("    %s%-50s  %d programme(s)", marker, school["name"], prog_count)

    # Flag any programmes that look like they need review
    suspect = db["programmes"].count_documents({"is_reviewed": False})
    if suspect > 0:
        log.info("")
        log.info(
            "  ℹ️  %d programme(s) flagged for review in the admin panel.",
            suspect,
        )
        log.info(
            "     Run the FastAPI server and visit http://localhost:8000/admin/programmes"
        )


# Main entry point

def main():
    """Orchestrate the full seed + scrape pipeline."""
    log.info("🚀  Central Course Guide — Database Seeder v1.0")
    log.info("")

    # 1. Connect
    client = connect_to_mongodb()
    db = client[DATABASE_NAME]

    # 2. Phase 1 — Seed schools
    slug_to_id = seed_schools(db)

    # 3. Phase 2 — Scrape programmes
    with httpx.Client(
        headers={
            "User-Agent": (
                "CentralCourseGuide-Seeder/1.0 "
                "(educational project; contact: admin@central-course-guide.local)"
            ),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        },
        follow_redirects=True,
    ) as http_client:
        total = scrape_all_schools(db, slug_to_id, http_client)

    # 4. Summary
    print_summary(db, total)

    # 5. Create indexes for query performance
    log.info("")
    log.info("Creating indexes…")
    db["schools"].create_index("slug", unique=True)
    db["schools"].create_index("code", unique=True)
    db["programmes"].create_index("school_id")
    db["programmes"].create_index("slug")
    db["programmes"].create_index("is_reviewed")
    log.info("✅  Indexes created.")

    log.info("")
    log.info("🏁  All done! Database '%s' is ready.", DATABASE_NAME)
    client.close()


if __name__ == "__main__":
    main()
