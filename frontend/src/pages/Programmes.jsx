/**
 * Programmes.jsx — Browse All Programmes (No Emojis)
 *
 * Route: "/programmes"
 *
 * Full programme list with client-side search and filters (school, level,
 * interest). For students who prefer reading through courses instead of
 * taking the quiz.
 */

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import ProgrammeCard from "../components/ProgrammeCard";
import { SearchIcon, SparklesIcon, InterestIcon } from "../components/Icons";

export default function Programmes() {
  const [programmes, setProgrammes] = useState([]);
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [search, setSearch] = useState("");
  const [schoolId, setSchoolId] = useState("");
  const [level, setLevel] = useState("");
  const [interestTag, setInterestTag] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [progRes, interestsRes] = await Promise.all([
          api.get("/programmes"),
          api.get("/interests"),
        ]);
        setProgrammes(progRes.data);
        setInterests(interestsRes.data);
      } catch {
        setError("Could not load programmes. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const schools = useMemo(() => {
    const map = new Map();
    programmes.forEach((p) => {
      if (p.school_id && p.school_name && !map.has(p.school_id)) {
        map.set(p.school_id, p.school_name);
      }
    });
    return [...map.entries()].sort((a, b) => a[1].localeCompare(b[1]));
  }, [programmes]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return programmes.filter((p) => {
      if (schoolId && p.school_id !== schoolId) return false;
      if (level && p.level !== level) return false;
      if (interestTag && !(p.interest_tags || []).includes(interestTag)) return false;
      if (q) {
        const haystack = [p.name, p.school_name, ...(p.career_paths || [])]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [programmes, search, schoolId, level, interestTag]);

  const hasFilters = search || schoolId || level || interestTag;

  const clearFilters = () => {
    setSearch("");
    setSchoolId("");
    setLevel("");
    setInterestTag("");
  };

  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-text-primary">
            All Programmes
          </h1>
          <p className="mt-1.5 sm:mt-2 text-text-secondary text-sm sm:text-lg">
            Read through all {programmes.length} programmes at Central University.
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
            placeholder="Search programmes, careers…"
            className="w-full pl-11 pr-4 py-2.5 sm:py-3 rounded-xl border border-surface-alt bg-surface text-text-primary text-sm sm:text-base placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-maroon/20 focus:border-maroon transition-all"
          />
        </div>
      </div>

      {/* Quiz CTA banner */}
      <div className="mt-5 sm:mt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-maroon/5 border border-maroon/10 rounded-2xl px-4 sm:px-6 py-3.5 sm:py-4">
        <div className="flex items-center gap-2.5 text-sm text-text-secondary">
          <SparklesIcon className="h-5 w-5 text-maroon shrink-0" />
          <span>
            Not sure where to start? Tap your interests and let the matcher
            rank these for you.
          </span>
        </div>
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-maroon text-white text-sm font-semibold rounded-lg hover:bg-maroon-dark transition-all shrink-0"
        >
          Get Matched →
        </Link>
      </div>

      {/* Filters */}
      <div className="mt-5 sm:mt-6 flex flex-wrap items-center gap-2.5 sm:gap-3">
        <select
          value={schoolId}
          onChange={(e) => setSchoolId(e.target.value)}
          className="px-3 py-2 rounded-lg border border-surface-alt bg-surface text-sm text-text-secondary focus:outline-none focus:border-maroon cursor-pointer"
        >
          <option value="">All Schools</option>
          {schools.map(([id, name]) => (
            <option key={id} value={id}>{name}</option>
          ))}
        </select>

        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="px-3 py-2 rounded-lg border border-surface-alt bg-surface text-sm text-text-secondary focus:outline-none focus:border-maroon cursor-pointer"
        >
          <option value="">All Levels</option>
          <option value="undergraduate">Undergraduate</option>
          <option value="postgraduate">Postgraduate &amp; Professional</option>
        </select>

        <select
          value={interestTag}
          onChange={(e) => setInterestTag(e.target.value)}
          className="px-3 py-2 rounded-lg border border-surface-alt bg-surface text-sm text-text-secondary focus:outline-none focus:border-maroon cursor-pointer"
        >
          <option value="">All Interests</option>
          {interests.map((i) => (
            <option key={i.id} value={i.id}>{i.label}</option>
          ))}
        </select>

        {hasFilters && (
          <button
            type="button"
            onClick={clearFilters}
            className="text-sm font-medium text-maroon hover:underline"
          >
            Clear filters
          </button>
        )}

        <span className="ml-auto text-xs sm:text-sm text-text-muted">
          {filtered.length} programme{filtered.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Active interest chip strip (quick filter) */}
      {interestTag && (
        <div className="mt-3 flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-maroon text-white text-xs font-medium">
            <InterestIcon id={interestTag} className="h-3.5 w-3.5" />
            {interests.find((i) => i.id === interestTag)?.label || interestTag}
            <button
              type="button"
              onClick={() => setInterestTag("")}
              className="ml-0.5 hover:opacity-70"
              aria-label="Remove interest filter"
            >
              ✕
            </button>
          </span>
        </div>
      )}

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
            No programmes match your filters.
          </p>
          <button
            type="button"
            onClick={clearFilters}
            className="mt-4 text-sm font-medium text-maroon hover:underline"
          >
            Clear filters
          </button>
        </div>
      )}

      {/* Programme Cards */}
      {!loading && !error && filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
          {filtered.map((prog) => (
            <ProgrammeCard key={prog._id} programme={prog} showSchool />
          ))}
        </div>
      )}
    </section>
  );
}
