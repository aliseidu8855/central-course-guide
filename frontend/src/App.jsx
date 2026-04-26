/**
 * App.jsx — Root Application Component
 *
 * Sets up React Router with:
 *   • A persistent Navbar + Footer rendered on every page.
 *   • Client-side routes for all pages.
 *   • An <Outlet /> that swaps page content based on the active route.
 */

import {
  createBrowserRouter,
  RouterProvider,
  Outlet,
} from "react-router-dom";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Schools from "./pages/Schools";
import SchoolDetail from "./pages/SchoolDetail";
import ProgrammeDetail from "./pages/ProgrammeDetail";

import ScrollToTop from "./components/ScrollToTop";

// Layout: Wraps every route with Navbar + Footer
function RootLayout() {
  return (
    <div className="flex flex-col min-h-screen">
      <ScrollToTop />
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

// Router configuration
const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: "schools", element: <Schools /> },
      { path: "schools/:schoolId", element: <SchoolDetail /> },
      { path: "programmes/:programmeId", element: <ProgrammeDetail /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
