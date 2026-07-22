# Central Course Guide

A comprehensive course discovery platform for Central University, Ghana — helping
prospective students find the right programme through an interest matcher, browse
all courses, and ask questions to a course-aware chatbot.

**Stack:** React 19 + Vite + Tailwind CSS v4 (frontend) · FastAPI + MongoDB/Motor (backend)

## Features

- **Real-Time Course Matcher** (landing page) — students tap up to 5 interests
  (technology, health, business, art, law, ministry…) and matches update live with
  an animated "analysing" sequence, a typed-out reasoning summary, a Best Match
  spotlight with inline study-time composition bars, and staggered runner-up cards.
  Postgraduate programmes sit behind a toggle.

- **Course Q&A Chatbot** — a floating chat widget (bottom-right on every page) powered
  by Llama 3.1 8B Instruct via NVIDIA NIM (free tier). Sends the full programme
  catalogue as context so answers are grounded in real data: subjects, career paths,
  entry requirements, interest tags, and study-time composition. Supports conversation
  history.

- **Browse All Programmes** (`/programmes`) — client-side search with filters by
  school, level (undergraduate / postgraduate), and interest tag.

- **Study-Time Composition** — every programme page shows a "What You'll Spend Your
  Time On" section with percentage bars across six dimensions: coding, mathematics,
  theory, practicals, creativity, and people skills. Bars are sorted largest first
  and hidden entirely when a programme hasn't been curated yet.

- **Schools & Programme detail pages** — descriptions, subjects, entry requirements,
  career paths, and interest tag pills.

- **Admin panel** (`/admin-panel`) — edit programme names, codes, descriptions,
  career paths, interest tags (checkbox grid), and composition percentages (six
  number inputs with live total; blocks save unless total is exactly 100 or blank).
  Status badges show Tags/Comp curation coverage per programme.

## Project Structure

```
central-course-guide/
├── backend/
│   ├── main.py                  FastAPI app, CORS, health routes, admin HTML
│   ├── database.py              Motor async MongoDB client
│   ├── import_database.py       Seeds MongoDB from database_dump/*.json
│   ├── enrich_programmes.py     Curated interest tags + composition for all 40
│   │                            programmes ($set only those fields, nothing else)
│   ├── requirements.txt
│   ├── .env / .env.example      MONGO_URI, DATABASE_NAME, NVIDIA_API_KEY
│   ├── models/
│   │   ├── schemas.py           Pydantic models (Programme, School, Subject)
│   │   └── taxonomy.py          Fixed vocabularies: 14 interests, 6 composition
│   │                            dimensions, programme-level classifier
│   └── routes/
│       ├── schools.py           Public read-only API (GET /schools, /programmes/…)
│       ├── discovery.py         Quiz + browse endpoints (GET /interests, /programmes,
│       │                        POST /recommendations)
│       ├── chat.py              Chatbot endpoint (POST /chat → Gemini)
│       └── admin.py             Admin CRUD (PUT /programmes/:id, review, delete)
├── frontend/
│   ├── src/
│   │   ├── App.jsx              React Router config
│   │   ├── index.css            Tailwind v4 theme tokens + animations
│   │   ├── services/api.js      Axios instance (base /api, proxied to :8000)
│   │   ├── pages/
│   │   │   ├── Home.jsx          Landing page — the matcher IS the hero
│   │   │   ├── Schools.jsx       School cards with search
│   │   │   ├── SchoolDetail.jsx  School header + programme grid
│   │   │   ├── Programmes.jsx    Browse all with filters
│   │   │   └── ProgrammeDetail.jsx  Full detail + composition bars
│   │   └── components/
│   │       ├── InterestQuiz.jsx   The matcher (embedded on Home)
│   │       ├── ChatWidget.jsx     Floating chatbot (rendered globally)
│   │       ├── ProgrammeCard.jsx  Shared card (used everywhere)
│   │       ├── CompositionBars.jsx Horizontal percentage bars
│   │       ├── Icons.jsx          All SVG icons (interests, UI, chat)
│   │       ├── Navbar.jsx
│   │       ├── Footer.jsx
│   │       └── ScrollToTop.jsx
│   ├── package.json
│   └── vite.config.js
└── database_dump/
    ├── schools.json      (10 schools)
    └── programmes.json   (40 programmes, includes interest_tags + composition)
```

## Getting Started

### Prerequisites

- **Node.js** v18+
- **Python** 3.10+
- **MongoDB** — local instance (Homebrew: `brew install mongodb-community`) or Atlas
- **NVIDIA API key** (free — for the chatbot; the rest of the app works without it)

### 1. Database

Ensure MongoDB is running. The default connection string is
`mongodb://localhost:27017` (database `central_course_guide`).

### 2. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — at minimum set MONGO_URI if yours differs.
# For the chatbot, add:  NVIDIA_API_KEY=your-key-here
# Get a free key at https://aistudio.google.com/apikey

# Import the database (dump already includes curated interest tags + composition)
python import_database.py

# Start the server
python main.py
# or: uvicorn main:app --reload --port 8000
```

API available at **http://localhost:8000** · Swagger docs at **/docs**

### 3. Frontend

```bash
cd frontend

npm install
npm run dev
```

Web app available at **http://localhost:5173** (Vite proxies `/api` → `:8000`)

### 4. Chatbot setup (optional)

1. Get a **free** NVIDIA API key at [build.nvidia.com](https://build.nvidia.com/explore/discover)
   (sign up, generate a key — free tier included)
2. Add it to `backend/.env`:
   ```
   NVIDIA_API_KEY=your-key-here
   ```
3. Restart the backend — the floating chat bubble on every page will start
   answering questions grounded in the actual course data, powered by
   Llama 3.1 8B Instruct.

If the key is missing, the widget shows a friendly "not configured" message
instead of a broken error.

## Data Curation

Interest tags (14-category taxonomy) and study-time composition percentages
(six dimensions, always totalling 100%) were hand-curated for all 40 programmes
and live in `backend/enrich_programmes.py`:

```bash
python enrich_programmes.py           # $set curated data on live DB + update dump
python enrich_programmes.py --db-only # database only
python enrich_programmes.py --dump-only  # JSON dump only
python enrich_programmes.py --pull    # save admin-panel edits back into the dump
```

The script only touches `interest_tags` and `composition` (plus `updated_at`) —
all other admin edits (names, descriptions, career paths) survive re-runs.

## API Endpoints

### Public (no prefix)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/schools` | All schools with programme counts |
| GET | `/schools/{id}` | Single school |
| GET | `/schools/{id}/programmes` | Programmes under a school |
| GET | `/programmes/{id}` | Single programme (with nested school) |
| GET | `/programmes` | All 40 programmes with `level` (discovery) |
| GET | `/interests` | 14 interest taxonomy items |
| GET | `/composition-dimensions` | 6 composition dimensions |
| POST | `/recommendations` | Score programmes against selected interests |
| GET | `/search?q=` | Regex search across schools + programmes |

### Chat (`/chat`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Send `{message, history?}`, receive `{reply}` |

Requires `NVIDIA_API_KEY` in `.env`. The backend keyword-searches all programmes
(including composition data), sends the top 15 as context to Llama 3.1 8B,
and returns a grounded answer.

### Admin (`/admin`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/stats` | Dashboard counts |
| GET | `/admin/schools` | All schools |
| GET | `/admin/programmes` | List (filterable by school + reviewed status) |
| PUT | `/admin/programmes/{id}` | Update fields including interest_tags + composition |
| DELETE | `/admin/programmes/{id}` | Delete a programme |
| POST | `/admin/programmes/{id}/review` | Mark single programme reviewed |
| POST | `/admin/programmes/review-all` | Mark all reviewed |

## Admin Panel

Visit **http://localhost:8000/admin-panel** for a self-contained dashboard:

- **Stats cards** — total schools, programmes, reviewed / pending counts
- **Filters** — by school and review status
- **Edit modal** — name, code, duration, description, career paths (comma-separated),
  interest tags (checkbox grid populated from `/interests`), and composition
  percentages (six number inputs with a live total that turns red unless it equals
  0 or 100). Save is blocked if composition doesn't add up.
- **Table badges** — "Tags" and "Comp" badges in the status column show green when
  present and amber when missing, so you can see curation coverage at a glance.
- **Bulk actions** — Mark All Reviewed, per-row review and delete

## Design Notes

- **No emojis** — the public site uses inline SVG icons only (`frontend/src/components/Icons.jsx`).
  The admin panel uses plain text labels.
- **Tailwind v4** CSS-first configuration — design tokens live in
  `frontend/src/index.css` (`@theme` block): maroon `#8B0000`, gold accent
  `#D4A853`, neutral backgrounds, Inter font.
- **Animations** respect `prefers-reduced-motion`.
- **`enrich_programmes.py`** is the single source of truth for curated data;
  `database_dump/programmes.json` stays in sync so fresh `import_database.py`
  runs get the fields immediately.
