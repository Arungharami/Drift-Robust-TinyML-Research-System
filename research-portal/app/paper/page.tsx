import type { Metadata } from "next";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { ArtifactLink } from "@/components/ArtifactLink";
import { getClaims, getFigures, getProjectStatus, getTables, githubRawUrl } from "@/lib/evidence";

export const metadata: Metadata = { title: "Paper" };

const SECTIONS: { name: string; status: "PLANNED" | "RUNNING" | "EXECUTED" }[] = [
  { name: "Abstract", status: "PLANNED" },
  { name: "Introduction", status: "PLANNED" },
  { name: "Related Work", status: "PLANNED" },
  { name: "Research Gap", status: "PLANNED" },
  { name: "Methodology", status: "RUNNING" },
  { name: "Dataset", status: "RUNNING" },
  { name: "Chronological Evaluation Protocol", status: "RUNNING" },
  { name: "Models", status: "RUNNING" },
  { name: "Resource-Aware Explainability", status: "PLANNED" },
  { name: "Fidelity", status: "PLANNED" },
  { name: "Stability", status: "PLANNED" },
  { name: "TinyML Deployment", status: "PLANNED" },
  { name: "Energy Measurement", status: "PLANNED" },
  { name: "Results", status: "PLANNED" },
  { name: "Discussion", status: "PLANNED" },
  { name: "Threats to Validity", status: "PLANNED" },
  { name: "Reproducibility", status: "RUNNING" },
  { name: "Conclusion", status: "PLANNED" },
];

export default function PaperPage() {
  const claims = getClaims();
  const figures = getFigures();
  const tables = getTables();
  const status = getProjectStatus();

  return (
    <div className="container">
      <div className="section-label">Manuscript</div>
      <h1>Paper</h1>
      <p className="lede">
        Evidence-controlled manuscript pipeline. Results, Discussion, and the final Abstract are
        intentionally left undrafted — see{" "}
        <ArtifactLink path="paper/RESULTS_DRAFT.md" label="paper/RESULTS_DRAFT.md" />, which
        states plainly: &ldquo;No prose result claims are drafted until verified artifacts and
        the claim-evidence matrix support them.&rdquo;
      </p>

      <h2>Section status</h2>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Section</th><th>Status</th></tr></thead>
          <tbody>
            {SECTIONS.map((s) => (
              <tr key={s.name}>
                <td>{s.name}</td>
                <td><EvidenceBadge status={s.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Claim–evidence matrix</h2>
      <p style={{ fontSize: "0.88rem" }}>
        Every candidate claim is linked to its experiment ID, dataset/config hash, git commit,
        and result artifact — status <code>SUPPORTED</code> or <code>UNSUPPORTED</code>, decided
        by the artifact, not by narrative convenience.
      </p>
      <div className="table-scroll">
        <table>
          <thead><tr><th>ID</th><th>Claim</th><th>Metric</th><th>Status</th></tr></thead>
          <tbody>
            {claims.map((c) => (
              <tr key={c.claim_id}>
                <td>{c.claim_id}</td>
                <td style={{ maxWidth: "28rem" }}>{c.candidate_claim}</td>
                <td><code>{c.metric}</code></td>
                <td>
                  <span
                    className={`badge ${c.status === "SUPPORTED" ? "badge-EXECUTED" : "badge-FAILED"}`}
                  >
                    {c.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p style={{ fontSize: "0.85rem" }}>
        Full matrix: <ArtifactLink path="paper/claim_evidence_matrix.csv" />
      </p>

      <h2>Figures ({figures.length})</h2>
      <div className="card-grid">
        {figures.map((fig) => (
          <div className="card" key={fig.id}>
            {/* eslint-disable-next-line @next/next/no-img-element -- SVG figure from GitHub; next/image's raster pipeline isn't a fit for vector output */}
            <img
              src={githubRawUrl(fig.svg_path, status.git_commit)}
              alt={fig.id.replace(/_/g, " ")}
              style={{ width: "100%", height: "auto" }}
            />
            <p style={{ fontSize: "0.8rem", marginTop: "0.5rem", marginBottom: 0 }}>
              {fig.id.replace(/_/g, " ")}
              {fig.source_csv ? (
                <>
                  {" "}
                  · <ArtifactLink path={fig.source_csv} label="source" />
                </>
              ) : null}
            </p>
          </div>
        ))}
      </div>

      <h2>Tables ({tables.length})</h2>
      <ul style={{ fontSize: "0.9rem" }}>
        {tables.map((t) => (
          <li key={t.id}>
            <ArtifactLink path={t.markdown_path} label={t.id.replace(/_/g, " ")} />
          </li>
        ))}
      </ul>
    </div>
  );
}
