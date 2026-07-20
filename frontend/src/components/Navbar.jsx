/**
 * Navbar.jsx — Responsive Top Navigation Bar
 *
 * Sticky navbar with brand name, navigation links,
 * hamburger menu on mobile, and "Apply Now" CTA.
 */

import { useState } from "react";
import { NavLink } from "react-router-dom";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  const linkClass = ({ isActive }) =>
    `text-sm font-medium transition-colors duration-200 ${
      isActive
        ? "text-maroon border-b-2 border-maroon pb-0.5"
        : "text-text-secondary hover:text-maroon"
    }`;

  const mobileLinkClass = ({ isActive }) =>
    `block py-2.5 text-base font-medium transition-colors ${
      isActive ? "text-maroon" : "text-text-secondary hover:text-maroon"
    }`;

  return (
    <header className="sticky top-0 z-50 bg-surface/80 backdrop-blur-md border-b border-surface-alt">
      <nav className="max-w-6xl mx-auto flex items-center justify-between px-4 sm:px-6 py-3.5 sm:py-4">
        {/* Brand */}
        <NavLink to="/" className="flex items-center gap-1.5 sm:gap-2 group" onClick={() => setMenuOpen(false)}>
          <span className="text-xl sm:text-2xl font-extrabold text-maroon tracking-tight group-hover:opacity-80 transition-opacity">
            Central
          </span>
          <span className="text-xl sm:text-2xl font-extrabold text-text-primary tracking-tight">
            Course Guide
          </span>
        </NavLink>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-6">
          <ul className="flex items-center gap-6">
            <li>
              <NavLink to="/" end className={linkClass}>Home</NavLink>
            </li>
            <li>
              <NavLink to="/schools" className={linkClass}>Schools</NavLink>
            </li>
            <li>
              <NavLink to="/programmes" end className={linkClass}>Programmes</NavLink>
            </li>
          </ul>
          <a
            href="https://central.edu.gh/online"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-5 py-2 bg-maroon text-white text-sm font-semibold rounded-lg hover:bg-maroon-dark transition-all duration-200 shadow-sm hover:shadow-md"
          >
            Apply Now
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
              <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
            </svg>
          </a>
        </div>

        {/* Mobile Hamburger */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="md:hidden flex flex-col gap-1.5 p-2 -mr-2"
          aria-label="Toggle navigation menu"
        >
          <span className={`block w-6 h-0.5 bg-text-primary transition-all duration-200 ${menuOpen ? "rotate-45 translate-y-2" : ""}`} />
          <span className={`block w-6 h-0.5 bg-text-primary transition-all duration-200 ${menuOpen ? "opacity-0" : ""}`} />
          <span className={`block w-6 h-0.5 bg-text-primary transition-all duration-200 ${menuOpen ? "-rotate-45 -translate-y-2" : ""}`} />
        </button>
      </nav>

      {/* Mobile Menu Dropdown */}
      {menuOpen && (
        <div className="md:hidden bg-surface border-t border-surface-alt px-4 pb-4 animate-in">
          <NavLink to="/" end className={mobileLinkClass} onClick={() => setMenuOpen(false)}>
            Home
          </NavLink>
          <NavLink to="/schools" className={mobileLinkClass} onClick={() => setMenuOpen(false)}>
            Schools
          </NavLink>
          <NavLink to="/programmes" end className={mobileLinkClass} onClick={() => setMenuOpen(false)}>
            Programmes
          </NavLink>
          <a
            href="https://central.edu.gh/online"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 flex items-center justify-center gap-1.5 w-full px-5 py-2.5 bg-maroon text-white text-sm font-semibold rounded-lg"
          >
            Apply Now
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
              <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
            </svg>
          </a>
        </div>
      )}
    </header>
  );
}
