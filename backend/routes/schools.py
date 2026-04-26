"""
routes/schools.py — Public API Routes for Schools & Programmes

These are the frontend-facing read-only endpoints that the React app
calls to display data to students.
"""

from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from database import get_database

router = APIRouter(tags=["Schools"])

db = get_database()


def serialize_doc(doc: dict) -> dict:
    """Convert ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("/schools")
async def list_schools():
    """Return all schools with their programme counts, sorted alphabetically."""
    schools = []
    async for school in db["schools"].find().sort("name", 1):
        school_id = str(school["_id"])
        prog_count = await db["programmes"].count_documents({"school_id": school_id})
        doc = serialize_doc(school)
        doc["programme_count"] = prog_count
        schools.append(doc)
    return schools


@router.get("/schools/{school_id}")
async def get_school(school_id: str):
    """Get a single school by its MongoDB _id, including programme count."""
    try:
        doc = await db["schools"].find_one({"_id": ObjectId(school_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid school ID.")

    if not doc:
        raise HTTPException(status_code=404, detail="School not found.")

    doc = serialize_doc(doc)
    doc["programme_count"] = await db["programmes"].count_documents(
        {"school_id": school_id}
    )
    return doc


@router.get("/schools/{school_id}/programmes")
async def get_school_programmes(school_id: str):
    """Get all programmes under a specific school."""
    programmes = []
    async for prog in db["programmes"].find(
        {"school_id": school_id}
    ).sort("name", 1):
        programmes.append(serialize_doc(prog))

    return programmes


@router.get("/programmes/{programme_id}")
async def get_programme(programme_id: str):
    """Get a single programme by its MongoDB _id."""
    try:
        doc = await db["programmes"].find_one({"_id": ObjectId(programme_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid programme ID.")

    if not doc:
        raise HTTPException(status_code=404, detail="Programme not found.")

    # Also fetch the parent school info
    prog = serialize_doc(doc)
    if prog.get("school_id"):
        try:
            school = await db["schools"].find_one({"_id": ObjectId(prog["school_id"])})
            if school:
                prog["school"] = serialize_doc(school)
        except Exception:
            pass

    return prog


@router.get("/search")
async def search(q: str = Query(..., min_length=1, description="Search query")):
    """
    Search across schools and programmes by name.
    Returns matching schools and programmes in a combined response.
    """
    regex_pattern = {"$regex": q, "$options": "i"}

    # Search schools
    schools = []
    async for school in db["schools"].find({"name": regex_pattern}).sort("name", 1).limit(10):
        schools.append(serialize_doc(school))

    # Search programmes
    programmes = []
    async for prog in db["programmes"].find({"name": regex_pattern}).sort("name", 1).limit(20):
        programmes.append(serialize_doc(prog))

    return {
        "query": q,
        "schools": schools,
        "programmes": programmes,
        "total": len(schools) + len(programmes),
    }
