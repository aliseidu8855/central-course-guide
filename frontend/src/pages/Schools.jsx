/**
 * Schools.jsx — Schools Listing Page (No Emojis)
 *
 * Route: "/schools"
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import { SearchIcon } from "../components/Icons";

const ArrowIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
  </svg>
);

export default function Schools() {
  const [schools, setSchools] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchSchools = async () => {
      try {
        const res = await api.get("/schools");
        setSchools(res.data);
        setFiltered(res.data);
      } catch (err) {
        setError("Could not load schools. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    };
    fetchSchools();
  }, []);

  useEffect(() => {
    if (!search.trim()) {
      setFiltered(schools);
      return;
    }
    const q = search.toLowerCase();
    setFiltered(
      schools.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.code.toLowerCase().includes(q)
      )
    );
  }, [search, schools]);

  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-text-primary">
            Schools & Faculties
          </h1>
          <p className="mt-1.5 sm:mt-2 text-text-secondary text-sm sm:text-lg">
            Explore {schools.length} schools and faculties at Central University.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full md:w-80">
          <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-muted">
            <SearchIcon className="h-4 w-4 sm:h-5 sm:w-5" />
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search schools…"
            className="w-full pl-11 pr-4 py-2.5 sm:py-3 rounded-xl border border-surface-alt bg-surface text-text-primary text-sm sm:text-base placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-maroon/20 focus:border-maroon transition-all"
          />
        </div>
      </div>

      <hr className="my-6 sm:my-8 border-surface-alt" />

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-maroon border-t-transparent" />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-xl bg-surface border border-surface-alt p-6 sm:p-8 text-center text-text-secondary">
          <p className="text-base sm:text-lg font-medium">{error}</p>
        </div>
      )}

      {/* No results */}
      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-16 sm:py-20">
          <SearchIcon className="h-10 w-10 sm:h-12 sm:w-12 text-text-muted mx-auto mb-4" />
          <p className="text-text-muted text-base sm:text-lg">
            {search ? `No schools matching "${search}"` : "No schools found."}
          </p>
        </div>
      )}

      {/* School Cards */}
      {!loading && !error && filtered.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {filtered.map((school) => (
            <Link
              to={`/schools/${school._id}`}
              key={school._id}
              className="group bg-surface rounded-2xl p-5 sm:p-6 shadow-sm hover:shadow-lg transition-all duration-300 border border-surface-alt hover:border-maroon/20 hover:-translate-y-1"
            >
              <div className="flex items-start justify-between">
                <span className="inline-flex px-2.5 sm:px-3 py-1 rounded-lg bg-maroon/10 text-maroon text-xs font-bold tracking-wide">
                  {school.code}
                </span>
                <span className="text-text-muted group-hover:text-maroon transition-colors">
                  <ArrowIcon />
                </span>
              </div>

              <h2 className="mt-3 sm:mt-4 text-base sm:text-lg font-bold text-text-primary group-hover:text-maroon transition-colors leading-tight">
                {school.name}
              </h2>

              <p className="mt-1.5 sm:mt-2 text-text-secondary text-xs sm:text-sm line-clamp-2 min-h-[2rem] sm:min-h-[2.5rem]">
                {school.description || "Explore programmes and career paths under this school."}
              </p>

              <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-surface-alt flex items-center gap-2">
                <span className="text-sm font-semibold text-maroon">
                  {school.programme_count || 0}
                </span>
                <span className="text-xs sm:text-sm text-text-muted">
                  programme{(school.programme_count || 0) !== 1 ? "s" : ""} available
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
