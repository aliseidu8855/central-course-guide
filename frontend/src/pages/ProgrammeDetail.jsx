/**
 * ProgrammeDetail.jsx — Individual Programme Page (No Emojis)
 *
 * Route: "/programmes/:programmeId"
 */

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import {
  GraduationCapIcon,
  ClockIcon,
  BookOpenIcon,
  ClipboardIcon,
  ChecklistIcon,
  RocketIcon,
  FaceFrownIcon,
  DocumentIcon,
  CheckCircleIcon,
  ChartBarIcon,
  InterestIcon,
} from "../components/Icons";
import CompositionBars from "../components/CompositionBars";

const BackIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
  </svg>
);

export default function ProgrammeDetail() {
  const { programmeId } = useParams();
  const [programme, setProgramme] = useState(null);
  const [interestLabels, setInterestLabels] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProgramme = async () => {
      try {
        const [progRes, interestsRes] = await Promise.all([
          api.get(`/programmes/${programmeId}`),
          api.get("/interests"),
        ]);
        setProgramme(progRes.data);
        setInterestLabels(
          Object.fromEntries(interestsRes.data.map((i) => [i.id, i.label]))
        );
      } catch (err) {
        console.error("Failed to load programme:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProgramme();
  }, [programmeId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-maroon border-t-transparent" />
      </div>
    );
  }

  if (!programme) {
    return (
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12 sm:py-16 text-center">
        <FaceFrownIcon className="h-12 w-12 sm:h-14 sm:w-14 text-text-muted mx-auto mb-4" />
        <h2 className="text-xl sm:text-2xl font-bold text-text-primary">Programme Not Found</h2>
        <Link to="/schools" className="mt-4 inline-flex items-center gap-2 text-maroon font-medium hover:underline text-sm">
          <BackIcon /> Browse Schools
        </Link>
      </section>
    );
  }

  const school = programme.school;

  return (
    <section className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-text-muted mb-4 sm:mb-6 flex-wrap">
        <Link to="/schools" className="hover:text-maroon transition-colors">Schools</Link>
        <span>/</span>
        {school && (
          <>
            <Link to={`/schools/${school._id}`} className="hover:text-maroon transition-colors truncate max-w-[140px] sm:max-w-none">
              {school.name}
            </Link>
            <span>/</span>
          </>
        )}
        <span className="text-text-primary font-medium truncate max-w-[160px] sm:max-w-none">{programme.name}</span>
      </nav>

      {/* Programme Header Card */}
      <div className="bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
        {school && (
          <Link
            to={`/schools/${school._id}`}
            className="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1 rounded-lg bg-maroon/10 text-maroon text-[10px] sm:text-xs font-bold tracking-wide hover:bg-maroon/20 transition-colors mb-3 sm:mb-4"
          >
            {school.code} — {school.name}
          </Link>
        )}

        <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-text-primary leading-tight">
          {programme.name}
        </h1>

        {/* Quick info pills */}
        <div className="flex flex-wrap gap-2 sm:gap-3 mt-4 sm:mt-5">
          {programme.degree_type && (
            <span className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-maroon/10 text-xs sm:text-sm font-semibold text-maroon">
              <GraduationCapIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              {programme.degree_type}
            </span>
          )}
          {programme.duration_years && (
            <span className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-background text-xs sm:text-sm font-medium text-text-secondary">
              <ClockIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              {programme.duration_years} Year{programme.duration_years > 1 ? "s" : ""}
            </span>
          )}
          {programme.subjects && programme.subjects.length > 0 && (
            <span className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-background text-xs sm:text-sm font-medium text-text-secondary">
              <BookOpenIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              {programme.subjects.length} Subjects
            </span>
          )}
        </div>

        {/* Interest tags */}
        {programme.interest_tags && programme.interest_tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3 sm:mt-4">
            {programme.interest_tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full bg-accent/10 text-accent-dark text-xs font-semibold"
              >
                <InterestIcon id={tag} className="h-3.5 w-3.5" />
                {interestLabels[tag] || tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Composition — What You'll Spend Your Time On */}
      {programme.composition && Object.keys(programme.composition).length > 0 && (
        <div className="mt-5 sm:mt-8 bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2 mb-1.5 sm:mb-2">
            <ChartBarIcon className="h-5 w-5 sm:h-6 sm:w-6 text-maroon" />
            What You'll Spend Your Time On
          </h2>
          <p className="text-text-secondary text-xs sm:text-sm mb-4 sm:mb-5">
            Approximate breakdown of how study time is typically split in this programme.
          </p>
          <CompositionBars composition={programme.composition} />
        </div>
      )}

      {/* Description */}
      {programme.description && (
        <div className="mt-5 sm:mt-8 bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2 mb-3 sm:mb-4">
            <ClipboardIcon className="h-5 w-5 sm:h-6 sm:w-6 text-maroon" />
            About This Programme
          </h2>
          <p className="text-text-secondary text-sm sm:text-base leading-relaxed whitespace-pre-line">
            {programme.description}
          </p>
        </div>
      )}

      {/* Entry Requirements */}
      {programme.entry_requirements && programme.entry_requirements.length > 0 && (
        <div className="mt-5 sm:mt-8 bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2 mb-3 sm:mb-4">
            <ChecklistIcon className="h-5 w-5 sm:h-6 sm:w-6 text-maroon" />
            Entry Requirements
          </h2>
          <ul className="space-y-2.5 sm:space-y-3">
            {programme.entry_requirements.map((req, i) => (
              <li key={i} className="flex items-start gap-2.5 sm:gap-3">
                <span className="flex items-center justify-center h-5 w-5 sm:h-6 sm:w-6 rounded-full bg-accent/10 text-accent-dark shrink-0 mt-0.5">
                  <CheckCircleIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                </span>
                <span className="text-text-secondary text-sm sm:text-base">{req}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Subjects / Curriculum */}
      {programme.subjects && programme.subjects.length > 0 && (
        <div className="mt-5 sm:mt-8 bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2 mb-3 sm:mb-4">
            <BookOpenIcon className="h-5 w-5 sm:h-6 sm:w-6 text-maroon" />
            Subjects & Curriculum
          </h2>
          <p className="text-text-secondary text-xs sm:text-sm mb-4 sm:mb-5">
            Key courses you will study in this programme:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-2.5">
            {programme.subjects.map((subject, i) => (
              <div
                key={i}
                className="flex items-center gap-2.5 sm:gap-3 p-3 sm:p-3.5 rounded-xl bg-background border border-surface-alt hover:border-maroon/20 transition-colors"
              >
                <span className="flex items-center justify-center h-6 w-6 sm:h-7 sm:w-7 rounded-full bg-maroon/10 text-maroon text-[10px] sm:text-xs font-bold shrink-0">
                  {i + 1}
                </span>
                <span className="text-text-primary text-xs sm:text-sm font-medium">{subject}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Career Paths */}
      {programme.career_paths && programme.career_paths.length > 0 && (
        <div className="mt-5 sm:mt-8 bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2 mb-3 sm:mb-4">
            <RocketIcon className="h-5 w-5 sm:h-6 sm:w-6 text-maroon" />
            Career Paths & Opportunities
          </h2>
          <p className="text-text-secondary text-xs sm:text-sm mb-4 sm:mb-5">
            Graduates of this programme can pursue careers in the following areas:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3">
            {programme.career_paths.map((career, i) => (
              <div
                key={i}
                className="flex items-center gap-2.5 sm:gap-3 p-3 sm:p-4 rounded-xl bg-gradient-to-r from-background to-surface border border-surface-alt hover:border-accent/30 transition-colors"
              >
                <span className="flex items-center justify-center h-7 w-7 sm:h-8 sm:w-8 rounded-full bg-accent/10 text-accent-dark text-xs sm:text-sm font-bold shrink-0">
                  {i + 1}
                </span>
                <span className="text-text-primary text-sm font-medium">{career}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No data notice */}
      {!programme.description && (!programme.career_paths || programme.career_paths.length === 0) && (
        <div className="mt-5 sm:mt-8 bg-surface rounded-2xl p-6 sm:p-8 shadow-sm border border-surface-alt text-center">
          <DocumentIcon className="h-10 w-10 sm:h-12 sm:w-12 text-text-muted mx-auto mb-3" />
          <p className="text-text-muted text-sm sm:text-base">
            Detailed information for this programme is being updated.
            Check back soon for subject breakdowns, career paths, and more.
          </p>
        </div>
      )}

      {/* Back links */}
      <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row gap-3 sm:gap-4">
        {school && (
          <Link
            to={`/schools/${school._id}`}
            className="inline-flex items-center justify-center sm:justify-start gap-2 px-5 sm:px-6 py-2.5 sm:py-3 bg-maroon text-white font-semibold rounded-xl hover:bg-maroon-dark transition-all text-sm sm:text-base"
          >
            <BackIcon /> Back to {school.name}
          </Link>
        )}
        <Link
          to="/schools"
          className="inline-flex items-center justify-center sm:justify-start gap-2 px-5 sm:px-6 py-2.5 sm:py-3 border-2 border-surface-alt text-text-secondary font-semibold rounded-xl hover:border-maroon hover:text-maroon transition-all text-sm sm:text-base"
        >
          All Schools
        </Link>
      </div>
    </section>
  );
}
