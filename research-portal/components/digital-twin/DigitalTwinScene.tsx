"use client";

import { Canvas } from "@react-three/fiber";
import type { ElementRef, RefObject } from "react";
import { useMemo } from "react";
import { CameraController } from "./CameraController";
import { CloudAI } from "./CloudAI";
import { DataFlow } from "./DataFlow";
import { Gateway } from "./Gateway";
import { LabEnvironment } from "./LabEnvironment";
import { MCUBoard } from "./MCUBoard";
import { ProcessingNode } from "./ProcessingNode";
import { SampleChamber, SensorArrayNode } from "./SensorArray";
import type { TwinComponent } from "./types";
import { OrbitControls } from "@react-three/drei";

export interface DigitalTwinSceneProps {
  components: TwinComponent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  showLabels: boolean;
  showDataFlow: boolean;
  exploded: boolean;
  dark: boolean;
  reducedMotion: boolean;
  controlsRef: RefObject<ElementRef<typeof OrbitControls>>;
}

const EXPLODE_FACTOR = 1.45;

function effectivePosition(component: TwinComponent, exploded: boolean): [number, number, number] {
  const [x, y, z] = component.position;
  return [x * (exploded ? EXPLODE_FACTOR : 1), y, z];
}

export function DigitalTwinScene({
  components,
  selectedId,
  onSelect,
  showLabels,
  showDataFlow,
  exploded,
  dark,
  reducedMotion,
  controlsRef,
}: DigitalTwinSceneProps) {
  const orderedPositions = useMemo(
    () => components.map((component) => effectivePosition(component, exploded)),
    [components, exploded],
  );

  return (
    <Canvas
      shadows={false}
      dpr={[1, 1.5]}
      camera={{ position: [1, 6, 15], fov: 42 }}
      style={{ background: "transparent" }}
    >
      <LabEnvironment dark={dark} />
      <CameraController controlsRef={controlsRef} />
      <DataFlow points={orderedPositions} active={showDataFlow} reducedMotion={reducedMotion} />
      {components.map((component) => {
        const position = effectivePosition(component, exploded);
        const common = {
          component,
          position,
          selected: selectedId === component.id,
          showLabels,
          onSelect,
        };
        switch (component.id) {
          case "sensor-chamber":
            return <SampleChamber key={component.id} {...common} />;
          case "sensor-array":
            return <SensorArrayNode key={component.id} {...common} />;
          case "drift-detector":
          case "ml-model":
            return <ProcessingNode key={component.id} {...common} />;
          case "xai":
          case "cloud":
            return <CloudAI key={component.id} {...common} />;
          case "mcu":
            return <MCUBoard key={component.id} {...common} />;
          case "gateway":
            return <Gateway key={component.id} {...common} />;
          default:
            return null;
        }
      })}
    </Canvas>
  );
}
