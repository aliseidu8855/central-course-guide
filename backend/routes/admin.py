"""
routes/admin.py — Admin Panel API Routes
=========================================

Provides CRUD endpoints for reviewing, editing, and managing
scraped programme data. These endpoints power the admin panel UI.

All routes are prefixed with /admin when included in main.py.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from database import get_database
from models.taxonomy import clean_composition, clean_interest_tags

router = APIRouter(prefix="/admin", tags=["Admin"])

db = get_database()


# ============================================================================
# Pydantic models for admin operations
# ============================================================================

class ProgrammeUpdate(BaseModel):
    """Fields that can be updated via the admin panel."""
    name: Optional[str] = None
    code: Optional[str] = None
    duration_years: Optional[int] = None
    description: Optional[str] = None
    career_paths: Optional[list[str]] = None
    is_reviewed: Optional[bool] = None
    # Sending [] / {} clears the field (update_programme only skips None).
    interest_tags: Optional[list[str]] = None
    composition: Optional[dict[str, int]] = None

    @field_validator("interest_tags")
    @classmethod
    def _validate_interest_tags(cls, v):
        return v if v is None else clean_interest_tags(v)

    @field_validator("composition")
    @classmethod
    def _validate_composition(cls, v):
        return v if v is None else clean_composition(v)


class ProgrammeOut(BaseModel):
    """Programme as returned to the admin panel."""
    id: str = Field(alias="_id")
    name: str
    raw_name: Optional[str] = None
    slug: str
    school_id: str
    school_name: str
    code: Optional[str] = None
    duration_years: Optional[int] = None
    degree_type: Optional[str] = None
    description: Optional[str] = None
    career_paths: list[str] = []
    subjects: list[str] = []
    entry_requirements: list[str] = []
    interest_tags: list[str] = []
    composition: dict[str, int] = {}
    source_url: Optional[str] = None
    is_reviewed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"populate_by_name": True}


class SchoolOut(BaseModel):
    """School as returned to the admin panel."""
    id: str = Field(alias="_id")
    name: str
    code: str
    slug: str
    url: Optional[str] = None
    description: Optional[str] = None
    dean: Optional[str] = None
    location: Optional[str] = None
    programme_count: int = 0

    model_config = {"populate_by_name": True}


class StatsOut(BaseModel):
    """Dashboard statistics."""
    total_schools: int
    total_programmes: int
    reviewed_programmes: int
    unreviewed_programmes: int


# ============================================================================
# Helper to serialize MongoDB documents
# ============================================================================

def serialize_doc(doc: dict) -> dict:
    """Convert ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ============================================================================
# Routes
# ============================================================================

@router.get("/stats", response_model=StatsOut)
async def get_stats():
    """Get dashboard statistics — school/programme counts and review status."""
    total_schools = await db["schools"].count_documents({})
    total_programmes = await db["programmes"].count_documents({})
    reviewed = await db["programmes"].count_documents({"is_reviewed": True})
    unreviewed = await db["programmes"].count_documents({"is_reviewed": False})

    return StatsOut(
        total_schools=total_schools,
        total_programmes=total_programmes,
        reviewed_programmes=reviewed,
        unreviewed_programmes=unreviewed,
    )


@router.get("/schools")
async def list_schools():
    """List all schools with their programme counts."""
    schools = []
    async for school in db["schools"].find().sort("name", 1):
        school_id = str(school["_id"])
        prog_count = await db["programmes"].count_documents(
            {"school_id": school_id}
        )
        doc = serialize_doc(school)
        doc["programme_count"] = prog_count
        schools.append(doc)
    return schools


@router.get("/programmes")
async def list_programmes(
    school_id: Optional[str] = Query(None, description="Filter by school ID"),
    reviewed: Optional[bool] = Query(None, description="Filter by review status"),
):
    """
    List programmes with optional filters.
    Used by the admin panel to show all programmes or filter by school / review status.
    """
    query = {}
    if school_id:
        query["school_id"] = school_id
    if reviewed is not None:
        query["is_reviewed"] = reviewed

    programmes = []
    async for prog in db["programmes"].find(query).sort("name", 1):
        programmes.append(serialize_doc(prog))

    return programmes


@router.get("/programmes/{programme_id}")
async def get_programme(programme_id: str):
    """Get a single programme by ID."""
    try:
        doc = await db["programmes"].find_one({"_id": ObjectId(programme_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid programme ID format.")

    if not doc:
        raise HTTPException(status_code=404, detail="Programme not found.")

    return serialize_doc(doc)


@router.put("/programmes/{programme_id}")
async def update_programme(programme_id: str, updates: ProgrammeUpdate):
    """
    Update a programme's fields. The admin uses this to:
      - Clean up names
      - Add codes, descriptions, career paths
      - Mark as reviewed
    """
    try:
        oid = ObjectId(programme_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid programme ID format.")

    # Build the $set payload from non-None fields
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await db["programmes"].update_one(
        {"_id": oid},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Programme not found.")

    # Return the updated document
    doc = await db["programmes"].find_one({"_id": oid})
    return serialize_doc(doc)


@router.delete("/programmes/{programme_id}")
async def delete_programme(programme_id: str):
    """Delete a programme (e.g. if it was scraped incorrectly)."""
    try:
        oid = ObjectId(programme_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid programme ID format.")

    result = await db["programmes"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Programme not found.")

    return {"detail": "Programme deleted.", "id": programme_id}


@router.post("/programmes/{programme_id}/review")
async def mark_reviewed(programme_id: str):
    """Mark a single programme as reviewed."""
    try:
        oid = ObjectId(programme_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid programme ID format.")

    result = await db["programmes"].update_one(
        {"_id": oid},
        {"$set": {"is_reviewed": True, "updated_at": datetime.now(timezone.utc)}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Programme not found.")

    return {"detail": "Marked as reviewed.", "id": programme_id}


@router.post("/programmes/review-all")
async def mark_all_reviewed():
    """Mark ALL programmes as reviewed (bulk action)."""
    result = await db["programmes"].update_many(
        {"is_reviewed": False},
        {"$set": {"is_reviewed": True, "updated_at": datetime.now(timezone.utc)}},
    )
    return {
        "detail": f"Marked {result.modified_count} programme(s) as reviewed.",
        "modified_count": result.modified_count,
    }
