import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { ReproducibilityChecklist } from "@/components/ReproducibilityChecklist";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { getPlatform } from "@/lib/evidence";

export const metadata: Metadata = { title: "Reproducibility" };

export default function ReproducibilityPage() {
  const platform = getPlatform();

  return (
    <div className="container">
      <div className="section-label">Reproducibility</div>
      <h1>How to reproduce these experiments</h1>
      <p className="lede">
        Everything on this page is captured automatically — nothing here is a manually typed
        claim of reproducibility.
      </p>

      <h2>Recorded environment</h2>
      <ReproducibilityChecklist />

      <h2>Quick start</h2>
      <pre>
        <code>{`python -m venv .venv
python -m pip install -r requirements.txt
python scripts/download_dataset.py
python scripts/validate_dataset.py
python scripts/run_drift_analysis.py
pytest -q`}</code>
      </pre>
      <p style={{ fontSize: "0.88rem" }}>
        Full command reference: <ArtifactLink path="docs/REPRODUCIBILITY.md" /> ·{" "}
        <ArtifactLink path="docs/RESEARCH_PROTOCOL.md" />
      </p>

      <h2>Evidence policy</h2>
      <p style={{ maxWidth: "68ch" }}>
        Every number on this site traces to a saved artifact and a specific experiment ID. If an
        artifact does not exist, the corresponding value renders as{" "}
        <EvidenceBadge status="NOT_EXECUTED" /> — never a placeholder or estimated figure.
        Synthetic data is limited to unit tests and is never shown as a research result.
      </p>

      <h2>Google Colab</h2>
      <p style={{ maxWidth: "68ch" }}>
        Real Colab CLI execution is orchestrated from WSL2 via <code>scripts/colab/</code> and VS
        Code tasks (Mode B), or interactively via Select Kernel → Colab (Mode A). Current
        verified status: <ArtifactLink path="results/reproducibility/COLAB_STATUS.md" />.
      </p>

      <h2>Cross-platform provenance bridge</h2>
      <p style={{ maxWidth: "68ch" }}>
        GitHub, Hugging Face, and Kaggle CLI status, captured live (never fabricated):
      </p>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Platform</th><th>Authenticated</th><th>CLI version</th></tr></thead>
          <tbody>
            <tr>
              <td>GitHub</td>
              <td>{platform.github?.authenticated ? "Yes" : "No"}</td>
              <td><code>{platform.github?.cli_version ?? "—"}</code></td>
            </tr>
            <tr>
              <td>Hugging Face</td>
              <td>{platform.huggingface?.authenticated ? "Yes" : "No"}</td>
              <td><code>{platform.huggingface?.cli_version ?? "—"}</code></td>
            </tr>
            <tr>
              <td>Kaggle</td>
              <td>{platform.kaggle?.authenticated ? "Yes" : "No"}</td>
              <td><code>{platform.kaggle?.cli_version ?? "—"}</code></td>
            </tr>
          </tbody>
        </table>
      </div>
      <p style={{ fontSize: "0.85rem" }}>
        Full policy: <ArtifactLink path="docs/RESEARCH_PLATFORM_BRIDGE.md" />
      </p>
    </div>
  );
}
