"""
taxonomy.py — Interest & Composition Vocabularies (Single Source of Truth)
==========================================================================

Fixed vocabularies used by the interest quiz and the "what you'll spend
your time on" composition breakdown:

  • INTERESTS               — the interests a student can pick in the quiz.
  • COMPOSITION_DIMENSIONS  — the study-time dimensions a programme can
                              be described with (percentages summing to 100).

The public API (GET /interests, POST /recommendations), the admin panel,
and enrich_programmes.py all import from here so ids can never drift
between layers.

Display icons are rendered client-side as inline SVGs keyed by id
(frontend/src/components/Icons.jsx) — no emoji anywhere.
"""

# ===================================================================
# Interests
# ===================================================================

INTERESTS: list[dict] = [
    {"id": "technology",  "label": "Computers, Tech & Gaming"},
    {"id": "science",     "label": "Science & the Lab"},
    {"id": "health",      "label": "Caring for People & Health"},
    {"id": "numbers",     "label": "Numbers & Money"},
    {"id": "business",    "label": "Business & Entrepreneurship"},
    {"id": "leadership",  "label": "Leading & Organising People"},
    {"id": "law",         "label": "Law, Justice & Debating"},
    {"id": "media",       "label": "Media, Writing & Storytelling"},
    {"id": "creativity",  "label": "Art, Music & Creativity"},
    {"id": "building",    "label": "Building & Making Things"},
    {"id": "society",     "label": "Society, Politics & Communities"},
    {"id": "faith",       "label": "Faith & Ministry"},
    {"id": "teaching",    "label": "Teaching & Training"},
    {"id": "environment", "label": "Nature, Environment & Agriculture"},
]

INTEREST_IDS: set[str] = {i["id"] for i in INTERESTS}
INTERESTS_BY_ID: dict[str, dict] = {i["id"]: i for i in INTERESTS}


# ===================================================================
# Composition dimensions
# ===================================================================
# Each programme stores a subset of these as {dimension_id: percent}.
# Stored percentages must sum to exactly 100; an empty dict means the
# programme has not been curated yet (the UI hides the section).

COMPOSITION_DIMENSIONS: list[dict] = [
    {"id": "coding",      "label": "Coding & Software"},
    {"id": "mathematics", "label": "Maths & Calculations"},
    {"id": "theory",      "label": "Theory & Reading"},
    {"id": "practicals",  "label": "Practicals & Fieldwork"},
    {"id": "creativity",  "label": "Design & Creativity"},
    {"id": "people",      "label": "People & Communication"},
]

DIMENSION_IDS: set[str] = {d["id"] for d in COMPOSITION_DIMENSIONS}


# ===================================================================
# Programme level (undergraduate vs postgraduate)
# ===================================================================

UNDERGRAD_DEGREE_TYPES: set[str] = {"BSc", "BA", "BPharm", "LLB", "BArch"}


def programme_level(degree_type) -> str:
    """Classify a programme from its degree type. Unknown/missing → undergraduate."""
    if not degree_type or degree_type in UNDERGRAD_DEGREE_TYPES:
        return "undergraduate"
    return "postgraduate"


# ===================================================================
# Validators (shared by the admin API and enrich_programmes.py)
# ===================================================================

def clean_interest_tags(tags: list) -> list[str]:
    """Deduplicate interest tags preserving order. Raises ValueError on unknown ids."""
    cleaned: list[str] = []
    for tag in tags:
        if tag not in INTEREST_IDS:
            raise ValueError(f"Unknown interest tag: {tag!r}")
        if tag not in cleaned:
            cleaned.append(tag)
    return cleaned


def clean_composition(comp: dict) -> dict:
    """
    Validate a composition dict {dimension_id: percent}.

    Keys must be known dimensions, values integers 0–100. Zero values are
    dropped; the remaining values must sum to exactly 100 — unless the
    dict ends up empty ({} = not curated).
    """
    cleaned: dict[str, int] = {}
    for dim, value in comp.items():
        if dim not in DIMENSION_IDS:
            raise ValueError(f"Unknown composition dimension: {dim!r}")
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
            raise ValueError(f"Composition value for {dim!r} must be an integer 0–100.")
        if value > 0:
            cleaned[dim] = value
    total = sum(cleaned.values())
    if cleaned and total != 100:
        raise ValueError(f"Composition percentages must total exactly 100 (got {total}).")
    return cleaned
