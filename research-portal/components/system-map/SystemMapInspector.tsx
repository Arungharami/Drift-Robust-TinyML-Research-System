"use client";

import Link from "next/link";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import type { SystemComponent } from "@/lib/digital-twin/system-components";

interface SystemMapInspectorProps {
  component: SystemComponent | null;
  byId: Map<string, SystemComponent>;
  onSelect: (id: string) => void;
}

/** Detail panel for the selected pipeline node — the non-diagram, fully-accessible side of "select a node." */
export function SystemMapInspector({ component, byId, onSelect }: SystemMapInspectorProps) {
  if (!component) {
    return (
      <aside className="twin-inspector twin-inspector-empty" aria-live="polite">
        <p>Select a stage in the map — or in the list below — to inspect its role, dependencies, and evidence.</p>
      </aside>
    );
  }

  const dependents = Array.from(byId.values()).filter((c) => c.dependencies.includes(component.id));

  return (
    <aside className="twin-inspector" aria-live="polite">
      <div className="section-label">
        Stage {component.stage} · {component.group}
      </div>
      <h3>{component.name}</h3>
      <div>
        <span className="twin-inspector-badge-label">Research status</span>
        <EvidenceBadge status={component.researchStatus} />
      </div>
      <p>{component.description}</p>
      <dl className="twin-inspector-facts">
        <div>
          <dt>Role</dt>
          <dd>{component.role}</dd>
        </div>
        <div>
          <dt>Inputs</dt>
          <dd>{component.inputs.join(", ")}</dd>
        </div>
        <div>
          <dt>Outputs</dt>
          <dd>{component.outputs.join(", ")}</dd>
        </div>
        {component.algorithms && component.algorithms.length > 0 && (
          <div>
            <dt>Algorithms</dt>
            <dd>{component.algorithms.join(", ")}</dd>
          </div>
        )}
      </dl>
      {component.statusNote && <p className="twin-inspector-note">{component.statusNote}</p>}

      {component.dependencies.length > 0 && (
        <>
          <div className="section-label">Depends on</div>
          <ul className="twin-dependency-chips">
            {component.dependencies.map((depId) => {
              const dep = byId.get(depId);
              return (
                <li key={depId}>
                  <button type="button" className="twin-dependency-chip" onClick={() => onSelect(depId)}>
                    {dep?.name ?? depId}
                  </button>
                </li>
              );
            })}
          </ul>
        </>
      )}
      {dependents.length > 0 && (
        <>
          <div className="section-label">Required by</div>
          <ul className="twin-dependency-chips">
            {dependents.map((dep) => (
              <li key={dep.id}>
                <button type="button" className="twin-dependency-chip" onClick={() => onSelect(dep.id)}>
                  {dep.name}
                </button>
              </li>
            ))}
          </ul>
        </>
      )}

      {component.evidenceLinks.length > 0 && (
        <ul className="twin-inspector-links">
          {component.evidenceLinks.map((link) => (
            <li key={link.path}>
              <ArtifactLink path={link.path} label={link.label} />
            </li>
          ))}
        </ul>
      )}
      {(component.relatedModels?.length || component.relatedExperiments?.length) && (
        <dl className="twin-inspector-facts">
          {component.relatedModels && component.relatedModels.length > 0 && (
            <div>
              <dt>Related model(s)</dt>
              <dd>{component.relatedModels.map((m) => <code key={m}>{m}</code>)}</dd>
            </div>
          )}
          {component.relatedExperiments && component.relatedExperiments.length > 0 && (
            <div>
              <dt>Related experiment(s)</dt>
              <dd>{component.relatedExperiments.map((m) => <code key={m}>{m}</code>)}</dd>
            </div>
          )}
        </dl>
      )}
      {component.limitations && component.limitations.length > 0 && (
        <>
          <div className="section-label">Limitations</div>
          <ul className="twin-inspector-links">
            {component.limitations.map((limitation) => (
              <li key={limitation}>{limitation}</li>
            ))}
          </ul>
        </>
      )}
      {component.portalHref && (
        <p>
          <Link href={component.portalHref}>Full evidence for this stage →</Link>
        </p>
      )}
    </aside>
  );
}
