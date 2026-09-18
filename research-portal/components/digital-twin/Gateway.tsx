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

/** Gateway / laptop: a simple clamshell shape representing the planned host bridge. */
export function Gateway({ component, position, selected, showLabels, onSelect }: NodeProps) {
  const color = statusColor(String(component.status));
  return (
    <TwinNodeShell component={component} position={position} selected={selected} showLabels={showLabels} onSelect={onSelect}>
      <mesh position={[0, -0.35, 0.35]} rotation={[-0.15, 0, 0]}>
        <boxGeometry args={[1.4, 0.08, 1]} />
        <meshStandardMaterial color="#4a4738" metalness={0.4} roughness={0.5} />
      </mesh>
      <mesh position={[0, 0.15, -0.15]} rotation={[-1.15, 0, 0]}>
        <boxGeometry args={[1.4, 0.08, 0.85]} />
        <meshStandardMaterial color="#3a3830" metalness={0.4} roughness={0.5} />
      </mesh>
      <mesh position={[0, 0.15, -0.15]} rotation={[-1.15, 0, 0]}>
        <planeGeometry args={[1.2, 0.65]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.15} />
      </mesh>
    </TwinNodeShell>
  );
}
