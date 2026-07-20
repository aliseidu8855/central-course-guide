/**
 * InterestQuiz.jsx — Real-Time Course Matcher (No Emojis)
 *
 * The landing-page centrepiece. Feels like a live AI matcher:
 *
 *   - Matches update in real time as interests are tapped (debounced,
 *     no submit button).
 *   - First run shows a short staged "analysing" sequence.
 *   - A reasoning summary is typed out character-by-character.
 *   - The #1 programme gets a "Best Match" reveal with inline
 *     study-time bars; runners-up stream in with a stagger.
 *
 * All of it is deterministic and client-side over /recommendations —
 * no external AI service involved.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import ProgrammeCard from "./ProgrammeCard";
import CompositionBars from "./CompositionBars";
import {
  InterestIcon,
  SparklesIcon,
  FaceFrownIcon,
  CheckCircleIcon,
  ClockIcon,
} from "./Icons";

const MAX_SELECTED = 5;
const DEBOUNCE_MS = 450;
const FIRST_REVEAL_MS = 1200;
const UPDATE_MIN_MS = 250;

const THINKING_STEPS = [
  "Reading your interests…",
  "Scanning every programme…",
  "Ranking your matches…",
];

/** "a", "a and b", "a, b and c" */
const joinNatural = (items) => {
  if (items.length <= 1) return items[0] || "";
  return `${items.slice(0, -1).join(", ")} and ${items[items.length - 1]}`;
};

const buildSummary = (data) => {
  const picked = joinNatural(data.selected.map((s) => s.label));
  if (data.results.length === 0) {
    return `I looked at every programme, but nothing matches ${picked} yet at this level.`;
  }
  const top = data.results[0];
  let summary = `Based on your interest in ${picked}, your strongest fit is ${top.programme.name} — a ${top.score}% match.`;
  const others = data.results.slice(1, 3).map((r) => r.programme.name);
  if (others.length > 0) {
    summary += ` Also worth a look: ${joinNatural(others)}.`;
  }
  return summary;
};

export default function InterestQuiz() {
  const [interests, setInterests] = useState([]);
  const [selected, setSelected] = useState([]);
  const [includePostgrad, setIncludePostgrad] = useState(false);
  const [results, setResults] = useState(null);
  const [phase, setPhase] = useState("idle"); // idle | thinking | ready
  const [thinkingStep, setThinkingStep] = useState(0);
  const [updating, setUpdating] = useState(false);
  const [typed, setTyped] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const requestSeq = useRef(0);
  const hasRevealed = useRef(false);
  const resultsRef = useRef(null);

  // ---- Load the interest taxonomy once ----
  useEffect(() => {
    const fetchInterests = async () => {
      try {
        const res = await api.get("/interests");
        setInterests(res.data);
      } catch {
        setError("Could not load the matcher. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    };
    fetchInterests();
  }, []);

  // ---- Real-time matching: refetch whenever the selection changes ----
  useEffect(() => {
    if (selected.length === 0) {
      requestSeq.current += 1;
      hasRevealed.current = false;
      setResults(null);
      setPhase("idle");
      setUpdating(false);
      return;
    }

    const seq = ++requestSeq.current;
    const isFirst = !hasRevealed.current;
    setError(null);
    if (isFirst) {
      setPhase("thinking");
      setThinkingStep(0);
    } else {
      setUpdating(true);
    }

    const timer = setTimeout(async () => {
      const started = Date.now();
      try {
        const res = await api.post("/recommendations", {
          interests: selected,
          include_postgraduate: includePostgrad,
        });
        // Hold the reveal briefly so the analysis feels deliberate.
        const minWait = isFirst ? FIRST_REVEAL_MS : UPDATE_MIN_MS;
        const remaining = Math.max(0, minWait - (Date.now() - started));
        if (remaining > 0) await new Promise((r) => setTimeout(r, remaining));
        if (seq !== requestSeq.current) return;

        setResults(res.data);
        setPhase("ready");
        setUpdating(false);
        if (!hasRevealed.current) {
          hasRevealed.current = true;
          setTimeout(() => {
            resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
          }, 120);
        }
      } catch {
        if (seq !== requestSeq.current) return;
        setError("Something went wrong getting your matches. Please try again.");
        setPhase(hasRevealed.current ? "ready" : "idle");
        setUpdating(false);
      }
    }, DEBOUNCE_MS);

    return () => clearTimeout(timer);
  }, [selected, includePostgrad]);

  // ---- Cycle the "analysing" status lines ----
  useEffect(() => {
    if (phase !== "thinking") return;
    const interval = setInterval(() => {
      setThinkingStep((s) => Math.min(s + 1, THINKING_STEPS.length - 1));
    }, 380);
    return () => clearInterval(interval);
  }, [phase]);

  // ---- Type the reasoning summary out character-by-character ----
  const summary = useMemo(() => (results ? buildSummary(results) : ""), [results]);

  useEffect(() => {
    if (!summary || phase !== "ready") {
      setTyped("");
      return;
    }
    setTyped("");
    let i = 0;
    const interval = setInterval(() => {
      i += 2; // two chars per tick keeps it brisk
      setTyped(summary.slice(0, i));
      if (i >= summary.length) clearInterval(interval);
    }, 24);
    return () => clearInterval(interval);
  }, [summary, phase]);

  const toggleInterest = (id) => {
    setSelected((prev) => {
      if (prev.includes(id)) return prev.filter((s) => s !== id);
      if (prev.length >= MAX_SELECTED) return prev;
      return [...prev, id];
    });
  };

  const topMatch = results?.results?.[0] || null;
  const runnersUp = results?.results?.slice(1) || [];

  return (
    <div>
      {/* ---- Interest picker ---- */}
      <div className="bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-maroon border-t-transparent" />
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between gap-3 mb-4 sm:mb-5">
              <div>
                <h2 className="text-base sm:text-lg font-bold text-text-primary">
                  Tap what you enjoy
                </h2>
                <p className="text-xs sm:text-sm text-text-muted mt-0.5">
                  Your matches update live as you pick.
                </p>
              </div>
              <span
                className={`text-xs sm:text-sm font-semibold shrink-0 px-2.5 py-1 rounded-full transition-colors ${
                  selected.length > 0
                    ? "bg-maroon/10 text-maroon"
                    : "bg-surface-alt text-text-muted"
                }`}
              >
                {selected.length}/{MAX_SELECTED}
              </span>
            </div>

            <div className="flex flex-wrap justify-center sm:justify-start gap-2 sm:gap-2.5">
              {interests.map((interest) => {
                const isSelected = selected.includes(interest.id);
                const isDisabled = !isSelected && selected.length >= MAX_SELECTED;
                return (
                  <button
                    key={interest.id}
                    type="button"
                    onClick={() => toggleInterest(interest.id)}
                    className={`inline-flex items-center gap-1.5 sm:gap-2 px-3.5 sm:px-4 py-2 sm:py-2.5 rounded-full border text-xs sm:text-sm font-medium transition-all duration-150 cursor-pointer active:scale-95 ${
                      isSelected
                        ? "bg-maroon border-maroon text-white shadow-sm"
                        : isDisabled
                          ? "bg-surface border-surface-alt text-text-muted opacity-50 cursor-not-allowed"
                          : "bg-surface border-surface-alt text-text-secondary hover:border-maroon/40 hover:text-maroon hover:-translate-y-0.5"
                    }`}
                  >
                    <InterestIcon id={interest.id} className="h-4 w-4" />
                    {interest.label}
                  </button>
                );
              })}
            </div>

            <label className="flex items-center gap-2.5 mt-5 sm:mt-6 cursor-pointer select-none w-fit">
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
          </>
        )}

        {error && <p className="mt-4 text-sm text-maroon font-medium">{error}</p>}
      </div>

      {/* ---- Analysing sequence (first run) ---- */}
      {phase === "thinking" && (
        <div className="mt-6 sm:mt-8 bg-surface rounded-2xl p-5 sm:p-6 border border-surface-alt animate-fade-up">
          <div className="flex items-center gap-3">
            <span className="flex items-center justify-center h-9 w-9 rounded-full bg-maroon/10 text-maroon shrink-0">
              <SparklesIcon className="h-4.5 w-4.5" />
            </span>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-text-muted">
                Course Matcher
              </p>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-sm font-medium text-text-primary">
                  {THINKING_STEPS[thinkingStep]}
                </span>
                <span className="flex gap-1">
                  {[0, 1, 2].map((d) => (
                    <span
                      key={d}
                      className="thinking-dot h-1.5 w-1.5 rounded-full bg-maroon"
                      style={{ animationDelay: `${d * 0.15}s` }}
                    />
                  ))}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ---- Results ---- */}
      {phase === "ready" && results && (
        <div
          ref={resultsRef}
          className={`mt-6 sm:mt-8 scroll-mt-24 transition-opacity duration-200 ${
            updating ? "opacity-60" : "opacity-100"
          }`}
        >
          {/* Reasoning summary, typed out */}
          <div className="bg-maroon/5 border border-maroon/10 rounded-2xl p-4 sm:p-5 animate-fade-up">
            <div className="flex items-start gap-3">
              <span className="flex items-center justify-center h-9 w-9 rounded-full bg-maroon text-white shrink-0">
                <SparklesIcon className="h-4.5 w-4.5" />
              </span>
              <div className="min-w-0">
                <p className="text-[10px] font-bold uppercase tracking-wider text-text-muted flex items-center gap-2">
                  Course Matcher
                  {updating && (
                    <span className="flex gap-1 normal-case">
                      {[0, 1, 2].map((d) => (
                        <span
                          key={d}
                          className="thinking-dot h-1 w-1 rounded-full bg-maroon"
                          style={{ animationDelay: `${d * 0.15}s` }}
                        />
                      ))}
                    </span>
                  )}
                </p>
                <p className="mt-1 text-sm sm:text-base text-text-primary leading-relaxed">
                  {typed}
                  {typed.length < summary.length && (
                    <span className="animate-caret inline-block w-0.5 h-4 bg-maroon align-middle ml-0.5" />
                  )}
                </p>
              </div>
            </div>
          </div>

          {topMatch ? (
            <>
              {/* Best match reveal */}
              <div
                className="mt-4 sm:mt-5 relative bg-surface rounded-2xl border-2 border-maroon/25 shadow-md p-5 sm:p-8 animate-fade-up"
                style={{ animationDelay: "0.12s" }}
              >
                <div className="absolute -top-3 left-5 sm:left-8 flex items-center gap-1.5 bg-maroon text-white text-[10px] sm:text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full">
                  <CheckCircleIcon className="h-3.5 w-3.5" />
                  Best Match · {topMatch.score}%
                </div>

                <div className="grid grid-cols-1 md:grid-cols-[1fr_260px] gap-6 md:gap-8 mt-2">
                  <div className="min-w-0">
                    {topMatch.programme.school_name && (
                      <span className="inline-flex text-xs font-semibold text-maroon bg-maroon/10 px-2 py-0.5 rounded-md">
                        {topMatch.programme.school_name}
                      </span>
                    )}
                    <h3 className="mt-2 text-xl sm:text-2xl font-extrabold text-text-primary leading-tight">
                      {topMatch.programme.name}
                    </h3>

                    <div className="flex flex-wrap items-center gap-2 mt-2.5">
                      {topMatch.programme.degree_type && (
                        <span className="text-xs font-semibold text-maroon bg-maroon/8 px-2 py-0.5 rounded-md">
                          {topMatch.programme.degree_type}
                        </span>
                      )}
                      {topMatch.programme.duration_years && (
                        <span className="inline-flex items-center gap-1 text-xs text-text-muted">
                          <ClockIcon className="h-3.5 w-3.5" />
                          {topMatch.programme.duration_years} year
                          {topMatch.programme.duration_years > 1 ? "s" : ""}
                        </span>
                      )}
                      {topMatch.matched.map((m) => (
                        <span
                          key={m.id}
                          className="inline-flex items-center gap-1 text-xs bg-accent/10 text-accent-dark px-2 py-0.5 rounded-full font-medium"
                        >
                          <InterestIcon id={m.id} className="h-3 w-3" />
                          {m.label}
                        </span>
                      ))}
                    </div>

                    {topMatch.programme.description && (
                      <p className="mt-3 text-sm text-text-secondary leading-relaxed line-clamp-3">
                        {topMatch.programme.description}
                      </p>
                    )}

                    <Link
                      to={`/programmes/${topMatch.programme._id}`}
                      className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 bg-maroon text-white text-sm font-semibold rounded-xl hover:bg-maroon-dark transition-all"
                    >
                      View full programme →
                    </Link>
                  </div>

                  {topMatch.programme.composition &&
                    Object.keys(topMatch.programme.composition).length > 0 && (
                      <div className="md:border-l md:border-surface-alt md:pl-6">
                        <p className="text-xs font-bold uppercase tracking-wider text-text-muted mb-3">
                          How you'd spend your time
                        </p>
                        <CompositionBars composition={topMatch.programme.composition} />
                      </div>
                    )}
                </div>
              </div>

              {/* Runners-up, streaming in */}
              {runnersUp.length > 0 && (
                <div className="mt-6 sm:mt-8">
                  <div className="flex items-end justify-between gap-2 mb-3 sm:mb-4">
                    <h3 className="text-base sm:text-lg font-bold text-text-primary">
                      More good fits
                    </h3>
                    <Link
                      to="/programmes"
                      className="text-sm font-medium text-maroon hover:underline shrink-0"
                    >
                      Browse all programmes →
                    </Link>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4 text-left">
                    {runnersUp.map((result, i) => (
                      <ProgrammeCard
                        key={result.programme._id}
                        programme={result.programme}
                        showSchool
                        className="animate-fade-up"
                        style={{ animationDelay: `${0.2 + i * 0.08}s` }}
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
                </div>
              )}
            </>
          ) : (
            /* Empty state */
            <div
              className="mt-4 sm:mt-5 bg-surface rounded-2xl p-8 sm:p-10 text-center border border-surface-alt animate-fade-up"
              style={{ animationDelay: "0.12s" }}
            >
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
                    onClick={() => setIncludePostgrad(true)}
                    className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-maroon text-white text-sm font-semibold rounded-xl hover:bg-maroon-dark transition-all cursor-pointer"
                  >
                    Include postgraduate programmes
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
    </div>
  );
}
