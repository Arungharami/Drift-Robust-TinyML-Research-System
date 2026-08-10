import type { Metadata } from "next";
import { getProjectStatus } from "@/lib/evidence";

export const metadata: Metadata = { title: "About" };

export default function AboutPage() {
  const status = getProjectStatus();
  return (
    <div className="container">
      <div className="section-label">About</div>
      <h1>Researcher and project role</h1>

      <h2>Research interests</h2>
      <p style={{ maxWidth: "68ch" }}>
        Chronological evaluation of drift-affected sensor data, resource-constrained explainable
        AI, and reproducible research infrastructure connecting cloud compute, artifact
        publishing, and embedded deployment evidence.
      </p>

      <h2>Project role</h2>
      <p style={{ maxWidth: "68ch" }}>
        Sole researcher and engineer on this project: research design, dataset validation,
        classical baseline implementation, chronological evaluation, and the reproducibility /
        multi-platform infrastructure documented throughout this site.
      </p>

      <h2>Technical responsibilities</h2>
      <ul style={{ maxWidth: "68ch" }}>
        <li>Experimental protocol design and chronological split policy</li>
        <li>Dataset acquisition, validation, and hash-based provenance</li>
        <li>Classical model implementation and evaluation</li>
        <li>Reproducibility infrastructure (Colab CLI, GitHub/Hugging Face/Kaggle bridge)</li>
        <li>This research portal</li>
      </ul>

      <h2>Links</h2>
      <ul style={{ maxWidth: "68ch" }}>
        <li>
          GitHub: <a href={`https://github.com/${status.repository}`} target="_blank" rel="noreferrer">{status.repository}</a>
        </li>
        <li>ORCID: not yet linked</li>
        <li>Google Scholar: not yet linked</li>
      </ul>
      <p style={{ fontSize: "0.85rem", color: "var(--text-faint)" }}>
        Links above are shown only where verifiable; unlinked items are marked rather than
        guessed at.
      </p>
    </div>
  );
}
