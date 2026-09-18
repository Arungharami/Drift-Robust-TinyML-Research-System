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

/** Generic processing-stage node (drift detector, classical ML model): a rounded slab with a status-colored core. */
export function ProcessingNode({ component, position, selected, showLabels, onSelect }: NodeProps) {
  const color = statusColor(String(component.status));
  return (
    <TwinNodeShell component={component} position={position} selected={selected} showLabels={showLabels} onSelect={onSelect}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[1.3, 0.25, 1.3]} />
        <meshStandardMaterial color="#4a4738" metalness={0.35} roughness={0.5} />
      </mesh>
      <mesh position={[0, 0.28, 0]}>
        <octahedronGeometry args={[0.42, 0]} />
        <meshStandardMaterial color={color} metalness={0.2} roughness={0.35} />
      </mesh>
    </TwinNodeShell>
  );
}
