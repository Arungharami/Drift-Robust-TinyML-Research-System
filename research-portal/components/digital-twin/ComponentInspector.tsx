"use client";

import Link from "next/link";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import type { TwinComponent } from "./types";

/** Non-3D detail panel for the selected component — the accessible/textual side of the "inspect" interaction. */
export function ComponentInspector({ component }: { component: TwinComponent | null }) {
  if (!component) {
    return (
      <aside className="twin-inspector twin-inspector-empty" aria-live="polite">
        <p>Select a component in the scene — or in the text list below — to inspect its role, evidence, and status.</p>
      </aside>
    );
  }

  return (
    <aside className="twin-inspector" aria-live="polite">
      <div className="section-label">Component</div>
      <h3>{component.name}</h3>
      <EvidenceBadge status={component.status} />
      <dl className="twin-inspector-facts">
        <div>
          <dt>Role</dt>
          <dd>{component.role}</dd>
        </div>
        <div>
          <dt>Input</dt>
          <dd>{component.input}</dd>
        </div>
        <div>
          <dt>Output</dt>
          <dd>{component.output}</dd>
        </div>
      </dl>
      {component.statusNote && <p className="twin-inspector-note">{component.statusNote}</p>}
      {component.evidenceLinks.length > 0 && (
        <ul className="twin-inspector-links">
          {component.evidenceLinks.map((link) => (
            <li key={link.path}>
              <ArtifactLink path={link.path} label={link.label} />
            </li>
          ))}
        </ul>
      )}
      {component.portalHref && (
        <p>
          <Link href={component.portalHref}>Full evidence for this stage →</Link>
        </p>
      )}
    </aside>
  );
}
