/**
 * CompositionBars.jsx — Study-Time Composition Bars
 *
 * Renders a programme's composition dict ({dimension_id: percent}) as
 * horizontal bars, sorted largest first. Returns null when there is no
 * composition data, so callers can render it unconditionally.
 *
 * Dimension ids/labels mirror backend models/taxonomy.py; the label
 * fallback keeps unknown keys from ever crashing the page.
 */

const DIMENSION_META = {
  coding: { label: "Coding & Software", color: "bg-maroon" },
  mathematics: { label: "Maths & Calculations", color: "bg-maroon-light" },
  theory: { label: "Theory & Reading", color: "bg-accent-dark" },
  practicals: { label: "Practicals & Fieldwork", color: "bg-accent" },
  creativity: { label: "Design & Creativity", color: "bg-maroon-dark" },
  people: { label: "People & Communication", color: "bg-accent-light" },
};

export default function CompositionBars({ composition }) {
  if (!composition || Object.keys(composition).length === 0) return null;

  const entries = Object.entries(composition).sort((a, b) => b[1] - a[1]);

  return (
    <div className="space-y-3.5 sm:space-y-4">
      {entries.map(([dim, value]) => {
        const meta = DIMENSION_META[dim] || {
          label: dim.charAt(0).toUpperCase() + dim.slice(1),
          color: "bg-maroon",
        };
        return (
          <div key={dim}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs sm:text-sm font-medium text-text-secondary">
                {meta.label}
              </span>
              <span className="text-xs sm:text-sm font-semibold text-text-primary">
                {value}%
              </span>
            </div>
            <div className="h-2.5 rounded-full bg-surface-alt overflow-hidden">
              <div
                className={`h-full rounded-full ${meta.color} transition-all duration-500`}
                style={{ width: `${value}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
