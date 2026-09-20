// Plain three.js geometry factories for every digital-twin node type. This module replaces the
// former fiber/drei JSX components (TwinNodeShell.tsx, CloudAI.tsx, Gateway.tsx, LayerPanel.tsx,
// SensorArray.tsx, MCUBoard.tsx, ProcessingNode.tsx) after removing @react-three/fiber and
// @react-three/drei — see components/process/ProcessScene.tsx for why (react-reconciler@0.27.0
// mounting-order crash against react@18.3.1, confirmed in a real browser).
//
// Each builder returns a self-contained THREE.Group plus the meshes that should be raycast
// targets and a dispose() that frees every geometry/material it created. The calling scene
// (DigitalTwinScene.tsx / DeviceScene.tsx) owns position, the selection ring's visibility, and
// the floating DOM label — this module only builds the type-specific shape.

import * as THREE from "three";
import { statusColor } from "./statusColor";
import type { TwinComponent } from "./types";

export interface TwinNodeGroup {
  /** Positioned by the caller; contains the shape plus the (initially hidden) selection ring. */
  group: THREE.Group;
  /** Raycast targets, each tagged with userData.componentId. */
  meshes: THREE.Mesh[];
  ring: THREE.Mesh;
  dispose: () => void;
}

function track(mesh: THREE.Mesh, id: string, meshes: THREE.Mesh[], disposables: Array<{ dispose: () => void }>) {
  mesh.userData.componentId = id;
  meshes.push(mesh);
  disposables.push(mesh.geometry, mesh.material as THREE.Material);
  return mesh;
}

function buildSelectionRing(color: string, disposables: Array<{ dispose: () => void }>): THREE.Mesh {
  const geometry = new THREE.RingGeometry(0.82, 1, 40);
  const material = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
  const ring = new THREE.Mesh(geometry, material);
  ring.rotation.x = -Math.PI / 2;
  ring.position.y = -0.95;
  ring.visible = false;
  disposables.push(geometry, material);
  return ring;
}

function buildSampleChamber(id: string, color: string, meshes: THREE.Mesh[], disposables: Array<{ dispose: () => void }>): THREE.Object3D[] {
  const shell = new THREE.Mesh(
    new THREE.BoxGeometry(1.6, 1.2, 1.4),
    new THREE.MeshStandardMaterial({ color: "#3a3830", metalness: 0.2, roughness: 0.6, transparent: true, opacity: 0.55 }),
  );
  const inner = new THREE.Mesh(new THREE.BoxGeometry(1.45, 1.05, 1.25), new THREE.MeshStandardMaterial({ color, wireframe: true }));
  return [track(shell, id, meshes, disposables), track(inner, id, meshes, disposables)];
}

function buildSensorArray(id: string, color: string, meshes: THREE.Mesh[], disposables: Array<{ dispose: () => void }>): THREE.Object3D[] {
  const objects: THREE.Object3D[] = [];
  const base = new THREE.Mesh(
    new THREE.CylinderGeometry(0.95, 0.95, 0.15, 32),
    new THREE.MeshStandardMaterial({ color: "#3a3830", metalness: 0.3, roughness: 0.5 }),
  );
  base.position.set(0, -0.5, 0);
  objects.push(track(base, id, meshes, disposables));

  const count = 16;
  const radius = 0.75;
  for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2;
    const pin = new THREE.Mesh(
      new THREE.CylinderGeometry(0.08, 0.08, 0.5, 12),
      new THREE.MeshStandardMaterial({ color, metalness: 0.4, roughness: 0.4 }),
    );
    pin.position.set(Math.cos(angle) * radius, -0.15, Math.sin(angle) * radius);
    objects.push(track(pin, id, meshes, disposables));
  }
  return objects;
}

function buildMCUBoard(id: string, color: string, meshes: THREE.Mesh[], disposables: Array<{ dispose: () => void }>): THREE.Object3D[] {
  const objects: THREE.Object3D[] = [];
  const board = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.12, 1.2), new THREE.MeshStandardMaterial({ color: "#1f4d3d", metalness: 0.1, roughness: 0.7 }));
  objects.push(track(board, id, meshes, disposables));

  const chip = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.14, 0.55), new THREE.MeshStandardMaterial({ color, metalness: 0.5, roughness: 0.35 }));
  chip.position.set(0.2, 0.14, 0);
  objects.push(track(chip, id, meshes, disposables));

  for (const x of [-0.6, -0.2, 0.6]) {
    const pin = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.06, 0.18), new THREE.MeshStandardMaterial({ color: "#8a8375", metalness: 0.6, roughness: 0.4 }));
    pin.position.set(x, 0.1, -0.35);
    objects.push(track(pin, id, meshes, disposables));
  }
  return objects;
}

function buildProcessingNode(id: string, color: string, meshes: THREE.Mesh[], disposables: Array<{ dispose: () => void }>): THREE.Object3D[] {
  const slab = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.25, 1.3), new THREE.MeshStandardMaterial({ color: "#4a4738", metalness: 0.35, roughness: 0.5 }));
  const core = new THREE.Mesh(new THREE.OctahedronGeometry(0.42, 0), new THREE.MeshStandardMaterial({ color, metalness: 0.2, roughness: 0.35 }));
  core.position.set(0, 0.28, 0);
  return [track(slab, id, meshes, disposables), track(core, id, meshes, disposables)];
}

const CLOUD_SATELLITE_OFFSETS: [number, number, number][] = [
  [0.55, 0.25, 0],
  [-0.55, -0.15, 0.2],
  [0.15, -0.35, -0.45],
  [-0.2, 0.4, 0.4],
];

function buildCloudAI(id: string, color: string, meshes: THREE.Mesh[], disposables: Array<{ dispose: () => void }>): THREE.Object3D[] {
  const core = new THREE.Mesh(new THREE.IcosahedronGeometry(0.5, 1), new THREE.MeshStandardMaterial({ color, metalness: 0.25, roughness: 0.4, wireframe: true }));
  const objects: THREE.Object3D[] = [track(core, id, meshes, disposables)];
  for (const [x, y, z] of CLOUD_SATELLITE_OFFSETS) {
    const satellite = new THREE.Mesh(new THREE.SphereGeometry(0.09, 12, 12), new THREE.MeshStandardMaterial({ color, metalness: 0.3, roughness: 0.3 }));
    satellite.position.set(x, y, z);
    objects.push(track(satellite, id, meshes, disposables));
  }
  return objects;
}

function buildGateway(id: string, color: string, meshes: THREE.Mesh[], disposables: Array<{ dispose: () => void }>): THREE.Object3D[] {
  const base = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.08, 1), new THREE.MeshStandardMaterial({ color: "#4a4738", metalness: 0.4, roughness: 0.5 }));
  base.position.set(0, -0.35, 0.35);
  base.rotation.set(-0.15, 0, 0);

  const lid = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.08, 0.85), new THREE.MeshStandardMaterial({ color: "#3a3830", metalness: 0.4, roughness: 0.5 }));
  lid.position.set(0, 0.15, -0.15);
  lid.rotation.set(-1.15, 0, 0);

  const screen = new THREE.Mesh(
    new THREE.PlaneGeometry(1.2, 0.65),
    new THREE.MeshStandardMaterial({ color, emissive: new THREE.Color(color), emissiveIntensity: 0.15 }),
  );
  screen.position.set(0, 0.15, -0.15);
  screen.rotation.set(-1.15, 0, 0);

  return [track(base, id, meshes, disposables), track(lid, id, meshes, disposables), track(screen, id, meshes, disposables)];
}

function buildLayerPanel(id: string, color: string, meshes: THREE.Mesh[], disposables: Array<{ dispose: () => void }>): THREE.Object3D[] {
  const panel = new THREE.Mesh(
    new THREE.BoxGeometry(2.1, 0.22, 1.6),
    new THREE.MeshStandardMaterial({ color: "#4a4738", metalness: 0.25, roughness: 0.6, transparent: true, opacity: 0.85 }),
  );
  const inlay = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.02, 1.4), new THREE.MeshStandardMaterial({ color, wireframe: true }));
  inlay.position.set(0, 0.13, 0);
  return [track(panel, id, meshes, disposables), track(inlay, id, meshes, disposables)];
}

/** Builds the type-specific shape for a component, dispatching by id exactly like the former DigitalTwinScene/DeviceScene switch statements. */
export function buildTwinNodeGroup(component: TwinComponent): TwinNodeGroup {
  const color = statusColor(String(component.status));
  const meshes: THREE.Mesh[] = [];
  const disposables: Array<{ dispose: () => void }> = [];
  const group = new THREE.Group();

  let shapeObjects: THREE.Object3D[];
  switch (component.id) {
    case "sensor-chamber":
      shapeObjects = buildSampleChamber(component.id, color, meshes, disposables);
      break;
    case "sensor-array":
      shapeObjects = buildSensorArray(component.id, color, meshes, disposables);
      break;
    case "mcu":
      shapeObjects = buildMCUBoard(component.id, color, meshes, disposables);
      break;
    case "drift-detector":
    case "ml-model":
    case "inference-layer":
      shapeObjects = buildProcessingNode(component.id, color, meshes, disposables);
      break;
    case "xai":
    case "cloud":
      shapeObjects = buildCloudAI(component.id, color, meshes, disposables);
      break;
    case "gateway":
      shapeObjects = buildGateway(component.id, color, meshes, disposables);
      break;
    default:
      shapeObjects = buildLayerPanel(component.id, color, meshes, disposables);
      break;
  }
  for (const obj of shapeObjects) group.add(obj);

  const ring = buildSelectionRing(color, disposables);
  group.add(ring);

  return {
    group,
    meshes,
    ring,
    dispose: () => {
      for (const d of disposables) d.dispose();
    },
  };
}
