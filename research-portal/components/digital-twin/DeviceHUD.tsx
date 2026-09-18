"use client";

interface DeviceHUDProps {
  showLabels: boolean;
  onToggleLabels: () => void;
  exploded: boolean;
  onToggleExploded: () => void;
  onResetCamera: () => void;
}

/** Plain-HTML toolbar for the device view — assembled/exploded is the primary control here. */
export function DeviceHUD({ showLabels, onToggleLabels, exploded, onToggleExploded, onResetCamera }: DeviceHUDProps) {
  return (
    <div className="twin-hud" role="toolbar" aria-label="Device view controls">
      <button type="button" className="btn" aria-pressed={showLabels} onClick={onToggleLabels}>
        {showLabels ? "Hide labels" : "Show labels"}
      </button>
      <button type="button" className="btn" aria-pressed={exploded} onClick={onToggleExploded}>
        {exploded ? "Assembled view" : "Exploded view"}
      </button>
      <button type="button" className="btn" onClick={onResetCamera}>
        Reset camera
      </button>
    </div>
  );
}
