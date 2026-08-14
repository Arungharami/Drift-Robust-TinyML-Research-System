const DOCS = {
  prepare: "https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/prepare_board.html",
  current: "https://docs.nordicsemi.com/r/bundle/ug_nrf52840_dk/page/ug/dk/hw_measure_current.html",
  ppk2: "https://docs.nordicsemi.com/r/bundle/ug_ppk2/page/ug/ppk/measure_current_source_meter.html",
};

export function HardwareConnectionDiagram() {
  return <figure className="hardware-diagram">
    <div className="planned-label">PLANNED CONNECTION — NOT PHYSICALLY EXECUTED</div>
    <svg viewBox="0 0 1040 430" role="img" aria-labelledby="hardware-connection-title hardware-connection-desc">
      <title id="hardware-connection-title">Planned computer, PPK2, and nRF52840 DK measurement topology</title>
      <desc id="hardware-connection-desc">A computer connects to a Power Profiler Kit II over USB. The PPK2 planned VOUT and ground path supplies or measures an nRF52840 development kit through its dedicated measurement header. An optional GPIO trigger marks inference windows. Current traces return to the computer and are exported as files.</desc>
      <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" /></marker></defs>
      <g className="diagram-node"><rect x="25" y="85" width="240" height="180" rx="14"/><path d="M78 132h132v80H78zM60 230h168"/><text x="145" y="116">Computer</text><text x="145" y="158">nRF Connect for Desktop</text><text x="145" y="183">Power Profiler app</text><text x="145" y="250">raw trace + exports</text></g>
      <g className="diagram-node"><rect x="400" y="85" width="240" height="180" rx="14"/><rect x="455" y="125" width="130" height="85" rx="8"/><circle cx="480" cy="235" r="7"/><circle cx="515" cy="235" r="7"/><circle cx="550" cy="235" r="7"/><text x="520" y="116">Power Profiler Kit II</text><text x="520" y="160">SMU or ampere mode</text><text x="520" y="187">USB + digital input</text><text x="520" y="250">VOUT · GND · trigger</text></g>
      <g className="diagram-node"><rect x="775" y="85" width="240" height="180" rx="14"/><rect x="825" y="122" width="140" height="100" rx="6"/><circle cx="853" cy="150" r="9"/><circle cx="937" cy="150" r="9"/><text x="895" y="116">nRF52840 DK</text><text x="895" y="179">P22 / SB40 path</text><text x="895" y="204">optional GPIO trigger</text><text x="895" y="250">normal USB power off*</text></g>
      <path className="diagram-line" d="M265 135H400" markerEnd="url(#arrow)"/><text className="diagram-edge-label" x="332" y="122">USB</text>
      <path className="diagram-line power" d="M640 150H775" markerEnd="url(#arrow)"/><text className="diagram-edge-label" x="707" y="132">VOUT + GND</text>
      <path className="diagram-line trigger" d="M775 210H640" markerEnd="url(#arrow)"/><text className="diagram-edge-label" x="708" y="233">optional GPIO marker</text>
      <path className="diagram-line trace" d="M400 235C330 345 250 345 205 265" markerEnd="url(#arrow)"/><text className="diagram-edge-label" x="292" y="338">raw current trace</text>
      <g className="diagram-file"><path d="M420 330h220v62H420zM600 330v20h40"/><text x="530" y="357">hardware/ppk2_logs/</text><text x="530" y="379">exported trace destination</text></g>
      <path className="diagram-line trace" d="M265 265C320 300 355 345 420 360" markerEnd="url(#arrow)"/>
    </svg>
    <figcaption>Planned physical measurement topology. The PPK2 communicates with the Power Profiler application through USB and supplies or measures the nRF52840 DK through its dedicated current-measurement path. An optional GPIO trigger can mark inference and explanation windows. This diagram documents the proposed setup and is not evidence that physical measurement has occurred.<span>* P22/SB40 preparation, measurement mode, and removal of normal DK USB power depend on the verified DK revision and official Nordic procedure; no board modification is instructed or recorded here.</span></figcaption>
    <div className="diagram-links" aria-label="Official Nordic connection guidance"><a href={DOCS.prepare} target="_blank" rel="noreferrer">Prepare the DK</a><a href={DOCS.current} target="_blank" rel="noreferrer">DK current measurement</a><a href={DOCS.ppk2} target="_blank" rel="noreferrer">PPK2 source-meter guidance</a></div>
  </figure>;
}
