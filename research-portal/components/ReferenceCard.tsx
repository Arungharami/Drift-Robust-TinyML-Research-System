export interface Reference {
  id: string;
  authors: string;
  title: string;
  year: number;
  venue: string;
  doi?: string;
  url?: string;
  topic: string;
  relevance: string;
  novelty_threat?: string;
  notes?: string;
}

export function ReferenceCard({ reference }: { reference: Reference }) {
  return (
    <div className="card" style={{ marginBottom: "0.75rem" }}>
      <div className="section-label">{reference.topic}</div>
      <h3 style={{ margin: "0.1rem 0 0.25rem" }}>
        {reference.url || reference.doi ? (
          <a href={reference.url ?? `https://doi.org/${reference.doi}`} target="_blank" rel="noreferrer">
            {reference.title}
          </a>
        ) : (
          reference.title
        )}
      </h3>
      <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", margin: "0 0 0.5rem" }}>
        {reference.authors} ({reference.year}) — <em>{reference.venue}</em>
      </p>
      <p style={{ fontSize: "0.88rem", margin: "0 0 0.35rem" }}>{reference.relevance}</p>
      {reference.novelty_threat ? (
        <p style={{ fontSize: "0.82rem", color: "var(--status-planned-fg)", margin: 0 }}>
          Novelty consideration: {reference.novelty_threat}
        </p>
      ) : null}
    </div>
  );
}
