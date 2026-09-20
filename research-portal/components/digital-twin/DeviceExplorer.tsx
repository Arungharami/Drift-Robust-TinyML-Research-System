"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { ComponentInspector } from "./ComponentInspector";
import { DeviceHUD } from "./DeviceHUD";
import { DeviceLegend } from "./DeviceLegend";
import { DeviceScene } from "./DeviceScene";
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

/** Client-only root for /digital-twin/device — mirrors DigitalTwinExplorer's structure and adds `?component=` deep linking. */
export function DeviceExplorer({ layers }: { layers: TwinComponent[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const initialComponent = searchParams.get("component");

  const [selectedId, setSelectedId] = useState<string | null>(
    initialComponent && layers.some((l) => l.id === initialComponent) ? initialComponent : null,
  );
  const [showLabels, setShowLabels] = useState(true);
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

  const handleSelect = useCallback(
    (id: string) => {
      setSelectedId((current) => {
        const next = current === id ? null : id;
        const params = new URLSearchParams(searchParams.toString());
        if (next) params.set("component", next);
        else params.delete("component");
        const query = params.toString();
        router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
        return next;
      });
    },
    [pathname, router, searchParams],
  );

  const handleResetCamera = useCallback(() => {
    controlsRef.current?.reset();
  }, []);

  const selectedComponent = layers.find((l) => l.id === selectedId) ?? null;

  return (
    <div className="twin-explorer">
      <DeviceLegend />
      <DeviceHUD
        showLabels={showLabels}
        onToggleLabels={() => setShowLabels((v) => !v)}
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
              <DeviceScene
                layers={layers}
                selectedId={selectedId}
                onSelect={handleSelect}
                showLabels={showLabels}
                exploded={exploded || false}
                dark={dark}
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
      <h2>Device layers (text equivalent)</h2>
      <p className="twin-legend-disclaimer">
        Every layer below is also selectable in the 3D scene above; this list is the full
        keyboard- and screen-reader-accessible equivalent, not a summary.{" "}
        {reducedMotion && "Motion is reduced because your system requests it."}
      </p>
      <TwinComponentList components={layers} selectedId={selectedId} onSelect={handleSelect} />
    </div>
  );
}
