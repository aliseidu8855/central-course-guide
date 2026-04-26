# Central Course Guide

A comprehensive guide for university courses, featuring a React frontend and a FastAPI backend with MongoDB.

## Project Structure

- `frontend/`: React application (Vite).
- `backend/`: FastAPI application (Python).

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

5.  **Seed the Database**:
    Initialize the database with course and school data:
    ```bash
    python seed_database.py
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

## Development

- **API Documentation**: Once the backend is running, visit `http://localhost:8000/docs` for the interactive Swagger UI.
- **Environment**: Make sure to keep the `.env` file secure and never commit it to version control.
