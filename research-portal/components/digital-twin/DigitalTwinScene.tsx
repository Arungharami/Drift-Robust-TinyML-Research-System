"use client";

import type { MutableRefObject } from "react";
import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { buildDataFlow } from "./DataFlow";
import { addLabEnvironment } from "./LabEnvironment";
import { statusColor } from "./statusColor";
import { buildTwinNodeGroup } from "./twinNodeGeometry";
import type { TwinComponent } from "./types";

export interface DigitalTwinSceneProps {
  components: TwinComponent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  showLabels: boolean;
  showDataFlow: boolean;
  exploded: boolean;
  dark: boolean;
  reducedMotion: boolean;
  controlsRef: MutableRefObject<{ reset: () => void } | null>;
}

const EXPLODE_FACTOR = 1.45;

function basePosition(component: TwinComponent): THREE.Vector3 {
  const [x, y, z] = component.position;
  return new THREE.Vector3(x, y, z);
}
function explodedPosition(component: TwinComponent): THREE.Vector3 {
  const [x, y, z] = component.position;
  return new THREE.Vector3(x * EXPLODE_FACTOR, y, z);
}

interface NodeEntry {
  component: TwinComponent;
  group: THREE.Group;
  ring: THREE.Mesh;
  label: HTMLDivElement;
  basePos: THREE.Vector3;
  explodedPos: THREE.Vector3;
  dispose: () => void;
}

/**
 * Plain three.js (no @react-three/fiber/drei): fiber's react-reconciler pin causes a real
 * mounting-order crash against this repo's react@18.3.1 (`Cannot read properties of undefined
 * (reading 'ReactCurrentBatchConfig')`), confirmed in a browser — see
 * components/process/ProcessScene.tsx, the reference implementation this mirrors. The scene is
 * built once per `components` identity (stable for the page's lifetime) and torn down fully on
 * unmount; selection/labels/explode/data-flow/theme are applied to the live scene via refs.
 */
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
  const containerRef = useRef<HTMLDivElement>(null);
  const nodesRef = useRef<NodeEntry[]>([]);
  const dataFlowRef = useRef<ReturnType<typeof buildDataFlow> | null>(null);
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
    dataFlowRef.current?.setActive(showDataFlow);
  }, [showDataFlow]);
  useEffect(() => {
    dataFlowRef.current?.setReducedMotion(reducedMotion);
  }, [reducedMotion]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = Math.max(container.clientWidth, 1);
    const height = Math.max(container.clientHeight, 1);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    camera.position.set(1, 6, 15);

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

    const dataFlow = buildDataFlow();
    dataFlow.setActive(showDataFlow);
    dataFlow.setReducedMotion(reducedMotion);
    dataFlowRef.current = dataFlow;
    scene.add(dataFlow.group);

    const entries: NodeEntry[] = [];
    for (const component of components) {
      const { group, ring, dispose } = buildTwinNodeGroup(component);
      const basePos = basePosition(component);
      const explodedPos = explodedPosition(component);
      group.position.copy(explodedRef.current ? explodedPos : basePos);
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

      entries.push({ component, group, ring, label, basePos, explodedPos, dispose });
    }
    nodesRef.current = entries;

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
    const flowPoints: THREE.Vector3[] = [];
    let frameId: number;
    const clock = new THREE.Clock();
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      flowPoints.length = 0;
      for (const entry of nodesRef.current) {
        const selected = entry.component.id === selectedIdRef.current;
        const target = explodedRef.current ? entry.explodedPos : entry.basePos;
        entry.group.position.lerp(target, 0.12);
        entry.ring.visible = selected;
        entry.label.style.display = showLabelsRef.current ? "block" : "none";
        entry.label.classList.toggle("twin-label-selected", selected);

        flowPoints.push(entry.group.position);

        projected.copy(entry.group.position).setY(entry.group.position.y + 1.5).project(camera);
        const behind = projected.z > 1;
        if (behind) {
          entry.label.style.display = "none";
        } else if (showLabelsRef.current) {
          const x = (projected.x * 0.5 + 0.5) * container.clientWidth;
          const y = (-projected.y * 0.5 + 0.5) * container.clientHeight;
          entry.label.style.transform = `translate(-50%, -100%) translate(${x}px, ${y}px)`;
        }
      }
      dataFlow.update(clock.getElapsedTime(), flowPoints);
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
      dataFlow.dispose();
      for (const entry of entries) {
        entry.dispose();
        entry.label.remove();
      }
      if (container.contains(renderer.domElement)) container.removeChild(renderer.domElement);
      if (container.contains(labelLayer)) container.removeChild(labelLayer);
      nodesRef.current = [];
      dataFlowRef.current = null;
      envRef.current = null;
      controlsRef.current = null;
    };
    // Rebuilt only if the component list identity changes (stable for the page's lifetime).
    // Selection/labels/explode/data-flow/theme are applied to the live scene by the refs/effects above.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [components]);

  // Theme changes recolor the live environment (lights + grid) in place — no WebGL context
  // teardown. Node/status colors are theme-invariant (see statusColor.ts), so nothing else here
  // needs to change on a theme flip.
  useEffect(() => {
    envRef.current?.setDark(dark);
  }, [dark]);

  return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
