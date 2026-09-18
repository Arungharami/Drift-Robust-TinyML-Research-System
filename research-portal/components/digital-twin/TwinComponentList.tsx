"use client";

import { EvidenceBadge } from "@/components/EvidenceBadge";
import type { TwinComponent } from "./types";

interface TwinComponentListProps {
  components: TwinComponent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

/**
 * Non-3D equivalent of "click a component to inspect it." Always rendered — not gated behind
 * WebGL or JS-heavy interaction — so keyboard and screen-reader users have full parity with the
 * 3D scene, per the portal's accessibility requirement that every 3D interaction has a text path.
 */
export function TwinComponentList({ components, selectedId, onSelect }: TwinComponentListProps) {
  return (
    <ol className="twin-component-list">
      {components.map((component) => (
        <li key={component.id}>
          <button
            type="button"
            className="twin-component-list-item"
            aria-pressed={selectedId === component.id}
            onClick={() => onSelect(component.id)}
          >
            <span className="twin-component-list-name">{component.name}</span>
            <EvidenceBadge status={component.status} />
            <span className="twin-component-list-role">{component.role}</span>
          </button>
        </li>
      ))}
    </ol>
  );
}
