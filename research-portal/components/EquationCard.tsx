import { ArtifactLink } from "./ArtifactLink";

export function EquationCard({
  name,
  equation,
  symbols,
  implementation,
  stage,
}: {
  name: string;
  equation: string;
  symbols: { symbol: string; meaning: string }[];
  implementation?: string;
  stage?: string;
}) {
  return (
    <div className="card" style={{ marginBottom: "0.75rem" }}>
      <h3 style={{ marginTop: 0 }}>{name}</h3>
      <pre style={{ fontSize: "0.95rem" }}>
        <code>{equation}</code>
      </pre>
      <ul style={{ fontSize: "0.86rem", paddingLeft: "1.1rem", margin: "0.5rem 0" }}>
        {symbols.map((s) => (
          <li key={s.symbol}>
            <code>{s.symbol}</code> — {s.meaning}
          </li>
        ))}
      </ul>
      <div style={{ fontSize: "0.82rem", color: "var(--text-faint)" }}>
        {implementation ? (
          <span>
            Implementation: <ArtifactLink path={implementation} />
          </span>
        ) : (
          <span>Implementation: not yet written (NOT EXECUTED)</span>
        )}
        {stage ? <span> · Pipeline stage: {stage}</span> : null}
      </div>
    </div>
  );
}
