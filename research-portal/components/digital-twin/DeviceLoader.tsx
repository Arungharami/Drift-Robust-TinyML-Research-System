"use client";

import dynamic from "next/dynamic";
import { Suspense } from "react";
import type { TwinComponent } from "./types";

// Same ssr:false client-boundary pattern as DigitalTwinLoader — the three.js/R3F bundle for
// this route is isolated from every other page, including /digital-twin.
const DeviceExplorer = dynamic(() => import("./DeviceExplorer").then((m) => m.DeviceExplorer), {
  ssr: false,
  loading: () => <p className="twin-canvas-fallback">Loading interactive 3D model…</p>,
});

export function DeviceLoader({ layers }: { layers: TwinComponent[] }) {
  return (
    <Suspense fallback={<p className="twin-canvas-fallback">Loading interactive 3D model…</p>}>
      <DeviceExplorer layers={layers} />
    </Suspense>
  );
}
