"use client";

import { useEffect, useRef, useState } from "react";

type Stage = { id: string; name: string; status: string };
const slides = [
  { title: "Can we trust a tiny electronic nose as its sensors change?", tag: "Final class presentation", points: ["Drift-Robust Explainable TinyML for Electronic-Nose Sensing", "Chronological evaluation · explanation quality · reproducible deployment", "Arun Kumar Gharami"], notes: "My research asks whether a small sensing system can remain useful when its input changes over time. I will explain the evidence collected so far, the unsuccessful experiments, and the work still needed before deployment.", link: "/research" },
  { title: "The problem starts after training", tag: "Why this matters", points: ["Sensor responses can change over time, so yesterday’s model may perform differently tomorrow.", "A strong random-split score does not establish future-batch performance.", "An explanation must also be evaluated; a plausible explanation is not evidence of reliability."], notes: "Think of calibrating a measuring instrument once and assuming it stays accurate forever. This motivates chronological testing. Industrial sensing and environmental monitoring are potential applications, not deployments demonstrated by this project.", link: "/dataset" },
  { title: "My approach: evaluate trust as a chain of evidence", tag: "Research concept", points: ["Prediction: measure performance on future chronological batches.", "Explanation: evaluate fidelity, stability, and host computational cost separately.", "Deployment: verify numerical equivalence, then obtain physical resource measurements."], notes: "I designed the workflow around separate questions. Accuracy, explanation quality, and physical deployment each need their own evidence. Passing one gate cannot substitute for another. The contribution is being investigated; this is not a claim that the full research question has been solved.", link: "/system-map" },
  { title: "Time determines the train–test boundary", tag: "Methodology", points: ["FIXED_ORIGIN: train preprocessing and models on Batch 1; evaluate Batches 2–10 without retraining.", "EXPANDING_WINDOW: retrain using only batches earlier than the test batch.", "IID_DIAGNOSTIC: random splitting is a diagnostic comparison, not the primary result.", "Keep preprocessing fitted within training data to avoid future-data leakage."], notes: "The two chronological protocols answer different questions: what happens without adaptation, and what changes when historical data becomes available. The comparison uses frozen protocols rather than tuning against future batches.", link: "/methodology" },
  { title: "Future-batch performance falls", tag: "Recorded baseline evidence", points: ["The table reads the portal’s generated evidence through its central loader.", "All evaluated models have lower Batch 10 accuracy than Batch 2.", "This endpoint comparison does not imply a monotonic decrease between every batch."], notes: "Show the endpoint comparison and refer the audience to the full per-batch results. These are repository-recorded measurements, not new experiments run for this presentation. A percentage-point drop is a subtraction of percentages, not a relative percent decrease.", link: "/results" },
  { title: "Adaptation helps, but does not finish the problem", tag: "Interpretation", points: ["The claim matrix supports higher mean accuracy under expanding-window retraining for all evaluated models.", "The IID diagnostic exceeds mean fixed-origin future accuracy for all evaluated models.", "A consistent statistically supported global drift–performance association is not established."], notes: "These conclusions are scoped to the evaluated dataset, models, and protocols. Retraining requires historical labeled data. Performance differences alone do not establish a causal explanation for every failure.", link: "/failure-analysis" },
  { title: "Explanations need their own evaluation", tag: "Explainable AI", points: ["Generate model-compatible global importance and local explanations.", "Fidelity asks whether important features affect predictions as expected.", "Stability asks how explanations change under the defined comparisons.", "Several universal fidelity and stability claims are unsupported; host cost results are method-dependent."], notes: "An executed experiment is not the same as a supported hypothesis. The XAI experiments ran, but their negative and unresolved findings remain part of the result. Host explanation cost cannot be presented as MCU energy.", link: "/xai" },
  { title: "A failed export led to a different architecture", tag: "Embedded pathway", points: ["Standalone FP32 export and explicit preprocessing repair failed frozen criteria.", "Later C1 fused FP32 inference and local-XAI equivalence passed separate host protocols.", "The weights-only INT8 protocol is frozen; its experiment is not executed.", "Host numerical equivalence is a prerequisite, not a physical deployment result."], notes: "The original failed results remain visible. The fused representation was evaluated with a separately frozen protocol, so its success does not erase the earlier failure. The next quantization step also needs its own execution and evidence.", link: "/embedded" },
  { title: "What is complete—and what is blocked", tag: "Live pipeline registry", points: ["The stage list below comes from the portal evidence snapshot.", "Physical nRF52840 deployment, Flash/SRAM, latency, and PPK2 energy remain blocked.", "The digital twin explains the proposed system; it is not a live hardware measurement."], notes: "Be explicit that the final class presentation reports current research progress. It does not declare a finished hardware study. Show the pipeline page if the professor asks to inspect artifact paths and dependencies.", link: "/pipeline" },
  { title: "Demonstrate the evidence, then the concept", tag: "Live project walkthrough", points: ["Results: inspect chronological baseline comparisons.", "XAI: inspect explanation evaluation and limitations.", "Embedded / hardware: show host equivalence and remaining gates.", "Digital twin: explain the proposed device and data flow."], notes: "Use the buttons below to open the main project sections in a separate tab. Start with the measured results. Introduce the 3D device as a conceptual aid and return to the presentation afterward.", link: "/digital-twin/device" },
  { title: "Next steps require separate success criteria", tag: "Research plan", points: ["Execute the frozen INT8 protocol and report pass or fail without relaxing criteria.", "Resolve hardware prerequisites before compilation, flashing, and physical verification.", "Measure memory, inference latency, and power traces on actual hardware.", "Evaluate generalization on additional datasets under versioned protocols."], notes: "Each next step should produce a saved artifact with dataset, configuration, and source identity. Broader benchmarking and validation are planned improvements, not results already achieved.", link: "/reproducibility" },
  { title: "Questions I expect from the class", tag: "Discussion preparation", points: ["Why chronological splits? They test future-batch behavior without mixing future observations into training.", "Does XAI solve drift? No; it supplies an additional object of evaluation.", "Why lightweight models? Their deployment and explanation costs can be studied explicitly.", "Is this running on hardware? No; physical measurement remains blocked.", "What is the contribution? Investigating a reproducible chain linking drift, explanations, and embedded equivalence; novelty needs literature comparison."], notes: "Answer questions within the evidence scope. If asked for a missing hardware number, say it has not been measured. Ask for feedback on the evaluation design, suitable additional benchmarks, and the most valuable next experiment.", link: "/references" },
  { title: "Trust requires evidence at every stage", tag: "Closing", points: ["Chronological evaluation reveals a deployment-relevant performance gap.", "Explanation quality must be tested rather than assumed.", "Software equivalence and physical feasibility are separate claims.", "Class feedback will guide the next version of the study."], notes: "My main takeaway is that a trustworthy tiny sensing system needs a traceable argument at every stage. The project already records useful results and failures, while the physical deployment question remains open. Thank you; I welcome questions.", link: "/professor-review" },
];

function percentage(value: string | undefined) {
  if (!value || !Number.isFinite(Number(value))) return "NOT EXECUTED";
  return (Number(value) * 100).toFixed(1) + "%";
}

export function ClassPresentation({ baselines, stages, commit }: { baselines: Record<string, string>[]; stages: Stage[]; commit: string }) {
  const [index, setIndex] = useState(0);
  const [notes, setNotes] = useState(false);
  const [all, setAll] = useState(false);
  const [message, setMessage] = useState("");
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const keydown = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLElement && /INPUT|TEXTAREA|SELECT|BUTTON|A/.test(event.target.tagName)) return;
      if (event.key === "ArrowRight" || event.key === "PageDown") { event.preventDefault(); setIndex(v => Math.min(v + 1, slides.length - 1)); }
      if (event.key === "ArrowLeft" || event.key === "PageUp") { event.preventDefault(); setIndex(v => Math.max(v - 1, 0)); }
      if (event.key.toLowerCase() === "n") setNotes(v => !v);
    };
    window.addEventListener("keydown", keydown);
    return () => window.removeEventListener("keydown", keydown);
  }, []);
  async function fullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (root.current?.requestFullscreen) await root.current.requestFullscreen();
      else setMessage("Fullscreen is unavailable in this browser. Use browser presentation or zoom controls.");
    } catch { setMessage("Fullscreen is unavailable. The slides remain usable in this window."); }
  }
  return <div className="class-deck" ref={root}>
    <div className="deck-toolbar">
      <a href="/">Research portal</a>
      <button onClick={() => setNotes(v => !v)} aria-pressed={notes}>Speaker notes</button>
      <button onClick={() => setAll(v => !v)} aria-pressed={all}>All slides</button>
      <button onClick={fullscreen}>Fullscreen</button>
      <button onClick={() => window.print()}>Print / Save PDF</button>
    </div>
    <p className="deck-help">← / → change slide · N toggles notes · Suggested delivery: 12–15 minutes plus discussion</p>
    {message ? <p role="status">{message}</p> : null}
    {slides.map((slide, position) => <section key={slide.title} className={"deck-slide " + (!all && index !== position ? "deck-hidden" : "")} aria-label={"Slide " + (position + 1)}>
      <div className="deck-tag">{slide.tag} <span>{String(position + 1).padStart(2, "0")} / {slides.length}</span></div>
      <h1>{slide.title}</h1>
      <ul>{slide.points.map(point => <li key={point}>{point}</li>)}</ul>
      {position === 4 ? <div className="deck-table"><table><caption>FIXED_ORIGIN accuracy: training on Batch 1</caption><thead><tr><th>Model</th><th>Batch 2</th><th>Batch 10</th><th>Drop (pp)</th></tr></thead><tbody>{baselines.map(row => <tr key={row.model}><td>{row.model_name || row.model}</td><td>{percentage(row.b2_accuracy)}</td><td>{percentage(row.b10_accuracy)}</td><td>{Number.isFinite(Number(row.b2_to_b10_accuracy_drop_pp)) && row.b2_to_b10_accuracy_drop_pp ? Number(row.b2_to_b10_accuracy_drop_pp).toFixed(1) : "NOT EXECUTED"}</td></tr>)}</tbody></table></div> : null}
      {position === 8 ? <div className="deck-stages">{stages.filter(stage => /^(09|10|11|12|14|14R|14F-EXEC|14F-XAI|14Q-GATE|15|16|17|18)$/.test(stage.id)).map(stage => <div key={stage.id}><span>{stage.id} · {stage.name}</span><strong>{stage.status}</strong></div>)}</div> : null}
      {position === 9 ? <div className="deck-links">{["results", "xai", "embedded", "hardware", "digital-twin/device"].map(path => <a href={"/" + path} key={path} target="_blank" rel="noreferrer">{path}</a>)}</div> : null}
      <a className="deck-source" href={slide.link} target="_blank" rel="noreferrer">Open supporting project section ↗</a>
      <aside className={"deck-notes " + (!notes ? "deck-notes-hidden" : "")}><strong>Speaker notes</strong><p>{slide.notes}</p></aside>
    </section>)}
    <div className="deck-controls"><button disabled={index === 0 || all} onClick={() => setIndex(v => v - 1)}>← Previous</button><select aria-label="Select slide" value={index} onChange={event => setIndex(Number(event.target.value))}>{slides.map((slide, i) => <option key={slide.title} value={i}>{i + 1}. {slide.title}</option>)}</select><button disabled={index === slides.length - 1 || all} onClick={() => setIndex(v => v + 1)}>Next →</button></div>
    <p className="deck-provenance">Pipeline-recorded evidence snapshot: {commit}. Final class presentation; hardware research is ongoing. Scientific claims are scoped to the saved artifacts.</p>
    <style jsx>{`
      .class-deck{max-width:1280px;margin:0 auto;padding:24px;background:#07182c;color:#f3f6fb;min-height:85vh;overflow:auto}
      .class-deck:fullscreen{max-width:none;padding:3vh 5vw}
      .deck-toolbar,.deck-controls,.deck-links{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
      button,select{background:#16304d;color:#fff;border:1px solid #587590;border-radius:8px;padding:10px 16px;font:inherit}
      button{cursor:pointer}button:disabled{opacity:.4;cursor:default}
      button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid #69d7de;outline-offset:4px}
      a{color:#84e0e6}.deck-help,.deck-provenance{color:#bccbdd;font-size:.85rem}
      .deck-slide{padding:clamp(24px,4vw,60px);margin:20px 0;border:1px solid #37516b;border-radius:18px;background:linear-gradient(135deg,#102740,#081b30);min-height:58vh}
      .deck-hidden,.deck-notes-hidden{display:none}
      .deck-tag{text-transform:uppercase;letter-spacing:.14em;color:#7adce0;font-size:.85rem;display:flex;justify-content:space-between;gap:16px}
      h1{color:#fff;font-size:clamp(1.8rem,3.1vw,3.1rem);line-height:1.15;margin:24px 0;max-width:1000px}
      li{font-size:clamp(1.05rem,1.6vw,1.4rem);line-height:1.5;margin:14px 0}
      .deck-source{display:inline-block;margin-top:18px}.deck-notes{margin-top:22px;padding:18px;background:#203a54;border-left:4px solid #7adce0}
      .deck-notes p{color:#e0eaf4;margin-bottom:0}
      .deck-table{overflow-x:auto}table{width:100%;margin-top:24px;border-collapse:collapse;color:#fff}caption{text-align:left;color:#bccbdd}
      th,td{padding:12px;border-bottom:1px solid #3b5672;text-align:left}
      .deck-stages{display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:.85rem;margin-top:24px}
      .deck-stages div{display:flex;justify-content:space-between;gap:12px;padding:10px;background:#142e48}.deck-stages strong{color:#9ce5e5}
      .deck-links a{padding:12px;border:1px solid #587590;border-radius:8px}
      .deck-controls select{flex:1;min-width:140px;max-width:100%}
      @media(max-width:650px){.class-deck{padding:12px}.deck-stages{grid-template-columns:1fr}.deck-slide{padding:24px 18px}.deck-controls{gap:8px}}
      @media print{.class-deck{background:white;color:#111;max-width:none;padding:0}.deck-toolbar,.deck-controls,.deck-help,.deck-provenance{display:none}.deck-slide,.deck-hidden{display:block;background:white;color:#111;border:0;break-after:page;padding:20px;min-height:0}h1,table,.deck-tag,a{color:#111}.deck-notes-hidden{display:none}.deck-notes,.deck-stages div{background:#eee;color:#111}.deck-stages strong{color:#111}}
    `}</style>
  </div>;
}
