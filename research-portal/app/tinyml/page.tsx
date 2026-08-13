import type { Metadata } from "next";
import { PlannedPage } from "@/components/PlannedPage";

export const metadata: Metadata = { title: "TinyML" };

export default function TinyMlPage() {
  return (
    <PlannedPage
      title="TinyML deployment"
      status="NOT_EXECUTED"
      summary="Target hardware: Nordic nRF52840, ARM Cortex-M4F. No quantization, embedded export, or on-device measurement has occurred — model size shown on /results is host-serialized (joblib), not an embedded footprint."
      plan={[
        "Quantization of an evidence-selected model (stage 13)",
        "Embedded export via a defined compiler/toolchain (stage 14)",
        "Firmware integration and tensor-arena sizing on nRF52840 (stage 15)",
        "Flash/SRAM measurement on the physical device (stage 16)",
        "See /hardware for the physical measurement protocol and /results for current host-side model-complexity evidence",
      ]}
    />
  );
}
