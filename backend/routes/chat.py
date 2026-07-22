"""
routes/chat.py — Course Q&A Chatbot (Llama 3.1 8B via NVIDIA NIM)
==================================================================

A lightweight chatbot grounded in the actual programme data.

Flow:
  1. User sends a question about Central University courses.
  2. We keyword-score all 40 programmes and select the top matches.
  3. The question, full programme context (subjects, careers, entry
     requirements, interest tags, composition), and conversation
     history are sent to Llama 3.1 8B Instruct via NVIDIA NIM.
  4. The reply is returned.

NVIDIA NIM uses an OpenAI-compatible API — no SDK needed, just httpx.

Requires NVIDIA_API_KEY in backend/.env.
Get a free key at: https://build.nvidia.com/explore/discover
"""

import os
import re as _re

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from database import get_database

router = APIRouter(prefix="/chat", tags=["Chatbot"])

db = get_database()

# ---------------------------------------------------------------------------
# NVIDIA NIM config
# ---------------------------------------------------------------------------
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_ID = "meta/llama-3.1-8b-instruct"

SYSTEM_PROMPT = (
    "Your name is Biggie. You are a professional course advisor for Central "
    "University in Ghana. You have the ENTIRE programme catalogue in front "
    "of you — every message includes all 40 programmes with their subjects, "
    "career paths, entry requirements, interest tags, and study-time "
    "composition percentages.\n\n"
    "CRITICAL RULES:\n"
    "1. Answer ONLY from the catalogue provided. Never invent programmes, "
    "modules, tracks, or departments.\n"
    "2. If someone asks about a course Central University DOESN'T offer "
    "(like sports or dance): look through the full catalogue, say \"We "
    "don't offer a [topic] programme.\" Only suggest alternatives if you "
    "can see genuinely related programmes in the catalogue. If nothing is "
    "related, stop there — one sentence is enough.\n"
    "3. Course-adjacent questions (applications, fees, deadlines, "
    "accommodation): say \"I don't have that info — check central.edu.gh.\"\n"
    "4. Truly off-topic (math, weather, politics): politely say you only "
    "help with course questions.\n"
    "5. Social messages (thank you, hello, bye): ONE warm sentence. "
    "No course lists.\n\n"
    "FORMAT:\n"
    "- Bullet points (-) for lists. **bold** for names and numbers.\n"
    "- Short paragraphs. Blank line between sections."
)

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    reply: str


# ---------------------------------------------------------------------------
# Programme search & context building
# ---------------------------------------------------------------------------


def _programme_summary(prog: dict) -> dict:
    """Extract the fields we send to the LLM from a raw programme doc."""
    return {
        "_id": str(prog["_id"]),
        "name": prog.get("name", ""),
        "school_name": prog.get("school_name", ""),
        "degree_type": prog.get("degree_type", ""),
        "duration_years": prog.get("duration_years"),
        "description": prog.get("description", ""),
        "subjects": prog.get("subjects", [])[:8],
        "career_paths": prog.get("career_paths", []),
        "entry_requirements": prog.get("entry_requirements", []),
        "interest_tags": prog.get("interest_tags", []),
        "composition": prog.get("composition", {}),
    }


def _searchable_text(doc: dict) -> str:
    """All the text we want to keyword-match against, lowercased."""
    comp_keys = " ".join(doc.get("composition", {}).keys())
    return (
        doc["name"] + " "
        + doc.get("description", "") + " "
        + " ".join(doc.get("subjects", [])) + " "
        + " ".join(doc.get("career_paths", [])) + " "
        + " ".join(doc.get("interest_tags", [])) + " "
        + comp_keys
    ).lower()


async def _search_programmes(query: str, limit: int = 15) -> list[dict]:
    """Score all 40 programmes against the query and return the top matches."""
    STOPWORDS = {
        "a", "also", "an", "and", "any", "are", "about", "bye", "can",
        "central","course", "courses", "do", "does", "for", "get", "have",
        "hello", "help", "hey", "hi", "how", "i", "in", "involve", "is",
        "it", "just", "know", "like", "many", "me", "need", "of", "ok",
        "okay", "or", "programme", "programmes", "tell", "thank", "thanks",
        "the", "there", "to", "university", "want", "what", "which",
        "with", "would", "you",
    }

    # Strip punctuation so "nursing?" becomes "nursing"
    raw = _re.sub(r"[^\w\s]", "", query.lower())
    raw_words = [
        w for w in raw.split()
        if len(w) > 1 and w not in STOPWORDS
    ]
    if not raw_words:
        return []  # no keywords = social/off-topic; caller sends no context

    words = [_re.sub(r"s$", "", w) for w in raw_words]

    scored: list[tuple[int, dict]] = []
    async for prog in db["programmes"].find({}):
        doc = _programme_summary(prog)
        text = _searchable_text(doc)
        score = sum(1 for w in words if w in text)
        if score > 0:
            scored.append((score, doc))

    # Never fall back — if keywords didn't match anything, return empty.
    # Sending random programmes causes the LLM to hallucinate connections
    # (e.g. inventing a "Sports Management" track inside Business).
    # Let the endpoint handle empty results with a social/off-topic hint.

    scored.sort(key=lambda x: -x[0])
    return [doc for _, doc in scored[:limit]]


def _build_context(programmes: list[dict]) -> str:
    """Turn matched programmes into a compact text block for the LLM."""
    if not programmes:
        return "No matching programmes found."

    parts = []
    for i, p in enumerate(programmes, 1):
        lines = [
            f"{i}. {p['name']} ({p.get('degree_type', 'N/A')})",
            f"   School: {p.get('school_name', 'N/A')}",
            f"   Duration: {p.get('duration_years', 'N/A')} years",
        ]
        if p.get("description"):
            lines.append(f"   Description: {p['description'][:400]}")
        if p.get("subjects"):
            lines.append(f"   Subjects: {', '.join(p['subjects'][:6])}")
        if p.get("career_paths"):
            lines.append(f"   Careers: {', '.join(p['career_paths'][:6])}")
        if p.get("entry_requirements"):
            lines.append(f"   Entry requirements: {', '.join(p['entry_requirements'][:4])}")
        if p.get("interest_tags"):
            lines.append(f"   Interests: {', '.join(p['interest_tags'])}")
        if p.get("composition"):
            pcts = [f"{k}={v}%" for k, v in sorted(p["composition"].items(), key=lambda x: -x[1])]
            lines.append(f"   Study time split: {', '.join(pcts)}")
        parts.append("\n".join(lines))

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not NVIDIA_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Chatbot is not configured. Add NVIDIA_API_KEY to backend/.env",
        )

    # 1. Always send ALL 40 programmes as context — Llama 3.1 has a 128K
    #    window, so ~20 KB of course data is trivial. Biggie can honestly
    #    scan the entire catalogue and never needs to guess or invent.
    all_progs = []
    async for prog in db["programmes"].find({}).sort("name", 1):
        all_progs.append(_programme_summary(prog))
    context = _build_context(all_progs)

    # Still score for ranking (used in the user message to hint relevance)
    scored = await _search_programmes(request.message)
    top_names = [p["name"] for p in scored[:5]] if scored else []

    # 2. Build the messages array (OpenAI-compatible format)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Include conversation history
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})

    # Add the current question with context
    if top_names:
        hint = (
            f"The student's question best matched: {', '.join(top_names)}. "
            "Use the full catalogue above to give a complete answer."
        )
    else:
        hint = (
            "No programme specifically matched the student's query. "
            "If this is a social message (thank you, hello), respond "
            "warmly in one sentence. If they're asking about a course "
            "CU doesn't offer, say so honestly and suggest genuinely "
            "related programmes from the catalogue if any exist. If "
            "it's about applications or fees, redirect to central.edu.gh."
        )

    user_text = (
        "Here is the COMPLETE Central University programme catalogue:\n\n"
        f"{context}\n\n"
        f"{hint}\n\n"
        f"Student question: {request.message}"
    )
    messages.append({"role": "user", "content": user_text})

    body = {
        "model": MODEL_ID,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 800,
        "top_p": 0.9,
    }

    # 3. Call NVIDIA NIM
    async with httpx.AsyncClient(timeout=25) as client:
        try:
            resp = await client.post(
                NVIDIA_URL,
                json=body,
                headers={
                    "Authorization": f"Bearer {NVIDIA_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            detail = e.response.text[:300]
            if "401" in str(e.response.status_code) or "403" in str(e.response.status_code):
                raise HTTPException(
                    status_code=502,
                    detail="Invalid NVIDIA API key — check NVIDIA_API_KEY in backend/.env.",
                )
            if "429" in str(e.response.status_code):
                raise HTTPException(
                    status_code=502,
                    detail="NVIDIA API rate limit reached — try again in a moment.",
                )
            raise HTTPException(
                status_code=502,
                detail=f"NVIDIA API error: {detail}",
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail="Could not reach NVIDIA API. Check your network.",
            )

    # 4. Extract the reply
    try:
        reply = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        reply = "I couldn't generate a good response. Try asking differently!"

    return ChatResponse(reply=reply.strip())
