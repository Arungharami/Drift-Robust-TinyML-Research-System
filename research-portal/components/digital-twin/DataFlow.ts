// Plain three.js signal-flow visualization: a curve through every component plus moving
// "packets" along it. Replaces the former drei <Line>/fiber useFrame version (see
// twinNodeGeometry.ts for why @react-three/* was removed). Only used by DigitalTwinScene.tsx —
// DeviceScene.tsx never had a data-flow toggle.
//
// The curve is rebuilt from live point positions every frame (cheap for ~8 points) rather than
// once at construction, so the flow line stays attached to nodes while they lerp between
// assembled and exploded layout — a small improvement over the discrete jump the fiber version had.

import * as THREE from "three";

const PACKET_COUNT = 4;
const ACTIVE_COLOR = 0x6fb28f;
const INACTIVE_COLOR = 0x8a8375;
const CURVE_SAMPLES = 80;

export interface DataFlowHandle {
  group: THREE.Group;
  setActive: (active: boolean) => void;
  setReducedMotion: (reduced: boolean) => void;
  update: (elapsedSeconds: number, points: THREE.Vector3[]) => void;
  dispose: () => void;
}

export function buildDataFlow(): DataFlowHandle {
  const group = new THREE.Group();

  const lineGeometry = new THREE.BufferGeometry();
  lineGeometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array((CURVE_SAMPLES + 1) * 3), 3));
  const lineMaterial = new THREE.LineBasicMaterial({ color: INACTIVE_COLOR, transparent: true, opacity: 0.25 });
  const line = new THREE.Line(lineGeometry, lineMaterial);
  group.add(line);

  const packetGeometry = new THREE.SphereGeometry(0.08, 10, 10);
  const packets: THREE.Mesh[] = [];
  for (let i = 0; i < PACKET_COUNT; i++) {
    const material = new THREE.MeshStandardMaterial({ color: ACTIVE_COLOR, emissive: ACTIVE_COLOR, emissiveIntensity: 0.6 });
    const packet = new THREE.Mesh(packetGeometry, material);
    packet.visible = false;
    group.add(packet);
    packets.push(packet);
  }

  let active = false;
  let reducedMotion = false;

  function applyState() {
    lineMaterial.color.set(active ? ACTIVE_COLOR : INACTIVE_COLOR);
    lineMaterial.opacity = active ? 0.55 : 0.25;
    const showPackets = active && !reducedMotion;
    for (const packet of packets) packet.visible = showPackets;
  }
  applyState();

  return {
    group,
    setActive: (next: boolean) => {
      active = next;
      applyState();
    },
    setReducedMotion: (next: boolean) => {
      reducedMotion = next;
      applyState();
    },
    update: (elapsedSeconds: number, points: THREE.Vector3[]) => {
      if (points.length < 2) return;
      const curve = new THREE.CatmullRomCurve3(
        points.map((p) => new THREE.Vector3(p.x, p.y + 0.15, p.z)),
        false,
        "catmullrom",
        0.15,
      );
      const sampled = curve.getPoints(CURVE_SAMPLES);
      const positionAttr = lineGeometry.getAttribute("position") as THREE.BufferAttribute;
      sampled.forEach((p, i) => positionAttr.setXYZ(i, p.x, p.y, p.z));
      positionAttr.needsUpdate = true;
      lineGeometry.setDrawRange(0, sampled.length);
      lineGeometry.computeBoundingSphere();

      if (!active || reducedMotion) return;
      packets.forEach((packet, i) => {
        const offset = i / PACKET_COUNT;
        const progress = (((elapsedSeconds * 0.12 + offset) % 1) + 1) % 1;
        curve.getPointAt(progress, packet.position);
      });
    },
    dispose: () => {
      lineGeometry.dispose();
      lineMaterial.dispose();
      packetGeometry.dispose();
      for (const packet of packets) (packet.material as THREE.Material).dispose();
    },
  };
}
