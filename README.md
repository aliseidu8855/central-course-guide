# Central Course Guide

A comprehensive guide for university courses, featuring a React frontend and a FastAPI backend with MongoDB.

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
    Instead of scraping the website again, you can just import the provided data:
    ```bash
    python import_database.py
    ```

6.  Start the backend server:
    ```bash
    python main.py
    ```
    The API will be available at `http://localhost:8000`.

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

---

## Advanced: Scraper Scripts

If you want to re-scrape the latest data from the university website:
1. `python seed_database.py` (Base schools and programmes)
2. `python update_school_descriptions.py` (Official descriptions)
3. `python enrich_programmes.py` (Detailed course info)
4. `python export_database.py` (Save current DB state to `database_dump/`)
