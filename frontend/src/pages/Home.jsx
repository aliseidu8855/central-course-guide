/**
 * Home.jsx — Landing / Home Page (Fully Responsive, No Emojis)
 *
 * Route: "/"
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import { SchoolIcon, BookOpenIcon, RocketIcon, GraduationCapIcon } from "../components/Icons";

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
    <>
      {/* ---------- Hero Section ---------- */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-maroon/5 via-transparent to-accent/5 pointer-events-none" />

        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 py-14 sm:py-20 md:py-28 text-center">
          {/* Badge */}
          <span className="inline-flex items-center gap-2 px-3 sm:px-4 py-1.5 rounded-full bg-maroon/10 text-maroon text-xs sm:text-sm font-semibold mb-6 sm:mb-8">
            <GraduationCapIcon className="h-4 w-4" />
            Central University Course Guide
          </span>

          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-text-primary leading-tight">
            Discover Your{" "}
            <span className="text-maroon">Academic Path</span>
          </h1>

          <p className="mt-4 sm:mt-6 max-w-2xl mx-auto text-base sm:text-lg text-text-secondary leading-relaxed px-2">
            Explore every school, programme, and subject Central University has to
            offer — all in one place. Make informed decisions about your academic
            journey and future career.
          </p>

          {/* CTA Buttons */}
          <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-4 sm:px-0">
            <Link
              to="/quiz"
              className="inline-flex items-center justify-center gap-2 px-6 sm:px-8 py-3 sm:py-3.5 bg-maroon text-white font-semibold rounded-xl shadow-lg hover:bg-maroon-dark transition-all duration-200 hover:shadow-xl hover:-translate-y-0.5"
            >
              Find Your Course
              <span aria-hidden="true">→</span>
            </Link>
            <Link
              to="/schools"
              className="inline-flex items-center justify-center gap-2 px-6 sm:px-8 py-3 sm:py-3.5 border-2 border-maroon text-maroon font-semibold rounded-xl hover:bg-maroon hover:text-white transition-all duration-200"
            >
              Browse Schools
            </Link>
          </div>

          {/* Live Stats */}
          {(stats.schools > 0 || stats.programmes > 0) && (
            <div className="mt-10 sm:mt-14 flex justify-center gap-6 sm:gap-8 md:gap-14">
              <div className="text-center">
                <p className="text-3xl sm:text-4xl font-extrabold text-maroon">{stats.schools}</p>
                <p className="text-xs sm:text-sm text-text-muted mt-1">Schools & Faculties</p>
              </div>
              <div className="h-10 sm:h-12 w-px bg-surface-alt" />
              <div className="text-center">
                <p className="text-3xl sm:text-4xl font-extrabold text-maroon">{stats.programmes}</p>
                <p className="text-xs sm:text-sm text-text-muted mt-1">Programmes Available</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ---------- Feature Highlights ---------- */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
          {/* All Schools — clickable */}
          <Link
            to="/schools"
            className="group bg-surface rounded-2xl p-5 sm:p-7 shadow-sm hover:shadow-lg transition-all duration-300 border border-surface-alt hover:border-maroon/20 hover:-translate-y-1"
          >
            <div className="h-10 w-10 sm:h-12 sm:w-12 rounded-xl bg-maroon/10 flex items-center justify-center text-maroon">
              <SchoolIcon className="h-5 w-5 sm:h-6 sm:w-6" />
            </div>
            <h3 className="mt-3 sm:mt-4 text-lg sm:text-xl font-bold text-text-primary group-hover:text-maroon transition-colors">
              All Schools
            </h3>
            <p className="mt-1.5 sm:mt-2 text-text-secondary text-sm leading-relaxed">
              Browse every faculty and school in the university with detailed descriptions.
            </p>
            <span className="mt-3 sm:mt-4 inline-flex text-sm font-medium text-maroon opacity-0 group-hover:opacity-100 transition-opacity">
              Browse Schools →
            </span>
          </Link>

          {/* All Programmes — clickable */}
          <Link
            to="/programmes"
            className="group bg-surface rounded-2xl p-5 sm:p-7 shadow-sm hover:shadow-lg transition-all duration-300 border border-surface-alt hover:border-maroon/20 hover:-translate-y-1"
          >
            <div className="h-10 w-10 sm:h-12 sm:w-12 rounded-xl bg-accent/10 flex items-center justify-center text-accent-dark">
              <BookOpenIcon className="h-5 w-5 sm:h-6 sm:w-6" />
            </div>
            <h3 className="mt-3 sm:mt-4 text-lg sm:text-xl font-bold text-text-primary group-hover:text-maroon transition-colors">
              All Programmes
            </h3>
            <p className="mt-1.5 sm:mt-2 text-text-secondary text-sm leading-relaxed">
              Read through every programme — subjects, entry requirements, and how
              you'll spend your study time.
            </p>
            <span className="mt-3 sm:mt-4 inline-flex text-sm font-medium text-maroon opacity-0 group-hover:opacity-100 transition-opacity">
              Browse Programmes →
            </span>
          </Link>

          {/* Career Paths — informational */}
          <div className="bg-surface rounded-2xl p-5 sm:p-7 shadow-sm border border-surface-alt">
            <div className="h-10 w-10 sm:h-12 sm:w-12 rounded-xl bg-maroon/5 flex items-center justify-center text-maroon-light">
              <RocketIcon className="h-5 w-5 sm:h-6 sm:w-6" />
            </div>
            <h3 className="mt-3 sm:mt-4 text-lg sm:text-xl font-bold text-text-primary">
              Career Paths
            </h3>
            <p className="mt-1.5 sm:mt-2 text-text-secondary text-sm leading-relaxed">
              Discover where each programme can take your career with real job opportunities.
            </p>
          </div>
        </div>
      </section>

      {/* ---------- How It Works ---------- */}
      <section id="how-it-works" className="bg-surface py-12 sm:py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-text-primary">
              How It Works
            </h2>
            <p className="mt-2 sm:mt-3 text-text-secondary max-w-xl mx-auto text-sm sm:text-base">
              Three simple steps to find the right programme for you.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8">
            {[
              {
                step: "01",
                title: "Take the Interest Quiz",
                desc: "Pick the things you enjoy — gaming, caring for people, business, art — and get matched to programmes instantly.",
              },
              {
                step: "02",
                title: "Explore Programmes",
                desc: "Read through recommended or all programmes, with subjects, entry requirements, and study-time breakdowns.",
              },
              {
                step: "03",
                title: "Discover Career Paths",
                desc: "See potential career opportunities and job roles available to graduates of each programme.",
              },
            ].map((item) => (
              <div key={item.step} className="relative">
                <span className="text-4xl sm:text-5xl font-extrabold text-maroon/10">{item.step}</span>
                <h3 className="mt-1 sm:mt-2 text-base sm:text-lg font-bold text-text-primary">{item.title}</h3>
                <p className="mt-1.5 sm:mt-2 text-text-secondary text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------- CTA Section ---------- */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
        <div className="bg-maroon rounded-2xl p-8 sm:p-10 md:p-14 text-center text-white">
          <h2 className="text-2xl sm:text-3xl font-extrabold">Not Sure What to Study?</h2>
          <p className="mt-3 sm:mt-4 text-white/80 max-w-lg mx-auto text-sm sm:text-base">
            Don't choose a course blindly. Take the interest quiz and get matched to
            programmes that fit you.
          </p>
          <div className="mt-6 sm:mt-8 flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
            <Link
              to="/quiz"
              className="inline-flex items-center justify-center gap-2 px-6 sm:px-8 py-3 sm:py-3.5 bg-white text-maroon font-bold rounded-xl hover:bg-gray-100 transition-all shadow-lg text-sm sm:text-base"
            >
              Take the Interest Quiz →
            </Link>
            <Link
              to="/programmes"
              className="inline-flex items-center justify-center gap-2 px-6 sm:px-8 py-3 sm:py-3.5 border-2 border-white/40 text-white font-semibold rounded-xl hover:bg-white/10 transition-all text-sm sm:text-base"
            >
              Browse All Programmes
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
