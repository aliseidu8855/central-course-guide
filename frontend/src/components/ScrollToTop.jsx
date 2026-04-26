/**
 * ScrollToTop.jsx — Reset scroll position on route change
 *
 * Without this, React Router preserves the scroll position
 * when navigating between pages, causing users to land at
 * the bottom of new pages.
 */

import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export default function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}
