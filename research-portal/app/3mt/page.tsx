import type { Metadata } from "next";
import Link from "next/link";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { MetricCard } from "@/components/MetricCard";
import { DigitalTwinLoader } from "@/components/digital-twin/DigitalTwinLoader";
import { buildTwinComponents } from "@/components/digital-twin/twin-data";
import { DriftJourneyPanel, type BatchJourneyRow } from "@/components/three-mt/DriftJourneyPanel";
import { ThreeMTSlide } from "@/components/three-mt/ThreeMTSlide";
import { ThreeMTSpeech } from "@/components/three-mt/ThreeMTSpeech";
import { getBaselines, getDataset, getDrift, getEmbedded, getPlatform, getProjectStatus, getXai } from "@/lib/evidence";
import { SLIDE_ASSET_PATH, SPEECH_SOURCE_PATH } from "@/lib/three-mt/content";

export const metadata: Metadata = {
  title: "3-Minute Thesis",
  description:
    "A three-minute explanation of drift-robust explainable TinyML for electronic-nose sensing, linked directly to the underlying evidence.",
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
  { href: "/3mt#speech", label: "This page: the 3-minute version" },
  { href: "/process", label: "How it works, step by step" },
  { href: "/digital-twin", label: "The interactive digital twin" },
  { href: "/system-map", label: "The full system architecture" },
  { href: "/methodology", label: "Chronological evaluation methodology" },
  { href: "/experiments", label: "Every registered experiment" },
  { href: "/results", label: "Results dashboard" },
  { href: "/reproducibility", label: "How to reproduce this" },
];

const NEW_DOORS = [
  {
    title: "Reliable environmental sensing",
    body: "Chronological-drift-aware evaluation is directly applicable to any long-lived environmental sensor network (air quality, water quality) where recalibration is expensive or impossible.",
  },
  {
    title: "Industrial gas and process monitoring",
    body: "Industrial electronic-nose deployments run for years without replacement — a drift-honest evaluation protocol could inform maintenance/recalibration scheduling.",
  },
  {
    title: "Food quality assessment",
    body: "Spoilage and freshness detection is a natural electronic-nose application; this work's chronological protocol could validate whether a food-safety model still holds after sensor aging.",
  },
  {
    title: "Portable diagnostics research",
    body: "Breath- or odor-based diagnostic research faces the same sensor-drift risk; resource-aware explainability could support clinician trust in a constrained device.",
  },
  {
    title: "Edge AI under distribution shift, broadly",
    body: "The chronological-evaluation and resource-aware-explanation methodology is not electronic-nose-specific — it generalizes to any TinyML system where the sensor or input distribution changes after deployment.",
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
      {/* ---------- Hero ---------- */}
      <section aria-labelledby="threemt-hero-title">
        <div className="section-label">Three-Minute Thesis</div>
        <h1 id="threemt-hero-title">Drift-Robust Explainable TinyML for Electronic-Nose Sensing</h1>
        <p className="lede">
          Can lightweight models retain useful predictive performance and interpretable behavior
          under chronological sensor drift while fitting resource-constrained TinyML hardware?
        </p>
        <p style={{ maxWidth: "68ch" }}>
          Electronic-nose sensors age and drift — a model trained on early sensor readings loses
          accuracy as time passes, even though nothing about the underlying chemistry changed. This
          project evaluates that decay honestly (in real chronological order, never shuffled),
          studies whether explanations of a model&apos;s predictions stay stable as sensors drift,
          and works toward a resource-aware path to a physical nRF52840 microcontroller — while
          reporting plainly what has and has not yet been executed.
        </p>
        <p className="btn-row">
          <Link className="btn btn-primary" href="/system-map">
            Explore the Research →
          </Link>
          <Link className="btn" href="/digital-twin">
            Explore the Digital Twin
          </Link>
          <a className="btn" href="#evidence">
            See What&apos;s Verified
          </a>
        </p>
      </section>

      {/* ---------- Start here ---------- */}
      <section aria-labelledby="threemt-start-title">
        <h2 id="threemt-start-title">New to the project? Start here.</h2>
        <p style={{ maxWidth: "62ch" }}>A recommended reading order, in roughly three minutes to three hours:</p>
        <ol className="threemt-start-list">
          {START_HERE.map((item, i) => (
            <li key={item.href}>
              <span className="threemt-start-index">{i + 1}</span>
              <Link href={item.href}>{item.label}</Link>
            </li>
          ))}
        </ol>
      </section>

      {/* ---------- 3MT speech + slide ---------- */}
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
          criteria before a fused-architecture variant passed on host only. INT8 quantization has{" "}
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

      {/* ---------- Interactive research view ---------- */}
      <section aria-labelledby="threemt-interactive-title">
        <h2 id="threemt-interactive-title">Interactive Research View</h2>
        <p style={{ maxWidth: "68ch" }}>
          The conceptual 3D pipeline below is the same evidence-driven digital twin used on{" "}
          <Link href="/digital-twin">/digital-twin</Link> — sample chamber → sensor array → drift
          detector → classical model → explanation → nRF52840 (currently hardware-blocked) →
          gateway → evidence registry. Every status shown is real; nothing here is a fabricated
          measurement.
        </p>
        <DigitalTwinLoader components={twinComponents} />

        <h3>Move between chronological batches</h3>
        <p style={{ maxWidth: "68ch" }}>
          Select a test batch to see its real drift score (relative to Batch 1) and the lightest
          baseline model&apos;s real accuracy at that point in time — the same numbers behind the
          3MT slide&apos;s 81%→37% figure, drawn directly from{" "}
          <ArtifactLink path="results/drift/global_drift_by_batch.csv" label="results/drift/global_drift_by_batch.csv" /> and{" "}
          <ArtifactLink path="results/baselines/fixed_origin_by_batch.csv" label="results/baselines/fixed_origin_by_batch.csv" />.
        </p>
        <DriftJourneyPanel rows={journeyRows} chartData={accuracyChartData} />
      </section>

      {/* ---------- New doors ---------- */}
      <section aria-labelledby="threemt-doors-title">
        <h2 id="threemt-doors-title">New Doors This Work Could Open</h2>
        <p style={{ maxWidth: "68ch" }}>
          These are potential application directions that this methodology could inform — they are
          not demonstrated outcomes, and each would require its own domain-specific validation.
        </p>
        <div className="card-grid">
          {NEW_DOORS.map((door) => (
            <div className="card" key={door.title}>
              <h3 style={{ marginTop: 0 }}>{door.title}</h3>
              <p style={{ fontSize: "0.9rem" }}>{door.body}</p>
            </div>
          ))}
        </div>

        <h3>Collaboration</h3>
        <p style={{ maxWidth: "68ch" }}>
          This research is at a stage where specific kinds of help would directly unblock the next
          experiments:
        </p>
        <ul style={{ maxWidth: "62ch" }}>
          <li>
            <strong>Experimental review</strong> — a second opinion on the chronological protocol,
            the resource-aware explanation methodology, or the fidelity/stability evaluation design.
          </li>
          <li>
            <strong>nRF52840 hardware access</strong> — a physical nRF52840 development kit and
            debug probe would unblock Stages 15–20 (the entire physical measurement chain), which
            have been architecturally ready and blocked on hardware access since Stage 13.
          </li>
          <li>
            <strong>Measurement guidance</strong> — experience with Nordic Power Profiler Kit II
            energy-measurement methodology, or with INT8 quantization-aware export for Cortex-M4F.
          </li>
        </ul>
        <p style={{ fontSize: "0.9rem" }}>
          Reach out via the <a href={`https://github.com/${project.repository}`} target="_blank" rel="noreferrer">GitHub repository</a>{" "}
          or the <Link href="/professor-review">professor/reviewer page</Link>.
        </p>
      </section>

      {/* ---------- Evidence and status ---------- */}
      <section id="evidence" aria-labelledby="threemt-evidence-title">
        <h2 id="threemt-evidence-title">Evidence and Status</h2>
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
            <div className="k">TinyML export / quantization</div>
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
    </div>
  );
}
