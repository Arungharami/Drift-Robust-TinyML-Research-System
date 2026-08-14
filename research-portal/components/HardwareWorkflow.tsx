const STEPS = ["Model export", "Firmware build", "Board programming", "Functional validation", "Repeated inference", "PPK2 trace capture", "Trigger-window extraction", "Energy integration", "Evidence registration"];

export function HardwareWorkflow() {
  return <figure className="workflow-figure"><ol className="hardware-workflow" aria-label="Planned physical measurement workflow">{STEPS.map((label, index) => <li className={`workflow-step workflow-${index === 0 ? "complete" : "blocked"}`} key={label}><span className="workflow-number">{index + 1}</span><strong>{label}</strong><small>{index === 0 ? "Host artifact available" : "Blocked by hardware"}</small></li>)}</ol><figcaption>After real traces exist, inference and explanation windows will be integrated separately using <code>E = ∫ V(t)I(t)dt</code>. No post-detection step is shown as completed.</figcaption></figure>;
}
