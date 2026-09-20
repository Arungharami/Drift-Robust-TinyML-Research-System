"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import type { ProcessPhase } from "@/lib/process-phases";

// Flat, matte colors matching app/globals.css --status-*-fg tokens (light and dark).
const STATUS_COLOR: Record<string, { light: number; dark: number }> = {
  EXECUTED: { light: 0x1e5c33, dark: 0x8fd7a5 },
  VALIDATED: { light: 0x1e5c33, dark: 0x8fd7a5 },
  RUNNING: { light: 0x1f4c8f, dark: 0x8fb6ea },
  PROTOCOL_FROZEN: { light: 0x7a5c12, dark: 0xe0c069 },
  PLANNED: { light: 0x7a5c12, dark: 0xe0c069 },
  FAILED: { light: 0x9c2c22, dark: 0xec9187 },
  BLOCKED: { light: 0x6b5f45, dark: 0xc9bd97 },
  BLOCKED_HARDWARE: { light: 0x6b5f45, dark: 0xc9bd97 },
  NOT_EXECUTED: { light: 0x6f6a5c, dark: 0xa49c86 },
  NOT_MEASURED: { light: 0x6f6a5c, dark: 0xa49c86 },
};
const DEFAULT_COLOR = { light: 0x6f6a5c, dark: 0xa49c86 };
const OUTLINE_COLOR = { light: 0x1c1a16, dark: 0xece8dd };
const EDGE_COLOR = { light: 0xb9b2a2, dark: 0x6f6a54 };

function colorFor(status: string, theme: "light" | "dark") {
  return (STATUS_COLOR[status] ?? DEFAULT_COLOR)[theme];
}

interface NodeEntry {
  phase: ProcessPhase;
  group: THREE.Group;
  mesh: THREE.Mesh<THREE.BoxGeometry, THREE.MeshStandardMaterial>;
  outline: THREE.LineSegments<THREE.EdgesGeometry, THREE.LineBasicMaterial>;
  label: HTMLDivElement;
  position: THREE.Vector3;
}

/**
 * Plain three.js (no @react-three/fiber/drei): fiber's react-reconciler pin is incompatible
 * with react@18.3's internals (verified during build — see PR description), and downgrading
 * React just for this view was out of scope. This imperative scene is mounted once per
 * `phases` identity and torn down fully on unmount/rebuild; selection and theme are applied to
 * the live scene without recreating the WebGL context.
 */
export function ProcessScene({
  phases,
  selectedPhaseId,
  onSelect,
  reducedMotion,
  theme,
}: {
  phases: ProcessPhase[];
  selectedPhaseId: string | null;
  onSelect: (id: string) => void;
  reducedMotion: boolean;
  theme: "light" | "dark";
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const nodesRef = useRef<NodeEntry[]>([]);
  const edgeMaterialsRef = useRef<{ normal: THREE.LineBasicMaterial; blocked: THREE.LineBasicMaterial } | null>(null);
  const selectedIdRef = useRef(selectedPhaseId);
  const onSelectRef = useRef(onSelect);

  useEffect(() => {
    selectedIdRef.current = selectedPhaseId;
  }, [selectedPhaseId]);
  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = Math.max(container.clientWidth, 1);
    const height = Math.max(container.clientHeight, 1);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    // Base framing (distance 7.4, y 3.1) was tuned against the desktop box's wide aspect ratio
    // (~2.8:1). A narrow phone viewport needs the camera pulled back and slightly higher so all
    // six nodes are visible before the visitor has to drag/zoom at all.
    const aspect = width / height;
    const baseAspect = 1166 / 420;
    const distance = THREE.MathUtils.clamp(7.4 * (baseAspect / Math.max(aspect, 0.9)), 7.4, 12.5);
    const camY = THREE.MathUtils.clamp(3.1 * (distance / 7.4), 3.1, 5.2);
    camera.position.set(0, camY, distance);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
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
    controls.enablePan = false;
    controls.minDistance = 4.5;
    controls.maxDistance = 15;
    controls.maxPolarAngle = Math.PI / 2.05;
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.autoRotate = !reducedMotion;
    controls.autoRotateSpeed = 0.45;
    controls.addEventListener("start", () => {
      controls.autoRotate = false;
    });

    scene.add(new THREE.AmbientLight(0xffffff, 0.95));
    const directional = new THREE.DirectionalLight(0xffffff, 0.55);
    directional.position.set(3, 4, 2);
    scene.add(directional);

    const spacing = 2.5;
    const mid = (phases.length - 1) / 2;
    const positions = new Map<string, THREE.Vector3>();
    const entries: NodeEntry[] = [];

    const boxGeometry = new THREE.BoxGeometry(1.5, 0.95, 0.5);
    const edgesGeometry = new THREE.EdgesGeometry(boxGeometry);

    phases.forEach((phase, i) => {
      const position = new THREE.Vector3((i - mid) * spacing, 0, Math.sin(i * 1.15) * 0.85);
      positions.set(phase.id, position);

      const group = new THREE.Group();
      group.position.copy(position);

      const material = new THREE.MeshStandardMaterial({
        color: colorFor(phase.dominantStatus, theme),
        roughness: 1,
        metalness: 0,
      });
      const mesh = new THREE.Mesh(boxGeometry, material);
      mesh.userData.phaseId = phase.id;
      group.add(mesh);

      const outline = new THREE.LineSegments(edgesGeometry, new THREE.LineBasicMaterial({ color: OUTLINE_COLOR[theme] }));
      outline.scale.setScalar(1.03);
      outline.visible = phase.id === selectedIdRef.current;
      group.add(outline);

      scene.add(group);

      const label = document.createElement("div");
      label.className = "process-node-label";
      // Required for the translate(-50%, -100%) centering trick below: without an explicit
      // position, a block-level div has no intrinsic width to center against and instead
      // stretches to fill labelLayer, making the percentage translate wildly wrong.
      label.style.position = "absolute";
      label.style.left = "0";
      label.style.top = "0";
      label.style.width = "max-content";
      const executedCount = phase.stages.filter((s) => s.status === "EXECUTED" || s.status === "VALIDATED").length;
      label.innerHTML = `<strong>${phase.shortLabel}</strong><span>${executedCount}/${phase.stages.length}</span>`;
      labelLayer.appendChild(label);

      entries.push({ phase, group, mesh, outline, label, position });
    });

    nodesRef.current = entries;

    const edgeMaterial = new THREE.LineBasicMaterial({ color: EDGE_COLOR[theme], transparent: true, opacity: 0.85 });
    const blockedEdgeMaterial = new THREE.LineBasicMaterial({ color: EDGE_COLOR[theme], transparent: true, opacity: 0.35 });
    edgeMaterialsRef.current = { normal: edgeMaterial, blocked: blockedEdgeMaterial };
    const edgeLines: THREE.Line[] = [];
    for (const phase of phases) {
      for (const depId of phase.dependsOnPhaseIds) {
        const from = positions.get(depId);
        const to = positions.get(phase.id);
        if (!from || !to) continue;
        const geometry = new THREE.BufferGeometry().setFromPoints([from, to]);
        const blocked = phase.hasBlocker || phase.hasFailure;
        const line = new THREE.Line(geometry, blocked ? blockedEdgeMaterial : edgeMaterial);
        scene.add(line);
        edgeLines.push(line);
      }
    }

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const meshes = entries.map((e) => e.mesh);

    function pickPhaseId(clientX: number, clientY: number): string | null {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hit = raycaster.intersectObjects(meshes, false)[0];
      return hit ? (hit.object.userData.phaseId as string) : null;
    }

    function handleClick(event: MouseEvent) {
      const id = pickPhaseId(event.clientX, event.clientY);
      if (id) onSelectRef.current(id);
    }

    function handleMove(event: PointerEvent) {
      const id = pickPhaseId(event.clientX, event.clientY);
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
      for (const entry of nodesRef.current) {
        const selected = entry.phase.id === selectedIdRef.current;
        const targetY = selected ? 0.18 : 0;
        const targetScale = selected ? 1.1 : 1;
        entry.group.position.y += (targetY - entry.group.position.y) * 0.15;
        const s = entry.group.scale.x + (targetScale - entry.group.scale.x) * 0.2;
        entry.group.scale.setScalar(s);
        entry.outline.visible = selected;
        entry.label.classList.toggle("process-node-label-active", selected);

        projected.copy(entry.position).setY(entry.position.y + 0.85).project(camera);
        const behind = projected.z > 1;
        entry.label.style.display = behind ? "none" : "block";
        if (!behind) {
          const x = (projected.x * 0.5 + 0.5) * container.clientWidth;
          const y = (-projected.y * 0.5 + 0.5) * container.clientHeight;
          entry.label.style.transform = `translate(-50%, -100%) translate(${x}px, ${y}px)`;
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
      boxGeometry.dispose();
      edgesGeometry.dispose();
      edgeMaterial.dispose();
      blockedEdgeMaterial.dispose();
      for (const line of edgeLines) line.geometry.dispose();
      for (const entry of entries) {
        entry.mesh.material.dispose();
        entry.outline.material.dispose();
        entry.label.remove();
      }
      if (container.contains(renderer.domElement)) container.removeChild(renderer.domElement);
      if (container.contains(labelLayer)) container.removeChild(labelLayer);
      nodesRef.current = [];
      edgeMaterialsRef.current = null;
    };
    // Rebuilt only if the phase list identity changes (stable for the page's lifetime).
    // Selection/theme are applied to the live scene by the effects below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phases]);

  // Theme changes recolor the live scene in place — no WebGL context teardown.
  useEffect(() => {
    for (const entry of nodesRef.current) {
      entry.mesh.material.color.setHex(colorFor(entry.phase.dominantStatus, theme));
      entry.outline.material.color.setHex(OUTLINE_COLOR[theme]);
    }
    if (edgeMaterialsRef.current) {
      edgeMaterialsRef.current.normal.color.setHex(EDGE_COLOR[theme]);
      edgeMaterialsRef.current.blocked.color.setHex(EDGE_COLOR[theme]);
    }
  }, [theme]);

  return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
