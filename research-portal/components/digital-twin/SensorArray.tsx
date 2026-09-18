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

/** Sample chamber: a simple enclosure box. */
export function SampleChamber({ component, position, selected, showLabels, onSelect }: NodeProps) {
  const color = statusColor(String(component.status));
  return (
    <TwinNodeShell component={component} position={position} selected={selected} showLabels={showLabels} onSelect={onSelect}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[1.6, 1.2, 1.4]} />
        <meshStandardMaterial color="#3a3830" metalness={0.2} roughness={0.6} transparent opacity={0.55} />
      </mesh>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1.45, 1.05, 1.25]} />
        <meshStandardMaterial color={color} wireframe />
      </mesh>
    </TwinNodeShell>
  );
}

/** 16-channel sensor array: a ring of small cylindrical sensor elements. */
export function SensorArrayNode({ component, position, selected, showLabels, onSelect }: NodeProps) {
  const color = statusColor(String(component.status));
  const count = 16;
  const radius = 0.75;

  return (
    <TwinNodeShell component={component} position={position} selected={selected} showLabels={showLabels} onSelect={onSelect}>
      <mesh position={[0, -0.5, 0]}>
        <cylinderGeometry args={[0.95, 0.95, 0.15, 32]} />
        <meshStandardMaterial color="#3a3830" metalness={0.3} roughness={0.5} />
      </mesh>
      {Array.from({ length: count }, (_, i) => {
        const angle = (i / count) * Math.PI * 2;
        return (
          <mesh key={i} position={[Math.cos(angle) * radius, -0.15, Math.sin(angle) * radius]}>
            <cylinderGeometry args={[0.08, 0.08, 0.5, 12]} />
            <meshStandardMaterial color={color} metalness={0.4} roughness={0.4} />
          </mesh>
        );
      })}
    </TwinNodeShell>
  );
}
