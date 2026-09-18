"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import type { ElementRef, RefObject } from "react";
import { CameraController } from "./CameraController";
import { LabEnvironment } from "./LabEnvironment";
import { LayerPanel } from "./LayerPanel";
import { MCUBoard } from "./MCUBoard";
import { ProcessingNode } from "./ProcessingNode";
import { SampleChamber, SensorArrayNode } from "./SensorArray";
import type { TwinComponent } from "./types";

export interface DeviceSceneProps {
  layers: TwinComponent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  showLabels: boolean;
  exploded: boolean;
  dark: boolean;
  controlsRef: RefObject<ElementRef<typeof OrbitControls>>;
}

const EXPLODE_GAP = 1.6;

/** Assembled (stacked) vs exploded (spread) Y position for a layer, by its fixed stack index. */
function layerPosition(component: TwinComponent, index: number, exploded: boolean): [number, number, number] {
  const [x, , z] = component.position;
  const centered = index - 4.5; // 10 layers, index 0..9 -> centered around 0
  const y = exploded ? centered * EXPLODE_GAP : centered * 0.62;
  return [x, y, z];
}

export function DeviceScene({ layers, selectedId, onSelect, showLabels, exploded, dark, controlsRef }: DeviceSceneProps) {
  return (
    <Canvas shadows={false} dpr={[1, 1.5]} camera={{ position: [7, 1, 9], fov: 42 }} style={{ background: "transparent" }}>
      <LabEnvironment dark={dark} />
      <CameraController controlsRef={controlsRef} />
      {layers.map((component, index) => {
        const position = layerPosition(component, index, exploded);
        const common = { component, position, selected: selectedId === component.id, showLabels, onSelect };
        switch (component.id) {
          case "sensor-chamber":
            return <SampleChamber key={component.id} {...common} />;
          case "sensor-array":
            return <SensorArrayNode key={component.id} {...common} />;
          case "mcu":
            return <MCUBoard key={component.id} {...common} />;
          case "inference-layer":
            return <ProcessingNode key={component.id} {...common} />;
          default:
            return <LayerPanel key={component.id} {...common} />;
        }
      })}
    </Canvas>
  );
}
