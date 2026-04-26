/**
 * api.js — Pre-configured Axios Instance
 * ========================================
 *
 * A single Axios instance pointed at the FastAPI backend.
 * Every service / hook in the app should import this instance
 * instead of the raw `axios` package so that:
 *
 *   • The base URL is set in one place.
 *   • Global interceptors (auth headers, error handling, etc.)
 *     can be added later without touching every call-site.
 *
 * Usage:
 *   import api from "../services/api";
 *   const res = await api.get("/schools");
 */

import axios from "axios";

// ---------------------------------------------------------------------------
// Base URL — points to the FastAPI dev server by default.
// Override via the VITE_API_URL environment variable in .env if needed.
// ---------------------------------------------------------------------------
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10_000, // 10-second timeout
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// ---------------------------------------------------------------------------
// Optional: Global response interceptor for error logging
// ---------------------------------------------------------------------------
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log the error for debugging in development
    console.error(
      "[API Error]",
      error.response?.status,
      error.response?.data || error.message
    );
    return Promise.reject(error);
  }
);

export default api;
