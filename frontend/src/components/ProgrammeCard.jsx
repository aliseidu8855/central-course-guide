/**
 * ProgrammeCard.jsx — Shared Programme Card
 *
 * Used by SchoolDetail, the Programmes browse page, and the Quiz results.
 *
 * Props:
 *   programme  — the programme document.
 *   showSchool — also render the parent school name badge.
 *   extra      — optional node rendered at the bottom (e.g. quiz match info).
 *   className / style — merged onto the card (e.g. stagger animations).
 *
 * The card is an <a>; the explicit `block` keeps its background painting
 * correctly even when it isn't a direct grid/flex item.
 */

import { Link } from "react-router-dom";

export default function ProgrammeCard({
  programme,
  showSchool = false,
  extra = null,
  className = "",
  style,
}) {
  return (
    <Link
      to={`/programmes/${programme._id}`}
      style={style}
      className={`group block bg-surface rounded-xl p-4 sm:p-5 border border-surface-alt hover:border-maroon/30 hover:shadow-md transition-all duration-200 ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {showSchool && programme.school_name && (
            <span className="inline-flex mb-1.5 text-xs font-semibold text-maroon bg-maroon/10 px-2 py-0.5 rounded-md">
              {programme.school_name}
            </span>
          )}

          <h3 className="font-bold text-sm sm:text-base text-text-primary group-hover:text-maroon transition-colors leading-tight">
            {programme.name}
          </h3>

          <div className="flex flex-wrap items-center gap-2 mt-1.5">
            {programme.degree_type && (
              <span className="text-xs font-semibold text-maroon bg-maroon/8 px-2 py-0.5 rounded-md">
                {programme.degree_type}
              </span>
            )}
            {programme.duration_years && (
              <span className="text-xs text-text-muted">
                • {programme.duration_years} year{programme.duration_years > 1 ? "s" : ""}
              </span>
            )}
          </div>

          {programme.description && (
            <p className="text-xs sm:text-sm text-text-secondary mt-2 line-clamp-2">
              {programme.description}
            </p>
          )}

          {programme.career_paths && programme.career_paths.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2.5 sm:mt-3">
              {programme.career_paths.slice(0, 2).map((cp) => (
                <span key={cp} className="text-xs bg-accent/10 text-accent-dark px-2 py-0.5 rounded-full font-medium">
                  {cp}
                </span>
              ))}
              {programme.career_paths.length > 2 && (
                <span className="text-xs text-text-muted">+{programme.career_paths.length - 2} more</span>
              )}
            </div>
          )}

          {extra}
        </div>
        <span className="text-text-muted group-hover:text-maroon transition-colors mt-1 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        </span>
      </div>
    </Link>
  );
}
