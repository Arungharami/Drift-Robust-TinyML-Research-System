"use client";

import dynamic from "next/dynamic";
import type { TwinComponent } from "./types";

// next/dynamic with ssr:false must be called from a Client Component in the App Router —
// this file exists solely to be that boundary for the server-rendered page.
const DigitalTwinExplorer = dynamic(() => import("./DigitalTwinExplorer").then((m) => m.DigitalTwinExplorer), {
  ssr: false,
  loading: () => <p className="twin-canvas-fallback">Loading interactive 3D model…</p>,
});

export function DigitalTwinLoader({ components }: { components: TwinComponent[] }) {
  return <DigitalTwinExplorer components={components} />;
}
