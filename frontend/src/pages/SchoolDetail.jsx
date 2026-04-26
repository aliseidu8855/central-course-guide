/**
 * SchoolDetail.jsx — Individual School Page (No Emojis)
 *
 * Route: "/schools/:schoolId"
 */

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import { FaceFrownIcon } from "../components/Icons";

const BackIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
  </svg>
);

export default function SchoolDetail() {
  const { schoolId } = useParams();
  const [school, setSchool] = useState(null);
  const [programmes, setProgrammes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [schoolRes, progRes] = await Promise.all([
          api.get(`/schools/${schoolId}`),
          api.get(`/schools/${schoolId}/programmes`),
        ]);
        setSchool(schoolRes.data);
        setProgrammes(progRes.data);
      } catch (err) {
        console.error("Failed to load school:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [schoolId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-maroon border-t-transparent" />
      </div>
    );
  }

  if (!school) {
    return (
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12 sm:py-16 text-center">
        <FaceFrownIcon className="h-12 w-12 sm:h-14 sm:w-14 text-text-muted mx-auto mb-4" />
        <h2 className="text-xl sm:text-2xl font-bold text-text-primary">School Not Found</h2>
        <Link to="/schools" className="mt-4 inline-flex items-center gap-2 text-maroon font-medium hover:underline">
          <BackIcon /> Back to Schools
        </Link>
      </section>
    );
  }

  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
      {/* Breadcrumb */}
      <Link
        to="/schools"
        className="inline-flex items-center gap-2 text-sm text-text-muted hover:text-maroon transition-colors mb-4 sm:mb-6"
      >
        <BackIcon /> All Schools
      </Link>

      {/* School Header */}
      <div className="bg-surface rounded-2xl p-5 sm:p-8 shadow-sm border border-surface-alt">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <span className="inline-flex px-2.5 sm:px-3 py-1 rounded-lg bg-maroon/10 text-maroon text-xs font-bold tracking-wide mb-2 sm:mb-3">
              {school.code}
            </span>
            <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-text-primary leading-tight">
              {school.name}
            </h1>
            {school.description && (
              <p className="mt-2 sm:mt-3 text-text-secondary max-w-2xl leading-relaxed text-sm sm:text-base">
                {school.description}
              </p>
            )}
          </div>

          <div className="flex gap-4 md:flex-col md:items-end shrink-0">
            <div className="bg-background rounded-xl px-4 sm:px-5 py-2.5 sm:py-3 text-center">
              <p className="text-xl sm:text-2xl font-extrabold text-maroon">{programmes.length}</p>
              <p className="text-xs text-text-muted font-medium">Programmes</p>
            </div>
          </div>
        </div>

        {(school.dean || school.location) && (
          <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-surface-alt flex flex-col sm:flex-row flex-wrap gap-3 sm:gap-6 text-sm text-text-secondary">
            {school.dean && (
              <div className="flex items-center gap-2">
                <span className="font-semibold text-text-primary">Dean:</span>
                {school.dean}
              </div>
            )}
            {school.location && (
              <div className="flex items-center gap-2">
                <span className="font-semibold text-text-primary">Location:</span>
                {school.location}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Programmes List */}
      <div className="mt-8 sm:mt-10">
        <h2 className="text-xl sm:text-2xl font-bold text-text-primary mb-4 sm:mb-6">
          Programmes Offered
        </h2>

        {programmes.length === 0 ? (
          <div className="bg-surface rounded-xl p-6 sm:p-8 text-center border border-surface-alt">
            <p className="text-text-muted text-sm sm:text-base">No programmes listed for this school yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
            {programmes.map((prog) => (
              <Link
                to={`/programmes/${prog._id}`}
                key={prog._id}
                className="group bg-surface rounded-xl p-4 sm:p-5 border border-surface-alt hover:border-maroon/30 hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-sm sm:text-base text-text-primary group-hover:text-maroon transition-colors leading-tight">
                      {prog.name}
                    </h3>

                    <div className="flex flex-wrap items-center gap-2 mt-1.5">
                      {prog.degree_type && (
                        <span className="text-xs font-semibold text-maroon bg-maroon/8 px-2 py-0.5 rounded-md">
                          {prog.degree_type}
                        </span>
                      )}
                      {prog.duration_years && (
                        <span className="text-xs text-text-muted">
                          • {prog.duration_years} year{prog.duration_years > 1 ? "s" : ""}
                        </span>
                      )}
                    </div>

                    {prog.description && (
                      <p className="text-xs sm:text-sm text-text-secondary mt-2 line-clamp-2">
                        {prog.description}
                      </p>
                    )}

                    {prog.career_paths && prog.career_paths.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-2.5 sm:mt-3">
                        {prog.career_paths.slice(0, 2).map((cp) => (
                          <span key={cp} className="text-xs bg-accent/10 text-accent-dark px-2 py-0.5 rounded-full font-medium">
                            {cp}
                          </span>
                        ))}
                        {prog.career_paths.length > 2 && (
                          <span className="text-xs text-text-muted">+{prog.career_paths.length - 2} more</span>
                        )}
                      </div>
                    )}
                  </div>
                  <span className="text-text-muted group-hover:text-maroon transition-colors mt-1 shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
