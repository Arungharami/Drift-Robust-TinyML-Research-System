"use client";

import type { MutableRefObject } from "react";
import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { addLabEnvironment } from "./LabEnvironment";
import { statusColor } from "./statusColor";
import { buildTwinNodeGroup } from "./twinNodeGeometry";
import type { TwinComponent } from "./types";

export interface DeviceSceneProps {
  layers: TwinComponent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  showLabels: boolean;
  exploded: boolean;
  dark: boolean;
  controlsRef: MutableRefObject<{ reset: () => void } | null>;
}

const EXPLODE_GAP = 1.6;
const ASSEMBLED_GAP = 0.62;

/** Assembled (stacked) vs exploded (spread) Y position for a layer, by its fixed stack index. */
function layerPosition(component: TwinComponent, index: number, gap: number): THREE.Vector3 {
  const [x, , z] = component.position;
  const centered = index - 4.5; // 10 layers, index 0..9 -> centered around 0
  return new THREE.Vector3(x, centered * gap, z);
}

interface LayerEntry {
  component: TwinComponent;
  group: THREE.Group;
  ring: THREE.Mesh;
  label: HTMLDivElement;
  assembledPos: THREE.Vector3;
  explodedPos: THREE.Vector3;
  dispose: () => void;
}

/**
 * Plain three.js (no @react-three/fiber/drei) — same reconciler-vs-react@18.3 incompatibility as
 * DigitalTwinScene.tsx; see that file's doc comment and components/process/ProcessScene.tsx.
 */
export function DeviceScene({ layers, selectedId, onSelect, showLabels, exploded, dark, controlsRef }: DeviceSceneProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const entriesRef = useRef<LayerEntry[]>([]);
  const envRef = useRef<ReturnType<typeof addLabEnvironment> | null>(null);
  const selectedIdRef = useRef(selectedId);
  const onSelectRef = useRef(onSelect);
  const showLabelsRef = useRef(showLabels);
  const explodedRef = useRef(exploded);

  useEffect(() => {
    selectedIdRef.current = selectedId;
  }, [selectedId]);
  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);
  useEffect(() => {
    showLabelsRef.current = showLabels;
  }, [showLabels]);
  useEffect(() => {
    explodedRef.current = exploded;
  }, [exploded]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = Math.max(container.clientWidth, 1);
    const height = Math.max(container.clientHeight, 1);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    camera.position.set(7, 1, 9);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.setSize(width, height);
    container.style.position = "relative";
    container.appendChild(renderer.domElement);

    const labelLayer = document.createElement("div");
    labelLayer.style.position = "absolute";
    labelLayer.style.inset = "0";
    labelLayer.style.pointerEvents = "none";
    labelLayer.style.overflow = "hidden";
    container.appendChild(labelLayer);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 4;
    controls.maxDistance = 28;
    controls.maxPolarAngle = Math.PI * 0.49;
    controls.target.set(0, 0.3, 0);
    controls.update();
    controlsRef.current = controls;

    const env = addLabEnvironment(scene, dark);
    envRef.current = env;

    const entries: LayerEntry[] = [];
    layers.forEach((component, index) => {
      const { group, ring, dispose } = buildTwinNodeGroup(component);
      const assembledPos = layerPosition(component, index, ASSEMBLED_GAP);
      const explodedPos = layerPosition(component, index, EXPLODE_GAP);
      group.position.copy(explodedRef.current ? explodedPos : assembledPos);
      scene.add(group);

      const label = document.createElement("div");
      label.className = "twin-label";
      label.style.position = "absolute";
      label.style.left = "0";
      label.style.top = "0";
      label.style.width = "max-content";
      label.style.borderColor = statusColor(String(component.status));
      label.textContent = component.name;
      label.style.display = showLabelsRef.current ? "block" : "none";
      labelLayer.appendChild(label);

      entries.push({ component, group, ring, label, assembledPos, explodedPos, dispose });
    });
    entriesRef.current = entries;

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const raycastTargets = entries.flatMap((entry) => entry.group.children.filter((child): child is THREE.Mesh => (child as THREE.Mesh).isMesh && child !== entry.ring));

    function pickComponentId(clientX: number, clientY: number): string | null {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hit = raycaster.intersectObjects(raycastTargets, false)[0];
      return hit ? (hit.object.userData.componentId as string) : null;
    }

    function handleClick(event: MouseEvent) {
      const id = pickComponentId(event.clientX, event.clientY);
      if (id) onSelectRef.current(id);
    }
    function handleMove(event: PointerEvent) {
      const id = pickComponentId(event.clientX, event.clientY);
      renderer.domElement.style.cursor = id ? "pointer" : "auto";
    }
    renderer.domElement.addEventListener("click", handleClick);
    renderer.domElement.addEventListener("pointermove", handleMove);

    const resizeObserver = new ResizeObserver(() => {
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (w === 0 || h === 0) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });
    resizeObserver.observe(container);

    const projected = new THREE.Vector3();
    let frameId: number;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      for (const entry of entriesRef.current) {
        const selected = entry.component.id === selectedIdRef.current;
        const target = explodedRef.current ? entry.explodedPos : entry.assembledPos;
        entry.group.position.lerp(target, 0.12);
        entry.ring.visible = selected;
        entry.label.classList.toggle("twin-label-selected", selected);

        projected.copy(entry.group.position).setY(entry.group.position.y + 1.5).project(camera);
        const behind = projected.z > 1;
        if (behind) {
          entry.label.style.display = "none";
        } else if (showLabelsRef.current) {
          entry.label.style.display = "block";
          const x = (projected.x * 0.5 + 0.5) * container.clientWidth;
          const y = (-projected.y * 0.5 + 0.5) * container.clientHeight;
          entry.label.style.transform = `translate(-50%, -100%) translate(${x}px, ${y}px)`;
        } else {
          entry.label.style.display = "none";
        }
      }
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(frameId);
      resizeObserver.disconnect();
      renderer.domElement.removeEventListener("click", handleClick);
      renderer.domElement.removeEventListener("pointermove", handleMove);
      controls.dispose();
      renderer.dispose();
      env.dispose();
      for (const entry of entries) {
        entry.dispose();
        entry.label.remove();
      }
      if (container.contains(renderer.domElement)) container.removeChild(renderer.domElement);
      if (container.contains(labelLayer)) container.removeChild(labelLayer);
      entriesRef.current = [];
      envRef.current = null;
      controlsRef.current = null;
    };
    // Rebuilt only if the layer list identity changes (stable for the page's lifetime).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [layers]);

  useEffect(() => {
    envRef.current?.setDark(dark);
  }, [dark]);

  return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
