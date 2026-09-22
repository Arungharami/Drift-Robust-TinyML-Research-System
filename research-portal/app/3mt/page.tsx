import type { Metadata } from "next";
import Link from "next/link";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { MetricCard } from "@/components/MetricCard";
import { buildTwinComponents } from "@/components/digital-twin/twin-data";
import { AccuracyCollapse } from "@/components/three-mt/AccuracyCollapse";
import { ApplicationExplorer } from "@/components/three-mt/ApplicationExplorer";
import { DigitalTwinPreview } from "@/components/three-mt/DigitalTwinPreview";
import { DriftJourneyPanel, type BatchJourneyRow } from "@/components/three-mt/DriftJourneyPanel";
import { EvidenceStatusBar } from "@/components/three-mt/EvidenceStatusBar";
import { ExplainabilityView } from "@/components/three-mt/ExplainabilityView";
import { FinalStatement } from "@/components/three-mt/FinalStatement";
import { JudgeMode } from "@/components/three-mt/JudgeMode";
import { NoMagicSection } from "@/components/three-mt/NoMagicSection";
import { ThinkAboutThis } from "@/components/three-mt/ThinkAboutThis";
import { ThreeMTHero } from "@/components/three-mt/ThreeMTHero";
import { ThreeMTSlide } from "@/components/three-mt/ThreeMTSlide";
import { ThreeMTSpeech } from "@/components/three-mt/ThreeMTSpeech";
import { TimeAxis } from "@/components/three-mt/TimeAxis";
import { TinyMLTransition } from "@/components/three-mt/TinyMLTransition";
import { TrustFramework } from "@/components/three-mt/TrustFramework";
import { getBaselines, getDataset, getDrift, getEmbedded, getPlatform, getProjectStatus, getXai } from "@/lib/evidence";
import { SLIDE_ASSET_PATH, SPEECH_SOURCE_PATH } from "@/lib/three-mt/content";

export const metadata: Metadata = {
  title: "3-Minute Thesis",
  description:
    "When AI loses its sense of smell: a three-minute, evidence-linked explanation of drift-robust explainable TinyML for electronic-nose sensing.",
};

function pivotByBatch(rows: Record<string, string>[], metric: string) {
  const byBatch = new Map<string, Record<string, number | string>>();
  for (const row of rows) {
    const batch = row.test_batch ?? "";
    const model = row.model ?? "";
    if (!batch) continue;
    if (!byBatch.has(batch)) byBatch.set(batch, { test_batch: Number(batch) });
    const entry = byBatch.get(batch)!;
    entry[`${model}_${metric}`] = Number(row[metric] ?? NaN);
  }
  return Array.from(byBatch.values()).sort((a, b) => Number(a.test_batch) - Number(b.test_batch));
}

function buildJourneyRows(): BatchJourneyRow[] {
  const drift = getDrift();
  const baselines = getBaselines();
  const driftByBatch = new Map<number, number>();
  for (const row of drift.global_drift_by_batch) {
    if (row.metric !== "normalized_wasserstein") continue;
    driftByBatch.set(Number(row.comparison_batch), Number(row.median_feature_drift));
  }
  const accuracyByBatch = new Map<number, number>();
  for (const row of baselines.fixed_origin_by_batch) {
    if (row.model !== "MODEL-C1") continue;
    accuracyByBatch.set(Number(row.test_batch), Number(row.accuracy));
  }
  const batches = Array.from(new Set([...driftByBatch.keys(), ...accuracyByBatch.keys()])).sort((a, b) => a - b);
  return batches.map((batch) => ({
    batch,
    driftWasserstein: driftByBatch.has(batch) ? driftByBatch.get(batch)! : null,
    modelC1Accuracy: accuracyByBatch.has(batch) ? accuracyByBatch.get(batch)! : null,
  }));
}

const START_HERE = [
  { href: "#speech", label: "The original 3MT speech and slide, verbatim" },
  { href: "/process", label: "How it works, step by step" },
  { href: "/digital-twin", label: "The interactive digital twin" },
  { href: "/system-map", label: "The full system architecture" },
  { href: "/methodology", label: "Chronological evaluation methodology" },
  { href: "/experiments", label: "Every registered experiment" },
  { href: "/results", label: "Results dashboard" },
  { href: "/reproducibility", label: "How to reproduce this" },
];

const COLLABORATION_ITEMS = [
  {
    title: "Experimental review",
    body: "A second opinion on the chronological protocol, the resource-aware explanation methodology, or the fidelity/stability evaluation design.",
  },
  {
    title: "nRF52840 hardware access",
    body: "A physical nRF52840 development kit and debug probe would unblock Stages 15–20 (the entire physical measurement chain), architecturally ready and blocked on hardware access since Stage 13.",
  },
  {
    title: "Measurement guidance",
    body: "Experience with Nordic Power Profiler Kit II energy-measurement methodology, or with INT8 quantization-aware export for Cortex-M4F.",
  },
];

export default function ThreeMinuteThesisPage() {
  const dataset = getDataset();
  const baselines = getBaselines();
  const xai = getXai();
  const embedded = getEmbedded();
  const project = getProjectStatus();
  const platform = getPlatform();
  const gate = embedded.stage15_hardware_gate;
  const hardwareStatus = String(gate?.scientific_execution_status ?? project.hardware_state);

  const journeyRows = buildJourneyRows();
  const accuracyChartData = pivotByBatch(baselines.fixed_origin_by_batch, "accuracy");
  const twinComponents = buildTwinComponents();

  return (
    <div className="container threemt-page">
      <ThreeMTHero rows={journeyRows} baselinesStatus={baselines.evidence_status} />

      <JudgeMode rows={journeyRows} hardwareStatus={hardwareStatus} />

      <TimeAxis />

      <AccuracyCollapse rows={journeyRows} />

      <ThinkAboutThis />

      {/* ---------- Watch the sensor drift ---------- */}
      <section aria-labelledby="threemt-drift-title">
        <h2 id="threemt-drift-title">Watch the Sensor Drift</h2>
        <p style={{ maxWidth: "68ch" }}>
          Select a chronological test batch to see its real drift score relative to Batch 1, and
          the lightest baseline model&apos;s real accuracy at that point in time — the same
          numbers behind the 81.4%→37.4% figure above, drawn directly from{" "}
          <ArtifactLink path="results/drift/global_drift_by_batch.csv" label="results/drift/global_drift_by_batch.csv" /> and{" "}
          <ArtifactLink path="results/baselines/fixed_origin_metrics.csv" label="results/baselines/fixed_origin_metrics.csv" />.
          Nothing here is simulated or estimated.
        </p>
        <DriftJourneyPanel rows={journeyRows} chartData={accuracyChartData} />
      </section>

      <ExplainabilityView xai={xai} />

      <TinyMLTransition embedded={embedded} />

      <TrustFramework accuracyStatus={baselines.evidence_status} explanationStatus={xai.evidence_status} deployabilityStatus={hardwareStatus} />

      <DigitalTwinPreview components={twinComponents} />

      <EvidenceStatusBar project={project} />

      <ApplicationExplorer />

      <NoMagicSection />

      {/* ---------- Start here / verbatim source materials ---------- */}
      <section aria-labelledby="threemt-start-title">
        <h2 id="threemt-start-title">Go Deeper: 3 Minutes → 15 Minutes → Full Research</h2>
        <p style={{ maxWidth: "62ch" }}>The story above is the three-minute version. A recommended reading order beyond it:</p>
        <ol className="threemt-start-list">
          {START_HERE.map((item, i) => (
            <li key={item.href}>
              <span className="threemt-start-index">{i + 1}</span>
              <Link href={item.href}>{item.label}</Link>
            </li>
          ))}
        </ol>
      </section>

      <section id="speech" aria-labelledby="threemt-speech-title">
        <h2 id="threemt-speech-title">The 3MT Speech and Slide</h2>
        <p style={{ maxWidth: "62ch" }}>
          The actual speech and single slide submitted for the FAU 2026 Three Minute Thesis
          competition, reproduced verbatim — not a paraphrase.
        </p>
        <ThreeMTSlide />
        <ThreeMTSpeech />
      </section>

      {/* ---------- Research outline ---------- */}
      <section aria-labelledby="threemt-outline-title">
        <h2 id="threemt-outline-title">Complete Research Outline</h2>

        <h3>Motivation and research gap</h3>
        <p style={{ maxWidth: "68ch" }}>
          Electronic-nose classifiers are usually evaluated on randomly shuffled train/test splits,
          which can blend sensor behavior from different time periods and produce an optimistic
          estimate of real-world performance. This project instead evaluates strictly in
          chronological order, and treats explainability and TinyML deployability as first-class,
          separately-measured research questions rather than afterthoughts.
        </p>

        <h3>Research questions and hypotheses</h3>
        <p style={{ maxWidth: "68ch" }}>
          10 research questions (RQ1–RQ10) and 10 hypotheses (H1–H10), each tied to explicit
          acceptance criteria and linked experiment IDs. See{" "}
          <ArtifactLink path="research/questions.yaml" label="research/questions.yaml" /> and{" "}
          <ArtifactLink path="research/hypotheses.yaml" label="research/hypotheses.yaml" />.
        </p>

        <h3>Dataset and chronology</h3>
        <p style={{ maxWidth: "68ch" }}>
          UCI Gas Sensor Array Drift Dataset: {dataset.validation?.samples ?? "—"} samples,{" "}
          {dataset.validation?.features ?? "—"} features (16 sensors × 8 response characteristics),{" "}
          {dataset.validation?.batches ?? "—"} chronological batches, {dataset.validation?.classes ?? "—"} gas
          classes. <EvidenceBadge status={dataset.evidence_status} /> — full provenance on{" "}
          <Link href="/dataset">/dataset</Link>.
        </p>

        <h3>Data validation, frozen preprocessing, leakage controls</h3>
        <p style={{ maxWidth: "68ch" }}>
          Preprocessing (standardization) is fit once on Batch 1 only and frozen; the chronological
          split is defined before any model is trained. Details on{" "}
          <Link href="/methodology">/methodology</Link> and{" "}
          <ArtifactLink path="configs/chronological_protocol.yaml" />.
        </p>

        <h3>Baselines, fixed-origin evaluation, expanding-window adaptation</h3>
        <p style={{ maxWidth: "68ch" }}>
          Four classical models (Logistic Regression, Random Forest, RBF-SVM, MLP) evaluated under
          <code> FIXED_ORIGIN</code> (train once on Batch 1) and <code>EXPANDING_WINDOW</code>{" "}
          (periodic retraining) protocols. <EvidenceBadge status={baselines.evidence_status} /> — see{" "}
          <Link href="/results">/results</Link>.
        </p>

        <h3>Resource-aware explanations, fidelity, and stability</h3>
        <p style={{ maxWidth: "68ch" }}>
          Permutation importance, intrinsic coefficients/impurity, and single-feature
          ablation — deliberately not SHAP or LIME. Fidelity and stability evidence is executed but{" "}
          <strong>predominantly unsupported or mixed</strong>, stated plainly rather than
          minimized. <EvidenceBadge status={xai.evidence_status} /> — see <Link href="/xai">/xai</Link>.
        </p>

        <h3>Quantization and export for nRF52840 / Cortex-M4F</h3>
        <p style={{ maxWidth: "68ch" }}>
          Host-compiled (x86-64) numerical-equivalence export exists for two model candidates; the
          first two export attempts <strong>failed</strong> their preprocessing-equivalence
          criteria before a fused-architecture variant passed on host only. A weights-only INT8
          quantization protocol is frozen; INT8 quantization itself has{" "}
          <strong>not been executed</strong> at any tier. See <Link href="/tinyml">/tinyml</Link>.
        </p>

        <h3>Planned physical measurement</h3>
        <p style={{ maxWidth: "68ch" }}>
          Flash, SRAM, on-device latency, and PPK2 energy all require a physical nRF52840 board and
          debug probe. <EvidenceBadge status={hardwareStatus} /> — no board has ever been detected.
          See <Link href="/hardware">/hardware</Link>.
        </p>

        <h3>Pareto analysis, reproducibility, limitations, next experiments</h3>
        <p style={{ maxWidth: "68ch" }}>
          The accuracy/fidelity/resource Pareto analysis is blocked on physical hardware
          measurement and has not been produced. Reproducibility guarantees (seed, dataset hash,
          config hash, git commit per artifact) are documented on{" "}
          <Link href="/reproducibility">/reproducibility</Link>; the next planned experiment and
          every known limitation are stated on <Link href="/professor-review">/professor-review</Link>.
        </p>
      </section>

      {/* ---------- Collaboration ---------- */}
      <section aria-labelledby="threemt-collab-title">
        <h2 id="threemt-collab-title">Collaboration</h2>
        <p style={{ maxWidth: "68ch" }}>
          This research is at a stage where specific kinds of help would directly unblock the next
          experiments:
        </p>
        <ul style={{ maxWidth: "62ch" }}>
          {COLLABORATION_ITEMS.map((item) => (
            <li key={item.title}>
              <strong>{item.title}</strong> — {item.body}
            </li>
          ))}
        </ul>
        <p style={{ fontSize: "0.9rem" }}>
          Reach out via the <a href={`https://github.com/${project.repository}`} target="_blank" rel="noreferrer">GitHub repository</a>{" "}
          or the <Link href="/professor-review">professor/reviewer page</Link>.
        </p>
      </section>

      {/* ---------- Evidence and status (full accounting) ---------- */}
      <section id="evidence" aria-labelledby="threemt-evidence-title">
        <h2 id="threemt-evidence-title">Evidence and Status, in Full</h2>
        <p style={{ maxWidth: "68ch" }}>
          Every status below comes from the same evidence registry as the rest of this portal (
          <ArtifactLink path="configs/pipeline_stages.yaml" />) — nothing on this page is a separate
          or more favorable accounting.
        </p>
        <div className="card-grid">
          {Object.entries(project.pipeline_stage_counts).map(([status, count]) => (
            <MetricCard key={status} label={status.replace(/_/g, " ")} value={count} unit={`/ ${project.pipeline_total_stages} stages`} status="EXECUTED" />
          ))}
        </div>

        <h3>By category</h3>
        <div className="kv-grid">
          <div className="kv-item">
            <div className="k">Software research pipeline (baselines, drift analysis)</div>
            <div className="v"><EvidenceBadge status={baselines.evidence_status} /></div>
          </div>
          <div className="kv-item">
            <div className="k">Explainability (fidelity/stability mixed)</div>
            <div className="v"><EvidenceBadge status={xai.evidence_status} /></div>
          </div>
          <div className="kv-item">
            <div className="k">TinyML export</div>
            <div className="v"><EvidenceBadge status="HOST_EXECUTED" /></div>
          </div>
          <div className="kv-item">
            <div className="k">Quantization</div>
            <div className="v"><EvidenceBadge status="NOT_EXECUTED" /></div>
          </div>
          <div className="kv-item">
            <div className="k">Physical MCU deployment</div>
            <div className="v"><EvidenceBadge status={hardwareStatus} /></div>
          </div>
          <div className="kv-item">
            <div className="k">Latency / energy (physical)</div>
            <div className="v"><EvidenceBadge status="NOT_MEASURED" /></div>
          </div>
          <div className="kv-item">
            <div className="k">Manuscript</div>
            <div className="v">{project.paper_state}</div>
          </div>
          <div className="kv-item">
            <div className="k">Hugging Face dataset/model repos</div>
            <div className="v">
              {platform.huggingface?.authenticated ? <EvidenceBadge status="EXECUTED" /> : <span>In preparation — see <Link href="/huggingface">/huggingface</Link></span>}
            </div>
          </div>
        </div>

        <p className="btn-row">
          <a className="btn" href={`https://github.com/${project.repository}`} target="_blank" rel="noreferrer">
            View Source on GitHub
          </a>
          <Link className="btn" href="/pipeline">
            Full Pipeline Registry
          </Link>
          <Link className="btn" href="/paper">
            Read the Paper Draft
          </Link>
          <a className="btn" href={SLIDE_ASSET_PATH} download>
            Download 3MT Slide
          </a>
        </p>
        <p style={{ fontSize: "0.82rem", color: "var(--text-faint)" }}>
          3MT source materials: <ArtifactLink path={SPEECH_SOURCE_PATH} label="speech transcript" /> ·{" "}
          <ArtifactLink path="research-portal/public/3mt/Arun_Gharami_FAU_3MT_2026_Single_Slide.pptx" label="original slide (PPTX)" />
        </p>
      </section>

      <FinalStatement />
    </div>
  );
}
