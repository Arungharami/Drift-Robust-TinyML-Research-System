"use client";

import { Html } from "@react-three/drei";
import type { ThreeEvent } from "@react-three/fiber";
import type { ReactNode } from "react";
import { statusColor } from "./statusColor";
import type { TwinComponent } from "./types";

interface TwinNodeShellProps {
  component: TwinComponent;
  position: [number, number, number];
  selected: boolean;
  showLabels: boolean;
  onSelect: (id: string) => void;
  children: ReactNode;
}

/** Shared click/hover/label/selection-ring behavior for every twin component. */
export function TwinNodeShell({ component, position, selected, showLabels, onSelect, children }: TwinNodeShellProps) {
  const color = statusColor(String(component.status));

  const handleClick = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation();
    onSelect(component.id);
  };
  const handleOver = (event: ThreeEvent<PointerEvent>) => {
    event.stopPropagation();
    document.body.style.cursor = "pointer";
  };
  const handleOut = () => {
    document.body.style.cursor = "auto";
  };

  return (
    <group position={position} onClick={handleClick} onPointerOver={handleOver} onPointerOut={handleOut}>
      {children}
      {selected && (
        <mesh position={[0, -0.95, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.82, 1, 40]} />
          <meshBasicMaterial color={color} transparent opacity={0.9} />
        </mesh>
      )}
      {showLabels && (
        <Html position={[0, 1.5, 0]} center distanceFactor={13} occlude>
          <div className={`twin-label${selected ? " twin-label-selected" : ""}`} style={{ borderColor: color }}>
            {component.name}
          </div>
        </Html>
      )}
    </group>
  );
}
