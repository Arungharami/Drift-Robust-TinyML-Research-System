"use client";

interface DigitalTwinHUDProps {
  showLabels: boolean;
  onToggleLabels: () => void;
  showDataFlow: boolean;
  onToggleDataFlow: () => void;
  exploded: boolean;
  onToggleExploded: () => void;
  onResetCamera: () => void;
}

/** Plain-HTML toolbar over the canvas — every toggle here has no hidden-only 3D effect. */
export function DigitalTwinHUD({
  showLabels,
  onToggleLabels,
  showDataFlow,
  onToggleDataFlow,
  exploded,
  onToggleExploded,
  onResetCamera,
}: DigitalTwinHUDProps) {
  return (
    <div className="twin-hud" role="toolbar" aria-label="Digital twin scene controls">
      <button type="button" className="btn" aria-pressed={showLabels} onClick={onToggleLabels}>
        {showLabels ? "Hide labels" : "Show labels"}
      </button>
      <button type="button" className="btn" aria-pressed={showDataFlow} onClick={onToggleDataFlow}>
        {showDataFlow ? "Hide data flow" : "Show data flow"}
      </button>
      <button type="button" className="btn" aria-pressed={exploded} onClick={onToggleExploded}>
        {exploded ? "Collapse spacing" : "Exploded spacing"}
      </button>
      <button type="button" className="btn" onClick={onResetCamera}>
        Reset camera
      </button>
    </div>
  );
}
