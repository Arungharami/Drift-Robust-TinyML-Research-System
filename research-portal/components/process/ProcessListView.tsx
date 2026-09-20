import { EvidenceBadge } from "@/components/EvidenceBadge";
import type { ProcessPhase } from "@/lib/process-phases";

/** Accessible, always-available alternative to the 3D scene: real buttons, fully keyboard
 * operable, identical onSelect contract so switching modes never loses selection state. */
export function ProcessListView({
  phases,
  selectedPhaseId,
  onSelect,
}: {
  phases: ProcessPhase[];
  selectedPhaseId: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <ol className="process-list" aria-label="Research process phases, in pipeline order">
      {phases.map((phase, i) => (
        <li key={phase.id}>
          <button
            type="button"
            className={`process-list-item${phase.id === selectedPhaseId ? " process-list-item-active" : ""}`}
            aria-current={phase.id === selectedPhaseId ? "true" : undefined}
            onClick={() => onSelect(phase.id)}
          >
            <span className="process-list-index">{i + 1}</span>
            <span className="process-list-body">
              <strong>{phase.title}</strong>
              <EvidenceBadge status={phase.dominantStatus} />
            </span>
          </button>
          {i < phases.length - 1 && (
            <span className="process-list-arrow" aria-hidden="true">
              ↓
            </span>
          )}
        </li>
      ))}
    </ol>
  );
}
