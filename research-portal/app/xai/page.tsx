import type { Metadata } from "next";
import { PlannedPage } from "@/components/PlannedPage";

export const metadata: Metadata = { title: "XAI" };

export default function XaiPage() {
  return (
    <PlannedPage
      title="Resource-aware explainability"
      status="NOT_EXECUTED"
      summary="Explanation strategies suitable for constrained inference — evaluated for cost and fidelity, not assumed reliable. Heavy SHAP/LIME execution on the MCU is not implied unless actually implemented and measured."
      plan={[
        "Off-device explanation candidates: model coefficients (linear models), permutation importance, top-k sparse attribution",
        "Explicit distinction between off-device, on-device, proxy, and evaluation-only explanation strategies once implemented",
        "Explanation fidelity: perturbation-based agreement against a reference explainer (see /paper for equation once written)",
        "Explanation stability: rank correlation / top-k overlap of attributions across chronologically drifting batches",
        "Explanation latency, first measured host-side, then on nRF52840 once stage 15 is complete",
      ]}
    />
  );
}
