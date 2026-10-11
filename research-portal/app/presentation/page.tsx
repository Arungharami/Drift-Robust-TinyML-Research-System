import { getBaselines, getPipeline, getProjectStatus } from "@/lib/evidence";
import { ClassPresentation } from "@/components/ClassPresentation";

export const metadata = { title: "Final Class Presentation | Drift-Robust TinyML" };

export default function PresentationPage() {
  return <ClassPresentation baselines={getBaselines().fixed_origin_summary} stages={getPipeline().map(({ id, name, status }) => ({ id, name, status }))} commit={getProjectStatus().git_commit} />;
}
