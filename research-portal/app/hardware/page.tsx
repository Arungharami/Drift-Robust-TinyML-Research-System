import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { HardwareConnectionDiagram } from "@/components/HardwareConnectionDiagram";
import { HardwareStatus } from "@/components/HardwareStatus";
import { HardwareWorkflow } from "@/components/HardwareWorkflow";
import { getEmbedded, getProjectStatus } from "@/lib/evidence";

export const metadata: Metadata = { title: "Hardware" };
const DK_URL = "https://www.nordicsemi.com/Products/Development-hardware/nrf52840-dk";
const PPK2_URL = "https://www.nordicsemi.com/Products/Development-hardware/Power-Profiler-Kit-2";

export default function HardwarePage() {
  const embedded = getEmbedded();
  const project = getProjectStatus();
  const gate = embedded.stage15_hardware_gate;
  const serial = String(gate?.serial_ports_json ?? "").includes("COM1") ? "Legacy COM1 only" : "No compatible interface detected";

  return <div className="container hardware-page">
    <section className="hardware-hero" aria-labelledby="hardware-title">
      <div><div className="section-label">Stage 15 physical prerequisite</div><EvidenceBadge status={String(gate?.scientific_execution_status ?? project.hardware_state)} /><h1 id="hardware-title">Hardware execution blocked</h1><p className="lede">No compatible nRF52840 board or supported debug probe was detected. The prerequisite check was completed, but physical deployment and measurement cannot proceed until the target hardware is connected and identified.</p></div>
      <div className="hardware-facts" aria-label="Verified hardware facts">
        <div><span>Board identity</span><code>{String(gate?.board_identity ?? "NOT_RECORDED")}</code></div>
        <div><span>Detected serial interface</span><strong>{serial}</strong></div>
        <div><span>Zephyr target</span><code>{String(gate?.zephyr_board_target ?? "NOT_SELECTED")}</code></div>
        <div><span>Physical execution</span><code>{String(gate?.physical_golden ?? "NOT_EXECUTED")}</code></div>
        <div><span>Memory</span><code>{String(gate?.linked_rom_footprint ?? "NOT_MEASURED")}</code></div>
        <div><span>Latency</span><code>{String(gate?.mcu_latency ?? "NOT_MEASURED")}</code></div>
        <div><span>Energy</span><code>{String(gate?.energy ?? "NOT_MEASURED")}</code></div>
      </div>
    </section>

    <section aria-labelledby="planned-system-title"><div className="section-heading"><div><div className="section-label">Proposed laboratory equipment</div><h2 id="planned-system-title">Planned hardware system</h2></div><p>Official product photographs identify the intended equipment only. They are not evidence that the laboratory owns or has connected either device.</p></div>
      <div className="device-gallery">
        <article className="device-card"><figure><Image src="https://www.nordicsemi.cn/assets/images/nrf52840dk.png" width={1600} height={739} alt="Official Nordic product photograph of the green nRF52840 development kit"/><figcaption>nRF52840 DK product photograph. © Nordic Semiconductor; externally hosted and not covered by this repository&apos;s MIT license.</figcaption></figure><div className="device-content"><EvidenceBadge status="BLOCKED_HARDWARE"/><h3>Nordic nRF52840 DK</h3><p>Target embedded inference platform with a 64 MHz Arm Cortex-M4F. The intended board identity has not been physically confirmed and no compatible device was detected.</p><a href={DK_URL} target="_blank" rel="noreferrer">Official Nordic product page</a></div></article>
        <article className="device-card"><figure><Image src="https://www.nordicsemi.cn/assets/images/ppk2.png" width={1600} height={927} alt="Official Nordic product photograph of the Power Profiler Kit II measurement board"/><figcaption>Power Profiler Kit II product photograph. © Nordic Semiconductor; externally hosted and not covered by this repository&apos;s MIT license.</figcaption></figure><div className="device-content"><EvidenceBadge status="NOT_EXECUTED"/><h3>Nordic Power Profiler Kit II</h3><p>Planned physical current and energy instrument supporting source-meter and ampere-meter configurations. Raw traces would support separate inference and explanation energy integration; no physical PPK2 trace exists.</p><a href={PPK2_URL} target="_blank" rel="noreferrer">Official Nordic product page</a></div></article>
      </div>
    </section>

    <section aria-labelledby="connection-title"><div className="section-label">Technical topology</div><h2 id="connection-title">Planned connection</h2><HardwareConnectionDiagram /></section>
    <section aria-labelledby="workflow-title"><div className="section-label">Evidence sequence</div><h2 id="workflow-title">Measurement workflow</h2><HardwareWorkflow /></section>
    <section aria-labelledby="measurements-title"><div className="section-label">Current evidence boundary</div><h2 id="measurements-title">Measurements</h2><p>No zeros, estimates, simulated values, or host-to-MCU conversions are presented.</p><HardwareStatus /></section>

    <section className="related-evidence" aria-labelledby="evidence-title"><div><div className="section-label">Traceability</div><h2 id="evidence-title">Evidence and related pages</h2></div><div className="related-grid">
      <div className="card"><h3>Stage 15 evidence</h3><ul><li><ArtifactLink path="docs/embedded/EXP_MCU_C1_FP32_PORT_001.md" label="Stage 15 report"/></li><li><ArtifactLink path="results/embedded/stage15_hardware_detection.json" label="Hardware detection JSON"/></li><li><ArtifactLink path="results/embedded/stage15_toolchain_inventory.csv" label="Toolchain inventory"/></li><li><ArtifactLink path="results/embedded/stage15_manifest.csv" label="Evidence manifest"/></li></ul></div>
      <nav className="card" aria-label="Related research pages"><h3>Related pages</h3><ul><li><Link href="/tinyml">TinyML deployment plan</Link></li><li><Link href="/methodology">Methodology</Link></li><li><Link href="/reproducibility">Reproducibility policy</Link></li><li><Link href="/professor-review">Advisor questions</Link></li><li><a href="https://github.com/Arungharami/Drift-Robust-TinyML-Research-System" target="_blank" rel="noreferrer">GitHub repository</a></li></ul></nav>
    </div></section>
  </div>;
}
