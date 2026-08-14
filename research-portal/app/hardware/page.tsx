import type { Metadata } from "next";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { HardwareStatus } from "@/components/HardwareStatus";

export const metadata: Metadata = { title: "Hardware" };

export default function HardwarePage() {
  return (
    <div className="container">
      <div className="section-label">Physical hardware</div>
      <div style={{ marginBottom: "0.75rem" }}>
        <EvidenceBadge status="NOT_EXECUTED" />
      </div>
      <h1>Hardware measurement</h1>
      <p className="lede">
        Target hardware: Nordic nRF52840 (ARM Cortex-M4F). Energy instrumentation: Nordic Power
        Profiler Kit II (PPK2). Colab and any other cloud compute used elsewhere on this site is{" "}
        <strong>not</strong> embedded hardware and never substitutes for the measurements below.
      </p>

      <h2>Measurement status</h2>
      <HardwareStatus />

      <h2>Planned PPK2 protocol</h2>
      <p style={{ maxWidth: "68ch" }}>
        Once hardware access is confirmed, the measurement protocol will record: board
        configuration, supply voltage, sampling setup, idle baseline, inference trigger,
        repetitions, integration window, and raw trace storage under{" "}
        <code>hardware/ppk2_logs/</code>. Energy will be computed via the physical relationship{" "}
        <code>E = ∫ V(t) I(t) dt</code>, integrated over the inference (and separately,
        explanation) window. No PPK2 log exists yet — this directory is not yet created.
      </p>

      <h2>Why this matters</h2>
      <p style={{ maxWidth: "68ch" }}>
        A software timer or host-side profiler is not a substitute for physical measurement.
        This project deliberately refuses to report MCU latency or energy numbers until they are
        measured on real hardware — see the <a href="/reproducibility">evidence policy</a>.
      </p>
    </div>
  );
}
