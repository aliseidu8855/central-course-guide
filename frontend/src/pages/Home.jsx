/**
 * Home.jsx — Landing Page (No Emojis)
 *
 * Route: "/"
 *
 * The landing page IS the quiz: no feature cards, no "how it works",
 * no marketing filler. Students land, tap what they love, and get
 * programme matches on the spot.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import InterestQuiz from "../components/InterestQuiz";

export default function Home() {
  const [stats, setStats] = useState({ schools: 0, programmes: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get("/schools");
        const totalProgs = res.data.reduce(
          (sum, s) => sum + (s.programme_count || 0),
          0
        );
        setStats({ schools: res.data.length, programmes: totalProgs });
      } catch {
        // Stats are decorative
      }
    };
    fetchStats();
  }, []);

  return (
    <section className="relative overflow-hidden">
      {/* Soft decorative background */}
      <div className="absolute inset-0 bg-linear-to-br from-maroon/5 via-transparent to-accent/10 pointer-events-none" />
      <div className="absolute -top-24 -right-24 h-72 w-72 rounded-full bg-accent/15 blur-3xl pointer-events-none" />
      <div className="absolute top-64 -left-32 h-80 w-80 rounded-full bg-maroon/10 blur-3xl pointer-events-none" />

      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 pt-12 sm:pt-20 pb-16 sm:pb-24">
        {/* Headline */}
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-text-primary leading-[1.05]">
            Don't pick a course.
            <br />
            <span className="text-maroon">Pick what you love.</span>
          </h1>
          <p className="mt-4 sm:mt-6 max-w-xl mx-auto text-base sm:text-lg text-text-secondary leading-relaxed">
            Tap a few things you enjoy — we'll match you to the right programme
            {stats.programmes > 0
              ? ` out of ${stats.programmes} across ${stats.schools} schools at Central University.`
              : " at Central University."}
          </p>
        </div>

        {/* The quiz, right here on the landing page */}
        <div className="mt-8 sm:mt-12">
          <InterestQuiz />
        </div>

        {/* Quiet alternatives — no banners, no cards */}
        <p className="mt-8 sm:mt-10 text-center text-sm text-text-muted">
          Prefer to read through them yourself?{" "}
          <Link to="/programmes" className="font-medium text-maroon hover:underline">
            All programmes
          </Link>
          <span className="mx-2">·</span>
          <Link to="/schools" className="font-medium text-maroon hover:underline">
            Schools &amp; faculties
          </Link>
        </p>
      </div>
    </section>
  );
}
