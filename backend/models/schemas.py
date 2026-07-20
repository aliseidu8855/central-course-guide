"""
schemas.py — Pydantic Models (Data Validation & Serialization)
==============================================================

These models define the shape of data flowing in and out of the API.
FastAPI uses them automatically for:
  • Request body validation
  • Response serialization
  • Auto-generated OpenAPI / Swagger docs

Naming conventions:
  • *Base   — shared fields (used for both create & read)
  • *Create — fields required when creating a new record
  • *Read   — fields returned to the client (includes DB id)
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models.taxonomy import clean_composition, clean_interest_tags


# ===================================================================
# Subject
# ===================================================================

class SubjectBase(BaseModel):
    """Core fields shared across Subject operations."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Full name of the subject (e.g. 'Introduction to Computing').",
    )
    code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Subject code (e.g. 'CS101').",
    )
    credit_hours: int = Field(
        ...,
        ge=1,
        le=20,
        description="Number of credit hours for this subject.",
    )
    semester: Optional[str] = Field(
        default=None,
        description="Semester the subject is offered (e.g. 'Semester 1').",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Brief overview of the subject content.",
    )


class SubjectCreate(SubjectBase):
    """Schema used when creating a new Subject (no id yet)."""
    pass


class SubjectRead(SubjectBase):
    """Schema returned to the client — includes the MongoDB document id."""
    id: str = Field(
        ...,
        alias="_id",
        description="MongoDB ObjectId as a string.",
    )

    model_config = {"populate_by_name": True}


# ===================================================================
# Programme (a.k.a. Degree Programme / Course)
# ===================================================================

class ProgrammeBase(BaseModel):
    """Core fields shared across Programme operations."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Programme title (e.g. 'BSc Computer Science').",
    )
    code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Programme code (e.g. 'BSCS').",
    )
    slug: Optional[str] = Field(
        default=None,
        description="URL-friendly identifier (e.g. 'computer-science').",
    )
    duration_years: int = Field(
        ...,
        ge=1,
        le=10,
        description="Duration of the programme in years.",
    )
    degree_type: Optional[str] = Field(
        default=None,
        description="Degree awarded (e.g. 'BSc', 'MBA', 'PharmD').",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=3000,
        description="Overview of the programme.",
    )
    career_paths: list[str] = Field(
        default_factory=list,
        description="List of potential career paths for graduates.",
    )
    subjects: list[str] = Field(
        default_factory=list,
        description="Subjects/courses studied under this programme.",
    )
    entry_requirements: list[str] = Field(
        default_factory=list,
        description="Admission requirements for the programme.",
    )
    interest_tags: list[str] = Field(
        default_factory=list,
        description="Interest ids from the fixed taxonomy (see /interests).",
    )
    composition: dict[str, int] = Field(
        default_factory=dict,
        description=(
            "Study-time breakdown {dimension_id: percent}; values sum to 100. "
            "Empty dict = not curated (see /composition-dimensions)."
        ),
    )
    school_id: str = Field(
        ...,
        description="ID of the parent School this programme belongs to.",
    )
    school_name: Optional[str] = Field(
        default=None,
        description="Denormalized name of the parent school.",
    )
    is_reviewed: bool = Field(
        default=False,
        description="Whether an admin has reviewed this programme's data.",
    )

    @field_validator("interest_tags")
    @classmethod
    def _validate_interest_tags(cls, v: list[str]) -> list[str]:
        return clean_interest_tags(v)

    @field_validator("composition")
    @classmethod
    def _validate_composition(cls, v: dict[str, int]) -> dict[str, int]:
        return clean_composition(v)


class ProgrammeCreate(ProgrammeBase):
    """Schema used when creating a new Programme."""
    pass


class ProgrammeRead(ProgrammeBase):
    """Schema returned to the client — includes the MongoDB document id."""
    id: str = Field(
        ...,
        alias="_id",
        description="MongoDB ObjectId as a string.",
    )
    level: Optional[str] = Field(
        default=None,
        description="Derived from degree_type: 'undergraduate' or 'postgraduate'.",
    )

    model_config = {"populate_by_name": True}


# ===================================================================
# School (Faculty / College within the University)
# ===================================================================

class SchoolBase(BaseModel):
    """Core fields shared across School operations."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Official name of the school (e.g. 'School of Engineering').",
    )
    code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Short code for the school (e.g. 'SOE').",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=3000,
        description="Brief description of the school and its mission.",
    )
    dean: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Name of the current dean.",
    )
    location: Optional[str] = Field(
        default=None,
        max_length=300,
        description="Physical location / campus of the school.",
    )


class SchoolCreate(SchoolBase):
    """Schema used when creating a new School."""
    pass


class SchoolRead(SchoolBase):
    """Schema returned to the client — includes the MongoDB document id."""
    id: str = Field(
        ...,
        alias="_id",
        description="MongoDB ObjectId as a string.",
    )

    model_config = {"populate_by_name": True}
