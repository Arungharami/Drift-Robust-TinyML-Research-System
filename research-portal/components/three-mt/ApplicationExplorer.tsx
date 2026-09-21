"use client";

import { useState } from "react";

const SCENES = [
  {
    id: "factory",
    label: "Factory",
    tagline: "Detect changing industrial gas patterns.",
    body: "Industrial electronic-nose deployments run for years without sensor replacement — a drift-honest evaluation protocol could inform maintenance and recalibration scheduling.",
  },
  {
    id: "food",
    label: "Food",
    tagline: "Monitor freshness-related chemical patterns.",
    body: "Spoilage and freshness detection is a natural electronic-nose application; this project's chronological protocol could validate whether a food-safety model still holds after sensor aging.",
  },
  {
    id: "environment",
    label: "Environment",
    tagline: "Monitor long-lived sensing systems.",
    body: "Chronological-drift-aware evaluation applies directly to any long-lived environmental sensor network (air or water quality) where recalibration is expensive or impossible.",
  },
  {
    id: "edge",
    label: "Edge Devices",
    tagline: "Run intelligence under tight memory, compute, and energy constraints.",
    body: "The resource-aware explanation and TinyML export methodology targets exactly this constraint set — a microcontroller-class budget, not a server.",
  },
  {
    id: "research",
    label: "Research / Diagnostics",
    tagline: "Explore trustworthy sensing where sensor behavior can change.",
    body: "Breath- or odor-based diagnostic research faces the same sensor-drift risk; resource-aware explainability could support clinician trust in a constrained device.",
  },
] as const;

/** Section 8 — a single sensor platform moving through candidate deployment scenes. */
export function ApplicationExplorer() {
  const [active, setActive] = useState<(typeof SCENES)[number]["id"]>("factory");
  const scene = SCENES.find((s) => s.id === active)!;

  return (
    <section className="threemt-apps" aria-labelledby="threemt-apps-title">
      <h2 id="threemt-apps-title">Why This Matters</h2>
      <p className="threemt-apps-flag">Potential application directions — not demonstrated outcomes</p>
      <p style={{ maxWidth: "62ch" }}>
        One sensor platform, one methodology. Each scene below is a direction this work could
        inform, not a deployment this project has run.
      </p>

      <div className="threemt-apps-tabs" role="tablist" aria-label="Application directions">
        {SCENES.map((s) => (
          <button
            key={s.id}
            type="button"
            role="tab"
            aria-selected={s.id === active}
            className="threemt-apps-tab"
            onClick={() => setActive(s.id)}
          >
            {s.label}
          </button>
        ))}
      </div>

      <div className="threemt-apps-scene" role="tabpanel">
        <div className="threemt-apps-scene-platform" aria-hidden="true">
          <span className="threemt-apps-scene-dot" />
        </div>
        <div>
          <h3 style={{ marginTop: 0 }}>{scene.tagline}</h3>
          <p style={{ marginBottom: 0 }}>{scene.body}</p>
        </div>
      </div>
    </section>
  );
}
