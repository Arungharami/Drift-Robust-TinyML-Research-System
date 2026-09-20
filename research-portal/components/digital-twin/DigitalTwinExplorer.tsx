"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ComponentInspector } from "./ComponentInspector";
import { DigitalTwinHUD } from "./DigitalTwinHUD";
import { DigitalTwinLegend } from "./DigitalTwinLegend";
import { DigitalTwinScene } from "./DigitalTwinScene";
import { TwinCanvasBoundary } from "./TwinCanvasBoundary";
import { TwinComponentList } from "./TwinComponentList";
import type { TwinComponent } from "./types";

function supportsWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
    );
  } catch {
    return false;
  }
}

function computeDark(): boolean {
  const explicit = document.documentElement.getAttribute("data-theme");
  if (explicit === "dark") return true;
  if (explicit === "light") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

/** Client-only root for the digital twin: owns scene state and renders the 3D canvas plus its full non-3D equivalent. */
export function DigitalTwinExplorer({ components }: { components: TwinComponent[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showLabels, setShowLabels] = useState(true);
  const [showDataFlow, setShowDataFlow] = useState(true);
  const [exploded, setExploded] = useState(false);
  const [dark, setDark] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [webglOk] = useState(() => (typeof window === "undefined" ? true : supportsWebGL()));
  const controlsRef = useRef<{ reset: () => void } | null>(null);

  useEffect(() => {
    setDark(computeDark());
    const observer = new MutationObserver(() => setDark(computeDark()));
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

    const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const themeQuery = window.matchMedia("(prefers-color-scheme: dark)");
    setReducedMotion(motionQuery.matches);
    setShowDataFlow(!motionQuery.matches);
    const onMotionChange = () => setReducedMotion(motionQuery.matches);
    const onThemeChange = () => setDark(computeDark());
    motionQuery.addEventListener("change", onMotionChange);
    themeQuery.addEventListener("change", onThemeChange);

    return () => {
      observer.disconnect();
      motionQuery.removeEventListener("change", onMotionChange);
      themeQuery.removeEventListener("change", onThemeChange);
    };
  }, []);

  const handleSelect = useCallback((id: string) => {
    setSelectedId((current) => (current === id ? null : id));
  }, []);

  const handleResetCamera = useCallback(() => {
    controlsRef.current?.reset();
  }, []);

  const selectedComponent = components.find((c) => c.id === selectedId) ?? null;

  return (
    <div className="twin-explorer">
      <DigitalTwinLegend />
      <DigitalTwinHUD
        showLabels={showLabels}
        onToggleLabels={() => setShowLabels((v) => !v)}
        showDataFlow={showDataFlow}
        onToggleDataFlow={() => setShowDataFlow((v) => !v)}
        exploded={exploded}
        onToggleExploded={() => setExploded((v) => !v)}
        onResetCamera={handleResetCamera}
      />
      <div className="twin-stage">
        <div className="twin-canvas-wrap">
          {webglOk ? (
            <TwinCanvasBoundary
              fallback={
                <p className="twin-canvas-fallback">
                  The interactive 3D view could not start in this browser. The component reference
                  list below has the same information.
                </p>
              }
            >
              <DigitalTwinScene
                components={components}
                selectedId={selectedId}
                onSelect={handleSelect}
                showLabels={showLabels}
                showDataFlow={showDataFlow}
                exploded={exploded}
                dark={dark}
                reducedMotion={reducedMotion}
                controlsRef={controlsRef}
              />
            </TwinCanvasBoundary>
          ) : (
            <p className="twin-canvas-fallback">
              This browser does not support WebGL, so the interactive 3D view is unavailable. The
              component reference list below has the same information.
            </p>
          )}
        </div>
        <ComponentInspector component={selectedComponent} />
      </div>
      <h2>Component reference (text equivalent)</h2>
      <p className="twin-legend-disclaimer">
        Every component below is also selectable in the 3D scene above; this list is the full
        keyboard- and screen-reader-accessible equivalent, not a summary.
      </p>
      <TwinComponentList components={components} selectedId={selectedId} onSelect={handleSelect} />
    </div>
  );
}
