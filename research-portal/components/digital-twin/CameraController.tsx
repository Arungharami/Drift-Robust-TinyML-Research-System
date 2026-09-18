"use client";

import { OrbitControls } from "@react-three/drei";
import type { ElementRef, RefObject } from "react";

type ControlsRef = RefObject<ElementRef<typeof OrbitControls>>;

/** Orbit/zoom/pan camera control, tuned for inspecting a small scene rather than flying through a world. */
export function CameraController({ controlsRef }: { controlsRef: ControlsRef }) {
  return (
    <OrbitControls
      ref={controlsRef}
      makeDefault
      enableDamping
      dampingFactor={0.08}
      minDistance={4}
      maxDistance={28}
      maxPolarAngle={Math.PI * 0.49}
      target={[0, 0.3, 0]}
    />
  );
}
