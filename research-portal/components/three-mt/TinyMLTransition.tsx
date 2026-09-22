import { EvidenceBadge } from "@/components/EvidenceBadge";
import Link from "next/link";
import type { EmbeddedEvidence } from "@/lib/types";

/** Section 11 — the engineering constraint, with every stage labeled by its real status. */
export function TinyMLTransition({ embedded }: { embedded: EmbeddedEvidence }) {
  const flashBytes = embedded.target.physical_flash_bytes;
  const sramBytes = embedded.target.physical_sram_bytes;

  return (
    <section className="threemt-tinyml" aria-labelledby="threemt-tinyml-title">
      <h2 id="threemt-tinyml-title">From Workstation to Microcontroller</h2>

      <div className="threemt-tinyml-transition">
        <div className="threemt-tinyml-stage threemt-tinyml-stage-workstation">
          <span className="threemt-tinyml-stage-icon" aria-hidden="true" />
          <span className="k">Research workstation</span>
          <span className="v">Training, evaluation, explanation — full precision</span>
        </div>
        <span className="threemt-tinyml-transition-arrow" aria-hidden="true">→</span>
        <div className="threemt-tinyml-stage threemt-tinyml-stage-chip">
          <span className="threemt-tinyml-stage-icon threemt-tinyml-stage-icon-small" aria-hidden="true" />
          <span className="k">Embedded export</span>
          <span className="v">
            <EvidenceBadge status="HOST_EXECUTED" />
          </span>
        </div>
        <span className="threemt-tinyml-transition-arrow" aria-hidden="true">→</span>
        <div className="threemt-tinyml-stage threemt-tinyml-stage-target">
          <span className="threemt-tinyml-stage-icon threemt-tinyml-stage-icon-target" aria-hidden="true" />
          <span className="k">Target: nRF52840 / Cortex-M4F</span>
          <span className="v">
            <EvidenceBadge status="BLOCKED_HARDWARE" />
          </span>
        </div>
      </div>

      <p className="threemt-tinyml-thesis">Less memory. Less compute. Less energy.</p>

      <div className="threemt-tinyml-split">
        <div className="threemt-tinyml-split-col">
          <h3 className="threemt-tinyml-split-title">What we have measured</h3>
          <div className="kv-grid">
            <div className="kv-item">
              <div className="k">Host FP32 numerical equivalence</div>
              <div className="v"><EvidenceBadge status="HOST_EXECUTED" /></div>
            </div>
            <div className="kv-item">
              <div className="k">FLASH TARGET (nRF52840 physical limit)</div>
              <div className="v">{flashBytes.toLocaleString()} bytes</div>
            </div>
            <div className="kv-item">
              <div className="k">SRAM TARGET (nRF52840 physical limit)</div>
              <div className="v">{sramBytes.toLocaleString()} bytes</div>
            </div>
          </div>
        </div>
        <div className="threemt-tinyml-split-col">
          <h3 className="threemt-tinyml-split-title">What still requires hardware</h3>
          <div className="kv-grid">
            <div className="kv-item">
              <div className="k">INT8 quantization</div>
              <div className="v"><EvidenceBadge status="NOT_EXECUTED" /></div>
            </div>
            <div className="kv-item">
              <div className="k">FLASH / SRAM usage (compiled, on real hardware)</div>
              <div className="v"><EvidenceBadge status="NOT_MEASURED" /></div>
            </div>
            <div className="kv-item">
              <div className="k">On-device latency / PPK2 energy</div>
              <div className="v"><EvidenceBadge status="NOT_MEASURED" /></div>
            </div>
          </div>
        </div>
      </div>
      <p style={{ fontSize: "0.85rem", color: "var(--text-faint)" }}>
        A weights-only INT8 quantization protocol is frozen (not executed) and a fused-preprocessing
        candidate passed host-only numerical equivalence — see <Link href="/tinyml">/tinyml</Link> for
        the full gate-by-gate record.
      </p>
    </section>
  );
}
