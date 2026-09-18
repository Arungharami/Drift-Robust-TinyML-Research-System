# Device View (`/digital-twin/device`)

Status: implemented, Phase C. Extends the Phase-B digital twin
(`docs/architecture/current-system-audit.md`, section "3D Digital Twin") — it
does not replace or duplicate it.

## What this page is

An exploded, layer-by-layer 3D view of the *planned* physical TinyML device,
from the top enclosure down through the nRF52840 MCU to the bottom enclosure.
It is the same evidence-driven pattern as `/digital-twin`, applied at a finer
physical granularity (10 device layers instead of 8 pipeline-stage nodes).

## Conceptual geometry

Every shape on this page is procedural (boxes, cylinders, a wireframe status
core) — there is no CAD import and no photogrammetric scan. The page carries a
visible `CONCEPTUAL ENGINEERING VIEW` flag
(`components/digital-twin/DeviceLegend.tsx`) for exactly this reason, mirroring
the `CONCEPTUAL_3D_MODEL` framing already established on `/digital-twin`.

Where no physical component has actually been selected (enclosure, PCB,
signal-acquisition circuit, power regulation, communication interface), the
layer is named generically — e.g. "Signal Acquisition Module" — rather than
naming a specific part number that was never chosen. Only the nRF52840 itself
is named specifically, because it is the repository's actual, documented
hardware target.

## Component hierarchy

`components/digital-twin/device-data.ts` (`buildDeviceLayers()`) defines the
10 layers, top to bottom: Top Enclosure, Sample Chamber, Sensor Array,
Signal Acquisition Module, Main PCB, nRF52840 MCU, Model/Inference Layer,
Communication Layer, Power Layer, Bottom Enclosure. Three of these
(`sensor-chamber`, `sensor-array`, `mcu`) intentionally reuse the exact same
`id` as their `/digital-twin` counterpart in `twin-data.ts`, so the two pages
describe "the same thing" rather than two independently-derived facts —
selecting the MCU on either page is the same evidence, not a re-derivation.

## Scientific status rules

Every status is read through `research-portal/lib/evidence.ts`, the same rule
every other page in the portal follows. Concretely:

- MCU implementation status comes from `stage15_hardware_gate.flash`; its
  separate **hardware status** comes from `stage15_hardware_gate
  .scientific_execution_status` (`BLOCKED_HARDWARE`) — these are two different,
  real fields from `results/embedded/stage15_hardware_detection.json`, not one
  value duplicated to look more detailed.
- The Model/Inference layer's status comes from
  `embedded.fp32_summary.scientific_execution_status`, with an explicit note
  that this is a host-compiled (x86-64, Zig cc) numerical-equivalence build,
  never cross-compiled for Cortex-M4F.
- Layers with no corresponding code or protocol at all (enclosures, PCB,
  signal acquisition, communication, power) are marked `PLANNED`, not
  `NOT_EXECUTED` — `PLANNED` here means "architecture placeholder, work never
  started," which is the honest state.
- The Resource Evidence section reuses `components/HardwareStatus.tsx`
  verbatim (imported, not re-implemented) — the same component already used on
  `/hardware` and already covered by
  `tests/test_hardware_portal.py::test_hardware_mobile_cards_and_measurement_states`.
  This guarantees Flash/RAM/latency/energy can never silently diverge into a
  second source of truth between the two pages.

## Accessibility

- `DeviceExplorer` renders `TwinComponentList` (unchanged from Phase B) below
  the canvas — every layer is a keyboard-operable button with the same
  name/status/role information the 3D inspector shows.
- WebGL-unsupported and canvas-crash fallbacks reuse `TwinCanvasBoundary`
  unchanged from Phase B.
- `prefers-reduced-motion` is read the same way as `/digital-twin`; the device
  scene has no particle/data-flow animation to begin with; assembled/exploded
  transitions are a direct camera-relative position change, not an animated
  tween, so there is nothing further to gate behind the media query.

## Performance

The three.js/@react-three/fiber/@react-three/drei bundle is loaded through
`next/dynamic(..., { ssr: false })` in `DeviceLoader.tsx` — identical strategy
to `DigitalTwinLoader.tsx`. Next.js deduplicates this into the same lazy chunk
already used by `/digital-twin`, so visiting `/digital-twin/device` first does
not double-load the 3D runtime, and visiting neither page never loads it at
all. No route outside `/digital-twin*` references three.js.

## URL state

`?component=<id>` deep-links a specific layer (e.g.
`/digital-twin/device?component=mcu`). This is read client-side in
`DeviceExplorer.tsx` on mount and kept in sync via `router.replace(...,
{ scroll: false })` on selection — the same component ids used throughout this
file, no separate slug vocabulary.

## Future real-asset integration

Geometry is intentionally decoupled from metadata: `DeviceScene.tsx` switches
on `component.id` to pick a geometry component (`SampleChamber`,
`SensorArrayNode`, `MCUBoard`, `ProcessingNode`, or the generic `LayerPanel`
fallback). To replace a layer's procedural shape with a real `.glb` derived
from CAD or a physical scan later:

1. Add the asset under `research-portal/public/models/` (or another Next.js
   static asset path).
2. Add a geometry component that loads it with drei's `useGLTF`, matching the
   existing `NodeProps` shape (`component`, `position`, `selected`,
   `showLabels`, `onSelect`) so it drops into `TwinNodeShell` unchanged.
3. Add one `case` to the switch in `DeviceScene.tsx` for that component's id.

No change to `device-data.ts`, `ComponentInspector.tsx`, or the accessibility
list is needed — metadata and geometry are already separate concerns. Until
real CAD exists, the `CONCEPTUAL ENGINEERING VIEW` label and `DeviceLegend`
disclaimer must stay.
