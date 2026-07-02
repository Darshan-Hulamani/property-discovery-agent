import { useState, useEffect } from "react";
import Chat from "./components/Chat";
import "./App.css";

export default function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("theme") || "light";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <span className="brand-icon">🏠</span>
          <div>
            <h1>Property Discovery Agent</h1>
            <p>Autonomous AI assistant for Indian home buyers</p>
          </div>
        </div>
        <div className="header-controls">
          <button className="theme-toggle-btn" onClick={toggleTheme} aria-label="Toggle Theme">
            {theme === "light" ? "🌙 Dark" : "☀️ Light"}
          </button>
        </div>
      </header>
      <main>
        <Chat />
      </main>
    </div>
  );
}
