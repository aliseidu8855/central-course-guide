"""
database.py — Async MongoDB Connection Setup
=============================================

Uses Motor (motor.motor_asyncio) for non-blocking MongoDB operations.
Connection settings are loaded from environment variables so secrets
never leak into version control.

Usage:
    from database import get_database
    db = get_database()
    collection = db["schools"]
"""

import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# ---------------------------------------------------------------------------
# Load environment variables from a .env file (if present)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# MongoDB connection configuration
# ---------------------------------------------------------------------------
# Default to localhost if no MONGO_URI is supplied. In production, set the
# MONGO_URI environment variable to your Atlas / remote connection string.
MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "central_course_guide")

# ---------------------------------------------------------------------------
# Create a reusable Motor client instance
# ---------------------------------------------------------------------------
# Motor is thread-safe and manages its own connection pool, so a single
# client instance shared across the application is the recommended pattern.
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)


def get_database():
    """
    Return a reference to the application database.

    Returns:
        motor.motor_asyncio.AsyncIOMotorDatabase
    """
    return client[DATABASE_NAME]
