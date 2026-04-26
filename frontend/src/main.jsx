/**
 * main.jsx — Application Entry Point
 * =====================================
 *
 * Mounts the React application into the DOM.
 * Imports the global stylesheet that includes Tailwind CSS.
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
