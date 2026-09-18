"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo, useState } from "react";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import type { SystemComponent } from "@/lib/digital-twin/system-components";
import { SystemMapGraph } from "./SystemMapGraph";
import { SystemMapInspector } from "./SystemMapInspector";

/** Client root for /system-map: plain HTML/CSS graph + inspector, with `?stage=<id>` deep linking. No 3D, no dynamic import needed. */
export function SystemMapExplorer({ components }: { components: SystemComponent[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const initialStage = searchParams.get("stage");

  const byId = useMemo(() => new Map(components.map((c) => [c.id, c])), [components]);
  const [selectedId, setSelectedId] = useState<string | null>(
    initialStage && byId.has(initialStage) ? initialStage : null,
  );

  const handleSelect = useCallback(
    (id: string) => {
      setSelectedId((current) => {
        const next = current === id ? null : id;
        const params = new URLSearchParams(searchParams.toString());
        if (next) params.set("stage", next);
        else params.delete("stage");
        const query = params.toString();
        router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
        return next;
      });
    },
    [pathname, router, searchParams],
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
