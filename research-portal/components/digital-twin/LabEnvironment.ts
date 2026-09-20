// Plain three.js ground grid + lighting, added directly to a scene. Replaces the former drei
// <Grid>/<ambientLight>/<directionalLight> JSX after removing @react-three/drei (see
// twinNodeGeometry.ts for why). THREE.GridHelper has no infinite-fade shader like drei's Grid —
// a fixed-size, single-tone grid plane is an honest, simpler substitute for this restrained
// scene, and lets theme changes recolor it in place (no vertex-color material to fight).

import * as THREE from "three";

export interface LabEnvironment {
  grid: THREE.GridHelper;
  ambient: THREE.AmbientLight;
  directionalKey: THREE.DirectionalLight;
  directionalFill: THREE.DirectionalLight;
  setDark: (dark: boolean) => void;
  dispose: () => void;
}

const GRID_COLOR = { light: 0xb9b2a2, dark: 0x4c492f };

export function addLabEnvironment(scene: THREE.Scene, dark: boolean): LabEnvironment {
  const ambient = new THREE.AmbientLight(0xffffff, dark ? 0.55 : 0.75);
  const directionalKey = new THREE.DirectionalLight(0xffffff, dark ? 0.9 : 1.1);
  directionalKey.position.set(6, 10, 6);
  const directionalFill = new THREE.DirectionalLight(0xffffff, 0.35);
  directionalFill.position.set(-6, 4, -4);

  const grid = new THREE.GridHelper(40, 40, GRID_COLOR.light, GRID_COLOR.light);
  grid.position.y = -1.05;
  const gridMaterial = grid.material as THREE.LineBasicMaterial;
  gridMaterial.vertexColors = false;
  gridMaterial.color.set(dark ? GRID_COLOR.dark : GRID_COLOR.light);
  gridMaterial.transparent = true;
  gridMaterial.opacity = 0.6;

  scene.add(ambient, directionalKey, directionalFill, grid);

  return {
    grid,
    ambient,
    directionalKey,
    directionalFill,
    setDark: (nextDark: boolean) => {
      ambient.intensity = nextDark ? 0.55 : 0.75;
      directionalKey.intensity = nextDark ? 0.9 : 1.1;
      gridMaterial.color.set(nextDark ? GRID_COLOR.dark : GRID_COLOR.light);
    },
    dispose: () => {
      grid.geometry.dispose();
      gridMaterial.dispose();
    },
  };
}
