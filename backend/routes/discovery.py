"""
routes/discovery.py — Public API Routes for Course Discovery

Powers the interest quiz, the browse-all-programmes page, and the
composition breakdown UI:

  • GET  /interests               — the fixed interest taxonomy.
  • GET  /composition-dimensions  — the fixed composition vocabulary.
  • GET  /programmes              — every programme, for browsing/filtering.
  • POST /recommendations         — score programmes against selected interests.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from database import get_database
from models.taxonomy import (
    COMPOSITION_DIMENSIONS,
    INTERESTS,
    INTERESTS_BY_ID,
    clean_interest_tags,
    programme_level,
)
from routes.schools import serialize_doc

router = APIRouter(tags=["Discovery"])

db = get_database()


class RecommendationRequest(BaseModel):
    """Quiz answers sent by the frontend."""
    interests: list[str] = Field(
        ...,
        min_length=1,
        max_length=14,
        description="Interest ids picked by the student (see GET /interests).",
    )
    include_postgraduate: bool = Field(
        default=False,
        description="Also consider postgraduate/professional programmes.",
    )
    limit: int = Field(
        default=8,
        ge=1,
        le=40,
        description="Maximum number of recommendations to return.",
    )

    @field_validator("interests")
    @classmethod
    def _validate_interests(cls, v: list[str]) -> list[str]:
        return clean_interest_tags(v)


@router.get("/interests")
async def list_interests():
    """Return the fixed interest taxonomy used by the quiz and admin panel."""
    return INTERESTS


@router.get("/composition-dimensions")
async def list_composition_dimensions():
    """Return the fixed composition dimensions (id + label)."""
    return COMPOSITION_DIMENSIONS


@router.get("/programmes")
async def list_programmes():
    """Return all programmes with their derived level, for the browse page."""
    programmes = []
    async for prog in db["programmes"].find().sort("name", 1):
        doc = serialize_doc(prog)
        doc["level"] = programme_level(doc.get("degree_type"))
        programmes.append(doc)
    return programmes


@router.post("/recommendations")
async def recommend_programmes(request: RecommendationRequest):
    """
    Score programmes against the student's selected interests.

    Ranking: most matched interests first, then the share of the
    programme's own tags that matched (focused programmes beat broad
    ones), undergraduate before postgraduate, then name.
    """
    selected = set(request.interests)

    scored = []
    async for prog in db["programmes"].find(
        {"interest_tags": {"$exists": True, "$ne": []}}
    ):
        level = programme_level(prog.get("degree_type"))
        if level == "postgraduate" and not request.include_postgraduate:
            continue

        tags = prog.get("interest_tags") or []
        matched = [t for t in tags if t in selected]
        if not matched:
            continue

        doc = serialize_doc(prog)
        doc["level"] = level
        scored.append(
            {
                "programme": doc,
                "match_count": len(matched),
                "coverage": len(matched) / len(tags),
                "matched": [INTERESTS_BY_ID[t] for t in matched],
            }
        )

    scored.sort(
        key=lambda r: (
            -r["match_count"],
            -r["coverage"],
            0 if r["programme"]["level"] == "undergraduate" else 1,
            r["programme"].get("name", ""),
        )
    )

    return {
        "selected": [INTERESTS_BY_ID[t] for t in request.interests],
        "total_considered": len(scored),
        "results": [
            {
                "programme": r["programme"],
                "match_count": r["match_count"],
                "score": round(100 * r["match_count"] / len(selected)),
                "matched": r["matched"],
            }
            for r in scored[: request.limit]
        ],
    }
