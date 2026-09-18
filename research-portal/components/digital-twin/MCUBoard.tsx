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

/**
 * Conceptual nRF52840 board: a PCB slab with a highlighted MCU package.
 * This is a schematic placeholder, not a reconstruction of the physical board —
 * the scene disclaimer and component inspector both say so explicitly.
 */
export function MCUBoard({ component, position, selected, showLabels, onSelect }: NodeProps) {
  const color = statusColor(String(component.status));
  return (
    <TwinNodeShell component={component} position={position} selected={selected} showLabels={showLabels} onSelect={onSelect}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[1.8, 0.12, 1.2]} />
        <meshStandardMaterial color="#1f4d3d" metalness={0.1} roughness={0.7} />
      </mesh>
      <mesh position={[0.2, 0.14, 0]}>
        <boxGeometry args={[0.55, 0.14, 0.55]} />
        <meshStandardMaterial color={color} metalness={0.5} roughness={0.35} />
      </mesh>
      {[-0.6, -0.2, 0.6].map((x) => (
        <mesh key={x} position={[x, 0.1, -0.35]}>
          <boxGeometry args={[0.18, 0.06, 0.18]} />
          <meshStandardMaterial color="#8a8375" metalness={0.6} roughness={0.4} />
        </mesh>
      ))}
    </TwinNodeShell>
  );
}
