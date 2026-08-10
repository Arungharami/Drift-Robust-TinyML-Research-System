import {
  architecture,
  datasetFacts,
  equations,
  evidenceRules,
  huggingFacePlan,
  noveltyMap,
  pipeline,
  professorWorkflow,
  project,
  references,
  telemetryExample,
  type EvidenceStatus,
} from "@/lib/research";

function StatusPill({ status }: { status: EvidenceStatus }) {
  const className = `status status-${status.toLowerCase().replace("_", "-")}`;
  return <span className={className}>{status.replace("_", " ")}</span>;
}

function SectionHeading({ eyebrow, title, copy }: { eyebrow: string; title: string; copy?: string }) {
  return (
    <div className="section-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      {copy ? <p className="section-copy">{copy}</p> : null}
    </div>
  );
}

export default function Home() {
  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Research portal home">
          DRX-TinyML <span>Research System</span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#method">Method</a>
          <a href="#evidence">Evidence</a>
          <a href="#hardware">Hardware</a>
          <a href="#literature">Literature</a>
          <a href="#advisor">Advisor Review</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="hero-grid">
          <div>
            <p className="eyebrow">2026 · Explainable Edge AI Research</p>
            <h1>{project.title}</h1>
            <p className="hero-copy">{project.subtitle}</p>
            <div className="hero-actions">
              <a className="button button-primary" href="#method">
                Explore methodology
              </a>
              <a className="button" href={project.repository} target="_blank" rel="noreferrer">
                GitHub repository ↗
              </a>
              <a className="button" href={project.huggingFaceProfile} target="_blank" rel="noreferrer">
                Hugging Face ↗
              </a>
            </div>
          </div>

          <aside className="hero-panel" aria-label="Project status">
            <div className="signal-line">
              <span className="signal-dot" />
              Evidence-first research portal
            </div>
            <dl>
              <div>
                <dt>Researcher</dt>
                <dd>{project.author}</dd>
              </div>
              <div>
                <dt>Primary benchmark</dt>
                <dd>UCI Gas Sensor Array Drift</dd>
              </div>
              <div>
                <dt>Target edge platform</dt>
                <dd>nRF52840 / Cortex-M4F</dd>
              </div>
              <div>
                <dt>Physical energy</dt>
                <dd>Nordic PPK2</dd>
              </div>
              <div>
                <dt>Result policy</dt>
                <dd>No unexecuted numbers</dd>
              </div>
            </dl>
          </aside>
        </div>

        <div className="trust-strip">
          <span>Chronological evaluation</span>
          <span>Resource-aware XAI</span>
          <span>Reproducible artifacts</span>
          <span>Physical MCU evidence</span>
          <span>Publication-safe claims</span>
        </div>
      </section>

      <section className="section" id="evidence">
        <SectionHeading
          eyebrow="Research integrity"
          title="The evidence gate is part of the product"
          copy="The website is designed as an auditable research interface. Planned work and executed evidence are intentionally displayed differently."
        />
        <div className="evidence-layout">
          <ol className="rule-list">
            {evidenceRules.map((rule) => (
              <li key={rule}>{rule}</li>
            ))}
          </ol>
          <div className="evidence-card">
            <p className="eyebrow">Current public result state</p>
            <div className="big-status">NO FINAL RESULTS PUBLISHED</div>
            <p>
              This is deliberate. Metrics become public only after the frozen experiment produces a saved artifact with traceable provenance.
            </p>
          </div>
        </div>
      </section>

      <section className="section section-muted">
        <SectionHeading
          eyebrow="Benchmark"
          title="What the model must survive"
          copy="The UCI benchmark records a multi-year sensor system whose data distribution changes over time, making random pooled evaluation an incomplete picture of deployment risk."
        />
        <div className="fact-grid">
          {datasetFacts.map((fact) => (
            <article className="fact-card" key={fact.label}>
              <p>{fact.label}</p>
              <strong>{fact.value}</strong>
            </article>
          ))}
        </div>
        <p className="source-note">
          Canonical source: <a href={project.uciDataset} target="_blank" rel="noreferrer">UCI Machine Learning Repository ↗</a>
        </p>
      </section>

      <section className="section" id="method">
        <SectionHeading
          eyebrow="End-to-end method"
          title="From benchmark file to measured edge evidence"
          copy="Each stage has an explicit status. This becomes the semester execution board and the structure of the final paper."
        />
        <div className="pipeline">
          {pipeline.map((step) => (
            <article className="pipeline-card" key={step.id}>
              <div className="pipeline-index">{step.id}</div>
              <div>
                <div className="card-title-row">
                  <h3>{step.title}</h3>
                  <StatusPill status={step.status} />
                </div>
                <p>{step.detail}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="section section-muted">
        <SectionHeading
          eyebrow="Mathematical contract"
          title="Equations are tied to measurements"
          copy="These definitions explain what will be computed; they are not presented as experimental findings."
        />
        <div className="equation-grid">
          {equations.map((item) => (
            <article className="equation-card" key={item.name}>
              <h3>{item.name}</h3>
              <code>{item.equation}</code>
              <p>{item.note}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section" id="hardware">
        <SectionHeading
          eyebrow="System architecture"
          title="Research reproducibility and real-world deployment are connected—but not confused"
          copy="Hugging Face is the public ML artifact layer; the target MCU is the deployment layer; Vercel is the research communication layer."
        />
        <div className="architecture-grid">
          {architecture.map((item) => (
            <article className="architecture-card" key={item.title}>
              <p className="eyebrow">{item.title}</p>
              <p className="flow">{item.flow}</p>
            </article>
          ))}
        </div>

        <div className="two-column spacer-top">
          <article className="panel">
            <p className="eyebrow">Real-world telemetry contract</p>
            <h3>What the physical device will send</h3>
            <p>
              The schema below is intentionally nullable. Latency and energy are populated only after the corresponding hardware measurement exists.
            </p>
            <pre><code>{telemetryExample}</code></pre>
          </article>
          <article className="panel">
            <p className="eyebrow">Hardware evidence bundle</p>
            <h3>Minimum reproducible artifacts</h3>
            <ul className="clean-list">
              <li>firmware commit + compiler/toolchain version</li>
              <li>linker map for Flash/SRAM accounting</li>
              <li>raw latency log with repetition count</li>
              <li>PPK2 current trace + voltage configuration</li>
              <li>model/export checksum</li>
              <li>explanation implementation/version</li>
            </ul>
          </article>
        </div>
      </section>

      <section className="section section-muted">
        <SectionHeading
          eyebrow="Hugging Face integration"
          title="Use the Hub as an artifact registry, not a substitute for evidence"
          copy="Hugging Face repositories are version-controlled ML repositories, while Spaces can host interactive demos. The portal keeps the authoritative measurement lineage in GitHub and links outward to validated artifacts."
        />
        <div className="three-column">
          {huggingFacePlan.map((item) => (
            <article className="panel" key={item.title}>
              <div className="card-title-row">
                <h3>{item.title}</h3>
                <StatusPill status={item.status} />
              </div>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section" id="literature">
        <SectionHeading
          eyebrow="Novelty control"
          title="A literature map that can survive professor review"
          copy="The novelty claim is treated as a hypothesis to defend against recent drift-adaptation and TinyML-XAI work."
        />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Prior work</th>
                <th>What it already establishes</th>
                <th>Remaining question for this project</th>
              </tr>
            </thead>
            <tbody>
              {noveltyMap.map((row) => (
                <tr key={row.prior}>
                  <td><strong>{row.prior}</strong></td>
                  <td>{row.contribution}</td>
                  <td>{row.gapForThisProject}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="novelty-callout">
          <p className="eyebrow">Working novelty thesis</p>
          <p>
            The defensible contribution is not merely “TinyML + XAI.” It is the combined evidence chain: chronological electronic-nose drift evaluation, lightweight explanation fidelity/stability, deployable model/export artifacts, and physically measured MCU memory, latency, and energy—including explanation cost.
          </p>
        </div>
      </section>

      <section className="section section-muted" id="advisor">
        <SectionHeading
          eyebrow="Professor involvement"
          title="Turn the website into a research meeting instrument"
          copy="The portal should make it easy for a professor to challenge assumptions before expensive experiments and to inspect evidence after they run."
        />
        <div className="advisor-layout">
          <ol className="rule-list advisor-list">
            {professorWorkflow.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
          <aside className="panel advisor-card">
            <p className="eyebrow">Recommended professor view</p>
            <h3>Review these five things first</h3>
            <ul className="clean-list">
              <li>research question and contribution boundary</li>
              <li>chronological split and leakage controls</li>
              <li>baseline fairness and ablations</li>
              <li>hardware measurement protocol</li>
              <li>novelty threats and claim wording</li>
            </ul>
          </aside>
        </div>
      </section>

      <section className="section">
        <SectionHeading eyebrow="Paper pathway" title="The final manuscript is the last layer, not the first" />
        <div className="paper-path">
          <span>Protocol</span><b>→</b><span>Executed artifacts</span><b>→</b><span>Verified tables/figures</span><b>→</b><span>Discussion</span><b>→</b><span>Final abstract</span><b>→</b><span>Paper PDF</span>
        </div>
        <p className="section-copy compact-copy">
          Once the manuscript PDF is validated and committed under <code>paper/final/</code>, this portal can expose a direct paper link and citation block.
        </p>
      </section>

      <section className="section section-muted">
        <SectionHeading eyebrow="References" title="Core sources currently shaping the protocol" />
        <div className="reference-list">
          {references.map((reference, index) => (
            <a href={reference.url} target="_blank" rel="noreferrer" key={reference.url}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <strong>{reference.label}</strong>
                <small>{reference.year}</small>
              </div>
              <b>↗</b>
            </a>
          ))}
        </div>
      </section>

      <footer>
        <div>
          <strong>Drift-Robust Explainable TinyML</strong>
          <p>Evidence-first research system · {project.year}</p>
        </div>
        <div className="footer-links">
          <a href={project.repository} target="_blank" rel="noreferrer">GitHub</a>
          <a href={project.huggingFaceProfile} target="_blank" rel="noreferrer">Hugging Face</a>
          <a href={project.uciDataset} target="_blank" rel="noreferrer">UCI benchmark</a>
        </div>
      </footer>
    </main>
  );
}
