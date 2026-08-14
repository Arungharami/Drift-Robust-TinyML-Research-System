"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark" | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("theme");
    if (stored === "light" || stored === "dark") setTheme(stored);
  }, []);

  useEffect(() => {
    if (!theme) return;
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("theme", theme);
  }, [theme]);

  function toggle() {
    const current =
      theme ?? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    setTheme(current === "dark" ? "light" : "dark");
  }

  const dark = theme === "dark";
  const label = dark ? "Switch to light mode" : "Switch to dark mode";

  return (
    <button type="button" className="theme-toggle" onClick={toggle} aria-label={label} title={label}>
      <span className="theme-toggle-icon" aria-hidden="true">{dark ? "☀" : "☾"}</span>
      <span className="theme-toggle-label">{dark ? "Light mode" : "Dark mode"}</span>
    </button>
  );
}
