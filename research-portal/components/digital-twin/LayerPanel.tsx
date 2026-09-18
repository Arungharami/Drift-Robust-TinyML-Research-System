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
 * Generic flat layer panel — used for every device layer that has no dedicated shape
 * (enclosures, PCB, signal acquisition, communication, power). Deliberately plain: these
 * layers have no selected physical parts yet, so a specific shape would overclaim detail.
 */
export function LayerPanel({ component, position, selected, showLabels, onSelect }: NodeProps) {
  const color = statusColor(String(component.status));
  return (
    <TwinNodeShell component={component} position={position} selected={selected} showLabels={showLabels} onSelect={onSelect}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[2.1, 0.22, 1.6]} />
        <meshStandardMaterial color="#4a4738" metalness={0.25} roughness={0.6} transparent opacity={0.85} />
      </mesh>
      <mesh position={[0, 0.13, 0]}>
        <boxGeometry args={[1.9, 0.02, 1.4]} />
        <meshStandardMaterial color={color} wireframe />
      </mesh>
    </TwinNodeShell>
  );
}
