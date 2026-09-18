"use client";

import { EvidenceBadge } from "@/components/EvidenceBadge";
import { GROUP_LABELS, type SystemComponent, type SystemMapGroup } from "@/lib/digital-twin/system-components";

const GROUP_ORDER: SystemMapGroup[] = ["physical", "data-ml", "edge", "operations", "research"];

interface SystemMapGraphProps {
  components: SystemComponent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

/**
 * Plain HTML/CSS node-and-edge view: one column per domain group, nodes ordered by pipeline
 * stage, with a "↓" connector inside each column and dependency chips crossing columns.
 * Deliberately not a 3D scene (see Part 12 of the Phase-C brief) and not SVG-line-routed —
 * dependency chips in the inspector carry the cross-column edges instead, which stays legible
 * at any viewport width without custom line-layout code.
 */
export function SystemMapGraph({ components, selectedId, onSelect }: SystemMapGraphProps) {
  const byGroup = GROUP_ORDER.map((group) => ({
    group,
    nodes: components.filter((c) => c.group === group).sort((a, b) => a.stage - b.stage),
  })).filter((g) => g.nodes.length > 0);

  return (
    <div className="system-map-graph">
      {byGroup.map(({ group, nodes }) => (
        <div className="system-map-column" key={group}>
          <h3 className="system-map-column-title">{GROUP_LABELS[group]}</h3>
          <ol className="system-map-column-nodes">
            {nodes.map((node, i) => (
              <li key={node.id}>
                <button
                  type="button"
                  className="system-map-node"
                  aria-pressed={selectedId === node.id}
                  aria-current={selectedId === node.id ? "true" : undefined}
                  onClick={() => onSelect(node.id)}
                >
                  <span className="system-map-node-stage">{node.stage}</span>
                  <span className="system-map-node-name">{node.name}</span>
                  <EvidenceBadge status={node.researchStatus} />
                  {node.dependencies.length > 0 && (
                    <span className="system-map-node-deps">depends on {node.dependencies.length}</span>
                  )}
                </button>
                {i < nodes.length - 1 && (
                  <span className="system-map-connector" aria-hidden="true">
                    ↓
                  </span>
                )}
              </li>
            ))}
          </ol>
        </div>
      ))}
    </div>
  );
}
