/**
 * Quiz.jsx — Interest Quiz & Course Recommendations (No Emojis)
 *
 * Route: "/quiz"
 *
 * Single-page flow: pick up to MAX_SELECTED interests, optionally include
 * postgraduate programmes, then get ranked recommendations with
 * "why this matched" explanations. Results render below the chips so
 * students can tweak selections and instantly re-run.
 */

import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import ProgrammeCard from "../components/ProgrammeCard";
import {
  SparklesIcon,
  InterestIcon,
  FaceFrownIcon,
  CheckCircleIcon,
} from "../components/Icons";

const MAX_SELECTED = 5;

export default function Quiz() {
  const [interests, setInterests] = useState([]);
  const [selected, setSelected] = useState([]);
  const [includePostgrad, setIncludePostgrad] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    const fetchInterests = async () => {
      try {
        const res = await api.get("/interests");
        setInterests(res.data);
      } catch {
        setError("Could not load the quiz. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    };
    fetchInterests();
  }, []);

  const toggleInterest = (id) => {
    setSelected((prev) => {
      if (prev.includes(id)) return prev.filter((s) => s !== id);
      if (prev.length >= MAX_SELECTED) return prev;
      return [...prev, id];
    });
  };

  const fetchMatches = async (postgrad) => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.post("/recommendations", {
        interests: selected,
        include_postgraduate: postgrad,
      });
      setResults(res.data);
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } catch {
      setError("Something went wrong getting your matches. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = () => {
    if (selected.length === 0) return;
    fetchMatches(includePostgrad);
  };

  const retryWithPostgrad = () => {
    setIncludePostgrad(true);
    fetchMatches(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-maroon border-t-transparent" />
      </div>
    );
  }

  return (
    <section className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
      {/* Header */}
      <div className="text-center">
        <span className="inline-flex items-center gap-2 px-3 sm:px-4 py-1.5 rounded-full bg-maroon/10 text-maroon text-xs sm:text-sm font-semibold mb-4 sm:mb-6">
          <SparklesIcon className="h-4 w-4" />
          Interest Quiz
        </span>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-text-primary leading-tight">
          Find Your <span className="text-maroon">Course</span>
        </h1>
        <p className="mt-3 sm:mt-4 max-w-xl mx-auto text-sm sm:text-base text-text-secondary leading-relaxed">
          Pick the things you enjoy, and we'll match you to Central University
          programmes that fit your interests.
        </p>
      </div>

      {/* Interest picker */}
      <div className="mt-8 sm:mt-10 bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
        <div className="flex items-center justify-between mb-4 sm:mb-5">
          <h2 className="text-base sm:text-lg font-bold text-text-primary">
            What are you interested in?
          </h2>
          <span className="text-xs sm:text-sm text-text-muted font-medium shrink-0">
            Pick up to {MAX_SELECTED} · {selected.length} selected
          </span>
        </div>

        <div className="flex flex-wrap gap-2 sm:gap-2.5">
          {interests.map((interest) => {
            const isSelected = selected.includes(interest.id);
            const isDisabled = !isSelected && selected.length >= MAX_SELECTED;
            return (
              <button
                key={interest.id}
                type="button"
                onClick={() => toggleInterest(interest.id)}
                className={`inline-flex items-center gap-1.5 sm:gap-2 px-3.5 sm:px-4 py-2 sm:py-2.5 rounded-full border text-xs sm:text-sm font-medium transition-all duration-150 ${
                  isSelected
                    ? "bg-maroon border-maroon text-white shadow-sm"
                    : isDisabled
                      ? "bg-surface border-surface-alt text-text-muted opacity-50 cursor-not-allowed"
                      : "bg-surface border-surface-alt text-text-secondary hover:border-maroon/40 hover:text-maroon"
                }`}
              >
                <InterestIcon id={interest.id} className="h-4 w-4" />
                {interest.label}
              </button>
            );
          })}
        </div>

        {/* Postgraduate toggle */}
        <label className="flex items-center gap-2.5 mt-5 sm:mt-6 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={includePostgrad}
            onChange={(e) => setIncludePostgrad(e.target.checked)}
            className="h-4 w-4 rounded border-surface-alt accent-maroon cursor-pointer"
          />
          <span className="text-xs sm:text-sm text-text-secondary">
            Include postgraduate &amp; professional programmes (MBA, MPhil, PhD…)
          </span>
        </label>

        {/* Submit */}
        <div className="mt-5 sm:mt-6 flex flex-col sm:flex-row items-center gap-3">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={selected.length === 0 || submitting}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 sm:px-8 py-3 bg-maroon text-white font-semibold rounded-xl shadow-lg hover:bg-maroon-dark transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-maroon"
          >
            {submitting ? "Matching…" : results ? "Update My Matches" : "Show My Matches"}
          </button>
          {selected.length === 0 && (
            <span className="text-xs sm:text-sm text-text-muted">
              Select at least one interest to continue.
            </span>
          )}
        </div>

        {error && (
          <p className="mt-4 text-sm text-maroon font-medium">{error}</p>
        )}
      </div>

      {/* Results */}
      {results && (
        <div ref={resultsRef} className="mt-8 sm:mt-12 scroll-mt-24">
          {results.results.length > 0 ? (
            <>
              <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2 mb-4 sm:mb-6">
                <div>
                  <h2 className="text-xl sm:text-2xl font-bold text-text-primary">
                    Your Top Matches
                  </h2>
                  <p className="mt-1 text-xs sm:text-sm text-text-secondary">
                    {results.results.length} programme
                    {results.results.length !== 1 ? "s" : ""} matched your interests.
                  </p>
                </div>
                <Link
                  to="/programmes"
                  className="text-sm font-medium text-maroon hover:underline shrink-0"
                >
                  Browse all programmes →
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
                {results.results.map((result) => (
                  <ProgrammeCard
                    key={result.programme._id}
                    programme={result.programme}
                    showSchool
                    extra={
                      <div className="mt-3 pt-3 border-t border-surface-alt">
                        <div className="flex flex-wrap items-center gap-1.5">
                          <span className="inline-flex items-center gap-1 text-xs font-bold bg-maroon/10 text-maroon px-2.5 py-1 rounded-full">
                            <CheckCircleIcon className="h-3.5 w-3.5" />
                            {result.score}% match
                          </span>
                          {result.matched.map((m) => (
                            <span
                              key={m.id}
                              className="inline-flex items-center gap-1 text-xs bg-accent/10 text-accent-dark px-2 py-0.5 rounded-full font-medium"
                            >
                              <InterestIcon id={m.id} className="h-3 w-3" />
                              {m.label}
                            </span>
                          ))}
                        </div>
                      </div>
                    }
                  />
                ))}
              </div>
            </>
          ) : (
            <div className="bg-surface rounded-2xl p-8 sm:p-12 text-center border border-surface-alt">
              <FaceFrownIcon className="h-12 w-12 text-text-muted mx-auto mb-4" />
              <h2 className="text-lg sm:text-xl font-bold text-text-primary">
                No matches for that combination
              </h2>
              <p className="mt-2 text-sm text-text-secondary max-w-md mx-auto">
                {!includePostgrad
                  ? "Some interests (like Faith & Ministry or Teaching) are currently only covered by postgraduate programmes."
                  : "Try selecting different or fewer interests, or browse the full programme list."}
              </p>
              <div className="mt-5 sm:mt-6 flex flex-col sm:flex-row gap-3 justify-center">
                {!includePostgrad && (
                  <button
                    type="button"
                    onClick={retryWithPostgrad}
                    disabled={submitting}
                    className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-maroon text-white text-sm font-semibold rounded-xl hover:bg-maroon-dark transition-all disabled:opacity-40"
                  >
                    Include postgraduate programmes and retry
                  </button>
                )}
                <Link
                  to="/programmes"
                  className="inline-flex items-center justify-center gap-2 px-5 py-2.5 border-2 border-surface-alt text-text-secondary text-sm font-semibold rounded-xl hover:border-maroon hover:text-maroon transition-all"
                >
                  Browse all programmes →
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
