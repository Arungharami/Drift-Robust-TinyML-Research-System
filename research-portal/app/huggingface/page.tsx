import type { Metadata } from "next";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { ArtifactLink } from "@/components/ArtifactLink";
import { getPlatform } from "@/lib/evidence";

export const metadata: Metadata = { title: "Hugging Face" };

export default function HuggingFacePage() {
  const platform = getPlatform();
  const hf = platform.huggingface;

  return (
    <div className="container">
      <div className="section-label">Hugging Face Hub</div>
      <h1>Model and dataset publishing</h1>
      <p className="lede">
        Hugging Face is used as the artifact/model distribution layer, private by default. No
        dataset or model repository has been created yet — this page reports the real, live CLI
        status, not an aspirational one.
      </p>

      <h2>CLI status (live)</h2>
      <div className="kv-grid">
        <div className="kv-item">
          <div className="k">CLI installed</div>
          <div className="v">{hf ? "Yes (hf)" : "Unknown"}</div>
        </div>
        <div className="kv-item">
          <div className="k">CLI version</div>
          <div className="v">{hf?.cli_version ?? "—"}</div>
        </div>
        <div className="kv-item">
          <div className="k">Authenticated</div>
          <div className="v">
            {hf?.authenticated ? <EvidenceBadge status="EXECUTED" /> : <EvidenceBadge status="BLOCKED" />}
          </div>
        </div>
        <div className="kv-item">
          <div className="k">Last checked</div>
          <div className="v">{hf?.timestamp ?? "—"}</div>
        </div>
      </div>

      <h2>Planned repositories</h2>
      <div className="card-grid">
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Dataset repository</h3>
          <p style={{ fontSize: "0.9rem" }}>
            Derived reproducibility evidence only — never the raw UCI archive. Card drafted at{" "}
            <ArtifactLink path="platforms/huggingface/dataset/README.md" />.
          </p>
          <EvidenceBadge status="NOT_EXECUTED" />
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Model repository</h3>
          <p style={{ fontSize: "0.9rem" }}>
            Publishes only after an experiment reaches <code>COMPLETED</code> status with
            validated evidence. Card template at{" "}
            <ArtifactLink path="platforms/huggingface/model/README.md" />.
          </p>
          <EvidenceBadge status="NOT_EXECUTED" />
        </div>
      </div>

      <p style={{ fontSize: "0.85rem" }}>
        Full bridge policy: <ArtifactLink path="docs/RESEARCH_PLATFORM_BRIDGE.md" />
      </p>
    </div>
  );
}
