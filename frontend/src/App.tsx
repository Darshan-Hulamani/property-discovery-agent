import { useEffect, useState } from "react";
import Chat from "./components/Chat";
import "./App.css";

type Theme = "light" | "dark";
type View = "home" | "workspace";

function viewFromHash(): View {
  return ["#workspace", "#shortlist", "#map"].includes(window.location.hash) ? "workspace" : "home";
}

export default function App() {
  const [theme, setTheme] = useState<Theme>(() => {
    return (localStorage.getItem("theme") as Theme) || "light";
  });
  const [view, setView] = useState<View>(viewFromHash);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    const syncView = () => {
      setView(viewFromHash());
    };
    syncView();
    window.addEventListener("hashchange", syncView);
    return () => window.removeEventListener("hashchange", syncView);
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <div className="app">
      <div className="ambient-grid" aria-hidden="true" />
      <header className="app-header">
        <a className="brand" href="#home" aria-label="Property Discovery Agent home">
          <span className="brand-mark">P</span>
          <span>
            <strong>Property Discovery Agent</strong>
            <small>AI real estate advisor</small>
          </span>
        </a>
        <nav className="nav-links" aria-label="Product sections">
          <a href="#home">Home</a>
          <a href="#workspace">Advisor</a>
          <a href="#shortlist">Shortlist</a>
          <a href="#map">Map</a>
        </nav>
        <button className="theme-toggle-btn" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === "light" ? "Dark" : "Light"}
        </button>
      </header>

      <main className={view === "workspace" ? "workspace-view" : "home-view"}>
        {view === "home" && (
        <section id="home" className="hero-shell" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">AI property consultant for Indian buyers</p>
            <h1 id="hero-title">Find homes with reasoning, not random listings.</h1>
            <p>
              Compare budget, commute, schools, safety, metro access, and investment upside through a conversational agent that remembers your priorities.
            </p>
            <div className="hero-actions">
              <a className="hero-primary" href="#workspace">Open advisor</a>
              <a className="hero-secondary" href="#workspace">Start searching</a>
            </div>
          </div>
          <div className="hero-metrics" aria-label="Product highlights">
            <div>
              <strong>9-factor</strong>
              <span>ranking model</span>
            </div>
            <div>
              <strong>Live</strong>
              <span>commute routing</span>
            </div>
            <div>
              <strong>30+</strong>
              <span>curated listings</span>
            </div>
          </div>
          <footer className="home-footer">
            Developed by <strong>Darshan Hulamani</strong>
          </footer>
        </section>
        )}

        {view === "workspace" && (
        <section id="workspace" className="workspace-shell">
          <Chat />
        </section>
        )}
      </main>
    </div>
  );
}
