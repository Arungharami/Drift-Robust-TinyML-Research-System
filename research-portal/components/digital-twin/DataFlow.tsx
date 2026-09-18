"use client";

import { Line } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

interface DataFlowProps {
  points: [number, number, number][];
  active: boolean;
  reducedMotion: boolean;
}

const PACKET_COUNT = 4;
const PACKET_COLOR = "#6fb28f";

/** Animated signal-flow visualization: a curve through every component plus moving "packets" along it. */
export function DataFlow({ points, active, reducedMotion }: DataFlowProps) {
  const curve = useMemo(() => {
    const vectors = points.map(([x, y, z]) => new THREE.Vector3(x, y + 0.15, z));
    return new THREE.CatmullRomCurve3(vectors, false, "catmullrom", 0.15);
  }, [points]);

  const linePoints = useMemo(() => curve.getPoints(80), [curve]);
  const packetRefs = useRef<(THREE.Mesh | null)[]>([]);
  const animate = active && !reducedMotion;

  useFrame((state) => {
    if (!animate) return;
    const t = state.clock.getElapsedTime();
    packetRefs.current.forEach((mesh, i) => {
      if (!mesh) return;
      const offset = i / PACKET_COUNT;
      const progress = ((t * 0.12 + offset) % 1 + 1) % 1;
      const p = curve.getPointAt(progress);
      mesh.position.copy(p);
    });
  });

  return (
    <group>
      <Line points={linePoints} color={active ? PACKET_COLOR : "#8a8375"} lineWidth={1.2} transparent opacity={active ? 0.55 : 0.25} />
      {animate &&
        Array.from({ length: PACKET_COUNT }, (_, i) => (
          <mesh
            key={i}
            ref={(el) => {
              packetRefs.current[i] = el;
            }}
          >
            <sphereGeometry args={[0.08, 10, 10]} />
            <meshStandardMaterial color={PACKET_COLOR} emissive={PACKET_COLOR} emissiveIntensity={0.6} />
          </mesh>
        ))}
    </group>
  );
}
