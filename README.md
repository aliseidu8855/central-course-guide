# Central Course Guide

A comprehensive guide for university courses, featuring a React frontend and a FastAPI backend with MongoDB.

## Key Features

- **Real-Time Course Matcher** (landing page) — students tap up to 5 interests (tech, caring for people, business, art…) and matches update live: an "analysing" sequence, a typed-out reasoning summary, a Best Match spotlight with study-time bars, and ranked runners-up with "why this matched" chips. Postgraduate programmes are behind a toggle.
- **Browse All Programmes** (`/programmes`) — search plus filters by school, level (undergraduate/postgraduate), and interest.
- **Study-Time Composition** — each programme page shows a "What You'll Spend Your Time On" breakdown (coding, maths, theory, practicals, creativity, people skills) as percentage bars.
- **Schools & Programme detail pages** — descriptions, subjects, entry requirements, and career paths.

## Project Structure

- `frontend/`: React application (Vite).
- `backend/`: FastAPI application (Python).
- `database_dump/`: JSON data exports for easy database setup.

---

## Getting Started

### Prerequisites

- **Node.js** (v18 or later)
- **Python** (v3.10 or later)
- **MongoDB** (Local instance or Atlas)

### 1. Database Setup

Ensure MongoDB is running on your machine. By default, the application looks for `mongodb://localhost:27017`.

### 2. Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables:
    ```bash
    cp .env.example .env
    ```
    *(Edit `.env` if your MongoDB setup is different)*.

5.  **Import the Database**:
    Instead of scraping the website again, you can just import the provided data
    (the dump already includes the curated interest tags and composition percentages):
    ```bash
    python import_database.py
    ```

6.  Start the backend server:
    ```bash
    python main.py
    # or: uvicorn main:app --reload --port 8000
    ```
    The API will be available at `http://localhost:8000`.

7.  *(Optional)* **Re-seed quiz data**: `enrich_programmes.py` holds the curated
    interest tags + composition percentages for every programme. It only touches
    those two fields, so admin edits to names/descriptions survive:
    ```bash
    python enrich_programmes.py           # apply curated data to DB + dump
    python enrich_programmes.py --pull    # save admin-panel curation back into the dump
    ```

### 3. Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    The web app will be available at `http://localhost:5173`.

---

## Admin Panel

The backend includes an embedded admin panel for reviewing and editing the data:
- **URL**: `http://localhost:8000/admin-panel`
- **Features**: Filter by school, edit programme details, and mark data as "reviewed".
  The edit modal also manages the quiz **interest tags** (checkboxes) and the
  **composition percentages** (must total exactly 100, or be left blank). The
  status column shows "Tags"/"Comp" badges so you can see curation coverage at a glance.

---

## Development

- **API Documentation**: Once the backend is running, visit `http://localhost:8000/docs` for the interactive Swagger UI.
- **Environment**: Make sure to keep the `.env` file secure and never commit it to version control.
