"use client";

import { usePathname, useRouter } from "next/navigation";
import { useCallback, useMemo, useState } from "react";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import type { SystemComponent } from "@/lib/digital-twin/system-components";
import { SystemMapGraph } from "./SystemMapGraph";
import { SystemMapInspector } from "./SystemMapInspector";

interface SystemMapExplorerProps {
  components: SystemComponent[];
  /** Read server-side from the page's `searchParams` prop, not useSearchParams() — this keeps
   * the page fully server-rendered (no CSR bailout) since nothing here needs the browser. */
  initialStage: string | null;
}

/** Client root for /system-map: plain HTML/CSS graph + inspector, with `?stage=<id>` deep linking. No 3D, no dynamic import needed. */
export function SystemMapExplorer({ components, initialStage }: SystemMapExplorerProps) {
  const router = useRouter();
  const pathname = usePathname();

  const byId = useMemo(() => new Map(components.map((c) => [c.id, c])), [components]);
  const [selectedId, setSelectedId] = useState<string | null>(
    initialStage && byId.has(initialStage) ? initialStage : null,
  );

  const handleSelect = useCallback(
    (id: string) => {
      setSelectedId((current) => {
        const next = current === id ? null : id;
        router.replace(next ? `${pathname}?stage=${next}` : pathname, { scroll: false });
        return next;
      });
    },
    [pathname, router],
  );

  const selectedComponent = selectedId ? (byId.get(selectedId) ?? null) : null;

  return (
    <div className="twin-explorer">
      <div className="twin-stage">
        <SystemMapGraph components={components} selectedId={selectedId} onSelect={handleSelect} />
        <SystemMapInspector component={selectedComponent} byId={byId} onSelect={handleSelect} />
      </div>

      <h2>All stages (text list)</h2>
      <ol className="twin-component-list">
        {components.map((component) => (
          <li key={component.id}>
            <button
              type="button"
              className="twin-component-list-item"
              aria-pressed={selectedId === component.id}
              onClick={() => handleSelect(component.id)}
            >
              <span className="twin-component-list-name">
                {component.stage}. {component.name}
              </span>
              <EvidenceBadge status={component.researchStatus} />
              <span className="twin-component-list-role">{component.description}</span>
            </button>
          </li>
        ))}
      </ol>
    </div>
  );
}
