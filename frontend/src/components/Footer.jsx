/**
 * Footer.jsx — Responsive Site Footer (No Emojis)
 */

import { Link } from "react-router-dom";
import { MapPinIcon, PhoneIcon, DevicePhoneIcon, EnvelopeIcon } from "./Icons";

export default function Footer() {
  return (
    <footer className="bg-text-primary text-white mt-12 sm:mt-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 sm:py-14">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 sm:gap-10">
          {/* Brand */}
          <div className="sm:col-span-2 md:col-span-1">
            <h3 className="text-lg sm:text-xl font-extrabold">
              <span className="text-maroon-light">Central</span> Course Guide
            </h3>
            <p className="mt-2 sm:mt-3 text-xs sm:text-sm text-gray-400 leading-relaxed">
              Helping new students at Central University explore schools,
              programmes, subjects, and career paths — all in one place.
            </p>
            <p className="mt-3 sm:mt-4 text-xs text-gray-500">
              © {new Date().getFullYear()} Central University. All rights reserved.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-gray-400 mb-3 sm:mb-4">
              Quick Links
            </h4>
            <ul className="space-y-2 sm:space-y-2.5">
              {[
                { label: "Home", to: "/" },
                { label: "Schools & Faculties", to: "/schools" },
                { label: "Central University", href: "https://central.edu.gh" },
                { label: "Apply Now", href: "https://central.edu.gh/online" },
              ].map((link) =>
                link.to ? (
                  <li key={link.label}>
                    <Link to={link.to} className="text-xs sm:text-sm text-gray-300 hover:text-white transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ) : (
                  <li key={link.label}>
                    <a href={link.href} target="_blank" rel="noopener noreferrer" className="text-xs sm:text-sm text-gray-300 hover:text-white transition-colors">
                      {link.label} ↗
                    </a>
                  </li>
                )
              )}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-gray-400 mb-3 sm:mb-4">
              Contact
            </h4>
            <ul className="space-y-2.5 sm:space-y-3 text-xs sm:text-sm text-gray-300">
              <li className="flex items-center gap-2">
                <MapPinIcon className="h-3.5 w-3.5 shrink-0 text-gray-400" />
                Miotso, near Dawhenya, Accra
              </li>
              <li>
                <a href="tel:+2330303318580" className="flex items-center gap-2 hover:text-white transition-colors">
                  <PhoneIcon className="h-3.5 w-3.5 shrink-0 text-gray-400" />
                  +233 030 331 8580
                </a>
              </li>
              <li>
                <a href="tel:+2330307020540" className="flex items-center gap-2 hover:text-white transition-colors">
                  <DevicePhoneIcon className="h-3.5 w-3.5 shrink-0 text-gray-400" />
                  Admission: +233 030 702 0540
                </a>
              </li>
              <li>
                <a href="mailto:pr@central.edu.gh" className="flex items-center gap-2 hover:text-white transition-colors">
                  <EnvelopeIcon className="h-3.5 w-3.5 shrink-0 text-gray-400" />
                  pr@central.edu.gh
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 sm:mt-10 pt-5 sm:pt-6 border-t border-gray-700 flex flex-col items-center gap-2 sm:flex-row sm:justify-between text-[10px] sm:text-xs text-gray-500 text-center sm:text-left">
          <p>
            Built by Nicholas Agboada Jnr & Mubariq Sarfo — S.E.T Final Year Project
          </p>
          <p>Supervised by Mr. Charles Fomevor</p>
        </div>
      </div>
    </footer>
  );
}
