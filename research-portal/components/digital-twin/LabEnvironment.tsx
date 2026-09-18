"use client";

import { Grid } from "@react-three/drei";

/** Ground grid and lighting for the twin scene. Neutral/academic, not a game-engine "lab". */
export function LabEnvironment({ dark }: { dark: boolean }) {
  return (
    <>
      <ambientLight intensity={dark ? 0.55 : 0.75} />
      <directionalLight position={[6, 10, 6]} intensity={dark ? 0.9 : 1.1} />
      <directionalLight position={[-6, 4, -4]} intensity={0.35} />
      <Grid
        position={[0, -1.05, 0]}
        args={[40, 40]}
        cellSize={1}
        cellThickness={0.5}
        sectionSize={5}
        sectionThickness={1}
        cellColor={dark ? "#34321f" : "#ddd8ce"}
        sectionColor={dark ? "#4c492f" : "#b9b2a2"}
        fadeDistance={30}
        fadeStrength={1}
        infiniteGrid
      />
    </>
  );
}
