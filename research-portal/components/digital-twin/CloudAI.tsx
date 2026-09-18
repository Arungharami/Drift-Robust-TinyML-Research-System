"use client";

import { statusColor } from "./statusColor";
import { TwinNodeShell } from "./TwinNodeShell";
import type { TwinComponent } from "./types";

interface NodeProps {
  component: TwinComponent;
  position: [number, number, number];
  selected: boolean;
  showLabels: boolean;
  onSelect: (id: string) => void;
}

const SATELLITE_OFFSETS: [number, number, number][] = [
  [0.55, 0.25, 0],
  [-0.55, -0.15, 0.2],
  [0.15, -0.35, -0.45],
  [-0.2, 0.4, 0.4],
];

/** Research/AI layer node (explanation engine, evidence registry): a core sphere with orbiting satellite nodes. */
export function CloudAI({ component, position, selected, showLabels, onSelect }: NodeProps) {
  const color = statusColor(String(component.status));
  return (
    <TwinNodeShell component={component} position={position} selected={selected} showLabels={showLabels} onSelect={onSelect}>
      <mesh>
        <icosahedronGeometry args={[0.5, 1]} />
        <meshStandardMaterial color={color} metalness={0.25} roughness={0.4} wireframe />
      </mesh>
      {SATELLITE_OFFSETS.map((offset, i) => (
        <mesh key={i} position={offset}>
          <sphereGeometry args={[0.09, 12, 12]} />
          <meshStandardMaterial color={color} metalness={0.3} roughness={0.3} />
        </mesh>
      ))}
    </TwinNodeShell>
  );
}
