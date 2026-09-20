"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { ProcessListView } from "./ProcessListView";
import { ProcessSceneBoundary } from "./ProcessSceneBoundary";
import type { ProcessPhase } from "@/lib/process-phases";

// Loaded only on this route, client-side only: three.js touches window/navigator at module
// load, which breaks static generation, and this keeps the ~150kB three/fiber/drei chunk out
// of every other page's first-load JS.
const ProcessScene = dynamic(() => import("./ProcessScene").then((m) => m.ProcessScene), {
  ssr: false,
  loading: () => <div className="process-canvas-loading">Loading 3D view…</div>,
});

function detectWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return !!(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

export function ProcessExplorer({ phases }: { phases: ProcessPhase[] }) {
  const [selectedPhaseId, setSelectedPhaseId] = useState<string>(phases[0]?.id ?? "");
  const [webglSupported, setWebglSupported] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [viewMode, setViewMode] = useState<"3d" | "list">("list");
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [sceneFailed, setSceneFailed] = useState(false);

  // Client-only capability detection. Defaults to the accessible list view for SSR/first paint
  // and upgrades to 3D only once WebGL support is confirmed, so there is no hydration flash.
  useEffect(() => {
    const supported = detectWebGL();
    setWebglSupported(supported);
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setReducedMotion(reduce);
    setViewMode(supported ? "3d" : "list");

    const readTheme = (): "light" | "dark" => {
      const explicit = document.documentElement.getAttribute("data-theme");
      if (explicit === "light" || explicit === "dark") return explicit;
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    };
    setTheme(readTheme());
    const observer = new MutationObserver(() => setTheme(readTheme()));
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => observer.disconnect();
  }, []);

  const selectedPhase = useMemo(
    () => phases.find((p) => p.id === selectedPhaseId) ?? phases[0] ?? null,
    [phases, selectedPhaseId]
  );

  return (
    <div className="process-explorer">
      <div className="process-toolbar">
        <div className="process-toolbar-group" role="group" aria-label="Visualization mode">
          <button
            type="button"
            className={`process-toggle${viewMode === "3d" ? " process-toggle-active" : ""}`}
            onClick={() => setViewMode("3d")}
            disabled={!webglSupported}
            title={webglSupported ? "Interactive 3D view" : "3D view unavailable — WebGL not detected in this browser"}
          >
            3D view
          </button>
          <button
            type="button"
            className={`process-toggle${viewMode === "list" ? " process-toggle-active" : ""}`}
            onClick={() => setViewMode("list")}
          >
            List view
          </button>
        </div>
        {reducedMotion && viewMode === "3d" && (
          <span className="process-toolbar-note">Motion reduced — camera auto-rotation is off.</span>
        )}
      </div>

      <div className="process-canvas-wrap">
        {viewMode === "3d" && webglSupported && !sceneFailed ? (
          <ProcessSceneBoundary onError={() => setSceneFailed(true)}>
            <ProcessScene
              phases={phases}
              selectedPhaseId={selectedPhaseId}
              onSelect={setSelectedPhaseId}
              reducedMotion={reducedMotion}
              theme={theme}
            />
          </ProcessSceneBoundary>
        ) : (
          <ProcessListView phases={phases} selectedPhaseId={selectedPhaseId} onSelect={setSelectedPhaseId} />
        )}
      </div>

      {selectedPhase && (
        <div className="process-detail-panel" aria-live="polite">
          <div className="process-detail-heading">
            <div>
              <div className="section-label">
                Phase {selectedPhase.order + 1} of {phases.length}
              </div>
              <h3>{selectedPhase.title}</h3>
            </div>
            <EvidenceBadge status={selectedPhase.dominantStatus} />
          </div>
          <p>{selectedPhase.description}</p>
          <div className="process-stage-chips">
            {selectedPhase.stages.map((stage) => (
              <Link key={stage.id} href={`/pipeline#stage-${stage.id}`} className="process-stage-chip">
                <span>Stage {stage.id}</span>
                <EvidenceBadge status={stage.status} />
              </Link>
            ))}
          </div>
          {selectedPhase.dependsOnPhaseIds.length > 0 && (
            <p className="process-depends-note">
              Depends on: {selectedPhase.dependsOnPhaseIds.map((id) => phases.find((p) => p.id === id)?.title ?? id).join(", ")}
            </p>
          )}
          <details className="process-notes">
            <summary>Stage-by-stage notes</summary>
            <ul>
              {selectedPhase.stages.map((stage) => (
                <li key={stage.id}>
                  <strong>
                    Stage {stage.id} — {stage.name}:
                  </strong>{" "}
                  {stage.notes}
                  {stage.artifact_paths.length > 0 && (
                    <span className="process-artifact-links">
                      {" "}
                      {stage.artifact_paths.map((p) => (
                        <ArtifactLink key={p} path={p} commit={stage.git_commit ?? undefined} />
                      ))}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </details>
        </div>
      )}
    </div>
  );
}
